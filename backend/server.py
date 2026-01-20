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
    """
    Extract saint name from video title using flexible patterns
    Supports formats like:
    - "St. [Name]"
    - "Saint [Name]"
    - "Saint of the Day - [Name]"
    - "[Name] | St. [Short Name]"
    """
    import re
    
    # Pattern 1: "Saint of the Day - [Name]" or "Saint of the Day: [Name]"
    match = re.search(r'saint of the day[\s\-:]+([^|(]+)', title, re.IGNORECASE)
    if match:
        saint_name = match.group(1).strip()
        if not saint_name.lower().startswith('st'):
            return f"St. {saint_name}"
        return saint_name
    
    # Pattern 2: Standard "St. [Name]" or "Saint [Name]"
    patterns = [
        r'St\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'Saint\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            saint_name = match.group(1).strip()
            # Remove trailing punctuation
            saint_name = saint_name.rstrip('.,!?;:')
            return f"St. {saint_name}"
    
    # Pattern 3: "[Description] | St. [Name]" (name at end after pipe)
    match = re.search(r'\|\s*St\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', title)
    if match:
        saint_name = match.group(1).strip()
        saint_name = saint_name.rstrip('.,!?;:)')
        return f"St. {saint_name}"
    
    return None


def extract_feast_name_from_title(title: str):
    """
    Extract feast name from video title using flexible patterns
    Supports formats like:
    - "Feast of [Name/Event]"
    - "[Event] Feast"
    - "The [Event]"
    """
    import re
    
    # Pattern 1: "Feast of [Name/Event]"
    match = re.search(r'feast of ([^|(]+)', title, re.IGNORECASE)
    if match:
        feast_name = match.group(1).strip()
        feast_name = feast_name.rstrip('.,!?;:')
        return f"Feast of {feast_name}"
    
    # Pattern 2: "[Name] Feast Day" or "[Name] Feast"
    match = re.search(r'([A-Z][a-z\s]+)\s+feast\s*day', title, re.IGNORECASE)
    if match:
        feast_name = match.group(1).strip()
        return f"Feast of {feast_name}"
    
    return None


def extract_prayer_name_from_title(title: str):
    """
    Extract prayer name from video title using flexible patterns
    Supports formats like:
    - "[Prayer Name] - Full Prayer"
    - "[Prayer Name] Prayer"
    - "The [Prayer Name]"
    """
    import re
    
    # Common prayer name patterns
    title_clean = title
    
    # Remove common suffixes to get prayer name
    suffixes_to_remove = [
        r'\s*-\s*full prayer.*$',
        r'\s*-\s*prayer text.*$',
        r'\s*\(full prayer\).*$',
        r'\s*with.*$',  # "The Rosary with Bishop Sheen"
    ]
    
    for suffix_pattern in suffixes_to_remove:
        title_clean = re.sub(suffix_pattern, '', title_clean, flags=re.IGNORECASE)
    
    # Extract "The [Prayer Name]" pattern
    match = re.search(r'^the\s+([^|(]+)', title_clean, re.IGNORECASE)
    if match:
        prayer_name = match.group(1).strip()
        prayer_name = prayer_name.rstrip('.,!?;:')
        return prayer_name
    
    # Return cleaned title if it looks like a prayer name
    if len(title_clean) < 100:  # Prayer names are usually concise
        return title_clean.strip()
    
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


@api_router.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    try:
        # Check MongoDB connection
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


# ===================================
# MASS MAP MODELS & ENDPOINTS
# ===================================

# Sedevacantist groups to exclude (non-negotiable)
EXCLUDED_GROUPS = [
    'cmri', 'sspv', 'sspx-mc', 'sspx marian corps',
    'sedevacantist', 'vacantist', 'non una cum'
]

class MassLocationCreate(BaseModel):
    """Model for creating a new Mass location"""
    name: str
    entity_type: str = "Parish"  # Parish, Oratory, Chapel, Mission
    jurisdiction: str = "Diocese"  # Diocese, Eparchy, Ordinariate, Society
    affiliation: str  # Diocesan, FSSP, ICKSP, Ordinariate, SSPX, Eastern Catholic
    rite: str = "Latin"  # Latin, Byzantine, Maronite, Melkite, Ukrainian, Ruthenian, Chaldean
    use_or_liturgy: str = "1962 Roman Missal"  # 1962 Roman Missal, Ordinariate Use, Divine Liturgy
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"
    latitude: float
    longitude: float
    mass_schedule_url: Optional[str] = None
    confession_url: Optional[str] = None
    adoration_url: Optional[str] = None
    livestream_url: Optional[str] = None
    website_url: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    source_name: Optional[str] = None
    source_url: Optional[str] = None

class MassLocationUpdate(BaseModel):
    """Model for updating a Mass location"""
    name: Optional[str] = None
    entity_type: Optional[str] = None
    jurisdiction: Optional[str] = None
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
    mass_schedule_url: Optional[str] = None
    confession_url: Optional[str] = None
    adoration_url: Optional[str] = None
    livestream_url: Optional[str] = None
    website_url: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    last_verified_date: Optional[datetime] = None
    verification_method: Optional[str] = None

class MassLocationSubmission(BaseModel):
    """Model for user-submitted locations (requires approval)"""
    name: str
    entity_type: str = "Parish"
    jurisdiction: str = "Diocese"
    affiliation: str
    rite: str = "Latin"
    use_or_liturgy: str = "1962 Roman Missal"
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    mass_schedule_url: Optional[str] = None
    website_url: Optional[str] = None
    notes: Optional[str] = None
    submitter_email: Optional[str] = None

def check_exclusion(name: str, affiliation: str, notes: str = "") -> tuple:
    """Check if location should be excluded based on sedevacantist affiliation"""
    combined_text = f"{name} {affiliation} {notes}".lower()
    
    for excluded in EXCLUDED_GROUPS:
        if excluded in combined_text:
            return True, f"Matches excluded group: {excluded}"
    
    return False, None

def mass_location_helper(location) -> dict:
    """Convert MongoDB document to API response"""
    return {
        "id": str(location["_id"]),
        "location_id": location.get("location_id", str(location["_id"])),
        "name": location["name"],
        "entity_type": location.get("entity_type", "Parish"),
        "jurisdiction": location.get("jurisdiction", "Diocese"),
        "affiliation": location["affiliation"],
        "rite": location.get("rite", "Latin"),
        "use_or_liturgy": location.get("use_or_liturgy", "1962 Roman Missal"),
        "street": location.get("street", ""),
        "city": location["city"],
        "state": location["state"],
        "zip_code": location.get("zip_code", ""),
        "country": location.get("country", "USA"),
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "mass_schedule_url": location.get("mass_schedule_url"),
        "confession_url": location.get("confession_url"),
        "adoration_url": location.get("adoration_url"),
        "livestream_url": location.get("livestream_url"),
        "website_url": location.get("website_url"),
        "phone": location.get("phone"),
        "notes": location.get("notes"),
        "source_name": location.get("source_name"),
        "source_url": location.get("source_url"),
        "last_verified_date": location.get("last_verified_date"),
        "verification_method": location.get("verification_method"),
        "created_at": location.get("created_at", datetime.utcnow()),
        "updated_at": location.get("updated_at")
    }


@api_router.get("/mass-locations")
async def get_mass_locations(
    affiliation: Optional[str] = None,
    rite: Optional[str] = None,
    use_or_liturgy: Optional[str] = None,
    state: Optional[str] = None,
    city: Optional[str] = None,
    limit: int = 500
):
    """
    Get all Mass locations with optional filters
    Only returns non-excluded locations
    """
    query = {"exclude_flag": {"$ne": True}}
    
    if affiliation:
        query["affiliation"] = affiliation
    if rite:
        query["rite"] = rite
    if use_or_liturgy:
        query["use_or_liturgy"] = use_or_liturgy
    if state:
        query["state"] = {"$regex": state, "$options": "i"}
    if city:
        query["city"] = {"$regex": city, "$options": "i"}
    
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
    """
    Search Mass locations by text query or proximity to coordinates
    """
    query = {"exclude_flag": {"$ne": True}}
    
    if affiliation:
        query["affiliation"] = affiliation
    if rite:
        query["rite"] = rite
    
    # Text search by city, state, or zip
    if q:
        query["$or"] = [
            {"city": {"$regex": q, "$options": "i"}},
            {"state": {"$regex": q, "$options": "i"}},
            {"zip_code": {"$regex": q, "$options": "i"}},
            {"name": {"$regex": q, "$options": "i"}}
        ]
    
    locations = await db.mass_locations.find(query).to_list(500)
    result = [mass_location_helper(loc) for loc in locations]
    
    # If coordinates provided, filter by distance
    if lat is not None and lng is not None:
        import math
        
        def haversine(lat1, lon1, lat2, lon2):
            """Calculate distance between two points in miles"""
            R = 3959  # Earth's radius in miles
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            return R * c
        
        filtered = []
        for loc in result:
            distance = haversine(lat, lng, loc["latitude"], loc["longitude"])
            if distance <= radius_miles:
                loc["distance_miles"] = round(distance, 1)
                filtered.append(loc)
        
        # Sort by distance
        filtered.sort(key=lambda x: x.get("distance_miles", 999))
        return filtered
    
    return result


@api_router.get("/mass-locations/nearby")
async def get_nearby_locations(
    lat: float,
    lng: float,
    radius_miles: float = 25,
    affiliation: Optional[str] = None,
    rite: Optional[str] = None,
    limit: int = 50
):
    """
    Get Mass locations within radius of given coordinates
    """
    import math
    
    def haversine(lat1, lon1, lat2, lon2):
        R = 3959
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c
    
    query = {"exclude_flag": {"$ne": True}}
    if affiliation:
        query["affiliation"] = affiliation
    if rite:
        query["rite"] = rite
    
    # Get all locations and filter by distance
    locations = await db.mass_locations.find(query).to_list(1000)
    
    nearby = []
    for loc in locations:
        distance = haversine(lat, lng, loc["latitude"], loc["longitude"])
        if distance <= radius_miles:
            loc_data = mass_location_helper(loc)
            loc_data["distance_miles"] = round(distance, 1)
            nearby.append(loc_data)
    
    # Sort by distance and limit
    nearby.sort(key=lambda x: x["distance_miles"])
    return nearby[:limit]


@api_router.get("/mass-locations/filters")
async def get_mass_location_filters():
    """
    Get available filter options for the mass map
    """
    query = {"exclude_flag": {"$ne": True}}
    
    # Get distinct values for each filter field
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
    """
    Get statistics about Mass locations
    """
    query = {"exclude_flag": {"$ne": True}}
    
    total = await db.mass_locations.count_documents(query)
    
    # Count by affiliation
    pipeline = [
        {"$match": query},
        {"$group": {"_id": "$affiliation", "count": {"$sum": 1}}}
    ]
    affiliation_counts = await db.mass_locations.aggregate(pipeline).to_list(100)
    by_affiliation = {item["_id"]: item["count"] for item in affiliation_counts if item["_id"]}
    
    # Count by rite
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
    """
    Get a specific Mass location by ID
    """
    try:
        location = await db.mass_locations.find_one({
            "_id": ObjectId(location_id),
            "exclude_flag": {"$ne": True}
        })
        
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        return mass_location_helper(location)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/mass-locations")
async def create_mass_location(location: MassLocationCreate):
    """
    Create a new Mass location (admin only in production)
    """
    # Check exclusion rules
    exclude_flag, exclude_reason = check_exclusion(
        location.name, 
        location.affiliation, 
        location.notes or ""
    )
    
    location_dict = location.dict()
    location_dict["location_id"] = str(uuid.uuid4())
    location_dict["exclude_flag"] = exclude_flag
    location_dict["exclude_reason"] = exclude_reason
    location_dict["created_at"] = datetime.utcnow()
    location_dict["last_verified_date"] = datetime.utcnow()
    location_dict["verification_method"] = "initial_entry"
    
    # Check for duplicates based on name + address + proximity
    existing = await db.mass_locations.find_one({
        "name": location.name,
        "city": location.city,
        "state": location.state
    })
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="A location with this name and address already exists"
        )
    
    result = await db.mass_locations.insert_one(location_dict)
    new_location = await db.mass_locations.find_one({"_id": result.inserted_id})
    
    if exclude_flag:
        return {
            "message": "Location stored but excluded from public display",
            "exclude_reason": exclude_reason
        }
    
    return mass_location_helper(new_location)


