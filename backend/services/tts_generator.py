"""Text-to-Speech generation service using ElevenLabs"""
import logging
from typing import Optional
import os
import uuid
from pathlib import Path
from elevenlabs import ElevenLabs, VoiceSettings
from config.settings import get_settings
from config.constants import VOICE_IDS

logger = logging.getLogger(__name__)
settings = get_settings()


class TTSGenerationError(Exception):
    """Exception raised for TTS generation errors"""
    pass


class TTSGenerator:
    """Generate high-quality voiceovers using ElevenLabs"""
    
    def __init__(self):
        self.elevenlabs_available = bool(settings.elevenlabs_api_key)
        
        if self.elevenlabs_available:
            self.client = ElevenLabs(api_key=settings.elevenlabs_api_key)
        else:
            logger.warning("ElevenLabs API key not configured. TTS generation will fail.")
            self.client = None
    
    async def generate_voice(self, text: str, voice_id: Optional[str] = None, language: str = "en") -> str:
        """Generate voice audio from text
        
        Args:
            text: The script text to convert to speech
            voice_id: ElevenLabs voice ID (default: male_1)
            language: Language code (default: en)
        
        Returns:
            str: File path to the generated audio file
        """
        if not self.elevenlabs_available or not self.client:
            raise TTSGenerationError("ElevenLabs API key not configured")
        
        try:
            # Default to male voice if not specified
            if not voice_id:
                voice_id = VOICE_IDS.get("male_1", "21m00Tcm4TlvDq8ikWAM")
            
            # Generate unique filename
            audio_filename = f"voice_{uuid.uuid4()}.mp3"
            audio_path = os.path.join(settings.audio_storage_path, audio_filename)
            
            # Ensure directory exists
            Path(settings.audio_storage_path).mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Generating voice for text length: {len(text)} characters")
            
            # Generate audio using ElevenLabs
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                optimize_streaming_latency=0,
                output_format="mp3_44100_128",
                text=text,
                model_id="eleven_multilingual_v2",
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.0,
                    use_speaker_boost=True
                )
            )
            
            # Save audio to file
            with open(audio_path, "wb") as audio_file:
                for chunk in audio_generator:
                    audio_file.write(chunk)
            
            logger.info(f"Voice generated successfully: {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"ElevenLabs TTS generation failed: {str(e)}")
            raise TTSGenerationError(f"TTS generation failed: {str(e)}")
    
    async def generate_voice_for_script(self, script_data: dict, voice_id: Optional[str] = None) -> str:
        """Generate voice from a complete script (hook + body + ending)
        
        Args:
            script_data: Dictionary containing 'hook', 'body', 'ending'
            voice_id: ElevenLabs voice ID
        
        Returns:
            str: File path to the generated audio file
        """
        # Combine script parts
        full_text = f"{script_data.get('hook', '')} {script_data.get('body', '')} {script_data.get('ending', '')}"
        full_text = full_text.strip()
        
        if not full_text:
            raise TTSGenerationError("Script text is empty")
        
        return await self.generate_voice(full_text, voice_id)
    
    def get_available_voices(self) -> dict:
        """Get list of available voice IDs"""
        return VOICE_IDS


# Singleton instance
_tts_generator: Optional[TTSGenerator] = None

def get_tts_generator() -> TTSGenerator:
    """Get TTSGenerator singleton instance"""
    global _tts_generator
    if _tts_generator is None:
        _tts_generator = TTSGenerator()
    return _tts_generator
