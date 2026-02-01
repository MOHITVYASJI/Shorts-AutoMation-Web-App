from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone

class VideoScript(BaseModel):
    """Video script components"""
    hook: str
    story: str
    ending: str

class PublishedPlatform(BaseModel):
    """Published platform details"""
    platform: str
    account_id: str
    platform_video_id: str
    published_at: datetime
    url: str

class VideoCreate(BaseModel):
    """Model for creating a new video"""
    title: str
    description: str
    hashtags: List[str] = Field(default_factory=list)
    script: VideoScript
    niche: str
    language: str
    duration: int  # in seconds

class VideoUpdate(BaseModel):
    """Model for updating video metadata"""
    title: Optional[str] = None
    description: Optional[str] = None
    hashtags: Optional[List[str]] = None

class Video(BaseModel):
    """Video model for database"""
    model_config = ConfigDict(extra="ignore")
    
    user_id: str  # Reference to user
    title: str
    description: str
    hashtags: List[str] = Field(default_factory=list)
    
    # Content details
    script: VideoScript
    niche: str
    language: str
    duration: int  # in seconds
    
    # File paths
    video_file_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    voice_file_path: Optional[str] = None
    
    # Generation details
    visuals: List[str] = Field(default_factory=list)  # URLs or paths
    background_music: Optional[str] = None
    captions_enabled: bool = Field(default=True)
    
    # Status
    status: str = Field(default="draft")  # draft/rendering/published
    render_job_id: Optional[str] = None
    
    # Publishing info
    published_platforms: List[PublishedPlatform] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class VideoResponse(BaseModel):
    """Video response model"""
    id: str  # MongoDB _id converted to string
    title: str
    description: str
    hashtags: List[str]
    niche: str
    language: str
    duration: int
    status: str
    video_file_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    published_platforms: List[PublishedPlatform]
    created_at: datetime
    updated_at: datetime