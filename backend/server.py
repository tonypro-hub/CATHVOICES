from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Depends, Header, File, UploadFile
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
db = client[os.environ['DB_NAME']]

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

# Admin Models
class AdminLogin(BaseModel):
    username: str
    password: str

class AdminLocationUpdate(BaseModel):
    name: Optional[str] = None
    entity_type: Optional[str] = None
    affiliation: Optional[str] = None
    rite: Optional[str] = None
    use_or_liturgy: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    mass_schedule: Optional[str] = None
    website_url: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    diocese_or_archdiocese: Optional[str] = None
    public_access: Optional[str] = None

# User Suggestion Models
class LocationSuggestion(BaseModel):
    suggestion_type: str  # "edit" or "new"
    location_id: Optional[str] = None  # Only for edits
    user_email: EmailStr
    user_name: Optional[str] = None
    # Location fields (for new or suggested changes)
    name: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = "USA"
    affiliation: Optional[str] = None
    rite: Optional[str] = None
    mass_schedule: Optional[str] = None
    website_url: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    reason: Optional[str] = None  # Why they're suggesting the change
    honeypot: Optional[str] = None  # Anti-spam field (should be empty)

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
        "mass_schedule": loc.get("mass_schedule", ""),
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

# ===================================
# AUTHENTICATION HELPERS
# ===================================

def create_jwt_token(username: str) -> str:
    """Create a JWT token for admin authentication"""
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> dict:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency to verify admin authentication"""
    token = credentials.credentials
    payload = verify_jwt_token(token)
    return {"username": payload["sub"]}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def hash_password(password: str) -> str:
    """Hash a password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

async def send_suggestion_notification(suggestion: dict):
    """Send email notification for new suggestion"""
    if not RESEND_API_KEY or not ADMIN_EMAIL:
        logger.warning("Email not configured - skipping notification")
        return
    
    try:
        suggestion_type = "New Location" if suggestion.get("suggestion_type") == "new" else "Edit Suggestion"
        
        html_content = f"""
        <h2>New Location Suggestion</h2>
        <p><strong>Type:</strong> {suggestion_type}</p>
        <p><strong>From:</strong> {suggestion.get('user_name', 'Anonymous')} ({suggestion.get('user_email')})</p>
        <hr>
        <h3>Details:</h3>
        <ul>
            <li><strong>Name:</strong> {suggestion.get('name', 'N/A')}</li>
            <li><strong>Location:</strong> {suggestion.get('city', '')}, {suggestion.get('state', '')} {suggestion.get('country', '')}</li>
            <li><strong>Affiliation:</strong> {suggestion.get('affiliation', 'N/A')}</li>
            <li><strong>Address:</strong> {suggestion.get('street', 'N/A')}</li>
            <li><strong>Website:</strong> {suggestion.get('website_url', 'N/A')}</li>
        </ul>
        <p><strong>Reason/Notes:</strong> {suggestion.get('reason', 'No reason provided')}</p>
        <hr>
        <p><a href="{os.environ.get('REACT_APP_BACKEND_URL', '')}/admin/suggestions">Review in Admin Panel</a></p>
        """
        
        params = {
            "from": SENDER_EMAIL,
            "to": [ADMIN_EMAIL],
            "subject": f"[Catholic Voices] {suggestion_type}: {suggestion.get('name', 'Unknown')}",
            "html": html_content
        }
        
        await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Suggestion notification sent to {ADMIN_EMAIL}")
    except Exception as e:
        logger.error(f"Failed to send notification email: {str(e)}")

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

# Prayer playlist IDs (Catholic Voices and Prayers YouTube channel)
PRAYER_PLAYLISTS = {
    "rosary": os.environ.get("ROSARY_PLAYLIST_ID", ""),
    "novenas": os.environ.get("NOVENAS_PLAYLIST_ID", ""),
    "devotions": os.environ.get("DEVOTIONS_PLAYLIST_ID", "PLSFbA-IaB3xod9okzmBdtK4lYH5mKQAnx"),
    "fulton_sheen": os.environ.get("FULTON_SHEEN_PLAYLIST_ID", "PLSFbA-IaB3xo_0Ww_CToOktS5Z88eiPfC"),
    "saints": os.environ.get("SAINTS_PLAYLIST_ID", "PLSFbA-IaB3xprRODsXjEiXMV6QF9iGXol"),
}

def format_duration(duration_str: str) -> str:
    """Format YouTube duration (PT1H30M45S) to human readable"""
    seconds = parse_duration_to_seconds(duration_str)
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}:{secs:02d}"
    else:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours}:{mins:02d}:{secs:02d}"

