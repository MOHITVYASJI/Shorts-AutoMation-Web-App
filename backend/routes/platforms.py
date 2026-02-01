from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import logging

from services.auth_service import get_current_user
from services.youtube_publisher import get_youtube_publisher, YouTubePublisherError
from config.database import get_db

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# YouTube OAuth endpoints
@router.get("/youtube/auth-url")
async def get_youtube_auth_url(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get YouTube OAuth authorization URL"""
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        youtube_publisher = get_youtube_publisher()
        auth_url = youtube_publisher.get_authorization_url(str(user["_id"]))
        
        return {
            "success": True,
            "auth_url": auth_url,
            "platform": "youtube"
        }
        
    except YouTubePublisherError as e:
        logger.error(f"YouTube auth URL error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting YouTube auth URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate auth URL")

@router.post("/youtube/callback")
async def youtube_oauth_callback(
    code: str = Query(...),
    state: str = Query(...)
):
    """Handle YouTube OAuth callback
    
    Note: This endpoint is called by Google's OAuth redirect.
    State parameter contains user_id.
    """
    try:
        youtube_publisher = get_youtube_publisher()
        result = await youtube_publisher.handle_oauth_callback(code, state)
        
        # Return HTML that closes popup and notifies parent window
        return {
            "success": True,
            "message": "YouTube account connected successfully",
            "account": result
        }
        
    except YouTubePublisherError as e:
        logger.error(f"YouTube callback error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in YouTube callback: {str(e)}")
        raise HTTPException(status_code=500, detail="OAuth callback failed")

# Instagram OAuth endpoints
@router.get("/instagram/auth-url")
async def get_instagram_auth_url(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get Instagram OAuth authorization URL"""
    user = await get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Instagram credentials not configured yet
    raise HTTPException(
        status_code=503,
        detail="Instagram integration coming soon. Please configure Instagram App credentials."
    )

@router.post("/instagram/callback")
async def instagram_oauth_callback(code: str = Query(...), state: str = Query(...)):
    """Handle Instagram OAuth callback"""
    raise HTTPException(
        status_code=503,
        detail="Instagram integration coming soon"
    )

# Facebook OAuth endpoints
@router.get("/facebook/auth-url")
async def get_facebook_auth_url(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get Facebook OAuth authorization URL"""
    user = await get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Facebook credentials not configured yet
    raise HTTPException(
        status_code=503,
        detail="Facebook integration coming soon. Please configure Facebook App credentials."
    )

@router.post("/facebook/callback")
async def facebook_oauth_callback(code: str = Query(...), state: str = Query(...)):
    """Handle Facebook OAuth callback"""
    raise HTTPException(
        status_code=503,
        detail="Facebook integration coming soon"
    )

# Account management endpoints
@router.get("/accounts")
async def get_connected_accounts(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all connected accounts for the current user"""
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        db = get_db()
        accounts = await db.connected_accounts.find({
            "user_id": str(user["_id"])
        }).to_list(length=100)
        
        # Format accounts for response
        formatted_accounts = []
        for account in accounts:
            formatted_accounts.append({
                "id": str(account["_id"]),
                "platform": account["platform"],
                "account_id": account["account_id"],
                "account_name": account["account_name"],
                "status": account["status"],
                "connected_at": account.get("connected_at"),
            })
        
        return {
            "success": True,
            "accounts": formatted_accounts,
            "count": len(formatted_accounts)
        }
        
    except Exception as e:
        logger.error(f"Error fetching accounts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch connected accounts")

@router.delete("/accounts/{account_id}")
async def disconnect_account(
    account_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Disconnect a connected account"""
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        db = get_db()
        
        # Find account
        from bson import ObjectId
        account = await db.connected_accounts.find_one({
            "_id": ObjectId(account_id),
            "user_id": str(user["_id"])
        })
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Delete account
        await db.connected_accounts.delete_one({"_id": ObjectId(account_id)})
        
        logger.info(f"Disconnected {account['platform']} account for user: {user['email']}")
        
        return {
            "success": True,
            "message": f"{account['platform'].capitalize()} account disconnected successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disconnecting account: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to disconnect account")
