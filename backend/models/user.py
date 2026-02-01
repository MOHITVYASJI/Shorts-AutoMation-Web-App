from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime, timezone

class UserCreate(BaseModel):
    """Model for user registration"""
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2)

class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr
    password: str

class User(BaseModel):
    """User model for database"""
    model_config = ConfigDict(extra="ignore")
    
    email: EmailStr
    password_hash: str
    full_name: str
    google_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    subscription_plan: str = Field(default="free")
    is_active: bool = Field(default=True)

class UserResponse(BaseModel):
    """User response model (without password)"""
    email: EmailStr
    full_name: str
    subscription_plan: str
    created_at: datetime
    is_active: bool

class GoogleAuthPayload(BaseModel):
    """Google OAuth payload"""
    google_token: str
    full_name: str
    email: EmailStr