from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App configuration
    app_env: str = "development"
    secret_key: str = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    jwt_secret_key: str = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    
    # Database
    mongo_url: str = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    db_name: str = os.environ.get("DB_NAME", "autoshorts_ai")
    
    # OpenAI
    openai_api_key: Optional[str] = os.environ.get("OPENAI_API_KEY")
    
    # Gemini
    gemini_api_key: Optional[str] = os.environ.get("GEMINI_API_KEY")
    
    # ElevenLabs
    elevenlabs_api_key: Optional[str] = os.environ.get("ELEVENLABS_API_KEY")
    
    # YouTube OAuth
    youtube_client_id: Optional[str] = os.environ.get("YOUTUBE_CLIENT_ID")
    youtube_client_secret: Optional[str] = os.environ.get("YOUTUBE_CLIENT_SECRET")
    youtube_redirect_uri: Optional[str] = None
    
    # Instagram OAuth (Meta)
    instagram_app_id: Optional[str] = os.environ.get("INSTAGRAM_APP_ID")
    instagram_app_secret: Optional[str] = os.environ.get("INSTAGRAM_APP_SECRET")
    instagram_redirect_uri: Optional[str] = None
    
    # Facebook OAuth
    facebook_app_id: Optional[str] = os.environ.get("FACEBOOK_APP_ID")
    facebook_app_secret: Optional[str] = os.environ.get("FACEBOOK_APP_SECRET")
    facebook_redirect_uri: Optional[str] = None
    
    # Pexels (for stock footage)
    pexels_api_key: Optional[str] = os.environ.get("PEXELS_API_KEY")
    
    # Unsplash (for stock images)
    unsplash_access_key: Optional[str] = os.environ.get("UNSPLASH_ACCESS_KEY")
    
    # File storage paths
    video_storage_path: str = "/app/backend/storage/videos"
    audio_storage_path: str = "/app/backend/storage/audio"
    image_storage_path: str = "/app/backend/storage/images"
    temp_storage_path: str = "/app/backend/storage/temp"
    
    # FFmpeg
    ffmpeg_path: str = "/usr/bin/ffmpeg"
    
    # Background workers
    render_worker_enabled: bool = True
    scheduler_worker_enabled: bool = True
    
    # CORS
    cors_origins: str = "*"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Singleton instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get settings singleton instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings