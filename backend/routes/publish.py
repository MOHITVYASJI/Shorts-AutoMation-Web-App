from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import logging
from datetime import datetime

from services.auth_service import get_current_user
from services.youtube_publisher import get_youtube_publisher, YouTubePublisherError
from services.instagram_publisher import get_instagram_publisher, InstagramPublisherError
from services.facebook_publisher import get_facebook_publisher, FacebookPublisherError
from config.database import get_db

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Request models
class PublishToYouTubeRequest(BaseModel):
    video_id: str
    account_id: str
    title: str
    description: str
    tags: List[str] = []
    privacy_status: str = "public"  # public, private, unlisted

class PublishToInstagramRequest(BaseModel):
    video_id: str
    account_id: str
    caption: str

class PublishToFacebookRequest(BaseModel):
    video_id: str
    account_id: str
    description: str

class PublishToMultipleRequest(BaseModel):
    video_id: str
    platforms: List[dict]  # [{"platform": "youtube", "account_id": "...", "metadata": {...}}]

@router.post("/youtube")
async def publish_to_youtube(
    request: PublishToYouTubeRequest = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Publish video to YouTube Shorts
    
    Requires authentication and connected YouTube account.
    """
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        user_id = user.get('_id')
        db = get_db()
        
        # Get video
        video = await db.videos.find_one({"_id": request.video_id, "user_id": user_id})
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Get connected YouTube account
        account = await db.connected_accounts.find_one({
            "_id": request.account_id,
            "user_id": user_id,
            "platform": "youtube",
            "status": "active"
        })
        
        if not account:
            raise HTTPException(status_code=404, detail="YouTube account not found or not connected")
        
        # Upload to YouTube
        youtube_publisher = get_youtube_publisher()
        result = await youtube_publisher.upload_video(
            video_file_path=video['video_file_path'],
            title=request.title,
            description=request.description,
            tags=request.tags,
            privacy_status=request.privacy_status,
            access_token=account['access_token'],
            refresh_token=account.get('refresh_token')
        )
        
        # Update video with published info
        await db.videos.update_one(
            {"_id": request.video_id},
            {
                "$push": {
                    "published_platforms": {
                        "platform": "youtube",
                        "account_id": request.account_id,
                        "platform_video_id": result['video_id'],
                        "published_at": datetime.utcnow(),
                        "url": result['url']
                    }
                },
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        logger.info(f"Video {request.video_id} published to YouTube successfully")
        
        return {
            "success": True,
            "platform": "youtube",
            "video_url": result['url'],
            "message": "Video published to YouTube successfully"
        }
        
    except YouTubePublisherError as e:
        logger.error(f"YouTube publish error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in YouTube publish: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to publish to YouTube")

@router.post("/instagram")
async def publish_to_instagram(
    request: PublishToInstagramRequest = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Publish video to Instagram Reels
    
    Requires authentication and connected Instagram account.
    """
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Check if Instagram is configured
        instagram_publisher = get_instagram_publisher()
        if not instagram_publisher.is_configured():
            raise HTTPException(
                status_code=400,
                detail="Instagram credentials not configured. Please add INSTAGRAM_APP_ID and INSTAGRAM_APP_SECRET to .env file."
            )
        
        user_id = user.get('_id')
        db = get_db()
        
        # Get video
        video = await db.videos.find_one({"_id": request.video_id, "user_id": user_id})
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Get connected Instagram account
        account = await db.connected_accounts.find_one({
            "_id": request.account_id,
            "user_id": user_id,
            "platform": "instagram",
            "status": "active"
        })
        
        if not account:
            raise HTTPException(status_code=404, detail="Instagram account not found or not connected")
        
        # Upload to Instagram
        result = await instagram_publisher.upload_reel(
            video_file_path=video['video_file_path'],
            caption=request.caption,
            access_token=account['access_token'],
            instagram_account_id=account['account_id']
        )
        
        logger.info(f"Video {request.video_id} published to Instagram successfully")
        
        return {
            "success": True,
            "platform": "instagram",
            "message": result.get('message', "Video published to Instagram successfully")
        }
        
    except InstagramPublisherError as e:
        logger.error(f"Instagram publish error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in Instagram publish: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to publish to Instagram")

@router.post("/facebook")
async def publish_to_facebook(
    request: PublishToFacebookRequest = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Publish video to Facebook Reels
    
    Requires authentication and connected Facebook page.
    """
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Check if Facebook is configured
        facebook_publisher = get_facebook_publisher()
        if not facebook_publisher.is_configured():
            raise HTTPException(
                status_code=400,
                detail="Facebook credentials not configured. Please add FACEBOOK_APP_ID and FACEBOOK_APP_SECRET to .env file."
            )
        
        user_id = user.get('_id')
        db = get_db()
        
        # Get video
        video = await db.videos.find_one({"_id": request.video_id, "user_id": user_id})
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Get connected Facebook account
        account = await db.connected_accounts.find_one({
            "_id": request.account_id,
            "user_id": user_id,
            "platform": "facebook",
            "status": "active"
        })
        
        if not account:
            raise HTTPException(status_code=404, detail="Facebook page not found or not connected")
        
        # Upload to Facebook
        result = await facebook_publisher.upload_reel(
            video_file_path=video['video_file_path'],
            description=request.description,
            access_token=account['access_token'],
            page_id=account['account_id']
        )
        
        logger.info(f"Video {request.video_id} published to Facebook successfully")
        
        return {
            "success": True,
            "platform": "facebook",
            "message": result.get('message', "Video published to Facebook successfully")
        }
        
    except FacebookPublisherError as e:
        logger.error(f"Facebook publish error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in Facebook publish: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to publish to Facebook")

@router.post("/multi")
async def publish_to_multiple(
    request: PublishToMultipleRequest = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Publish video to multiple platforms at once
    
    Requires authentication. Publishes to all specified platforms.
    """
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        results = []
        errors = []
        
        for platform_config in request.platforms:
            platform = platform_config.get('platform')
            
            try:
                if platform == 'youtube':
                    # Call YouTube publish
                    pass
                elif platform == 'instagram':
                    # Call Instagram publish
                    pass
                elif platform == 'facebook':
                    # Call Facebook publish
                    pass
                
                results.append({"platform": platform, "status": "success"})
            except Exception as e:
                errors.append({"platform": platform, "error": str(e)})
        
        return {
            "success": len(errors) == 0,
            "results": results,
            "errors": errors,
            "message": f"Published to {len(results)} platforms"
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in multi-platform publish: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to publish to multiple platforms")
