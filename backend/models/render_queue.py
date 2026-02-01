from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid

class RenderQueueCreate(BaseModel):
    """Model for creating a render job"""
    video_id: str
    script: dict  # VideoScript as dict
    voice_url: Optional[str] = None
    visuals: List[str] = Field(default_factory=list)
    background_music: Optional[str] = None
    captions_enabled: bool = True

class RenderQueue(BaseModel):
    """Render queue model for database"""
    model_config = ConfigDict(extra="ignore")
    
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Reference to user
    video_id: str  # Reference to video
    
    # Render inputs
    script: dict  # VideoScript as dict
    voice_url: Optional[str] = None
    visuals: List[str] = Field(default_factory=list)
    background_music: Optional[str] = None
    captions_enabled: bool = True
    
    # Status tracking
    status: str = Field(default="pending")  # pending/processing/completed/failed
    progress: int = Field(default=0)  # 0-100
    error_message: Optional[str] = None
    
    output_file_path: Optional[str] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class RenderQueueResponse(BaseModel):
    """Render queue response model"""
    job_id: str
    video_id: str
    status: str
    progress: int
    error_message: Optional[str] = None
    output_file_path: Optional[str] = None
    created_at: datetime