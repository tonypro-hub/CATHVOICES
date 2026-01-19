from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import requests
from bson import ObjectId


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# YouTube API configuration
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
YOUTUBE_CHANNEL_ID = os.environ.get('YOUTUBE_CHANNEL_ID')
YOUTUBE_API_BASE = 'https://www.googleapis.com/youtube/v3'

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class VideoModel(BaseModel):
    id: Optional[str] = None
    videoId: str
    title: str
    description: str
    thumbnail: str
    duration: str
    publishedAt: str
    cachedAt: datetime = Field(default_factory=datetime.utcnow)

class PrayerModel(BaseModel):
    id: Optional[str] = None
    title: str
    videoId: str
    prayerText: str
    category: Optional[str] = "General"
    createdAt: datetime = Field(default_factory=datetime.utcnow)

class PrayerCreate(BaseModel):
    title: str
    videoId: str
    prayerText: str
    category: Optional[str] = "General"

class FeastDayMapping(BaseModel):
    """Manual mapping of videos to feast days and saints"""
    id: Optional[str] = None
    videoId: str
    feastDate: str  # Format: "MM-DD" (e.g., "01-18" for January 18)
    saintName: Optional[str] = None  # e.g., "St. Prisca"
    feastName: Optional[str] = None  # e.g., "Feast of St. Prisca"
    liturgicalCalendar: str = "roman"  # roman, traditional, regional
    priority: int = 100  # Higher = takes precedence (manual=100, auto=50)
    notes: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    isManualOverride: bool = True


# Helper function to convert ObjectId to string
def prayer_helper(prayer) -> dict:
    return {
        "id": str(prayer["_id"]),
        "title": prayer["title"],
        "videoId": prayer["videoId"],
        "prayerText": prayer["prayerText"],
        "category": prayer.get("category", "General"),
        "createdAt": prayer.get("createdAt", datetime.utcnow())
    }

def video_helper(video) -> dict:
    return {
        "id": str(video["_id"]),
        "videoId": video["videoId"],
        "title": video["title"],
        "description": video["description"],
        "thumbnail": video["thumbnail"],
        "duration": video["duration"],
        "publishedAt": video["publishedAt"],
        "category": video.get("category", "Prayers"),
        "isShort": video.get("isShort", False),
        "cachedAt": video.get("cachedAt", datetime.utcnow())
    }


