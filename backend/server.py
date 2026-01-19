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
    
    # A video is a Short if it's 60 seconds or less
    if duration_seconds <= 60:
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
    """Fetch ALL long-form videos from channel's Uploads playlist, excluding Shorts"""
    try:
        # Step 1: Get the uploads playlist ID
        uploads_playlist_id = get_uploads_playlist_id()
        if not uploads_playlist_id:
            logging.error("Could not retrieve uploads playlist ID")
            return []
        
        all_videos = []
        next_page_token = None
        page_count = 0
        shorts_filtered = 0
        
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
                
                # Skip if it's a Short
                if is_youtube_short(video_details):
                    shorts_filtered += 1
                    logging.info(f"Filtered out Short: {snippet['title'][:50]}...")
                    continue
                
                # Extract category/tags from title and description
                category = extract_category_from_metadata(snippet['title'], snippet['description'])
                
                all_videos.append({
                    'videoId': video_id,
                    'title': snippet['title'],
                    'description': snippet['description'],
                    'thumbnail': snippet['thumbnails']['high']['url'] if 'high' in snippet['thumbnails'] else snippet['thumbnails']['default']['url'],
                    'duration': video_details.get('duration', 'Unknown'),
                    'publishedAt': snippet['publishedAt'],
                    'category': category,
                    'tags': video_details.get('tags', []),
                    'cachedAt': datetime.utcnow()
                })
            
            # Check if there are more pages
            next_page_token = data.get('nextPageToken')
            if next_page_token:
                logging.info(f"Found nextPageToken, continuing to page {page_count + 1}")
            else:
                logging.info(f"No more pages. Total pages fetched: {page_count}")
                break
        
        logging.info(f"Successfully fetched {len(all_videos)} long-form videos (filtered out {shorts_filtered} Shorts)")
        return all_videos
    except Exception as e:
        logging.error(f"Error fetching YouTube videos: {str(e)}")
        return []

def extract_category_from_metadata(title: str, description: str):
    """Extract category from video title or description"""
    title_lower = title.lower()
    desc_lower = description.lower()
    
    # Define category keywords
    if 'rosary' in title_lower or 'rosary' in desc_lower:
        return 'The Rosary'
    elif 'novena' in title_lower or 'novena' in desc_lower:
        return 'Novenas'
    elif any(word in title_lower for word in ['our father', 'hail mary', 'glory be', 'apostles creed']):
        return 'Traditional Prayers'
    elif 'saint' in title_lower or 'st.' in title_lower or 'saint' in desc_lower:
        return 'Saints & Feast Days'
    elif 'chaplet' in title_lower or 'litany' in title_lower:
        return 'Devotions'
    else:
        return 'Prayers'

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
async def get_content(category: Optional[str] = None):
    """
    Get all content (videos with optional prayer text overlay)
    This is the primary content endpoint
    """
    query = {}
    if category:
        query["category"] = category
    
    # Get all videos
    videos = await db.videos.find(query).sort("publishedAt", -1).to_list(None)  # No limit - get all
    
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
            "prayerText": prayer["prayerText"] if prayer else None,
            "hasPrayerText": prayer is not None
        }
        content_items.append(content_item)
    
    return content_items


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