def detect_prayer_category(title: str, description: str) -> str:
    """Detect prayer category from title and description"""
    title_lower = title.lower()
    desc_lower = description.lower()
    combined = title_lower + " " + desc_lower
    
    # Fulton Sheen detection (highest priority)
    if any(kw in combined for kw in ['fulton sheen', 'bishop sheen', 'archbishop sheen']):
        return 'fulton-sheen'
    
    # Rosary detection (actual rosary prayers, not just mentions)
    rosary_prayer_keywords = ['pray the rosary', 'praying the rosary', 'full rosary', 
                              'sorrowful mysteries', 'joyful mysteries', 'glorious mysteries', 
                              'luminous mysteries', 'scriptural rosary', 'rosary meditation']
    if any(kw in combined for kw in rosary_prayer_keywords):
        return 'rosary'
    
    # Novena detection (actual novena prayers)
    if any(kw in title_lower for kw in ['novena day', 'day 1', 'day 2', 'day 3', 'day 4', 
                                         'day 5', 'day 6', 'day 7', 'day 8', 'day 9']):
        return 'novenas'
    
    # Prayer/Devotion detection
    prayer_keywords = ['chaplet', 'divine mercy chaplet', 'litany of', 'stations of the cross',
                       'angelus', 'regina caeli', 'morning prayer', 'night prayer', 
                       'evening prayer', 'pray with', 'prayer to', 'act of contrition']
    if any(kw in combined for kw in prayer_keywords):
        return 'devotions'
    
    # Saints content
    saint_patterns = ['st.', 'saint', '| st ', 'feast day', 'martyred', 'patron saint']
    if any(kw in title_lower for kw in saint_patterns):
        return 'saints'
    
    # Teachings/Educational
    teaching_keywords = ['why do', 'what is', 'how to', 'explained', 'the truth about',
                         'mother angelica', 'fr.', 'father', 'bishop', 'pope']
    if any(kw in title_lower for kw in teaching_keywords):
        return 'teachings'
    
    return 'teachings'

def detect_rosary_mystery(title: str, description: str) -> str:
    """Detect which Rosary mystery type"""
    combined = (title + " " + description).lower()
    if 'sorrowful' in combined:
        return 'Sorrowful Mysteries'
    if 'joyful' in combined:
        return 'Joyful Mysteries'
    if 'glorious' in combined:
        return 'Glorious Mysteries'
    if 'luminous' in combined:
        return 'Luminous Mysteries'
    if 'scriptural' in combined:
        return 'Scriptural Rosary'
    return 'Holy Rosary'

def detect_novena_day(title: str) -> Optional[int]:
    """Extract novena day number from title"""
    import re
    match = re.search(r'day\s*(\d+)', title.lower())
    if match:
        return int(match.group(1))
    return None

def prayer_video_helper(video: dict) -> dict:
    """Convert video document to prayer video response"""
    category = video.get('category', detect_prayer_category(video.get('title', ''), video.get('description', '')))
    
    result = {
        "id": video.get("id", str(video.get("_id", ""))),
        "videoId": video["videoId"],
        "title": video["title"],
        "description": video.get("description", ""),
        "thumbnail": video.get("thumbnail", ""),
        "duration": video.get("duration", ""),
        "durationFormatted": format_duration(video.get("duration", "PT0S")),
        "publishedAt": video.get("publishedAt", ""),
        "category": category,
        "isFultonSheen": 'fulton sheen' in (video.get('title', '') + video.get('description', '')).lower()
    }
    
    # Add rosary-specific fields
    if category == 'rosary':
        result["mysteryType"] = detect_rosary_mystery(video.get("title", ""), video.get("description", ""))
    
    # Add novena-specific fields
    if category == 'novenas':
        result["novenaDay"] = detect_novena_day(video.get("title", ""))
    
    return result

@api_router.get("/prayer-library")
async def get_prayer_library():
    """Get overview of entire prayer library with categories"""
    # Get all prayer videos
    videos = await db.prayer_videos.find({}).to_list(500)
    
    # Categorize videos
    categories = {
        "rosary": {"name": "Rosaries", "description": "Pray the Holy Rosary", "videos": [], "count": 0},
        "novenas": {"name": "Novenas", "description": "Nine-day devotional prayers", "videos": [], "count": 0},
        "devotions": {"name": "Prayers & Devotions", "description": "Chaplets, Litanies & Traditional Prayers", "videos": [], "count": 0},
        "saints": {"name": "Lives of the Saints", "description": "Daily saints and feast day reflections", "videos": [], "count": 0},
        "teachings": {"name": "Catholic Teachings", "description": "Faith formation and spiritual guidance", "videos": [], "count": 0},
        "fulton-sheen": {"name": "Bishop Fulton J. Sheen", "description": "Wisdom from the Venerable Archbishop", "videos": [], "count": 0}
    }
    
    for video in videos:
        formatted = prayer_video_helper(video)
        cat = formatted["category"]
        if cat in categories:
            categories[cat]["videos"].append(formatted)
            categories[cat]["count"] += 1
        else:
            # Default to teachings if category not found
            categories["teachings"]["videos"].append(formatted)
            categories["teachings"]["count"] += 1
        
        # Also add Fulton Sheen videos to their special category
        if formatted["isFultonSheen"] and cat != "fulton-sheen":
            categories["fulton-sheen"]["videos"].append(formatted)
            categories["fulton-sheen"]["count"] += 1
    
    # Sort videos in each category and limit for overview
    for cat in categories.values():
        cat["videos"] = cat["videos"][:6]
    
    return {
        "categories": categories,
        "totalVideos": len(videos)
    }

