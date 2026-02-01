from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.auth_service import get_current_user
from config.constants import NICHES, LANGUAGES, DURATION_OPTIONS

router = APIRouter()
security = HTTPBearer()

@router.get("/niches")
async def get_niches():
    """Get available content niches"""
    return {"niches": NICHES}

@router.get("/languages")
async def get_languages():
    """Get supported languages"""
    return {"languages": LANGUAGES}

@router.get("/durations")
async def get_durations():
    """Get available video durations"""
    return {"durations": DURATION_OPTIONS}

@router.post("/generate-script")
async def generate_script(
    platform: str,
    niche: str,
    language: str,
    duration: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Generate AI script for video"""
    user = await get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return {"message": "Script generation coming soon"}