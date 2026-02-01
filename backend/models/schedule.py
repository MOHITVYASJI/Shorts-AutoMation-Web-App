from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, timezone

class ScheduleMetadata(BaseModel):
    """Metadata for scheduled publishing"""
    title: str
    description: str
    hashtags: list[str] = Field(default_factory=list)
    visibility: str = Field(default="public")  # public/private/unlisted

class ScheduleCreate(BaseModel):
    """Model for creating a schedule"""
    video_id: str
    platform: str = Field(pattern="^(youtube|instagram|facebook)$")
    account_id: str
    scheduled_time: datetime
    metadata: ScheduleMetadata

class Schedule(BaseModel):
    """Schedule model for database"""
    model_config = ConfigDict(extra="ignore")
    
    user_id: str  # Reference to user
    video_id: str  # Reference to video
    
    platform: str  # youtube/instagram/facebook
    account_id: str  # Reference to connected account
    
    scheduled_time: datetime
    status: str = Field(default="pending")  # pending/published/failed/cancelled
    
    metadata: ScheduleMetadata
    
    error_message: Optional[str] = None
    published_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ScheduleResponse(BaseModel):
    """Schedule response model"""
    id: str  # MongoDB _id converted to string
    video_id: str
    platform: str
    account_id: str
    scheduled_time: datetime
    status: str
    metadata: ScheduleMetadata
    created_at: datetime