@api_router.get("/prayer-library/rosary")
async def get_rosary_prayers():
    """Get all Rosary videos"""
    videos = await db.prayer_videos.find({
        "$or": [
            {"category": "rosary"},
            {"title": {"$regex": "rosary|mysteries", "$options": "i"}}
        ]
    }).sort("publishedAt", -1).to_list(100)
    
    # Group by mystery type
    by_mystery = {}
    all_videos = []
    
    for video in videos:
        formatted = prayer_video_helper(video)
        formatted["category"] = "rosary"
        mystery = formatted.get("mysteryType", "Holy Rosary")
        
        if mystery not in by_mystery:
            by_mystery[mystery] = []
        by_mystery[mystery].append(formatted)
        all_videos.append(formatted)
    
    return {
        "title": "The Holy Rosary",
        "description": "Pray the sacred mysteries of the Rosary with guided video meditations",
        "byMystery": by_mystery,
        "videos": all_videos,
        "count": len(all_videos)
    }

@api_router.get("/prayer-library/novenas")
async def get_novena_prayers():
    """Get all Novena videos"""
    videos = await db.prayer_videos.find({
        "$or": [
            {"category": "novenas"},
            {"title": {"$regex": "novena|day \\d", "$options": "i"}}
        ]
    }).sort("publishedAt", -1).to_list(200)
    
    # Group novenas by saint/devotion
    novena_groups = {}
    all_videos = []
    
    for video in videos:
        formatted = prayer_video_helper(video)
        formatted["category"] = "novenas"
        
        # Try to extract novena name
        title = video.get("title", "")
        novena_name = "Other Novenas"
        
        # Common novena patterns
        import re
        match = re.search(r'novena to (st\.?\s*\w+|our lady|sacred heart|divine mercy|holy spirit)', title, re.IGNORECASE)
        if match:
            novena_name = f"Novena to {match.group(1).title()}"
        elif 'st.' in title.lower() or 'saint' in title.lower():
            saint_match = re.search(r'(st\.?\s*\w+|saint\s+\w+)', title, re.IGNORECASE)
            if saint_match:
                novena_name = f"Novena to {saint_match.group(1).title()}"
        
        if novena_name not in novena_groups:
            novena_groups[novena_name] = {"name": novena_name, "days": []}
        
        novena_groups[novena_name]["days"].append(formatted)
        all_videos.append(formatted)
    
    # Sort days within each novena
    for group in novena_groups.values():
        group["days"].sort(key=lambda x: x.get("novenaDay") or 99)
    
    return {
        "title": "Novenas",
        "description": "Nine-day prayers of devotion to saints and sacred mysteries",
        "novenas": list(novena_groups.values()),
        "videos": all_videos,
        "count": len(all_videos)
    }