@api_router.put("/mass-locations/{location_id}")
async def update_mass_location(location_id: str, location: MassLocationUpdate):
    """
    Update a Mass location (admin only in production)
    """
    try:
        update_data = {k: v for k, v in location.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        # Re-check exclusion rules if relevant fields updated
        if any(k in update_data for k in ["name", "affiliation", "notes"]):
            existing = await db.mass_locations.find_one({"_id": ObjectId(location_id)})
            if existing:
                name = update_data.get("name", existing.get("name", ""))
                affiliation = update_data.get("affiliation", existing.get("affiliation", ""))
                notes = update_data.get("notes", existing.get("notes", ""))
                exclude_flag, exclude_reason = check_exclusion(name, affiliation, notes)
                update_data["exclude_flag"] = exclude_flag
                update_data["exclude_reason"] = exclude_reason
        
        result = await db.mass_locations.update_one(
            {"_id": ObjectId(location_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Location not found")
        
        updated = await db.mass_locations.find_one({"_id": ObjectId(location_id)})
        return mass_location_helper(updated)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.delete("/mass-locations/{location_id}")
async def delete_mass_location(location_id: str):
    """
    Delete a Mass location (admin only in production)
    """
    try:
        result = await db.mass_locations.delete_one({"_id": ObjectId(location_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Location not found")
        
        return {"message": "Location deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/mass-locations/submit")
async def submit_mass_location(submission: MassLocationSubmission):
    """
    Submit a new Mass location for review (public endpoint)
    Requires admin approval before appearing on map
    """
    # Check exclusion rules first
    exclude_flag, exclude_reason = check_exclusion(
        submission.name,
        submission.affiliation,
        submission.notes or ""
    )
    
    if exclude_flag:
        return {
            "message": "Thank you for your submission. However, this location cannot be included.",
            "status": "rejected"
        }
    
    submission_dict = submission.dict()
    submission_dict["submission_id"] = str(uuid.uuid4())
    submission_dict["status"] = "pending"
    submission_dict["submitted_at"] = datetime.utcnow()
    
    # Check for potential duplicates
    existing = await db.mass_locations.find_one({
        "name": {"$regex": submission.name, "$options": "i"},
        "city": {"$regex": submission.city, "$options": "i"},
        "state": {"$regex": submission.state, "$options": "i"}
    })
    
    if existing:
        return {
            "message": "A similar location may already exist. Your submission will be reviewed.",
            "status": "review_duplicate"
        }
    
    await db.mass_location_submissions.insert_one(submission_dict)
    
    return {
        "message": "Thank you for your submission. It will be reviewed before appearing on the map.",
        "status": "pending"
    }


@api_router.post("/mass-locations/seed")
async def seed_mass_locations():
    """
    Seed the database with initial sample Mass locations
    This creates representative entries for each category
    """
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
            "mass_schedule_url": "https://www.cantius.org/mass-times",
            "website_url": "https://www.cantius.org",
            "notes": "One of Chicago's premier Traditional Latin Mass parishes",
            "source_name": "Official Website"
        },
        {
            "name": "Holy Innocents Church",
            "entity_type": "Parish",
            "jurisdiction": "Diocese",
            "affiliation": "Diocesan",
            "rite": "Latin",
            "use_or_liturgy": "1962 Roman Missal",
            "street": "128 W 37th St",
            "city": "New York",
            "state": "NY",
            "zip_code": "10018",
            "country": "USA",
            "latitude": 40.7527,
            "longitude": -73.9902,
            "mass_schedule_url": "https://www.holyinnocentsnyc.org/mass-times",
            "website_url": "https://www.holyinnocentsnyc.org",
            "source_name": "Official Website"
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
            "mass_schedule_url": "https://www.stmarymotherof god.org/mass-schedule",
            "website_url": "https://www.stmarymotherof god.org",
            "notes": "FSSP Apostolate",
            "source_name": "FSSP Directory"
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
            "website_url": "https://materdeiparish.com",
            "source_name": "FSSP Directory"
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
            "website_url": "https://institute-christ-king.org/stlouis",
            "notes": "Institute of Christ the King Sovereign Priest",
            "source_name": "ICKSP Directory"
        },
        {
            "name": "Shrine of Christ the King",
            "entity_type": "Oratory",
            "jurisdiction": "Society",
            "affiliation": "ICKSP",
            "rite": "Latin",
            "use_or_liturgy": "1962 Roman Missal",
            "street": "6415 S Woodlawn Ave",
            "city": "Chicago",
            "state": "IL",
            "zip_code": "60637",
            "country": "USA",
            "latitude": 41.7764,
            "longitude": -87.5962,
            "website_url": "https://institute-christ-king.org/chicago",
            "source_name": "ICKSP Directory"
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
            "website_url": "https://www.atonementonline.com",
            "notes": "Personal Ordinariate of the Chair of St. Peter",
            "source_name": "Ordinariate Directory"
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
            "website_url": "https://www.walsingham.org",
            "notes": "Cathedral of the Personal Ordinariate",
            "source_name": "Ordinariate Directory"
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
            "website_url": "https://sspx.org/en/chapel/st-marys-chapel-st-marys",
            "notes": "Society of St. Pius X",
            "source_name": "SSPX Directory"
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
            "longitude": -95.0525,
            "website_url": "https://sspx.org/en/chapel/queen-angels-chapel-dickinson",
            "source_name": "SSPX Directory"
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
            "website_url": "https://stjohnsbyzantine.com",
            "notes": "Byzantine Catholic Metropolia of Pittsburgh",
            "source_name": "Eparchy Directory"
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
            "longitude": -75.1536,
            "notes": "Ukrainian Catholic Archeparchy of Philadelphia",
            "source_name": "Eparchy Directory"
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
            "website_url": "https://ololc.org",
            "notes": "Eparchy of St. Maron of Brooklyn",
            "source_name": "Eparchy Directory"
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
            "website_url": "https://www.melkite.org/cathedral",
            "notes": "Melkite Greek Catholic Eparchy of Newton",
            "source_name": "Eparchy Directory"
        },
        # Eastern Catholic - Ruthenian
        {
            "name": "St. Gregory Byzantine Catholic Church",
            "entity_type": "Parish",
            "jurisdiction": "Eparchy",
            "affiliation": "Eastern Catholic",
            "rite": "Ruthenian",
            "use_or_liturgy": "Divine Liturgy",
            "street": "8710 S Hoyne Ave",
            "city": "Chicago",
            "state": "IL",
            "zip_code": "60620",
            "country": "USA",
            "latitude": 41.7353,
            "longitude": -87.6695,
            "notes": "Ruthenian Byzantine Catholic Eparchy of Parma",
            "source_name": "Eparchy Directory"
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
            "website_url": "https://www.mothergodchurch.org",
            "notes": "Chaldean Catholic Eparchy of St. Thomas the Apostle",
            "source_name": "Eparchy Directory"
        }
    ]
    
    inserted_count = 0
    skipped_count = 0
    
    for loc in sample_locations:
        # Check for existing
        existing = await db.mass_locations.find_one({
            "name": loc["name"],
            "city": loc["city"],
            "state": loc["state"]
        })
        
        if existing:
            skipped_count += 1
            continue
        
        # Check exclusion
        exclude_flag, exclude_reason = check_exclusion(
            loc["name"],
            loc["affiliation"],
            loc.get("notes", "")
        )
        
        loc["location_id"] = str(uuid.uuid4())
        loc["exclude_flag"] = exclude_flag
        loc["exclude_reason"] = exclude_reason
        loc["created_at"] = datetime.utcnow()
        loc["last_verified_date"] = datetime.utcnow()
        loc["verification_method"] = "initial_seed"
        
        await db.mass_locations.insert_one(loc)
        inserted_count += 1
    
    return {
        "message": "Database seeded successfully",
        "inserted": inserted_count,
        "skipped": skipped_count
    }


# ===================================
# DATA INGESTION MODE - BULK IMPORT
# ===================================

class BulkLocationImport(BaseModel):
    """Model for bulk importing locations"""
    locations: List[dict]
    source_name: str
    source_url: Optional[str] = None
    dry_run: bool = False  # If true, validates without inserting

class CSVImportConfig(BaseModel):
    """Configuration for CSV import"""
    source_name: str
    source_url: Optional[str] = None
    affiliation: str
    rite: str = "Latin"
    use_or_liturgy: str = "1962 Roman Missal"
    dry_run: bool = False

class IngestionReport(BaseModel):
    """Report generated after data ingestion"""
    total_processed: int
    inserted: int
    skipped_duplicate: int
    skipped_excluded: int
    errors: int
    error_details: List[dict]


def calculate_geo_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in miles using Haversine formula"""
    import math
    R = 3959  # Earth's radius in miles
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


async def find_duplicate(location: dict, threshold_miles: float = 0.5) -> Optional[dict]:
    """
    Find potential duplicate based on:
    1. Exact name + city + state match
    2. Similar name + geographic proximity (within threshold)
    """
    # Check exact match first
    exact_match = await db.mass_locations.find_one({
        "name": {"$regex": f"^{location.get('name', '')}$", "$options": "i"},
        "city": {"$regex": f"^{location.get('city', '')}$", "$options": "i"},
        "state": {"$regex": f"^{location.get('state', '')}$", "$options": "i"}
    })
    
    if exact_match:
        return exact_match
    
    # Check geographic proximity for similar names
    if location.get("latitude") and location.get("longitude"):
        # Find locations within the threshold distance
        all_locations = await db.mass_locations.find({
            "state": {"$regex": f"^{location.get('state', '')}$", "$options": "i"}
        }).to_list(1000)
        
        for existing in all_locations:
            if existing.get("latitude") and existing.get("longitude"):
                distance = calculate_geo_distance(
                    location["latitude"], location["longitude"],
                    existing["latitude"], existing["longitude"]
                )
                
                if distance <= threshold_miles:
                    # Check if names are similar (case-insensitive partial match)
                    existing_name = existing.get("name", "").lower()
                    new_name = location.get("name", "").lower()
                    
                    # Check for common words (excluding common prefixes)
                    common_prefixes = ["st.", "st", "saint", "our", "lady", "church", "parish", "the"]
                    
                    existing_words = set(w for w in existing_name.split() if w not in common_prefixes)
                    new_words = set(w for w in new_name.split() if w not in common_prefixes)
                    
                    # If significant overlap in words, likely duplicate
                    if len(existing_words & new_words) >= 2:
                        return existing
    
    return None


async def normalize_location(location: dict, source_name: str, source_url: str = None) -> dict:
    """Normalize location data to standard format"""
    normalized = {
        "location_id": str(uuid.uuid4()),
        "name": location.get("name", "").strip(),
        "entity_type": location.get("entity_type", "Parish"),
        "jurisdiction": location.get("jurisdiction", "Diocese"),
        "affiliation": location.get("affiliation", ""),
        "rite": location.get("rite", "Latin"),
        "use_or_liturgy": location.get("use_or_liturgy", "1962 Roman Missal"),
        "street": location.get("street", location.get("address", "")).strip(),
        "city": location.get("city", "").strip(),
        "state": location.get("state", "").strip().upper()[:2] if len(location.get("state", "")) <= 2 else location.get("state", "").strip(),
        "zip_code": str(location.get("zip_code", location.get("zip", ""))).strip(),
        "country": location.get("country", "USA"),
        "latitude": float(location.get("latitude", location.get("lat", 0))) if location.get("latitude") or location.get("lat") else None,
        "longitude": float(location.get("longitude", location.get("lng", location.get("lon", 0)))) if location.get("longitude") or location.get("lng") or location.get("lon") else None,
        "mass_schedule_url": location.get("mass_schedule_url", location.get("schedule_url")),
        "confession_url": location.get("confession_url"),
        "adoration_url": location.get("adoration_url"),
        "livestream_url": location.get("livestream_url"),
        "website_url": location.get("website_url", location.get("website")),
        "phone": location.get("phone"),
        "notes": location.get("notes", location.get("description")),
        "source_name": source_name,
        "source_url": source_url,
        "created_at": datetime.utcnow(),
        "last_verified_date": datetime.utcnow(),
        "verification_method": "bulk_import"
    }
    
    # Check exclusion
    exclude_flag, exclude_reason = check_exclusion(
        normalized["name"],
        normalized["affiliation"],
        normalized.get("notes", "")
    )
    normalized["exclude_flag"] = exclude_flag
    normalized["exclude_reason"] = exclude_reason
    
    return normalized


@api_router.post("/mass-locations/ingest/bulk")
async def ingest_bulk_locations(import_data: BulkLocationImport):
    """
    Bulk import locations from structured JSON data.
    
    Expects:
    {
        "locations": [
            {
                "name": "Parish Name",
                "street": "123 Main St",
                "city": "City",
                "state": "ST",
                "zip_code": "12345",
                "latitude": 40.1234,
                "longitude": -75.1234,
                "affiliation": "FSSP",
                "rite": "Latin",
                "use_or_liturgy": "1962 Roman Missal",
                ...
            }
        ],
        "source_name": "FSSP Official Directory",
        "source_url": "https://fssp.org/parishes",
        "dry_run": false
    }
    """
    report = {
        "total_processed": 0,
        "inserted": 0,
        "skipped_duplicate": 0,
        "skipped_excluded": 0,
        "errors": 0,
        "error_details": [],
        "dry_run": import_data.dry_run
    }
    
    for idx, loc in enumerate(import_data.locations):
        report["total_processed"] += 1
        
        try:
            # Normalize the location data
            normalized = await normalize_location(
                loc, 
                import_data.source_name, 
                import_data.source_url
            )
            
            # Validate required fields
            if not normalized.get("name") or not normalized.get("city") or not normalized.get("state"):
                report["errors"] += 1
                report["error_details"].append({
                    "index": idx,
                    "name": loc.get("name", "Unknown"),
                    "error": "Missing required fields (name, city, or state)"
                })
                continue
            
            # Check exclusion
            if normalized.get("exclude_flag"):
                report["skipped_excluded"] += 1
                report["error_details"].append({
                    "index": idx,
                    "name": normalized["name"],
                    "error": f"Excluded: {normalized.get('exclude_reason')}"
                })
                continue
            
            # Check for duplicates
            duplicate = await find_duplicate(normalized)
            if duplicate:
                report["skipped_duplicate"] += 1
                report["error_details"].append({
                    "index": idx,
                    "name": normalized["name"],
                    "error": f"Duplicate of existing: {duplicate.get('name')} in {duplicate.get('city')}, {duplicate.get('state')}"
                })
                continue
            
            # Insert if not dry run
            if not import_data.dry_run:
                await db.mass_locations.insert_one(normalized)
            
            report["inserted"] += 1
            
        except Exception as e:
            report["errors"] += 1
            report["error_details"].append({
                "index": idx,
                "name": loc.get("name", "Unknown"),
                "error": str(e)
            })
    
    return report


@api_router.post("/mass-locations/ingest/csv")
async def ingest_csv_locations(
    csv_content: str,
    config: CSVImportConfig
):
    """
    Import locations from CSV content.
    
    Expected CSV columns (flexible mapping):
    - name (required)
    - street OR address
    - city (required)
    - state (required)
    - zip_code OR zip
    - latitude OR lat
    - longitude OR lng OR lon
    - website OR website_url
    - phone
    - notes OR description
    
    Additional columns are ignored.
    """
    import csv
    import io
    
    report = {
        "total_processed": 0,
        "inserted": 0,
        "skipped_duplicate": 0,
        "skipped_excluded": 0,
        "errors": 0,
        "error_details": [],
        "dry_run": config.dry_run
    }
    
    try:
        # Parse CSV
        reader = csv.DictReader(io.StringIO(csv_content))
        locations = list(reader)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")
    
    for idx, loc in enumerate(locations):
        report["total_processed"] += 1
        
        try:
            # Add config values
            loc["affiliation"] = config.affiliation
            loc["rite"] = config.rite
            loc["use_or_liturgy"] = config.use_or_liturgy
            
            # Normalize
            normalized = await normalize_location(
                loc,
                config.source_name,
                config.source_url
            )
            
            # Validate
            if not normalized.get("name") or not normalized.get("city") or not normalized.get("state"):
                report["errors"] += 1
                report["error_details"].append({
                    "index": idx,
                    "name": loc.get("name", "Unknown"),
                    "error": "Missing required fields"
                })
                continue
            
            # Check exclusion
            if normalized.get("exclude_flag"):
                report["skipped_excluded"] += 1
                continue
            
            # Check duplicates
            duplicate = await find_duplicate(normalized)
            if duplicate:
                report["skipped_duplicate"] += 1
                continue
            
            # Insert if not dry run
            if not config.dry_run:
                await db.mass_locations.insert_one(normalized)
            
            report["inserted"] += 1
            
        except Exception as e:
            report["errors"] += 1
            report["error_details"].append({
                "index": idx,
                "name": loc.get("name", "Unknown"),
                "error": str(e)
            })
    
    return report


@api_router.get("/mass-locations/ingest/template")
async def get_csv_template():
    """
    Get CSV template for bulk import.
    """
    template = """name,street,city,state,zip_code,latitude,longitude,website,phone,notes
"Example Parish","123 Main St","City Name","ST","12345","40.1234","-75.1234","https://example.com","555-123-4567","Optional notes"
"""
    return {
        "template": template,
        "required_columns": ["name", "city", "state"],
        "optional_columns": ["street", "zip_code", "latitude", "longitude", "website", "phone", "notes"],
        "notes": [
            "latitude and longitude are required for accurate deduplication",
            "state should be 2-letter abbreviation (e.g., 'PA', 'TX')",
            "affiliation, rite, and use_or_liturgy are set via the import config"
        ]
    }


@api_router.get("/mass-locations/ingest/sources")
async def get_authoritative_sources():
    """
    List authoritative data sources for Mass Map ingestion.
    These are the ONLY approved sources for data.
    """
    return {
        "authoritative_sources": [
            {
                "name": "Latin Mass Directory",
                "url": "https://www.latinmassdir.org/",
                "affiliation": "Diocesan",
                "description": "Comprehensive directory of diocesan Traditional Latin Masses",
                "data_format": "Web scrape to structured data (manual curation required)"
            },
            {
                "name": "FSSP Official Parish Finder",
                "url": "https://fssp.org/where-to-find-us/",
                "affiliation": "FSSP",
                "description": "Official Priestly Fraternity of St. Peter locations",
                "data_format": "Structured directory"
            },
            {
                "name": "Institute of Christ the King",
                "url": "https://institute-christ-king.org/locations/",
                "affiliation": "ICKSP",
                "description": "Official ICKSP apostolates and oratories",
                "data_format": "Structured directory"
            },
            {
                "name": "Personal Ordinariate of the Chair of St. Peter",
                "url": "https://ordinariate.net/parish-finder",
                "affiliation": "Ordinariate",
                "description": "Official Ordinariate parish directory",
                "data_format": "Structured directory"
            },
            {
                "name": "SSPX Chapel Finder",
                "url": "https://sspx.org/en/mass-and-confession-schedule",
                "affiliation": "SSPX",
                "description": "Official Society of St. Pius X chapel listings",
                "data_format": "Structured directory"
            },
            {
                "name": "Byzantine Catholic Metropolia of Pittsburgh",
                "url": "https://www.archpitt.org/parishes/",
                "affiliation": "Eastern Catholic",
                "rite": "Byzantine",
                "description": "Byzantine Catholic parishes in Pittsburgh metropolitan area",
                "data_format": "Parish directory"
            },
            {
                "name": "Ukrainian Catholic Archeparchy of Philadelphia",
                "url": "https://ukrarcheparchy.us/parishes",
                "affiliation": "Eastern Catholic",
                "rite": "Ukrainian",
                "description": "Ukrainian Catholic parishes",
                "data_format": "Parish directory"
            },
            {
                "name": "Eparchy of St. Maron of Brooklyn",
                "url": "https://www.stmaron.org/parishes",
                "affiliation": "Eastern Catholic",
                "rite": "Maronite",
                "description": "Maronite Catholic parishes in the eastern US",
                "data_format": "Parish directory"
            },
            {
                "name": "Melkite Greek Catholic Eparchy of Newton",
                "url": "https://melkite.org/parishes",
                "affiliation": "Eastern Catholic",
                "rite": "Melkite",
                "description": "Melkite Greek Catholic parishes",
                "data_format": "Parish directory"
            },
            {
                "name": "Eparchy of Parma (Ruthenian)",
                "url": "https://parma.org/parishes",
                "affiliation": "Eastern Catholic",
                "rite": "Ruthenian",
                "description": "Ruthenian Byzantine Catholic parishes",
                "data_format": "Parish directory"
            },
            {
                "name": "Chaldean Catholic Eparchy of St. Thomas",
                "url": "https://www.chaldeandiocese.org/parishes",
                "affiliation": "Eastern Catholic",
                "rite": "Chaldean",
                "description": "Chaldean Catholic parishes",
                "data_format": "Parish directory"
            }
        ],
        "prohibited_sources": [
            "Unverified user submissions without admin review",
            "Social media posts",
            "Unofficial directories or aggregators",
            "Sedevacantist websites (CMRI, SSPV, etc.)"
        ],
        "ingestion_rules": [
            "All data must come from authoritative sources listed above",
            "Each import must specify source_name and source_url",
            "Exclusion rules are automatically applied",
            "Deduplication is aggressive - locations within 0.5 miles with similar names are flagged",
            "Dry run mode available for validation before commit"
        ]
    }


@api_router.get("/mass-locations/ingest/status")
async def get_ingestion_status():
    """
    Get current database status and ingestion statistics.
    """
    total = await db.mass_locations.count_documents({})
    excluded = await db.mass_locations.count_documents({"exclude_flag": True})
    active = await db.mass_locations.count_documents({"exclude_flag": {"$ne": True}})
    
    # Count by source
    pipeline = [
        {"$match": {"exclude_flag": {"$ne": True}}},
        {"$group": {"_id": "$source_name", "count": {"$sum": 1}}}
    ]
    source_counts = await db.mass_locations.aggregate(pipeline).to_list(100)
    by_source = {item["_id"] or "Unknown": item["count"] for item in source_counts}
    
    # Count by affiliation
    pipeline = [
        {"$match": {"exclude_flag": {"$ne": True}}},
        {"$group": {"_id": "$affiliation", "count": {"$sum": 1}}}
    ]
    affiliation_counts = await db.mass_locations.aggregate(pipeline).to_list(100)
    by_affiliation = {item["_id"] or "Unknown": item["count"] for item in affiliation_counts}
    
    # Count by state
    pipeline = [
        {"$match": {"exclude_flag": {"$ne": True}}},
        {"$group": {"_id": "$state", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    state_counts = await db.mass_locations.aggregate(pipeline).to_list(100)
    by_state = {item["_id"] or "Unknown": item["count"] for item in state_counts}
    
    # Recently added
    recent = await db.mass_locations.find(
        {"exclude_flag": {"$ne": True}}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    return {
        "database_status": {
            "total_records": total,
            "active_locations": active,
            "excluded_locations": excluded
        },
        "by_source": by_source,
        "by_affiliation": by_affiliation,
        "by_state": by_state,
        "coverage": {
            "states_covered": len([s for s in by_state.keys() if s != "Unknown"]),
            "total_us_states": 50
        },
        "recent_additions": [
            {
                "name": loc["name"],
                "city": loc["city"],
                "state": loc["state"],
                "affiliation": loc["affiliation"],
                "source": loc.get("source_name"),
                "added": loc.get("created_at")
            }
            for loc in recent
        ]
    }


@api_router.post("/mass-locations/ingest/validate")
async def validate_location(location: dict):
    """
    Validate a single location without inserting.
    Returns validation status and any issues found.
    """
    issues = []
    
    # Required fields
    if not location.get("name"):
        issues.append("Missing required field: name")
    if not location.get("city"):
        issues.append("Missing required field: city")
    if not location.get("state"):
        issues.append("Missing required field: state")
    if not location.get("affiliation"):
        issues.append("Missing required field: affiliation")
    
    # Valid affiliation
    valid_affiliations = ["Diocesan", "FSSP", "ICKSP", "Ordinariate", "SSPX", "Eastern Catholic"]
    if location.get("affiliation") and location["affiliation"] not in valid_affiliations:
        issues.append(f"Invalid affiliation: {location['affiliation']}. Must be one of: {valid_affiliations}")
    
    # Valid rite
    valid_rites = ["Latin", "Byzantine", "Maronite", "Melkite", "Ukrainian", "Ruthenian", "Chaldean"]
    if location.get("rite") and location["rite"] not in valid_rites:
        issues.append(f"Invalid rite: {location['rite']}. Must be one of: {valid_rites}")
    
    # Coordinates
    if location.get("latitude") or location.get("longitude"):
        try:
            lat = float(location.get("latitude", 0))
            lng = float(location.get("longitude", 0))
            if not (24 <= lat <= 50):  # US mainland latitude range
                issues.append(f"Latitude {lat} appears to be outside US mainland range (24-50)")
            if not (-125 <= lng <= -65):  # US mainland longitude range
                issues.append(f"Longitude {lng} appears to be outside US mainland range (-125 to -65)")
        except (ValueError, TypeError):
            issues.append("Invalid latitude or longitude format")
    else:
        issues.append("Warning: No coordinates provided - deduplication will be less accurate")
    
    # Check exclusion
    exclude_flag, exclude_reason = check_exclusion(
        location.get("name", ""),
        location.get("affiliation", ""),
        location.get("notes", "")
    )
    if exclude_flag:
        issues.append(f"EXCLUDED: {exclude_reason}")
    
    # Check for duplicates
    if location.get("name") and location.get("city") and location.get("state"):
        normalized = await normalize_location(location, "validation", None)
        duplicate = await find_duplicate(normalized)
        if duplicate:
            issues.append(f"Potential duplicate: {duplicate.get('name')} in {duplicate.get('city')}, {duplicate.get('state')}")
    
    return {
        "valid": len([i for i in issues if not i.startswith("Warning")]) == 0,
        "excluded": exclude_flag,
        "issues": issues,
        "location": location
    }


# ===================================
# DAILY SAINTS SYSTEM
# ===================================

# Daily Lives of the Saints Playlist ID
SAINTS_PLAYLIST_ID = os.environ.get('SAINTS_PLAYLIST_ID', 'PLSFbA-IaB3xprRODsXjEiXMV6QF9iGXol')

class DailySaintModel(BaseModel):
    """Model for daily saint entries"""
    id: Optional[str] = None
    videoId: str
    saintName: str
    feastDate: str  # Format: "YYYY-MM-DD"
    description: str
    thumbnail: str
    youtubeUrl: str
    publishedAt: str
    duration: str
    isActive: bool = True  # Currently displayed saint
    archivedAt: Optional[datetime] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)

def daily_saint_helper(saint) -> dict:
    """Convert MongoDB document to API response"""
    return {
        "id": str(saint["_id"]),
        "videoId": saint["videoId"],
        "saintName": saint["saintName"],
        "feastDate": saint["feastDate"],
        "description": saint["description"],
        "thumbnail": saint["thumbnail"],
        "youtubeUrl": saint["youtubeUrl"],
        "publishedAt": saint["publishedAt"],
        "duration": saint.get("duration", ""),
        "isActive": saint.get("isActive", False),
        "archivedAt": saint.get("archivedAt"),
        "createdAt": saint.get("createdAt", datetime.utcnow())
    }

def extract_saint_name_from_video(title: str, description: str) -> str:
    """Extract saint name from video title"""
    import re
    
    # Pattern: "Saint of the Day - St. [Name]" or similar
    patterns = [
        r'(?:Saint of the Day|Daily Lives of the Saints?)[\s\-:]+(?:St\.?\s+)?([A-Za-z\s]+?)(?:\s*[\|\-\(]|$)',
        r'St\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'Saint\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            name = name.rstrip('.,!?;:)')
            if not name.lower().startswith('st'):
                return f"St. {name}"
            return name
    
    # Fallback: use cleaned title
    clean_title = re.sub(r'[\|\-\(\)].*$', '', title).strip()
    return clean_title

def fetch_saints_playlist_videos():
    """
    Fetch videos from the Daily Lives of the Saints playlist
    Only returns Shorts (≤ 3 minutes)
    """
    try:
        all_videos = []
        next_page_token = None
        
        while True:
            url = f"{YOUTUBE_API_BASE}/playlistItems"
            params = {
                'key': YOUTUBE_API_KEY,
                'playlistId': SAINTS_PLAYLIST_ID,
                'part': 'snippet',
                'maxResults': 50
            }
            
            if next_page_token:
                params['pageToken'] = next_page_token
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            for item in data.get('items', []):
                video_id = item['snippet']['resourceId']['videoId']
                snippet = item['snippet']
                
                # Get video details for duration
                video_details = get_video_details(video_id)
                duration_str = video_details.get('duration', 'PT0S')
                duration_seconds = parse_duration_to_seconds(duration_str)
                
                # Only include Shorts (≤ 3 minutes / 180 seconds)
                if duration_seconds <= 180:
                    # Get best thumbnail available
                    thumbnails = snippet.get('thumbnails', {})
                    thumbnail_url = ''
                    for quality in ['maxres', 'high', 'medium', 'default']:
                        if quality in thumbnails and thumbnails[quality].get('url'):
                            thumbnail_url = thumbnails[quality]['url']
                            break
                    
                    video_data = {
                        'videoId': video_id,
                        'title': snippet['title'],
                        'description': snippet.get('description', ''),
                        'thumbnail': thumbnail_url,
                        'duration': duration_str,
                        'publishedAt': snippet['publishedAt'],
                    }
                    all_videos.append(video_data)
                    logging.info(f"Found saint video: {snippet['title'][:50]}...")
            
            next_page_token = data.get('nextPageToken')
            if not next_page_token:
                break
        
        logging.info(f"Fetched {len(all_videos)} saint videos from playlist")
        return all_videos
    except Exception as e:
        logging.error(f"Error fetching saints playlist: {str(e)}")
        return []

def get_cst_time():
    """Get current time in Central Standard Time (CST)"""
    from datetime import timezone, timedelta
    utc_now = datetime.now(timezone.utc)
    cst = timezone(timedelta(hours=-6))  # CST is UTC-6
    return utc_now.astimezone(cst)

def is_after_3pm_cst(published_at_str: str) -> bool:
    """Check if video was published at or after 3:00 PM CST"""
    from datetime import timezone, timedelta
    
    try:
        # Parse YouTube's ISO format
        published = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
        cst = timezone(timedelta(hours=-6))
        published_cst = published.astimezone(cst)
        
        # Check if it's at or after 3:00 PM (15:00)
        return published_cst.hour >= 15
    except Exception as e:
        logging.error(f"Error parsing date: {e}")
        return False


@api_router.get("/saints/today")
async def get_todays_saint():
    """
    Get today's Saint of the Day
    Returns the currently active saint, or the most recent saint if none for today
    """
    from datetime import timezone, timedelta
    
    # Get today's date in CST
    cst_now = get_cst_time()
    today_str = cst_now.strftime("%Y-%m-%d")
    
    # Try to find a saint for today
    todays_saint = await db.daily_saints.find_one({
        "feastDate": today_str
    })
    
    if todays_saint:
        # Mark as active
        await db.daily_saints.update_one(
            {"_id": todays_saint["_id"]},
            {"$set": {"isActive": True}}
        )
        return daily_saint_helper(todays_saint)
    
    # No saint for today - get the most recent one
    most_recent = await db.daily_saints.find_one(
        {"thumbnail": {"$ne": ""}},  # Exclude private videos
        sort=[("feastDate", -1)]
    )
    
    if most_recent:
        most_recent_data = daily_saint_helper(most_recent)
        
        # If it's past 3:15 PM CST and no new saint, show notice
        if cst_now.hour >= 15 and cst_now.minute >= 15:
            most_recent_data["notice"] = "Today's saint will be posted shortly."
        
        return most_recent_data
    
    # No saints at all - return placeholder
    return {
        "videoId": None,
        "saintName": "Saint of the Day",
        "feastDate": today_str,
        "description": "Today's saint will be posted shortly.",
        "thumbnail": "/placeholder-saint.jpg",
        "youtubeUrl": "",
        "notice": "Today's saint will be posted shortly."
    }


@api_router.get("/saints/archive")
async def get_saints_archive(
    limit: int = 100,
    offset: int = 0,
    month: Optional[int] = None,
    year: Optional[int] = None
):
    """
    Get archived saints with pagination and optional date filtering
    Excludes private videos (those with empty thumbnails)
    """
    query = {"thumbnail": {"$ne": ""}}  # Exclude private videos
    
    if month and year:
        # Filter by specific month/year
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        query["feastDate"] = {"$gte": start_date, "$lt": end_date}
    elif year:
        query["feastDate"] = {"$regex": f"^{year}"}
    
    # Get total count
    total = await db.daily_saints.count_documents(query)
    
    # Get saints with pagination, sorted by date descending
    saints = await db.daily_saints.find(query).sort(
        "feastDate", -1
    ).skip(offset).limit(limit).to_list(limit)
    
    return {
        "saints": [daily_saint_helper(saint) for saint in saints],
        "total": total,
        "limit": limit,
        "offset": offset,
        "hasMore": offset + len(saints) < total
    }


@api_router.get("/saints/{saint_id}")
async def get_saint_by_id(saint_id: str):
    """Get a specific saint entry by ID"""
    try:
        saint = await db.daily_saints.find_one({"_id": ObjectId(saint_id)})
        if not saint:
            raise HTTPException(status_code=404, detail="Saint not found")
        return daily_saint_helper(saint)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/saints/refresh")
async def refresh_saints_from_playlist():
    """
    Refresh saints from the YouTube playlist
    Checks for new videos published after 3 PM CST today
    Archives previous day's saint if needed
    """
    from datetime import timezone, timedelta
    
    cst_now = get_cst_time()
    today_str = cst_now.strftime("%Y-%m-%d")
    
    # Fetch videos from playlist
    videos = fetch_saints_playlist_videos()
    
    if not videos:
        return {"message": "No videos found in playlist", "added": 0}
    
    added_count = 0
    
    for video in videos:
        video_id = video['videoId']
        published_at = video['publishedAt']
        
        # Check if video already exists in our database
        existing = await db.daily_saints.find_one({"videoId": video_id})
        if existing:
            continue
        
        # Parse the publish date
        try:
            published_dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            cst = timezone(timedelta(hours=-6))
            published_cst = published_dt.astimezone(cst)
            video_date = published_cst.strftime("%Y-%m-%d")
        except:
            continue
        
        # Check if published at or after 3 PM CST
        if not is_after_3pm_cst(published_at):
            continue
        
        # Extract saint name
        saint_name = extract_saint_name_from_video(video['title'], video['description'])
        
        # Archive any currently active saint for a different date
        await db.daily_saints.update_many(
            {"isActive": True, "feastDate": {"$ne": video_date}},
            {"$set": {"isActive": False, "archivedAt": datetime.utcnow()}}
        )
        
        # Create new saint entry
        saint_entry = {
            "videoId": video_id,
            "saintName": saint_name,
            "feastDate": video_date,
            "description": video['description'][:500] if video['description'] else "",
            "thumbnail": video['thumbnail'],
            "youtubeUrl": f"https://www.youtube.com/shorts/{video_id}",
            "publishedAt": published_at,
            "duration": video['duration'],
            "isActive": video_date == today_str,
            "createdAt": datetime.utcnow()
        }
        
        await db.daily_saints.insert_one(saint_entry)
        added_count += 1
        logging.info(f"Added saint: {saint_name} for {video_date}")
    
    return {
        "message": f"Refresh complete",
        "added": added_count,
        "total_in_playlist": len(videos)
    }


@api_router.post("/saints/sync-all")
async def sync_all_saints_from_playlist():
    """
    Full sync: Import ALL videos from the saints playlist
    Useful for initial setup or re-syncing the entire archive
    """
    from datetime import timezone, timedelta
    
    videos = fetch_saints_playlist_videos()
    
    if not videos:
        return {"message": "No videos found in playlist", "synced": 0}
    
    synced_count = 0
    skipped_count = 0
    
    cst = timezone(timedelta(hours=-6))
    cst_now = get_cst_time()
    today_str = cst_now.strftime("%Y-%m-%d")
    
    for video in videos:
        video_id = video['videoId']
        
        # Skip if already exists
        existing = await db.daily_saints.find_one({"videoId": video_id})
        if existing:
            skipped_count += 1
            continue
        
        # Parse publish date for feast date
        try:
            published_dt = datetime.fromisoformat(video['publishedAt'].replace('Z', '+00:00'))
            published_cst = published_dt.astimezone(cst)
            video_date = published_cst.strftime("%Y-%m-%d")
        except:
            video_date = video['publishedAt'][:10]
        
        # Extract saint name
        saint_name = extract_saint_name_from_video(video['title'], video['description'])
        
        # Create saint entry
        saint_entry = {
            "videoId": video_id,
            "saintName": saint_name,
            "feastDate": video_date,
            "description": video['description'][:500] if video['description'] else "",
            "thumbnail": video['thumbnail'],
            "youtubeUrl": f"https://www.youtube.com/shorts/{video_id}",
            "publishedAt": video['publishedAt'],
            "duration": video['duration'],
            "isActive": video_date == today_str,
            "createdAt": datetime.utcnow()
        }
        
        await db.daily_saints.insert_one(saint_entry)
        synced_count += 1
    
    # Ensure only today's saint is active
    await db.daily_saints.update_many(
        {"feastDate": {"$ne": today_str}},
        {"$set": {"isActive": False}}
    )
    
    return {
        "message": "Full sync complete",
        "synced": synced_count,
        "skipped": skipped_count,
        "total_in_playlist": len(videos)
    }


@api_router.get("/saints/date/{date}")
async def get_saint_by_date(date: str):
    """
    Get saint for a specific date (format: YYYY-MM-DD)
    """
    saint = await db.daily_saints.find_one({"feastDate": date})
    
    if not saint:
        raise HTTPException(status_code=404, detail=f"No saint found for {date}")
    
    return daily_saint_helper(saint)


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
