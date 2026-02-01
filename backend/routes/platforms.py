from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.auth_service import get_current_user

router = APIRouter()
security = HTTPBearer()

@router.get("/youtube/auth-url")
async def get_youtube_auth_url(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get YouTube OAuth URL"""
    user = await get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return {"message": "YouTube OAuth integration coming soon"}

@router.post("/youtube/callback")
async def youtube_oauth_callback(code: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Handle YouTube OAuth callback"""
    user = await get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return {"message": "YouTube OAuth callback handler coming soon"}

@router.get("/accounts")
async def get_connected_accounts(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all connected accounts for user"""
    user = await get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return {"accounts": [], "message": "Account listing coming soon"}