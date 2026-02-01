from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone

class MetricsHistory(BaseModel):
    """Time-series metrics data"""
    date: datetime
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0

class Analytics(BaseModel):
    """Analytics model for database"""
    model_config = ConfigDict(extra="ignore")
    
    video_id: str  # Reference to video
    platform: str  # youtube/instagram/facebook
    account_id: str  # Reference to connected account
    platform_video_id: str
    
    # Current metrics
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    retention_percentage: Optional[float] = None
    
    # Time-series data
    metrics_history: List[MetricsHistory] = Field(default_factory=list)
    
    last_synced_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AnalyticsResponse(BaseModel):
    """Analytics response model"""
    video_id: str
    platform: str
    views: int
    likes: int
    comments: int
    shares: int
    retention_percentage: Optional[float] = None
    metrics_history: List[MetricsHistory]
    last_synced_at: datetime