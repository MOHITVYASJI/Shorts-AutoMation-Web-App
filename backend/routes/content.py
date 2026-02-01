from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import logging

from services.auth_service import get_current_user
from services.content_generator import get_content_generator, ContentGenerationError
from services.tts_generator import get_tts_generator, TTSGenerationError
from services.visual_generator import get_visual_generator, VisualGenerationError
from config.constants import NICHES, LANGUAGES, DURATION_OPTIONS, VOICE_IDS

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Request models
class ScriptGenerationRequest(BaseModel):
    platform: str
    niche: str
    language: str = "English"
    duration: int = 30

class VoiceGenerationRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None
    language: str = "en"

class VoiceFromScriptRequest(BaseModel):
    script: dict
    voice_id: Optional[str] = None

class VisualGenerationRequest(BaseModel):
    script: dict
    niche: str
    count: int = 3
    style: str = "realistic"

# Info endpoints
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

@router.get("/voices")
async def get_voices():
    """Get available voice IDs for TTS"""
    tts_gen = get_tts_generator()
    return {"voices": tts_gen.get_available_voices()}

# Content generation endpoints
@router.post("/generate-script")
async def generate_script(
    request: ScriptGenerationRequest = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Generate AI script for video
    
    Requires authentication. Generates a complete video script including:
    - Hook (attention-grabbing opening)
    - Body (main content)
    - Ending (loop-compatible ending)
    - Title, description, and hashtags
    """
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        logger.info(f"Generating script for user {user.get('email')} - niche: {request.niche}")
        
        content_gen = get_content_generator()
        script = await content_gen.generate_script(
            platform=request.platform,
            niche=request.niche,
            language=request.language,
            duration=request.duration
        )
        
        return {
            "success": True,
            "script": script,
            "message": "Script generated successfully"
        }
        
    except ContentGenerationError as e:
        logger.error(f"Content generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in script generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Script generation failed")

@router.post("/generate-voice")
async def generate_voice(
    request: VoiceGenerationRequest = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Generate voice from text using ElevenLabs TTS
    
    Requires authentication. Converts text to high-quality speech audio.
    """
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        logger.info(f"Generating voice for user {user.get('email')}")
        
        tts_gen = get_tts_generator()
        audio_path = await tts_gen.generate_voice(
            text=request.text,
            voice_id=request.voice_id,
            language=request.language
        )
        
        return {
            "success": True,
            "audio_path": audio_path,
            "message": "Voice generated successfully"
        }
        
    except TTSGenerationError as e:
        logger.error(f"TTS generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in voice generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Voice generation failed")

@router.post("/generate-voice-from-script")
async def generate_voice_from_script(
    request: VoiceFromScriptRequest = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Generate voice from a complete script (hook + body + ending)
    
    Requires authentication. Combines script parts and generates voice.
    """
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        logger.info(f"Generating voice from script for user {user.get('email')}")
        
        tts_gen = get_tts_generator()
        audio_path = await tts_gen.generate_voice_for_script(
            script_data=request.script,
            voice_id=request.voice_id
        )
        
        return {
            "success": True,
            "audio_path": audio_path,
            "message": "Voice generated successfully from script"
        }
        
    except TTSGenerationError as e:
        logger.error(f"TTS generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in voice generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Voice generation from script failed")

@router.post("/generate-visuals")
async def generate_visuals(
    request: VisualGenerationRequest = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Generate AI images for video based on script
    
    Requires authentication. Generates images using OpenAI DALL-E.
    """
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        logger.info(f"Generating visuals for user {user.get('email')} - count: {request.count}")
        
        visual_gen = get_visual_generator()
        image_paths = await visual_gen.generate_visuals(
            script_data=request.script,
            niche=request.niche,
            count=request.count,
            style=request.style
        )
        
        return {
            "success": True,
            "image_paths": image_paths,
            "count": len(image_paths),
            "message": f"Generated {len(image_paths)} images successfully"
        }
        
    except VisualGenerationError as e:
        logger.error(f"Visual generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in visual generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Visual generation failed")

@router.post("/generate-complete")
async def generate_complete_content(
    request: ScriptGenerationRequest = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Generate complete content package: script + voice + visuals
    
    Requires authentication. One-stop endpoint for generating all content.
    """
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        logger.info(f"Generating complete content for user {user.get('email')}")
        
        # Step 1: Generate script
        content_gen = get_content_generator()
        script = await content_gen.generate_script(
            platform=request.platform,
            niche=request.niche,
            language=request.language,
            duration=request.duration
        )
        
        # Step 2: Generate voice
        tts_gen = get_tts_generator()
        audio_path = await tts_gen.generate_voice_for_script(script)
        
        # Step 3: Generate visuals
        visual_gen = get_visual_generator()
        image_paths = await visual_gen.generate_visuals(
            script_data=script,
            niche=request.niche,
            count=3,
            style="realistic"
        )
        
        return {
            "success": True,
            "script": script,
            "audio_path": audio_path,
            "image_paths": image_paths,
            "message": "Complete content package generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Complete content generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")