@api_router.get("/prayer-library/devotions")
async def get_devotion_prayers():
    """Get all prayers and devotions from the main devotions playlist"""
    
    # First try to get from database (cached from playlist)
    videos = await db.prayer_videos.find({
        "source_playlist": "devotions-main"
    }).sort("publishedAt", -1).to_list(100)
    
    # If no cached videos, fetch directly from playlist
    if not videos and YOUTUBE_API_KEY:
        playlist_id = PRAYER_PLAYLISTS.get("devotions", "PLSFbA-IaB3xod9okzmBdtK4lYH5mKQAnx")
        if playlist_id:
            try:
                playlist_videos = fetch_playlist_videos(playlist_id, max_results=100)
                for video in playlist_videos:
                    video_doc = {
                        "videoId": video.get("videoId"),
                        "title": video.get("title", ""),
                        "description": video.get("description", ""),
                        "thumbnail": video.get("thumbnail", ""),
                        "duration": video.get("duration", ""),
                        "publishedAt": video.get("publishedAt"),
                        "category": "devotions",
                        "source_playlist": "devotions-main",
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                    # Upsert to avoid duplicates
                    await db.prayer_videos.update_one(
                        {"videoId": video_doc["videoId"]},
                        {"$set": video_doc},
                        upsert=True
                    )
                # Re-fetch from database
                videos = await db.prayer_videos.find({
                    "source_playlist": "devotions-main"
                }).sort("publishedAt", -1).to_list(100)
            except Exception as e:
                logger.error(f"Error fetching devotions playlist: {str(e)}")
    
    # Group by category: Rosary, Novenas, Chaplets, Devotions, Sleep, Fulton Sheen, Mother Theresa
    categories = {
        "rosary": {"name": "Rosary", "videos": []},
        "novenas": {"name": "Novenas", "videos": []},
        "chaplets": {"name": "Chaplets", "videos": []},
        "devotions": {"name": "Devotions", "videos": []},
        "sleep": {"name": "Sleep", "videos": []},
        "fulton_sheen": {"name": "Fulton Sheen", "videos": []},
        "mother_theresa": {"name": "Mother Theresa", "videos": []},
    }
    
    all_videos = []
    for video in videos:
        title_lower = video.get("title", "").lower()
        description_lower = video.get("description", "").lower()
        combined = title_lower + " " + description_lower
        
        # Skip "Best of Catholic Teachings" video
        if 'best of catholic teachings' in title_lower:
            continue
        
        formatted = prayer_video_helper(video)
        formatted["category"] = "devotions"
        
        # Check if it's a rosary video
        is_rosary = 'rosary' in title_lower or 'mysteries' in title_lower
        
        # Check person associations
        is_mother_theresa = 'mother teresa' in combined or 'mother theresa' in combined or 'teresa of calcutta' in combined or 'saint teresa of calcutta' in combined
        is_fulton_sheen = 'fulton sheen' in combined or 'bishop sheen' in combined or 'archbishop sheen' in combined
        
        # Add to Rosary section if it's a rosary (including Fulton Sheen and Mother Theresa rosaries)
        if is_rosary:
            categories["rosary"]["videos"].append(formatted)
        
        # Categorize into person-specific sections (rosaries will appear in both places)
        if is_mother_theresa:
            categories["mother_theresa"]["videos"].append(formatted)
        elif is_fulton_sheen:
            categories["fulton_sheen"]["videos"].append(formatted)
        elif 'sleep' in title_lower or 'rest' in title_lower or 'night' in title_lower or 'calming' in title_lower or 'peaceful' in title_lower:
            categories["sleep"]["videos"].append(formatted)
        elif is_rosary:
            # Already added to rosary, don't add to other categories
            pass
        elif 'novena' in title_lower or 'day 1' in title_lower or 'day 2' in title_lower or '30 day' in title_lower:
            categories["novenas"]["videos"].append(formatted)
        elif 'chaplet' in title_lower or 'coronilla' in title_lower or 'divine mercy' in title_lower:
            categories["chaplets"]["videos"].append(formatted)
        else:
            categories["devotions"]["videos"].append(formatted)
        
        all_videos.append(formatted)
    
    # Filter out empty categories and maintain order
    category_order = ["rosary", "novenas", "chaplets", "devotions", "sleep", "fulton_sheen", "mother_theresa"]
    devotions = [categories[key] for key in category_order if categories[key]["videos"]]
    
    return {
        "title": "Prayers & Devotions",
        "description": "Traditional Catholic prayers, rosaries, novenas, chaplets, and devotions",
        "devotions": devotions,
        "videos": all_videos,
        "count": len(all_videos)
    }

@api_router.get("/prayer-library/fulton-sheen")
async def get_fulton_sheen_prayers():
    """Get all prayers from Bishop Fulton J. Sheen playlist, organized into Rosaries and Novenas & Devotions"""
    
    # First try to get from database (cached from playlist)
    videos = await db.prayer_videos.find({
        "source_playlist": "fulton-sheen"
    }).sort("publishedAt", -1).to_list(100)
    
    # If no cached videos, fetch directly from playlist
    if not videos and YOUTUBE_API_KEY:
        playlist_id = PRAYER_PLAYLISTS.get("fulton_sheen", "PLSFbA-IaB3xo_0Ww_CToOktS5Z88eiPfC")
        if playlist_id:
            try:
                playlist_videos = fetch_playlist_videos(playlist_id, max_results=100)
                for video in playlist_videos:
                    video_doc = {
                        "videoId": video.get("videoId"),
                        "title": video.get("title", ""),
                        "description": video.get("description", ""),
                        "thumbnail": video.get("thumbnail", ""),
                        "duration": video.get("duration", ""),
                        "publishedAt": video.get("publishedAt"),
                        "category": "fulton-sheen",
                        "source_playlist": "fulton-sheen",
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                    # Upsert to avoid duplicates
                    await db.prayer_videos.update_one(
                        {"videoId": video_doc["videoId"]},
                        {"$set": video_doc},
                        upsert=True
                    )
                # Re-fetch from database
                videos = await db.prayer_videos.find({
                    "source_playlist": "fulton-sheen"
                }).sort("publishedAt", -1).to_list(100)
            except Exception as e:
                logger.error(f"Error fetching Fulton Sheen playlist: {str(e)}")
    
    all_videos = [prayer_video_helper(v) for v in videos]
    
    # Categorize into Rosaries and Novenas & Devotions
    rosaries = []
    novenas_devotions = []
    
    for v in all_videos:
        title_lower = v.get('title', '').lower()
        # Check if it's a rosary
        if any(kw in title_lower for kw in ['rosary', 'mysteries', 'sorrowful', 'joyful', 'glorious', 'luminous']):
            rosaries.append(v)
        else:
            # Everything else goes to Novenas & Devotions
            novenas_devotions.append(v)
    
    return {
        "title": "Pray with Bishop Fulton J. Sheen",
        "description": "Experience the profound spiritual guidance of the Venerable Archbishop Fulton J. Sheen through these guided prayers and reflections.",
        "featured": True,
        "rosaries": rosaries,
        "novenas_devotions": novenas_devotions,
        "videos": all_videos,
        "count": len(all_videos)
    }

@api_router.get("/prayer-library/saints")
async def get_saints_videos():
    """Get all Saints content from the dedicated playlist"""
    
    # First try to get from database (cached from playlist)
    videos = await db.prayer_videos.find({
        "source_playlist": "saints"
    }).sort("publishedAt", -1).to_list(200)
    
    # If no cached videos, fetch directly from playlist
    if not videos and YOUTUBE_API_KEY:
        playlist_id = PRAYER_PLAYLISTS.get("saints", "PLSFbA-IaB3xprRODsXjEiXMV6QF9iGXol")
        if playlist_id:
            try:
                playlist_videos = fetch_playlist_videos(playlist_id, max_results=200)
                for video in playlist_videos:
                    video_doc = {
                        "videoId": video.get("videoId"),
                        "title": video.get("title", ""),
                        "description": video.get("description", ""),
                        "thumbnail": video.get("thumbnail", ""),
                        "duration": video.get("duration", ""),
                        "publishedAt": video.get("publishedAt"),
                        "category": "saints",
                        "source_playlist": "saints",
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                    # Upsert to avoid duplicates
                    await db.prayer_videos.update_one(
                        {"videoId": video_doc["videoId"]},
                        {"$set": video_doc},
                        upsert=True
                    )
                # Re-fetch from database
                videos = await db.prayer_videos.find({
                    "source_playlist": "saints"
                }).sort("publishedAt", -1).to_list(200)
            except Exception as e:
                logger.error(f"Error fetching Saints playlist: {str(e)}")
    
    all_videos = [prayer_video_helper(v) for v in videos]
    
    return {
        "title": "Lives of the Saints",
        "description": "Daily saint reflections and feast day celebrations",
        "videos": all_videos,
        "count": len(all_videos)
    }

@api_router.get("/prayer-library/teachings")
async def get_teachings_videos():
    """Get all Catholic teachings content"""
    videos = await db.prayer_videos.find({
        "$or": [
            {"category": "teachings"},
            {"title": {"$regex": "why|what|how|explained|truth", "$options": "i"}}
        ]
    }).sort("publishedAt", -1).to_list(200)
    
    all_videos = [prayer_video_helper(v) for v in videos]
    
    return {
        "title": "Catholic Teachings",
        "description": "Faith formation, doctrine, and spiritual guidance",
        "videos": all_videos,
        "count": len(all_videos)
    }

@api_router.get("/prayer-library/video/{video_id}")
async def get_prayer_video(video_id: str):
    """Get a specific prayer video"""
    video = await db.prayer_videos.find_one({
        "$or": [
            {"videoId": video_id},
            {"id": video_id}
        ]
    })
    
    if not video:
        raise HTTPException(status_code=404, detail="Prayer video not found")
    
    result = prayer_video_helper(video)
    
    # Get related videos (same category)
    category = result.get("category", "devotions")
    related = await db.prayer_videos.find({
        "category": category,
        "videoId": {"$ne": video_id}
    }).limit(4).to_list(4)
    
    result["related"] = [prayer_video_helper(v) for v in related]
    
    return result

@api_router.post("/prayer-library/refresh")
async def refresh_prayer_library(background_tasks: BackgroundTasks):
    """Refresh prayer library from YouTube playlists"""
    
    async def fetch_and_store_prayers():
        logger.info("Refreshing prayer library from YouTube...")
        all_videos = []
        
        # Fetch from channel uploads or specific playlists
        # Using the channel uploads playlist (UU + channel_id[2:])
        channel_id = os.environ.get("YOUTUBE_CHANNEL_ID", "UCQfLhz9_2IFyM5X_bBqFGqA")
        uploads_playlist = f"UU{channel_id[2:]}" if channel_id.startswith("UC") else channel_id
        
        try:
            videos = fetch_playlist_videos(uploads_playlist, max_results=200)
            
            for video in videos:
                category = detect_prayer_category(video.get('title', ''), video.get('description', ''))
                video['category'] = category
                video['id'] = str(uuid.uuid4())
                video['refreshedAt'] = datetime.utcnow().isoformat()
                all_videos.append(video)
            
            if all_videos:
                # Clear old data
                await db.prayer_videos.delete_many({})
                # Insert new data
                await db.prayer_videos.insert_many(all_videos)
                logger.info(f"Prayer library refreshed: {len(all_videos)} videos")
            
        except Exception as e:
            logger.error(f"Failed to refresh prayer library: {str(e)}")
    
    background_tasks.add_task(fetch_and_store_prayers)
    
    return {"message": "Prayer library refresh started", "status": "processing"}

# Legacy content endpoints (for backward compatibility)
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
    videos = fetch_playlist_videos(DAILY_SAINTS_PLAYLIST_ID, max_results=100)
    
    if videos:
        await db.videos.delete_many({})
        
        for video in videos:
            video['category'] = detect_prayer_category(video['title'], video['description'])
            video['id'] = str(uuid.uuid4())
        
        await db.videos.insert_many(videos)
        return {"message": f"Refreshed {len(videos)} videos", "count": len(videos)}
    
    return {"message": "No videos fetched", "count": 0}

def detect_category(title: str, description: str) -> str:
    """Detect prayer category from title and description (legacy)"""
    return detect_prayer_category(title, description)

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

# ===================================
# ADMIN AUTHENTICATION ENDPOINTS
# ===================================

@api_router.post("/admin/login")
async def admin_login(credentials: AdminLogin):
    """Admin login endpoint"""
    # Check username
    if credentials.username != ADMIN_USERNAME:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check password
    if not ADMIN_PASSWORD_HASH:
        # If no password hash set, reject all logins
        raise HTTPException(status_code=401, detail="Admin not configured")
    
    if not verify_password(credentials.password, ADMIN_PASSWORD_HASH):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate token
    token = create_jwt_token(credentials.username)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRATION_HOURS * 3600
    }

@api_router.get("/admin/me")
async def get_admin_info(admin: dict = Depends(get_current_admin)):
    """Get current admin info (verify token)"""
    return {"username": admin["username"], "authenticated": True}

@api_router.post("/admin/setup")
async def setup_admin(password: str):
    """
    One-time admin setup - generates password hash.
    This endpoint should be disabled in production after setup.
    """
    if ADMIN_PASSWORD_HASH:
        raise HTTPException(status_code=400, detail="Admin already configured")
    
    hashed = hash_password(password)
    return {
        "message": "Add this to your .env file",
        "ADMIN_PASSWORD_HASH": hashed,
        "note": "Then restart the backend"
    }

# ===================================
# ADMIN LOCATION MANAGEMENT
# ===================================

@api_router.get("/admin/locations")
async def admin_get_locations(
    admin: dict = Depends(get_current_admin),
    page: int = 1,
    limit: int = 50,
    search: str = "",
    affiliation: str = ""
):
    """Get all locations for admin (paginated)"""
    query = {"exclude_flag": {"$ne": True}}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"city": {"$regex": search, "$options": "i"}},
            {"state": {"$regex": search, "$options": "i"}}
        ]
    
    if affiliation:
        query["affiliation"] = affiliation
    
    skip = (page - 1) * limit
    
    total = await db.mass_locations.count_documents(query)
    locations = await db.mass_locations.find(query).skip(skip).limit(limit).to_list(limit)
    
    return {
        "locations": [mass_location_helper(loc) for loc in locations],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@api_router.get("/admin/locations/{location_id}")
async def admin_get_location(location_id: str, admin: dict = Depends(get_current_admin)):
    """Get a single location for editing"""
    location = await db.mass_locations.find_one({
        "$or": [
            {"id": location_id},
            {"location_id": location_id}
        ]
    })
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Return full document including all fields
    result = mass_location_helper(location)
    result["diocese_or_archdiocese"] = location.get("diocese_or_archdiocese", "")
    result["mass_schedule"] = location.get("mass_schedule", "")
    result["public_access"] = location.get("public_access", True)
    result["source"] = location.get("source", "")
    result["verification_status"] = location.get("verification_status", "")
    result["created_at"] = location.get("created_at", "")
    result["updated_at"] = location.get("updated_at", "")
    
    return result

@api_router.put("/admin/locations/{location_id}")
async def admin_update_location(
    location_id: str,
    update: AdminLocationUpdate,
    admin: dict = Depends(get_current_admin)
):
    """Update a location"""
    location = await db.mass_locations.find_one({
        "$or": [
            {"id": location_id},
            {"location_id": location_id}
        ]
    })
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Build update document
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    update_data["updated_by"] = admin["username"]
    
    await db.mass_locations.update_one(
        {"_id": location["_id"]},
        {"$set": update_data}
    )
    
    logger.info(f"Admin {admin['username']} updated location: {location_id}")
    
    return {"message": "Location updated successfully", "id": location_id}

@api_router.delete("/admin/locations/{location_id}")
async def admin_delete_location(location_id: str, admin: dict = Depends(get_current_admin)):
    """Delete (soft delete) a location"""
    result = await db.mass_locations.update_one(
        {"$or": [{"id": location_id}, {"location_id": location_id}]},
        {"$set": {
            "exclude_flag": True,
            "deleted_at": datetime.now(timezone.utc).isoformat(),
            "deleted_by": admin["username"]
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Location not found")
    
    logger.info(f"Admin {admin['username']} deleted location: {location_id}")
    
    return {"message": "Location deleted successfully"}

@api_router.post("/admin/locations")
async def admin_create_location(
    location: MassLocationCreate,
    admin: dict = Depends(get_current_admin)
):
    """Create a new location"""
    new_location = {
        "id": str(uuid.uuid4()),
        "location_id": str(uuid.uuid4()),
        **location.dict(),
        "exclude_flag": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": admin["username"],
        "source": "admin",
        "verification_status": "Verified"
    }
    
    await db.mass_locations.insert_one(new_location)
    
    logger.info(f"Admin {admin['username']} created location: {new_location['id']}")
    
    return {"message": "Location created successfully", "id": new_location["id"]}


@api_router.post("/admin/bulk-upload-mass-times")
async def admin_bulk_upload_mass_times(
    file: UploadFile = File(...),
    admin: dict = Depends(get_current_admin)
):
    """
    Bulk upload mass times from CSV file.
    Expected CSV format: name,mass_schedule
    - name: Parish/Chapel name (will be matched using fuzzy search)
    - mass_schedule: Mass times text (e.g., "Sun: 10 AM, Mon-Sat: 7 AM")
    """
    import csv
    import io
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    # Read CSV content
    try:
        content = await file.read()
        text_content = content.decode('utf-8-sig')  # Handle BOM
        reader = csv.DictReader(io.StringIO(text_content))
        
        # Validate headers
        required_headers = {'name', 'mass_schedule'}
        if not required_headers.issubset(set(reader.fieldnames or [])):
            raise HTTPException(
                status_code=400, 
                detail=f"CSV must have headers: {', '.join(required_headers)}. Found: {reader.fieldnames}"
            )
        
        results = {
            "updated": 0,
            "not_found": 0,
            "skipped": 0,
            "errors": [],
            "details": []
        }
        
        for row_num, row in enumerate(reader, start=2):
            name = row.get('name', '').strip()
            mass_schedule = row.get('mass_schedule', '').strip()
            
            if not name:
                results["skipped"] += 1
                continue
            
            if not mass_schedule:
                results["skipped"] += 1
                results["details"].append(f"Row {row_num}: Skipped '{name}' - no mass schedule provided")
                continue
            
            # Try to find matching location(s)
            # First try exact match, then partial match
            query = {"exclude_flag": {"$ne": True}}
            
            # Try exact match first
            location = await db.mass_locations.find_one({
                **query,
                "name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}
            })
            
            # If no exact match, try partial match
            if not location:
                location = await db.mass_locations.find_one({
                    **query,
                    "name": {"$regex": re.escape(name), "$options": "i"}
                })
            
            if location:
                # Update the location
                await db.mass_locations.update_one(
                    {"_id": location["_id"]},
                    {
                        "$set": {
                            "mass_schedule": mass_schedule,
                            "updated_at": datetime.now(timezone.utc).isoformat(),
                            "updated_by": f"bulk_upload:{admin['username']}"
                        }
                    }
                )
                results["updated"] += 1
                results["details"].append(f"Row {row_num}: Updated '{location['name']}' ({location['city']}, {location['state']})")
            else:
                results["not_found"] += 1
                results["details"].append(f"Row {row_num}: No match found for '{name}'")
        
        logger.info(f"Admin {admin['username']} bulk uploaded mass times: {results['updated']} updated, {results['not_found']} not found")
        
        return {
            "message": f"Bulk upload complete. {results['updated']} locations updated.",
            "summary": {
                "updated": results["updated"],
                "not_found": results["not_found"],
                "skipped": results["skipped"]
            },
            "details": results["details"][:50]  # Limit details to prevent huge response
        }
        
    except csv.Error as e:
        raise HTTPException(status_code=400, detail=f"CSV parsing error: {str(e)}")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding error. Please use UTF-8 encoded CSV.")
    except Exception as e:
        logger.error(f"Bulk upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# ===================================
# USER SUGGESTION ENDPOINTS
# ===================================

@api_router.post("/suggestions")
async def submit_suggestion(suggestion: LocationSuggestion, background_tasks: BackgroundTasks):
    """Submit a location suggestion (new or edit)"""
    
    # Anti-spam: honeypot check
    if suggestion.honeypot:
        # Bot detected - silently accept but don't save
        return {"message": "Thank you for your suggestion!", "id": "spam-detected"}
    
    # Create suggestion document
    suggestion_doc = {
        "id": str(uuid.uuid4()),
        "suggestion_type": suggestion.suggestion_type,
        "location_id": suggestion.location_id,
        "user_email": suggestion.user_email,
        "user_name": suggestion.user_name,
        "name": suggestion.name,
        "street": suggestion.street,
        "city": suggestion.city,
        "state": suggestion.state,
        "zip_code": suggestion.zip_code,
        "country": suggestion.country,
        "affiliation": suggestion.affiliation,
        "rite": suggestion.rite,
        "mass_schedule": suggestion.mass_schedule,
        "website_url": suggestion.website_url,
        "phone": suggestion.phone,
        "notes": suggestion.notes,
        "reason": suggestion.reason,
        "status": "pending",  # pending, approved, rejected
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.location_suggestions.insert_one(suggestion_doc)
    
    logger.info(f"New suggestion submitted: {suggestion_doc['id']} from {suggestion.user_email}")
    
    # Send email notification in background
    background_tasks.add_task(send_suggestion_notification, suggestion_doc)
    
    return {
        "message": "Thank you for your suggestion! We'll review it soon.",
        "id": suggestion_doc["id"]
    }

@api_router.get("/admin/suggestions")
async def admin_get_suggestions(
    admin: dict = Depends(get_current_admin),
    status: str = "",
    page: int = 1,
    limit: int = 20
):
    """Get all suggestions for admin review"""
    query = {}
    if status:
        query["status"] = status
    
    skip = (page - 1) * limit
    
    total = await db.location_suggestions.count_documents(query)
    suggestions = await db.location_suggestions.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Remove MongoDB _id
    for s in suggestions:
        s.pop("_id", None)
    
    return {
        "suggestions": suggestions,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@api_router.get("/admin/suggestions/{suggestion_id}")
async def admin_get_suggestion(suggestion_id: str, admin: dict = Depends(get_current_admin)):
    """Get a single suggestion"""
    suggestion = await db.location_suggestions.find_one({"id": suggestion_id})
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    suggestion.pop("_id", None)
    
    # If it's an edit, also get the original location
    if suggestion.get("location_id"):
        original = await db.mass_locations.find_one({
            "$or": [
                {"id": suggestion["location_id"]},
                {"location_id": suggestion["location_id"]}
            ]
        })
        if original:
            suggestion["original_location"] = mass_location_helper(original)
    
    return suggestion

@api_router.put("/admin/suggestions/{suggestion_id}")
async def admin_update_suggestion(
    suggestion_id: str,
    action: str,  # "approve" or "reject"
    admin: dict = Depends(get_current_admin)
):
    """Approve or reject a suggestion"""
    suggestion = await db.location_suggestions.find_one({"id": suggestion_id})
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    if action == "approve":
        # Apply the suggestion
        if suggestion["suggestion_type"] == "new":
            # Create new location
            new_location = {
                "id": str(uuid.uuid4()),
                "location_id": str(uuid.uuid4()),
                "name": suggestion.get("name"),
                "street": suggestion.get("street", ""),
                "city": suggestion.get("city"),
                "state": suggestion.get("state"),
                "zip_code": suggestion.get("zip_code", ""),
                "country": suggestion.get("country", "USA"),
                "affiliation": suggestion.get("affiliation", "Diocesan"),
                "rite": suggestion.get("rite", "Latin"),
                "mass_schedule": suggestion.get("mass_schedule"),
                "website_url": suggestion.get("website_url"),
                "phone": suggestion.get("phone"),
                "notes": suggestion.get("notes"),
                "entity_type": "Parish",
                "latitude": 0,  # Will need geocoding
                "longitude": 0,
                "exclude_flag": False,
                "source": "user_suggestion",
                "verification_status": "User Submitted",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "approved_by": admin["username"]
            }
            await db.mass_locations.insert_one(new_location)
            logger.info(f"Created new location from suggestion: {new_location['id']}")
        else:
            # Update existing location
            update_data = {}
            for field in ["name", "street", "city", "state", "zip_code", "country", 
                         "affiliation", "rite", "mass_schedule", "website_url", "phone", "notes"]:
                if suggestion.get(field):
                    update_data[field] = suggestion[field]
            
            if update_data:
                update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
                update_data["updated_by"] = f"suggestion:{admin['username']}"
                
                await db.mass_locations.update_one(
                    {"$or": [
                        {"id": suggestion["location_id"]},
                        {"location_id": suggestion["location_id"]}
                    ]},
                    {"$set": update_data}
                )
                logger.info(f"Updated location from suggestion: {suggestion['location_id']}")
        
        status = "approved"
    else:
        status = "rejected"
    
    # Update suggestion status
    await db.location_suggestions.update_one(
        {"id": suggestion_id},
        {"$set": {
            "status": status,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "reviewed_by": admin["username"]
        }}
    )
    
    return {"message": f"Suggestion {status}", "id": suggestion_id}

@api_router.delete("/admin/suggestions/{suggestion_id}")
async def admin_delete_suggestion(suggestion_id: str, admin: dict = Depends(get_current_admin)):
    """Delete a suggestion"""
    result = await db.location_suggestions.delete_one({"id": suggestion_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    return {"message": "Suggestion deleted"}

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
