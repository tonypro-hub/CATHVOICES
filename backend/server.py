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
def fetch_youtube_videos():
    """Fetch ALL videos from YouTube channel's Videos section"""
    try:
        url = f"{YOUTUBE_API_BASE}/search"
        params = {
            'key': YOUTUBE_API_KEY,
            'channelId': YOUTUBE_CHANNEL_ID,
            'part': 'snippet',
            'type': 'video',
            'order': 'date',
            'maxResults': 50  # Fetch all videos, no duration filter
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        videos = []
        for item in data.get('items', []):
            video_id = item['id']['videoId']
            snippet = item['snippet']
            
            # Get video details for duration and other metadata
            video_details = get_video_details(video_id)
            
            # Extract category/tags from title and description
            category = extract_category_from_metadata(snippet['title'], snippet['description'])
            
            videos.append({
                'videoId': video_id,
                'title': snippet['title'],
                'description': snippet['description'],
                'thumbnail': snippet['thumbnails']['high']['url'],
                'duration': video_details.get('duration', 'Unknown'),
                'publishedAt': snippet['publishedAt'],
                'category': category,
                'tags': video_details.get('tags', []),
                'cachedAt': datetime.utcnow()
            })
        
        return videos
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
    """Manually refresh videos from YouTube"""
    videos = fetch_youtube_videos()
    
    if videos:
        # Clear existing cache
        await db.videos.delete_many({})
        
        # Insert new videos
        if videos:
            await db.videos.insert_many(videos)
        
        return {
            "message": f"Successfully cached {len(videos)} videos",
            "count": len(videos)
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to fetch videos from YouTube")


@api_router.get("/videos")
async def get_videos():
    """Get all cached videos"""
    videos = await db.videos.find().sort("publishedAt", -1).to_list(100)
    return [video_helper(video) for video in videos]


@api_router.get("/videos/{video_id}")
async def get_video(video_id: str):
    """Get a specific video by videoId"""
    video = await db.videos.find_one({"videoId": video_id})
    if video:
        return video_helper(video)
    raise HTTPException(status_code=404, detail="Video not found")


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
