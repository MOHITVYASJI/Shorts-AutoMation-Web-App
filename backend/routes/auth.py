from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from models.user import UserCreate, UserLogin, UserResponse, GoogleAuthPayload
from services.auth_service import (
    create_user,
    authenticate_user,
    get_current_user,
    google_auth_login
)
from utils.jwt_utils import create_access_token

router = APIRouter()
security = HTTPBearer()

@router.post("/signup", response_model=dict, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    """Register a new user"""
    try:
        user = await create_user(user_data)
        token = create_access_token(user["email"])
        
        return {
            "message": "User created successfully",
            "user": {
                "email": user["email"],
                "full_name": user["full_name"],
                "subscription_plan": user["subscription_plan"]
            },
            "access_token": token,
            "token_type": "bearer"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/login", response_model=dict)
async def login(credentials: UserLogin):
    """Login with email and password"""
    try:
        user = await authenticate_user(credentials.email, credentials.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        token = create_access_token(user["email"])
        
        return {
            "message": "Login successful",
            "user": {
                "email": user["email"],
                "full_name": user["full_name"],
                "subscription_plan": user["subscription_plan"]
            },
            "access_token": token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/google", response_model=dict)
async def google_login(payload: GoogleAuthPayload):
    """Login or signup with Google OAuth"""
    try:
        user = await google_auth_login(payload)
        token = create_access_token(user["email"])
        
        return {
            "message": "Google login successful",
            "user": {
                "email": user["email"],
                "full_name": user["full_name"],
                "subscription_plan": user["subscription_plan"]
            },
            "access_token": token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google auth error: {str(e)}")

@router.get("/profile", response_model=UserResponse)
async def get_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user profile"""
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return UserResponse(
            email=user["email"],
            full_name=user["full_name"],
            subscription_plan=user["subscription_plan"],
            created_at=user["created_at"],
            is_active=user["is_active"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching profile: {str(e)}")

@router.put("/profile", response_model=dict)
async def update_profile(
    full_name: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update user profile"""
    try:
        user = await get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # Update user profile logic here (to be implemented)
        return {"message": "Profile update functionality coming soon"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")