# YouTube API functions
def get_uploads_playlist_id():
    """Get the uploads playlist ID for the channel"""
    try:
        url = f"{YOUTUBE_API_BASE}/channels"
        params = {
            'key': YOUTUBE_API_KEY,
            'id': YOUTUBE_CHANNEL_ID,
            'part': 'contentDetails'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('items'):
            uploads_playlist_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            logging.info(f"Found uploads playlist ID: {uploads_playlist_id}")
            return uploads_playlist_id
        return None
    except Exception as e:
        logging.error(f"Error fetching uploads playlist ID: {str(e)}")
        return None

def parse_duration_to_seconds(duration_str: str):
    """Convert YouTube duration format (PT1M30S) to seconds"""
    import re
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return 0
    
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    
    return hours * 3600 + minutes * 60 + seconds

def is_youtube_short(video_details: dict):
    """Check if a video is a YouTube Short"""
    duration_str = video_details.get('duration', 'PT0S')
    duration_seconds = parse_duration_to_seconds(duration_str)
    
    # YouTube Shorts can be up to 3 minutes (180 seconds) as of 2024
    # But most traditional long-form content is significantly longer
    # We'll use 3 minutes as the cutoff for Shorts
    if duration_seconds <= 180:
        return True
    
    # Check if YouTube marks it as a short (sometimes in description or tags)
    description = video_details.get('description', '').lower()
    tags = video_details.get('tags', [])
    
    # Check for #shorts or #short tags
    if '#shorts' in description or '#short' in description:
        return True
    
    if tags:
        tags_lower = [tag.lower() for tag in tags]
        if 'shorts' in tags_lower or 'short' in tags_lower:
            return True
    
    return False

def fetch_youtube_videos():
    """Fetch ALL videos from channel's Uploads playlist, categorizing as long-form or Shorts"""
    try:
        # Step 1: Get the uploads playlist ID
        uploads_playlist_id = get_uploads_playlist_id()
        if not uploads_playlist_id:
            logging.error("Could not retrieve uploads playlist ID")
            return []
        
        all_videos = []
        shorts_videos = []
        next_page_token = None
        page_count = 0
        
        while True:
            page_count += 1
            logging.info(f"Fetching page {page_count} from uploads playlist...")
            
            url = f"{YOUTUBE_API_BASE}/playlistItems"
            params = {
                'key': YOUTUBE_API_KEY,
                'playlistId': uploads_playlist_id,
                'part': 'snippet',
                'maxResults': 50
            }
            
            if next_page_token:
                params['pageToken'] = next_page_token
                logging.info(f"Using pageToken: {next_page_token[:20]}...")
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            items_count = len(data.get('items', []))
            logging.info(f"Page {page_count}: Retrieved {items_count} items from playlist")
            
            # Process videos from this page
            for item in data.get('items', []):
                video_id = item['snippet']['resourceId']['videoId']
                snippet = item['snippet']
                
                # Get video details for duration and metadata
                video_details = get_video_details(video_id)
                
                # Extract category/tags from title and description
                category = extract_category_from_metadata(snippet['title'], snippet['description'])
                
                # Determine if it's a Short
                is_short = is_youtube_short(video_details)
                
                video_data = {
                    'videoId': video_id,
                    'title': snippet['title'],
                    'description': snippet['description'],
                    'thumbnail': snippet['thumbnails']['high']['url'] if 'high' in snippet['thumbnails'] else snippet['thumbnails']['default']['url'],
                    'duration': video_details.get('duration', 'Unknown'),
                    'publishedAt': snippet['publishedAt'],
                    'category': category,
                    'tags': video_details.get('tags', []),
                    'isShort': is_short,
                    'cachedAt': datetime.utcnow()
                }
                
                if is_short:
                    shorts_videos.append(video_data)
                    logging.info(f"Categorized as Short: {snippet['title'][:50]}...")
                else:
                    all_videos.append(video_data)
            
            # Check if there are more pages
            next_page_token = data.get('nextPageToken')
            if next_page_token:
                logging.info(f"Found nextPageToken, continuing to page {page_count + 1}")
            else:
                logging.info(f"No more pages. Total pages fetched: {page_count}")
                break
        
        logging.info(f"Successfully fetched {len(all_videos)} long-form videos and {len(shorts_videos)} Shorts")
        
        # Return both types combined with isShort flag
        return all_videos + shorts_videos
    except Exception as e:
        logging.error(f"Error fetching YouTube videos: {str(e)}")
        return []

def extract_feast_date_from_title(title: str, description: str):
    """Automatically extract feast date from video title or description"""
    import re
    
    # Common patterns: "Jan 18", "January 18", "(Jan 18)", etc.
    month_abbr = {
        'jan': '01', 'january': '01',
        'feb': '02', 'february': '02',
        'mar': '03', 'march': '03',
        'apr': '04', 'april': '04',
        'may': '05',
        'jun': '06', 'june': '06',
        'jul': '07', 'july': '07',
        'aug': '08', 'august': '08',
        'sep': '09', 'sept': '09', 'september': '09',
        'oct': '10', 'october': '10',
        'nov': '11', 'november': '11',
        'dec': '12', 'december': '12'
    }
    
    text = (title + ' ' + description).lower()
    
    # Pattern: Month Day (e.g., "Jan 18", "January 18")
    pattern = r'\b(jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|oct|october|nov|november|dec|december)\s+(\d{1,2})\b'
    match = re.search(pattern, text)
    
    if match:
        month_str = match.group(1)
        day = match.group(2).zfill(2)
        month = month_abbr.get(month_str)
        if month:
            return f"{month}-{day}"
    
    return None

def extract_saint_name_from_title(title: str):
    """Extract saint name from video title"""
    import re
    
    # Patterns for saint names
    patterns = [
        r'St\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',  # St. Name
        r'Saint\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',  # Saint Name
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            return f"St. {match.group(1)}"
    
    return None

def feast_day_helper(feast) -> dict:
    """Convert feast day mapping to dict"""
    return {
        "id": str(feast["_id"]),
        "videoId": feast["videoId"],
        "feastDate": feast["feastDate"],
        "saintName": feast.get("saintName"),
        "feastName": feast.get("feastName"),
        "liturgicalCalendar": feast.get("liturgicalCalendar", "roman"),
        "priority": feast.get("priority", 50),
        "notes": feast.get("notes"),
        "isManualOverride": feast.get("isManualOverride", False),
        "createdAt": feast.get("createdAt", datetime.utcnow())
    }

def extract_category_from_metadata(title: str, description: str):
    """
    Extract category from video title or description using prioritized keyword matching
    Title is prioritized over description for classification
    """
    # Combine title (weighted higher) with description
    title_lower = title.lower()
    desc_lower = description.lower()
    
    # PRIORITY 1: Check title first (most reliable signal)
    
    # The Rosary category
    rosary_keywords = ['rosary', 'mysteries', 'joyful mysteries', 'sorrowful mysteries', 
                       'glorious mysteries', 'luminous mysteries', 'decade']
    if any(keyword in title_lower for keyword in rosary_keywords):
        return 'The Rosary'
    
    # Novenas category
    novena_keywords = ['novena', '9 day', 'nine day', '9-day', 'nine-day']
    if any(keyword in title_lower for keyword in novena_keywords):
        return 'Novenas'
    
    # Saints & Feast Days category
    saint_keywords = ['saint', 'st.', 'st ', 'feast of', 'feast day', 
                      'saint of the day', 'patron saint']
    if any(keyword in title_lower for keyword in saint_keywords):
        return 'Saints & Feast Days'
    
    # Devotions category
    devotion_keywords = ['chaplet', 'litany', 'divine mercy', 'sacred heart',
                         'immaculate heart', 'consecration', 'devotion']
    if any(keyword in title_lower for keyword in devotion_keywords):
        return 'Devotions'
    
    # Traditional Prayers category
    traditional_keywords = ['our father', 'hail mary', 'glory be', 'apostles creed',
                           'nicene creed', 'act of contrition', 'angelus', 'magnificat',
                           'memorare', 'salve regina', 'ave maria', 'pater noster']
    if any(keyword in title_lower for keyword in traditional_keywords):
        return 'Traditional Prayers'
    
    # PRIORITY 2: Check description if title doesn't match
    
    if any(keyword in desc_lower for keyword in rosary_keywords):
        return 'The Rosary'
    
    if any(keyword in desc_lower for keyword in novena_keywords):
        return 'Novenas'
    
    if any(keyword in desc_lower for keyword in saint_keywords):
        return 'Saints & Feast Days'
    
    if any(keyword in desc_lower for keyword in devotion_keywords):
        return 'Devotions'
    
    if any(keyword in desc_lower for keyword in traditional_keywords):
        return 'Traditional Prayers'
    
    # Default category
    return 'Prayers'


def extract_prayer_text_from_description(description: str):
    """
    Extract full prayer text from video description when present
    Looks for common patterns like:
    - "Full Prayer:" or "Prayer Text:"
    - Text between specific markers
    - Structured prayer content
    """
    if not description:
        return None
    
    # Common markers for prayer text in descriptions
    prayer_markers = [
        'full prayer:',
        'prayer text:',
        'prayer:',
        'the prayer:',
        '---',  # Sometimes used to separate prayer text
    ]
    
    desc_lower = description.lower()
    
    # Find the start of prayer text
    start_idx = -1
    for marker in prayer_markers:
        idx = desc_lower.find(marker)
        if idx != -1:
            start_idx = idx + len(marker)
            break
    
    if start_idx == -1:
        # Check if description looks like prayer text (starts with traditional prayer phrases)
        prayer_starts = ['in the name of', 'our father', 'hail mary', 'glory be',
                        'o god', 'o lord', 'heavenly father', 'blessed virgin']
        if any(desc_lower.strip().startswith(phrase) for phrase in prayer_starts):
            # Entire description might be prayer text
            return description.strip()
        return None
    
    # Extract text from marker onwards
    prayer_text = description[start_idx:].strip()
    
    # Clean up common endings (links, channel info, etc.)
    end_markers = [
        '\n\nsubscribe',
        '\n\nfollow us',
        '\n\nvisit our',
        '\n\nwatch more',
        '\n\nhttps://',
        '\n\nhttp://',
    ]
    
    for end_marker in end_markers:
        idx = prayer_text.lower().find(end_marker)
        if idx != -1:
            prayer_text = prayer_text[:idx]
    
    # Return if we have meaningful prayer text (more than 50 characters)
    if len(prayer_text) > 50:
        return prayer_text.strip()
    
    return None

def get_video_details(video_id: str):
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
                'tags': item['snippet'].get('tags', [])
            }
        return {}
    except Exception as e:
        logging.error(f"Error fetching video details: {str(e)}")
        return {}


# API Routes
@api_router.get("/")
async def root():
    return {"message": "Catholic Voices and Prayers API"}


# ===================================
# FEAST DAY MAPPING ENDPOINTS
# ===================================

@api_router.post("/feast-days")
async def create_feast_day_mapping(feast: FeastDayMapping):
    """
    Manually map a video to a feast day or saint
    Priority: 100 = manual override, 50 = automatic
    """
    feast_dict = feast.dict(exclude={'id'})
    feast_dict['createdAt'] = datetime.utcnow()
    feast_dict['isManualOverride'] = True
    feast_dict['priority'] = 100  # Manual overrides always have priority 100
    
    result = await db.feast_days.insert_one(feast_dict)
    new_feast = await db.feast_days.find_one({"_id": result.inserted_id})
    
    return feast_day_helper(new_feast)


@api_router.get("/feast-days")
async def get_all_feast_day_mappings():
    """Get all feast day mappings (manual and automatic)"""
    feast_days = await db.feast_days.find().sort([("feastDate", 1), ("priority", -1)]).to_list(None)
    return [feast_day_helper(feast) for feast in feast_days]


@api_router.get("/feast-days/{feast_date}")
async def get_feast_day(feast_date: str):
    """
    Get all videos for a specific feast date (MM-DD format)
    Returns videos ordered by priority (manual overrides first)
    """
    # Find all mappings for this feast date
    feast_mappings = await db.feast_days.find(
        {"feastDate": feast_date}
    ).sort("priority", -1).to_list(None)
    
    if not feast_mappings:
        raise HTTPException(status_code=404, detail=f"No feast day content found for {feast_date}")
    
    # Get videos for each mapping
    videos_with_feast_info = []
    for feast in feast_mappings:
        video = await db.videos.find_one({"videoId": feast["videoId"]})
        if video:
            prayer = await db.prayers.find_one({"videoId": feast["videoId"]})
            
            videos_with_feast_info.append({
                "video": video_helper(video),
                "feastInfo": feast_day_helper(feast),
                "hasPrayerText": prayer is not None,
                "prayerText": prayer["prayerText"] if prayer else None
            })
    
    return videos_with_feast_info


@api_router.get("/feast-days/today/content")
async def get_todays_feast_day():
    """
    Get today's feast day content
    Automatically determines today's date and returns appropriate content
    """
    from datetime import datetime as dt
    today = dt.now().strftime("%m-%d")  # Format: MM-DD
    
    try:
        return await get_feast_day(today)
    except HTTPException:
        # No specific feast day mapped, return None
        return []


@api_router.put("/feast-days/{feast_id}")
async def update_feast_day_mapping(feast_id: str, feast_data: dict):
    """Update an existing feast day mapping"""
    try:
        result = await db.feast_days.update_one(
            {"_id": ObjectId(feast_id)},
            {"$set": feast_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Feast day mapping not found")
        
        updated_feast = await db.feast_days.find_one({"_id": ObjectId(feast_id)})
        return feast_day_helper(updated_feast)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.delete("/feast-days/{feast_id}")
async def delete_feast_day_mapping(feast_id: str):
    """Delete a feast day mapping"""
    try:
        result = await db.feast_days.delete_one({"_id": ObjectId(feast_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Feast day mapping not found")
        
        return {"message": "Feast day mapping deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/feast-days/auto-detect")
async def auto_detect_feast_days():
    """
    Automatically detect and create feast day mappings from video metadata
    Only creates mappings with priority=50 (automatic), won't override manual mappings
    """
    # Get all videos
    videos = await db.videos.find({"isShort": True}).to_list(None)  # Focus on Shorts for daily content
    
    created_count = 0
    skipped_count = 0
    
    for video in videos:
        title = video.get("title", "")
        description = video.get("description", "")
        video_id = video["videoId"]
        
        # Try to extract feast date
        feast_date = extract_feast_date_from_title(title, description)
        if not feast_date:
            continue
        
        # Check if manual mapping already exists
        existing_manual = await db.feast_days.find_one({
            "videoId": video_id,
            "feastDate": feast_date,
            "priority": 100
        })
        
        if existing_manual:
            skipped_count += 1
            continue
        
        # Check if automatic mapping already exists
        existing_auto = await db.feast_days.find_one({
            "videoId": video_id,
            "feastDate": feast_date,
            "priority": 50
        })
        
        if existing_auto:
            skipped_count += 1
            continue
        
        # Extract saint name if available
        saint_name = extract_saint_name_from_title(title)
        
        # Create automatic mapping
        feast_mapping = {
            "videoId": video_id,
            "feastDate": feast_date,
            "saintName": saint_name,
            "feastName": title,
            "liturgicalCalendar": "roman",
            "priority": 50,  # Automatic detection
            "notes": "Auto-detected from video metadata",
            "isManualOverride": False,
            "createdAt": datetime.utcnow()
        }
        
        await db.feast_days.insert_one(feast_mapping)
        created_count += 1
        logging.info(f"Auto-detected feast day: {feast_date} for video: {title[:50]}")
    
    return {
        "message": f"Auto-detection complete",
        "created": created_count,
        "skipped": skipped_count
    }


# ===================================
# EXISTING VIDEO ENDPOINTS
# ===================================

@api_router.get("/videos/refresh")
async def refresh_videos():
    """Fetch ALL videos from YouTube channel and cache them"""
    videos = fetch_youtube_videos()
    
    if videos:
        # Clear existing cache
        await db.videos.delete_many({})
        
        # Insert all videos
        if videos:
            await db.videos.insert_many(videos)
        
        return {
            "message": f"Successfully cached {len(videos)} videos from channel",
            "count": len(videos)
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to fetch videos from YouTube")


@api_router.get("/videos")
async def get_videos(category: Optional[str] = None):
    """Get all cached videos, optionally filtered by category"""
    query = {}
    if category:
        query["category"] = category
    
    videos = await db.videos.find(query).sort("publishedAt", -1).to_list(100)
    return [video_helper(video) for video in videos]


@api_router.get("/videos/{video_id}")
async def get_video(video_id: str):
    """Get a specific video by videoId"""
    video = await db.videos.find_one({"videoId": video_id})
    if video:
        return video_helper(video)
    raise HTTPException(status_code=404, detail="Video not found")


@api_router.get("/content")
async def get_content(category: Optional[str] = None, include_shorts: bool = False):
    """
    Get all PRIMARY content (long-form videos only by default)
    Set include_shorts=true to include Shorts as secondary content
    """
    query = {}
    if category:
        query["category"] = category
    
    # By default, exclude Shorts from primary content
    if not include_shorts:
        query["isShort"] = {"$ne": True}
    
    # Get videos
    videos = await db.videos.find(query).sort("publishedAt", -1).to_list(None)
    
    # Enhance with prayer text if available
    content_items = []
    for video in videos:
        video_id = video['videoId']
        
        # Check if there's a prayer entry for this video
        prayer = await db.prayers.find_one({"videoId": video_id})
        
        content_item = {
            "id": str(video["_id"]),
            "videoId": video_id,
            "title": video["title"],
            "description": video.get("description", ""),
            "thumbnail": video.get("thumbnail", ""),
            "category": video.get("category", "Prayers"),
            "duration": video.get("duration", ""),
            "publishedAt": video.get("publishedAt", ""),
            "isShort": video.get("isShort", False),
            "prayerText": prayer["prayerText"] if prayer else None,
            "hasPrayerText": prayer is not None
        }
        content_items.append(content_item)
    
    return content_items


@api_router.get("/shorts")
async def get_shorts(category: Optional[str] = None):
    """
    Get all Shorts (secondary content for daily highlights)
    """
    query = {"isShort": True}
    if category:
        query["category"] = category
    
    # Get only Shorts
    shorts = await db.videos.find(query).sort("publishedAt", -1).to_list(None)
    
    # Enhance with prayer text if available
    content_items = []
    for video in shorts:
        video_id = video['videoId']
        
        # Check if there's a prayer entry for this video
        prayer = await db.prayers.find_one({"videoId": video_id})
        
        content_item = {
            "id": str(video["_id"]),
            "videoId": video_id,
            "title": video["title"],
            "description": video.get("description", ""),
            "thumbnail": video.get("thumbnail", ""),
            "category": video.get("category", "Prayers"),
            "duration": video.get("duration", ""),
            "publishedAt": video.get("publishedAt", ""),
            "isShort": True,
            "prayerText": prayer["prayerText"] if prayer else None,
            "hasPrayerText": prayer is not None
        }
        content_items.append(content_item)
    
    return content_items


@api_router.get("/shorts/daily")
async def get_daily_short():
    """
    Get today's Short for daily reflection
    Returns the most recent Short published
    """
    # Get the most recent Short
    short = await db.videos.find_one(
        {"isShort": True},
        sort=[("publishedAt", -1)]
    )
    
    if not short:
        raise HTTPException(status_code=404, detail="No Shorts available")
    
    video_id = short['videoId']
    prayer = await db.prayers.find_one({"videoId": video_id})
    
    content_item = {
        "id": str(short["_id"]),
        "videoId": video_id,
        "title": short["title"],
        "description": short.get("description", ""),
        "thumbnail": short.get("thumbnail", ""),
        "category": short.get("category", "Prayers"),
        "duration": short.get("duration", ""),
        "publishedAt": short.get("publishedAt", ""),
        "isShort": True,
        "prayerText": prayer["prayerText"] if prayer else None,
        "hasPrayerText": prayer is not None
    }
    
    return content_item


@api_router.get("/content/{video_id}")
async def get_content_item(video_id: str):
    """Get a specific content item (video with optional prayer text)"""
    # Get video
    video = await db.videos.find_one({"videoId": video_id})
    if not video:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Check for prayer text
    prayer = await db.prayers.find_one({"videoId": video_id})
    
    content_item = {
        "id": str(video["_id"]),
        "videoId": video_id,
        "title": video["title"],
        "description": video.get("description", ""),
        "thumbnail": video.get("thumbnail", ""),
        "category": video.get("category", "Prayers"),
        "duration": video.get("duration", ""),
        "publishedAt": video.get("publishedAt", ""),
        "tags": video.get("tags", []),
        "prayerText": prayer["prayerText"] if prayer else None,
        "hasPrayerText": prayer is not None
    }
    
    return content_item


@api_router.post("/content/{video_id}/prayer-text")
async def add_prayer_text(video_id: str, prayer_data: dict):
    """Add or update prayer text for a video"""
    # Verify video exists
    video = await db.videos.find_one({"videoId": video_id})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Upsert prayer text
    prayer_text = prayer_data.get("prayerText", "")
    result = await db.prayers.update_one(
        {"videoId": video_id},
        {"$set": {
            "videoId": video_id,
            "title": video["title"],
            "prayerText": prayer_text,
            "category": video.get("category", "Prayers"),
            "updatedAt": datetime.utcnow()
        }},
        upsert=True
    )
    
    return {"message": "Prayer text added/updated successfully"}


@api_router.post("/prayers")
async def create_prayer(prayer: PrayerCreate):
    """Create a new prayer entry"""
    prayer_dict = prayer.dict()
    prayer_dict['createdAt'] = datetime.utcnow()
    
    result = await db.prayers.insert_one(prayer_dict)
    new_prayer = await db.prayers.find_one({"_id": result.inserted_id})
    
    return prayer_helper(new_prayer)


@api_router.get("/prayers")
async def get_prayers():
    """Get all prayers"""
    prayers = await db.prayers.find().sort("createdAt", -1).to_list(100)
    return [prayer_helper(prayer) for prayer in prayers]


@api_router.get("/prayers/{prayer_id}")
async def get_prayer(prayer_id: str):
    """Get a specific prayer by ID"""
    try:
        prayer = await db.prayers.find_one({"_id": ObjectId(prayer_id)})
        if prayer:
            return prayer_helper(prayer)
        raise HTTPException(status_code=404, detail="Prayer not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid prayer ID")


@api_router.delete("/prayers/{prayer_id}")
async def delete_prayer(prayer_id: str):
    """Delete a prayer"""
    try:
        result = await db.prayers.delete_one({"_id": ObjectId(prayer_id)})
        if result.deleted_count == 1:
            return {"message": "Prayer deleted successfully"}
        raise HTTPException(status_code=404, detail="Prayer not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid prayer ID")


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
