from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import requests
import re
from contextlib import asynccontextmanager
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
import jwt
import bcrypt
import resend

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'catholic_voices')]

# YouTube API configuration
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
DAILY_SAINTS_PLAYLIST_ID = 'PLSFbA-IaB3xprRODsXjEiXMV6QF9iGXol'
YOUTUBE_API_BASE = 'https://www.googleapis.com/youtube/v3'

# Admin/Auth configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH', '')

# Email configuration (Resend)
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', '')

# Initialize Resend
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# Security
security = HTTPBearer()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Scheduler for daily saint updates
scheduler = AsyncIOScheduler()

# ===================================
# YOUTUBE API HELPER FUNCTIONS
# ===================================

def parse_duration_to_seconds(duration_str: str) -> int:
    """Convert YouTube duration format (PT1M30S) to seconds"""
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return 0
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    return hours * 3600 + minutes * 60 + seconds

def is_youtube_short(duration_str: str) -> bool:
    """Check if video duration qualifies as a Short (≤ 3 minutes / 180 seconds)"""
    return parse_duration_to_seconds(duration_str) <= 180

def extract_saint_name_from_title(title: str) -> str:
    """Extract saint name from video title"""
    # Common patterns
    patterns = [
        r'St\.\s+([A-Za-z\s]+?)(?:\s*[-|•]|\s*\(|$)',
        r'Saint\s+([A-Za-z\s]+?)(?:\s*[-|•]|\s*\(|$)',
        r'^([A-Za-z\s]+?)(?:\s*[-|•]|\s*\()',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            saint_name = match.group(1).strip()
            if not saint_name.lower().startswith('st'):
                return f"St. {saint_name}"
            return saint_name
    
    # Fallback: use title cleaned up
    return title.split('-')[0].split('|')[0].strip()

def get_video_details(video_id: str) -> dict:
    """Get detailed information about a specific video"""
    try:
        url = f"{YOUTUBE_API_BASE}/videos"
        params = {
            'key': YOUTUBE_API_KEY,
            'id': video_id,
            'part': 'contentDetails,snippet'
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('items'):
            item = data['items'][0]
            return {
                'duration': item['contentDetails']['duration'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'publishedAt': item['snippet']['publishedAt'],
                'thumbnail': item['snippet']['thumbnails'].get('maxres', 
                    item['snippet']['thumbnails'].get('high', 
                    item['snippet']['thumbnails'].get('medium', 
                    item['snippet']['thumbnails'].get('default', {})))).get('url', '')
            }
        return {}
    except Exception as e:
        logger.error(f"Error fetching video details: {str(e)}")
        return {}

def fetch_playlist_videos(playlist_id: str, max_results: int = 50) -> List[dict]:
    """Fetch videos from a YouTube playlist"""
    videos = []
    next_page_token = None
    
    try:
        while len(videos) < max_results:
            url = f"{YOUTUBE_API_BASE}/playlistItems"
            params = {
                'key': YOUTUBE_API_KEY,
                'playlistId': playlist_id,
                'part': 'snippet',
                'maxResults': min(50, max_results - len(videos))
            }
            if next_page_token:
                params['pageToken'] = next_page_token
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            for item in data.get('items', []):
                video_id = item['snippet']['resourceId']['videoId']
                snippet = item['snippet']
                
                # Get additional video details
                details = get_video_details(video_id)
                
                video_data = {
                    'videoId': video_id,
                    'title': snippet['title'],
                    'description': snippet['description'],
                    'thumbnail': details.get('thumbnail', 
                        snippet['thumbnails'].get('high', snippet['thumbnails'].get('default', {})).get('url', '')),
                    'duration': details.get('duration', 'PT0S'),
                    'publishedAt': snippet['publishedAt'],
                    'isShort': is_youtube_short(details.get('duration', 'PT0S')),
                    'cachedAt': datetime.utcnow().isoformat()
                }
                videos.append(video_data)
            
            next_page_token = data.get('nextPageToken')
            if not next_page_token:
                break
                
        logger.info(f"Fetched {len(videos)} videos from playlist {playlist_id}")
        return videos
    except Exception as e:
        logger.error(f"Error fetching playlist videos: {str(e)}")
        return []

async def update_daily_saint():
    """
    Update the daily saint from YouTube playlist.
    Checks for Shorts published at or after 3:00 PM CST.
    """
    logger.info("Running daily saint update job...")
    
    try:
        # Get CST timezone
        cst = pytz.timezone('America/Chicago')
        now_cst = datetime.now(cst)
        today_str = now_cst.strftime('%Y-%m-%d')
        
        # Define 3:00 PM CST today
        three_pm_cst = cst.localize(datetime.strptime(f"{today_str} 15:00:00", '%Y-%m-%d %H:%M:%S'))
        
        # Fetch latest videos from the Daily Saints playlist
        videos = fetch_playlist_videos(DAILY_SAINTS_PLAYLIST_ID, max_results=20)
        
        # Filter for Shorts only
        shorts = [v for v in videos if v.get('isShort', False)]
        
        if not shorts:
            logger.warning("No Shorts found in the Daily Saints playlist")
            return
        
        # Find the most recent Short published at or after 3:00 PM CST
        qualifying_saint = None
        for video in shorts:
            try:
                published_at = datetime.fromisoformat(video['publishedAt'].replace('Z', '+00:00'))
                published_cst = published_at.astimezone(cst)
                
                # Check if published today at or after 3 PM CST
                if published_cst >= three_pm_cst:
                    if qualifying_saint is None or published_at > datetime.fromisoformat(qualifying_saint['publishedAt'].replace('Z', '+00:00')):
                        qualifying_saint = video
            except Exception as e:
                logger.error(f"Error parsing date for video {video['videoId']}: {e}")
                continue
        
        # If no video published after 3 PM today, use the most recent Short
        if qualifying_saint is None and shorts:
            qualifying_saint = shorts[0]
            logger.info("No Short published after 3 PM CST today, using most recent Short")
        
        if qualifying_saint:
            # Extract saint name from title
            saint_name = extract_saint_name_from_title(qualifying_saint['title'])
            
            # Create saint entry
            saint_entry = {
                'id': str(uuid.uuid4()),
                'videoId': qualifying_saint['videoId'],
                'saintName': saint_name,
                'feastDate': today_str,
                'description': qualifying_saint['description'],
                'thumbnail': qualifying_saint['thumbnail'],
                'youtubeUrl': f"https://www.youtube.com/shorts/{qualifying_saint['videoId']}",
                'publishedAt': qualifying_saint['publishedAt'],
                'createdAt': datetime.utcnow().isoformat(),
                'isActive': True
            }
            
            # Archive previous active saint
            await db.daily_saints.update_many(
                {'isActive': True},
                {'$set': {'isActive': False}}
            )
            
            # Check if saint for today already exists
            existing = await db.daily_saints.find_one({'feastDate': today_str})
            if existing:
                await db.daily_saints.update_one(
                    {'feastDate': today_str},
                    {'$set': saint_entry}
                )
                logger.info(f"Updated daily saint for {today_str}: {saint_name}")
            else:
                await db.daily_saints.insert_one(saint_entry)
                logger.info(f"Created new daily saint for {today_str}: {saint_name}")
                
    except Exception as e:
        logger.error(f"Error updating daily saint: {str(e)}")

# ===================================
# APP LIFECYCLE
# ===================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Catholic Voices & Prayers API...")
    
    # Start scheduler for daily saint updates at 3:15 PM CST
    scheduler.add_job(
        update_daily_saint,
        CronTrigger(hour=15, minute=15, timezone='America/Chicago'),
        id='daily_saint_update',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started - Daily saint update at 3:15 PM CST")
    
    # Run initial saint update if none exists for today
    cst = pytz.timezone('America/Chicago')
    today_str = datetime.now(cst).strftime('%Y-%m-%d')
    existing_saint = await db.daily_saints.find_one({'feastDate': today_str})
    if not existing_saint and YOUTUBE_API_KEY:
        logger.info("No saint for today, running initial update...")
        await update_daily_saint()
    
    yield
    
    # Shutdown
    scheduler.shutdown()
    client.close()
    logger.info("API shutdown complete")

# Create the main app
app = FastAPI(lifespan=lifespan, title="Catholic Voices & Prayers API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ===================================
# PYDANTIC MODELS
# ===================================

class SaintModel(BaseModel):
    id: Optional[str] = None
    videoId: str
    saintName: str
    feastDate: str
    description: str
    thumbnail: str
    youtubeUrl: str
    publishedAt: Optional[str] = None
    notice: Optional[str] = None

class ContentItem(BaseModel):
    id: Optional[str] = None
    videoId: str
    title: str
    description: str
    thumbnail: str
    category: str = "Prayers"
    duration: str
    publishedAt: str
    isShort: bool = False
    prayerText: Optional[str] = None
    hasPrayerText: bool = False

class PrayerCreate(BaseModel):
    title: str
    videoId: str
    prayerText: str
    category: str = "General"

class MassLocationCreate(BaseModel):
    name: str
    entity_type: str = "Parish"
    jurisdiction: str = "Diocese"
    affiliation: str
    rite: str = "Latin"
    use_or_liturgy: str = "1962 Roman Missal"
    street: Optional[str] = None
    city: str
    state: str
    zip_code: Optional[str] = None
    country: str = "USA"
    latitude: float
    longitude: float
    mass_schedule_url: Optional[str] = None
    website_url: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None

# ===================================
# HELPER FUNCTIONS
# ===================================

def saint_helper(saint) -> dict:
    return {
        "id": saint.get("id", str(saint.get("_id", ""))),
        "videoId": saint["videoId"],
        "saintName": saint["saintName"],
        "feastDate": saint["feastDate"],
        "description": saint.get("description", ""),
        "thumbnail": saint.get("thumbnail", ""),
        "youtubeUrl": saint.get("youtubeUrl", f"https://www.youtube.com/shorts/{saint['videoId']}"),
        "publishedAt": saint.get("publishedAt", ""),
        "notice": saint.get("notice")
    }

def content_helper(video, prayer=None) -> dict:
    return {
        "id": video.get("id", str(video.get("_id", ""))),
        "videoId": video["videoId"],
        "title": video["title"],
        "description": video.get("description", ""),
        "thumbnail": video.get("thumbnail", ""),
        "category": video.get("category", "Prayers"),
        "duration": video.get("duration", ""),
        "publishedAt": video.get("publishedAt", ""),
        "isShort": video.get("isShort", False),
        "prayerText": prayer.get("prayerText") if prayer else None,
        "hasPrayerText": prayer is not None
    }

def mass_location_helper(loc) -> dict:
    return {
        "id": str(loc.get("_id", loc.get("id", ""))),
        "location_id": loc.get("location_id", str(loc.get("_id", ""))),
        "name": loc["name"],
        "entity_type": loc.get("entity_type", "Parish"),
        "jurisdiction": loc.get("jurisdiction", "Diocese"),
        "affiliation": loc["affiliation"],
        "rite": loc.get("rite", "Latin"),
        "use_or_liturgy": loc.get("use_or_liturgy", "1962 Roman Missal"),
        "street": loc.get("street", ""),
        "city": loc["city"],
        "state": loc["state"],
        "zip_code": loc.get("zip_code", ""),
        "country": loc.get("country", "USA"),
        "latitude": loc["latitude"],
        "longitude": loc["longitude"],
        "mass_schedule_url": loc.get("mass_schedule_url"),
        "website_url": loc.get("website_url"),
        "phone": loc.get("phone"),
        "notes": loc.get("notes"),
        "distance_miles": loc.get("distance_miles")
    }

# Sedevacantist groups to exclude (non-negotiable)
EXCLUDED_GROUPS = [
    'cmri', 'sspv', 'sspx-mc', 'sspx marian corps',
    'sedevacantist', 'vacantist', 'non una cum'
]

def check_exclusion(name: str, affiliation: str, notes: str = "") -> tuple:
    """Check if location should be excluded based on sedevacantist affiliation"""
    combined_text = f"{name} {affiliation} {notes}".lower()
    for excluded in EXCLUDED_GROUPS:
        if excluded in combined_text:
            return True, f"Matches excluded group: {excluded}"
    return False, None

# ===================================
# API ROUTES - ROOT
# ===================================

@api_router.get("/")
async def root():
    return {"message": "Catholic Voices & Prayers API", "status": "running"}

@api_router.get("/health")
async def health_check():
    try:
        await db.command('ping')
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

# ===================================
# API ROUTES - DAILY SAINTS
# ===================================

@api_router.get("/saints/today")
async def get_todays_saint():
    """Get today's saint of the day"""
    cst = pytz.timezone('America/Chicago')
    today_str = datetime.now(cst).strftime('%Y-%m-%d')
    
    # First try to find today's saint
    saint = await db.daily_saints.find_one({'feastDate': today_str})
    
    if not saint:
        # Try to get the most recent active saint
        saint = await db.daily_saints.find_one(
            {'isActive': True},
            sort=[('feastDate', -1)]
        )
    
    if not saint:
        # Get any most recent saint
        saint = await db.daily_saints.find_one(
            {},
            sort=[('feastDate', -1)]
        )
    
    if saint:
        result = saint_helper(saint)
        # Add notice if not today's saint
        if saint.get('feastDate') != today_str:
            result['notice'] = "Today's saint will be posted shortly."
        return result
    
    raise HTTPException(status_code=404, detail="No daily saint available")

@api_router.get("/saints/archive")
async def get_saints_archive(limit: int = 24, offset: int = 0):
    """Get archive of all past saints"""
    total = await db.daily_saints.count_documents({})
    
    saints = await db.daily_saints.find({}).sort('feastDate', -1).skip(offset).limit(limit).to_list(limit)
    
    return {
        "saints": [saint_helper(s) for s in saints],
        "total": total,
        "hasMore": (offset + limit) < total
    }

@api_router.get("/saints/{saint_id}")
async def get_saint_by_id(saint_id: str):
    """Get a specific saint by ID"""
    saint = await db.daily_saints.find_one({'id': saint_id})
    if not saint:
        saint = await db.daily_saints.find_one({'videoId': saint_id})
    
    if saint:
        return saint_helper(saint)
    raise HTTPException(status_code=404, detail="Saint not found")

@api_router.post("/saints/refresh")
async def refresh_daily_saint(background_tasks: BackgroundTasks):
    """Manually trigger daily saint update"""
    background_tasks.add_task(update_daily_saint)
    return {"message": "Daily saint update triggered", "status": "processing"}

# ===================================
# API ROUTES - CONTENT & PRAYERS
# ===================================

@api_router.get("/content")
async def get_content(category: Optional[str] = None):
    """Get all primary content (long-form videos)"""
    query = {"isShort": {"$ne": True}}
    if category:
        query["category"] = category
    
    videos = await db.videos.find(query).sort("publishedAt", -1).to_list(100)
    
    content_items = []
    for video in videos:
        prayer = await db.prayers.find_one({"videoId": video["videoId"]})
        content_items.append(content_helper(video, prayer))
    
    return content_items

@api_router.get("/content/{video_id}")
async def get_content_item(video_id: str):
    """Get a specific content item"""
    video = await db.videos.find_one({"videoId": video_id})
    if not video:
        raise HTTPException(status_code=404, detail="Content not found")
    
    prayer = await db.prayers.find_one({"videoId": video_id})
    return content_helper(video, prayer)

@api_router.get("/videos/refresh")
async def refresh_videos():
    """Refresh video cache from YouTube channel"""
    # This would typically fetch from the main channel
    # For now, we'll use the playlist videos
    videos = fetch_playlist_videos(DAILY_SAINTS_PLAYLIST_ID, max_results=100)
    
    if videos:
        # Clear and refresh cache
        await db.videos.delete_many({})
        
        # Add category detection
        for video in videos:
            video['category'] = detect_category(video['title'], video['description'])
            video['id'] = str(uuid.uuid4())
        
        await db.videos.insert_many(videos)
        return {"message": f"Refreshed {len(videos)} videos", "count": len(videos)}
    
    return {"message": "No videos fetched", "count": 0}

def detect_category(title: str, description: str) -> str:
    """Detect prayer category from title and description"""
    title_lower = title.lower()
    desc_lower = description.lower()
    
    if any(kw in title_lower for kw in ['rosary', 'mysteries', 'decade']):
        return 'The Rosary'
    if any(kw in title_lower for kw in ['novena', '9 day', 'nine day']):
        return 'Novenas'
    if any(kw in title_lower for kw in ['saint', 'st.', 'feast']):
        return 'Saints & Feast Days'
    if any(kw in title_lower for kw in ['chaplet', 'litany', 'divine mercy']):
        return 'Devotions'
    
    return 'Prayers'

@api_router.get("/prayers")
async def get_prayers(category: Optional[str] = None):
    """Get all prayers"""
    query = {}
    if category:
        query["category"] = category
    
    prayers = await db.prayers.find(query).sort("createdAt", -1).to_list(100)
    return prayers

@api_router.post("/prayers")
async def create_prayer(prayer: PrayerCreate):
    """Create a new prayer"""
    prayer_dict = prayer.model_dump()
    prayer_dict['id'] = str(uuid.uuid4())
    prayer_dict['createdAt'] = datetime.utcnow().isoformat()
    
    await db.prayers.insert_one(prayer_dict)
    return prayer_dict

@api_router.get("/prayers/{prayer_id}")
async def get_prayer(prayer_id: str):
    """Get a specific prayer"""
    prayer = await db.prayers.find_one({"id": prayer_id})
    if not prayer:
        prayer = await db.prayers.find_one({"videoId": prayer_id})
    
    if prayer:
        prayer['_id'] = str(prayer['_id'])
        return prayer
    raise HTTPException(status_code=404, detail="Prayer not found")

# ===================================
# API ROUTES - MASS MAP
# ===================================

@api_router.get("/mass-locations")
async def get_mass_locations(
    affiliation: Optional[str] = None,
    rite: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = 500
):
    """Get all Mass locations with optional filters"""
    query = {"exclude_flag": {"$ne": True}}
    
    if affiliation:
        query["affiliation"] = affiliation
    if rite:
        query["rite"] = rite
    if state:
        query["state"] = {"$regex": state, "$options": "i"}
    
    locations = await db.mass_locations.find(query).limit(limit).to_list(limit)
    return [mass_location_helper(loc) for loc in locations]

@api_router.get("/mass-locations/search")
async def search_mass_locations(
    q: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius_miles: float = 50,
    affiliation: Optional[str] = None,
    rite: Optional[str] = None
):
    """Search Mass locations by text or proximity"""
    query = {"exclude_flag": {"$ne": True}}
    
    if affiliation:
        query["affiliation"] = affiliation
    if rite:
        query["rite"] = rite
    
    if q:
        query["$or"] = [
            {"city": {"$regex": q, "$options": "i"}},
            {"state": {"$regex": q, "$options": "i"}},
            {"zip_code": {"$regex": q, "$options": "i"}},
            {"name": {"$regex": q, "$options": "i"}}
        ]
    
    locations = await db.mass_locations.find(query).to_list(500)
    result = [mass_location_helper(loc) for loc in locations]
    
    # Filter by distance if coordinates provided
    if lat is not None and lng is not None:
        import math
        
        def haversine(lat1, lon1, lat2, lon2):
            R = 3959  # Earth's radius in miles
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            return R * c
        
        filtered = []
        for loc in result:
            if loc["latitude"] and loc["longitude"]:
                distance = haversine(lat, lng, loc["latitude"], loc["longitude"])
                if distance <= radius_miles:
                    loc["distance_miles"] = round(distance, 1)
                    filtered.append(loc)
        
        filtered.sort(key=lambda x: x.get("distance_miles", 999))
        return filtered
    
    return result

@api_router.get("/mass-locations/filters")
async def get_mass_location_filters():
    """Get available filter options"""
    query = {"exclude_flag": {"$ne": True}}
    
    affiliations = await db.mass_locations.distinct("affiliation", query)
    rites = await db.mass_locations.distinct("rite", query)
    liturgies = await db.mass_locations.distinct("use_or_liturgy", query)
    states = await db.mass_locations.distinct("state", query)
    
    return {
        "affiliations": sorted([a for a in affiliations if a]),
        "rites": sorted([r for r in rites if r]),
        "liturgies": sorted([l for l in liturgies if l]),
        "states": sorted([s for s in states if s])
    }

@api_router.get("/mass-locations/stats")
async def get_mass_location_stats():
    """Get Mass location statistics"""
    query = {"exclude_flag": {"$ne": True}}
    total = await db.mass_locations.count_documents(query)
    
    pipeline = [
        {"$match": query},
        {"$group": {"_id": "$affiliation", "count": {"$sum": 1}}}
    ]
    affiliation_counts = await db.mass_locations.aggregate(pipeline).to_list(100)
    by_affiliation = {item["_id"]: item["count"] for item in affiliation_counts if item["_id"]}
    
    pipeline = [
        {"$match": query},
        {"$group": {"_id": "$rite", "count": {"$sum": 1}}}
    ]
    rite_counts = await db.mass_locations.aggregate(pipeline).to_list(100)
    by_rite = {item["_id"]: item["count"] for item in rite_counts if item["_id"]}
    
    return {
        "total": total,
        "by_affiliation": by_affiliation,
        "by_rite": by_rite
    }

@api_router.get("/mass-locations/{location_id}")
async def get_mass_location(location_id: str):
    """Get a specific Mass location"""
    from bson import ObjectId
    try:
        location = await db.mass_locations.find_one({
            "_id": ObjectId(location_id),
            "exclude_flag": {"$ne": True}
        })
    except:
        location = await db.mass_locations.find_one({
            "id": location_id,
            "exclude_flag": {"$ne": True}
        })
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    return mass_location_helper(location)

@api_router.post("/mass-locations")
async def create_mass_location(location: MassLocationCreate):
    """Create a new Mass location"""
    exclude_flag, exclude_reason = check_exclusion(
        location.name,
        location.affiliation,
        location.notes or ""
    )
    
    location_dict = location.model_dump()
    location_dict["id"] = str(uuid.uuid4())
    location_dict["location_id"] = location_dict["id"]
    location_dict["exclude_flag"] = exclude_flag
    location_dict["exclude_reason"] = exclude_reason
    location_dict["created_at"] = datetime.utcnow().isoformat()
    
    # Check for duplicates
    existing = await db.mass_locations.find_one({
        "name": location.name,
        "city": location.city,
        "state": location.state
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Location already exists")
    
    await db.mass_locations.insert_one(location_dict)
    
    if exclude_flag:
        return {"message": "Location stored but excluded", "exclude_reason": exclude_reason}
    
    return mass_location_helper(location_dict)

@api_router.post("/mass-locations/seed")
async def seed_mass_locations():
    """Seed database with sample Mass locations"""
    sample_locations = [
        # Diocesan TLM
        {
            "name": "St. John Cantius Church",
            "entity_type": "Parish",
            "jurisdiction": "Diocese",
            "affiliation": "Diocesan",
            "rite": "Latin",
            "use_or_liturgy": "1962 Roman Missal",
            "street": "825 N Carpenter St",
            "city": "Chicago",
            "state": "IL",
            "zip_code": "60642",
            "country": "USA",
            "latitude": 41.8969,
            "longitude": -87.6524,
            "website_url": "https://www.cantius.org",
            "notes": "One of Chicago's premier Traditional Latin Mass parishes"
        },
        # FSSP
        {
            "name": "St. Mary Mother of God",
            "entity_type": "Parish",
            "jurisdiction": "Society",
            "affiliation": "FSSP",
            "rite": "Latin",
            "use_or_liturgy": "1962 Roman Missal",
            "street": "727 5th St NW",
            "city": "Washington",
            "state": "DC",
            "zip_code": "20001",
            "country": "USA",
            "latitude": 38.9006,
            "longitude": -77.0211,
            "notes": "FSSP Apostolate"
        },
        {
            "name": "Mater Dei Latin Mass Parish",
            "entity_type": "Parish",
            "jurisdiction": "Society",
            "affiliation": "FSSP",
            "rite": "Latin",
            "use_or_liturgy": "1962 Roman Missal",
            "street": "9550 Bauer Rd",
            "city": "Irving",
            "state": "TX",
            "zip_code": "75061",
            "country": "USA",
            "latitude": 32.8599,
            "longitude": -96.9808,
            "website_url": "https://materdeiparish.com"
        },
        # ICKSP
        {
            "name": "St. Francis de Sales Oratory",
            "entity_type": "Oratory",
            "jurisdiction": "Society",
            "affiliation": "ICKSP",
            "rite": "Latin",
            "use_or_liturgy": "1962 Roman Missal",
            "street": "2653 Ohio Ave",
            "city": "St. Louis",
            "state": "MO",
            "zip_code": "63118",
            "country": "USA",
            "latitude": 38.5934,
            "longitude": -90.2347,
            "website_url": "https://institute-christ-king.org/stlouis"
        },
        # Ordinariate
        {
            "name": "Our Lady of the Atonement",
            "entity_type": "Parish",
            "jurisdiction": "Ordinariate",
            "affiliation": "Ordinariate",
            "rite": "Latin",
            "use_or_liturgy": "Ordinariate Use",
            "street": "15415 Red Robin Rd",
            "city": "San Antonio",
            "state": "TX",
            "zip_code": "78255",
            "country": "USA",
            "latitude": 29.5889,
            "longitude": -98.6192,
            "website_url": "https://www.atonementonline.com"
        },
        {
            "name": "Our Lady of Walsingham",
            "entity_type": "Parish",
            "jurisdiction": "Ordinariate",
            "affiliation": "Ordinariate",
            "rite": "Latin",
            "use_or_liturgy": "Ordinariate Use",
            "street": "7809 Shadyvilla Ln",
            "city": "Houston",
            "state": "TX",
            "zip_code": "77055",
            "country": "USA",
            "latitude": 29.8055,
            "longitude": -95.4955,
            "website_url": "https://www.walsingham.org"
        },
        # SSPX
        {
            "name": "St. Mary's Church",
            "entity_type": "Chapel",
            "jurisdiction": "Society",
            "affiliation": "SSPX",
            "rite": "Latin",
            "use_or_liturgy": "1962 Roman Missal",
            "street": "411 N Rosemont St",
            "city": "St. Marys",
            "state": "KS",
            "zip_code": "66536",
            "country": "USA",
            "latitude": 39.1953,
            "longitude": -96.0718,
            "website_url": "https://sspx.org/en/chapel/st-marys-chapel-st-marys"
        },
        {
            "name": "Queen of Angels Chapel",
            "entity_type": "Chapel",
            "jurisdiction": "Society",
            "affiliation": "SSPX",
            "rite": "Latin",
            "use_or_liturgy": "1962 Roman Missal",
            "street": "12661 Shade Tree Ln",
            "city": "Dickinson",
            "state": "TX",
            "zip_code": "77539",
            "country": "USA",
            "latitude": 29.4563,
            "longitude": -95.0525
        },
        # Eastern Catholic - Byzantine
        {
            "name": "St. John Chrysostom Byzantine Catholic Church",
            "entity_type": "Parish",
            "jurisdiction": "Eparchy",
            "affiliation": "Eastern Catholic",
            "rite": "Byzantine",
            "use_or_liturgy": "Divine Liturgy",
            "street": "506 Saline St",
            "city": "Pittsburgh",
            "state": "PA",
            "zip_code": "15207",
            "country": "USA",
            "latitude": 40.4199,
            "longitude": -79.9233,
            "website_url": "https://stjohnsbyzantine.com"
        },
        # Eastern Catholic - Ukrainian
        {
            "name": "Immaculate Conception Ukrainian Catholic Cathedral",
            "entity_type": "Parish",
            "jurisdiction": "Eparchy",
            "affiliation": "Eastern Catholic",
            "rite": "Ukrainian",
            "use_or_liturgy": "Divine Liturgy",
            "street": "830 N Franklin St",
            "city": "Philadelphia",
            "state": "PA",
            "zip_code": "19123",
            "country": "USA",
            "latitude": 39.9633,
            "longitude": -75.1536
        },
        # Eastern Catholic - Maronite
        {
            "name": "Our Lady of Lebanon Maronite Cathedral",
            "entity_type": "Parish",
            "jurisdiction": "Eparchy",
            "affiliation": "Eastern Catholic",
            "rite": "Maronite",
            "use_or_liturgy": "Divine Liturgy",
            "street": "113 Remsen St",
            "city": "Brooklyn",
            "state": "NY",
            "zip_code": "11201",
            "country": "USA",
            "latitude": 40.6964,
            "longitude": -73.9969,
            "website_url": "https://ololc.org"
        },
        # Eastern Catholic - Melkite
        {
            "name": "Our Lady of the Annunciation Melkite Cathedral",
            "entity_type": "Parish",
            "jurisdiction": "Eparchy",
            "affiliation": "Eastern Catholic",
            "rite": "Melkite",
            "use_or_liturgy": "Divine Liturgy",
            "street": "7 VFW Parkway",
            "city": "West Roxbury",
            "state": "MA",
            "zip_code": "02132",
            "country": "USA",
            "latitude": 42.2794,
            "longitude": -71.1631,
            "website_url": "https://www.melkite.org/cathedral"
        },
        # Eastern Catholic - Chaldean
        {
            "name": "Mother of God Chaldean Catholic Church",
            "entity_type": "Parish",
            "jurisdiction": "Eparchy",
            "affiliation": "Eastern Catholic",
            "rite": "Chaldean",
            "use_or_liturgy": "Divine Liturgy",
            "street": "25585 Berg Rd",
            "city": "Southfield",
            "state": "MI",
            "zip_code": "48033",
            "country": "USA",
            "latitude": 42.4733,
            "longitude": -83.2691,
            "website_url": "https://www.mothergodchurch.org"
        }
    ]
    
    inserted_count = 0
    for loc in sample_locations:
        existing = await db.mass_locations.find_one({
            "name": loc["name"],
            "city": loc["city"],
            "state": loc["state"]
        })
        
        if existing:
            continue
        
        exclude_flag, exclude_reason = check_exclusion(
            loc["name"],
            loc["affiliation"],
            loc.get("notes", "")
        )
        
        loc["id"] = str(uuid.uuid4())
        loc["location_id"] = loc["id"]
        loc["exclude_flag"] = exclude_flag
        loc["exclude_reason"] = exclude_reason
        loc["created_at"] = datetime.utcnow().isoformat()
        
        await db.mass_locations.insert_one(loc)
        inserted_count += 1
    
    return {"message": f"Seeded {inserted_count} locations", "inserted": inserted_count}

@api_router.post("/mass-locations/scrape")
async def scrape_mass_locations(background_tasks: BackgroundTasks):
    """
    Trigger web scraper to fetch additional mass locations from:
    - ICKSP (Institute of Christ the King)
    - FSSP (Fraternity of St. Peter)
    - Latin Mass Directory
    
    This runs as a background task and may take several minutes.
    """
    import subprocess
    import sys
    
    async def run_scraper():
        try:
            logger.info("Starting mass location scraper...")
            result = subprocess.run(
                [sys.executable, "/app/scripts/scrape_locations.py"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            logger.info(f"Scraper completed. Output: {result.stdout}")
            if result.stderr:
                logger.error(f"Scraper errors: {result.stderr}")
        except Exception as e:
            logger.error(f"Scraper failed: {str(e)}")
    
    background_tasks.add_task(run_scraper)
    
    return {
        "message": "Scraper started in background. Check logs for progress.",
        "status": "running",
        "note": "This may take several minutes. Check /api/mass-locations/stats for updated counts."
    }

@api_router.get("/mass-locations/scraper-status")
async def get_scraper_status():
    """Check the current status and last run of the scraper"""
    # Get count of scraped locations
    scraped_count = await db.mass_locations.count_documents({
        "source": {"$exists": True}
    })
    
    # Get latest scraped entry
    latest = await db.mass_locations.find_one(
        {"source": {"$exists": True}},
        sort=[("created_at", -1)]
    )
    
    return {
        "scraped_locations": scraped_count,
        "last_scrape": latest.get("created_at") if latest else None,
        "sources": await db.mass_locations.distinct("source")
    }

# Include the router in the main app
app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
