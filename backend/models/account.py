from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, timezone

class ConnectedAccountCreate(BaseModel):
    """Model for connecting a new account"""
    platform: str = Field(pattern="^(youtube|instagram|facebook)$")
    account_id: str
    account_name: str
    account_email: Optional[str] = None
    access_token: str
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None

class ConnectedAccount(BaseModel):
    """Connected account model for database"""
    model_config = ConfigDict(extra="ignore")
    
    user_id: str  # Reference to user
    platform: str  # youtube/instagram/facebook
    account_id: str  # Platform's user/page ID
    account_name: str
    account_email: Optional[str] = None
    access_token: str  # Encrypted
    refresh_token: Optional[str] = None  # Encrypted
    token_expiry: Optional[datetime] = None
    connected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = Field(default="active")  # active/disconnected

class ConnectedAccountResponse(BaseModel):
    """Connected account response (without tokens)"""
    id: str  # MongoDB _id converted to string
    platform: str
    account_id: str
    account_name: str
    account_email: Optional[str] = None
    connected_at: datetime
    status: str