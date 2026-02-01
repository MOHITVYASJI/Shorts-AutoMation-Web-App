from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import logging
import os
import uuid
from datetime import datetime

from services.auth_service import get_current_user
from services.video_renderer import get_video_renderer, VideoRenderError
from config.database import get_db
from config.settings import get_settings

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)
settings = get_settings()

# Request models
class RenderVideoRequest(BaseModel):
    audio_path: str
    image_paths: List[str]
    duration: int = 30
    add_captions: bool = False
    background_music_path: Optional[str] = None
    script: Optional[dict] = None
    title: str
    description: str
    hashtags: List[str] = []
    niche: str

class UpdateVideoRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    hashtags: Optional[List[str]] = None

@router.post("/render")
async def render_video(
    request: RenderVideoRequest = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Render a video from audio and images
    
    Requires authentication. Creates a video by combining audio, images,
    and optionally captions and background music.
    """
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        user_id = user.get('_id')
        logger.info(f"Rendering video for user {user.get('email')}")
        
        # Generate unique video ID
        video_id = str(uuid.uuid4())
        
        # Render video
        renderer = get_video_renderer()
        output_filename = f"video_{video_id}.mp4"
        
        video_path = await renderer.render_video(
            audio_path=request.audio_path,
            image_paths=request.image_paths,
            duration=request.duration,
            output_filename=output_filename,
            add_captions=request.add_captions,
            background_music_path=request.background_music_path
        )
        
        # Store video metadata in database
        db = get_db()
        video_data = {
            "_id": video_id,
            "user_id": user_id,
            "title": request.title,
            "description": request.description,
            "hashtags": request.hashtags,
            "script": request.script,
            "niche": request.niche,
            "duration": request.duration,
            "video_file_path": video_path,
            "audio_file_path": request.audio_path,
            "image_paths": request.image_paths,
            "status": "completed",
            "published_platforms": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.videos.insert_one(video_data)
        
        logger.info(f"Video {video_id} rendered and saved successfully")
        
        return {
            "success": True,
            "video_id": video_id,
            "video_path": video_path,
            "message": "Video rendered successfully"
        }
        
    except VideoRenderError as e:
        logger.error(f"Video render error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in video rendering: {str(e)}")
        raise HTTPException(status_code=500, detail="Video rendering failed")

@router.get("/")
async def list_videos(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    skip: int = 0,
    limit: int = 50
):
    """List all videos for the authenticated user
    
    Supports pagination with skip and limit parameters.
    """
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        user_id = user.get('_id')
        db = get_db()
        
        # Get videos for user
        cursor = db.videos.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
        videos = await cursor.to_list(length=limit)
        
        # Count total videos
        total = await db.videos.count_documents({"user_id": user_id})
        
        return {
            "success": True,
            "videos": videos,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error listing videos: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch videos")

@router.get("/{video_id}")
async def get_video(
    video_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get details of a specific video"""
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        user_id = user.get('_id')
        db = get_db()
        
        # Get video
        video = await db.videos.find_one({"_id": video_id, "user_id": user_id})
        
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return {
            "success": True,
            "video": video
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching video: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch video")

@router.put("/{video_id}")
async def update_video(
    video_id: str,
    request: UpdateVideoRequest = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update video metadata"""
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        user_id = user.get('_id')
        db = get_db()
        
        # Check if video exists and belongs to user
        video = await db.videos.find_one({"_id": video_id, "user_id": user_id})
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Prepare update data
        update_data = {"updated_at": datetime.utcnow()}
        if request.title is not None:
            update_data["title"] = request.title
        if request.description is not None:
            update_data["description"] = request.description
        if request.hashtags is not None:
            update_data["hashtags"] = request.hashtags
        
        # Update video
        await db.videos.update_one(
            {"_id": video_id},
            {"$set": update_data}
        )
        
        logger.info(f"Video {video_id} updated successfully")
        
        return {
            "success": True,
            "message": "Video updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating video: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update video")

@router.delete("/{video_id}")
async def delete_video(
    video_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete a video"""
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        user_id = user.get('_id')
        db = get_db()
        
        # Check if video exists and belongs to user
        video = await db.videos.find_one({"_id": video_id, "user_id": user_id})
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Delete video file if it exists
        if video.get('video_file_path'):
            video_path = video['video_file_path']
            if os.path.exists(video_path):
                os.remove(video_path)
        
        # Delete from database
        await db.videos.delete_one({"_id": video_id})
        
        logger.info(f"Video {video_id} deleted successfully")
        
        return {
            "success": True,
            "message": "Video deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting video: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete video")

@router.get("/{video_id}/download")
async def download_video(
    video_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Download a video file"""
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        user_id = user.get('_id')
        db = get_db()
        
        # Get video
        video = await db.videos.find_one({"_id": video_id, "user_id": user_id})
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        video_path = video.get('video_file_path')
        if not video_path or not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video file not found")
        
        # Return file
        return FileResponse(
            path=video_path,
            media_type="video/mp4",
            filename=f"{video.get('title', 'video')}_{video_id}.mp4"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading video: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download video")
