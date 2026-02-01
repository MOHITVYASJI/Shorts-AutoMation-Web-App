from passlib.context import CryptContext
from datetime import datetime, timezone
from typing import Optional
import logging

from config.database import get_db
from models.user import UserCreate, User, GoogleAuthPayload
from utils.jwt_utils import verify_token

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

async def create_user(user_data: UserCreate) -> dict:
    """Create a new user"""
    db = get_db()
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise ValueError("User with this email already exists")
    
    # Create user object
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        created_at=datetime.now(timezone.utc),
        subscription_plan="free",
        is_active=True
    )
    
    # Convert to dict and store
    user_dict = user.model_dump()
    user_dict["created_at"] = user_dict["created_at"].isoformat()
    
    result = await db.users.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)
    
    logger.info(f"User created: {user_data.email}")
    return user_dict

async def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Authenticate a user with email and password"""
    db = get_db()
    
    user = await db.users.find_one({"email": email})
    if not user:
        return None
    
    if not verify_password(password, user["password_hash"]):
        return None
    
    # Convert datetime strings back if needed
    if isinstance(user.get("created_at"), str):
        user["created_at"] = datetime.fromisoformat(user["created_at"])
    
    logger.info(f"User authenticated: {email}")
    return user

async def get_current_user(token: str) -> Optional[dict]:
    """Get current user from JWT token"""
    try:
        payload = verify_token(token)
        if not payload:
            return None
        
        email = payload.get("sub")
        if not email:
            return None
        
        db = get_db()
        user = await db.users.find_one({"email": email})
        
        if not user:
            return None
        
        # Convert datetime strings back if needed
        if isinstance(user.get("created_at"), str):
            user["created_at"] = datetime.fromisoformat(user["created_at"])
        
        return user
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        return None

async def google_auth_login(payload: GoogleAuthPayload) -> dict:
    """Login or create user with Google OAuth"""
    db = get_db()
    
    # Check if user exists
    user = await db.users.find_one({"email": payload.email})
    
    if user:
        # User exists, update google_id if not set
        if not user.get("google_id"):
            await db.users.update_one(
                {"email": payload.email},
                {"$set": {"google_id": payload.google_token}}
            )
        
        # Convert datetime strings back if needed
        if isinstance(user.get("created_at"), str):
            user["created_at"] = datetime.fromisoformat(user["created_at"])
        
        logger.info(f"Google login: {payload.email}")
        return user
    else:
        # Create new user
        user = User(
            email=payload.email,
            password_hash="",  # No password for Google auth
            full_name=payload.full_name,
            google_id=payload.google_token,
            created_at=datetime.now(timezone.utc),
            subscription_plan="free",
            is_active=True
        )
        
        user_dict = user.model_dump()
        user_dict["created_at"] = user_dict["created_at"].isoformat()
        
        result = await db.users.insert_one(user_dict)
        user_dict["_id"] = str(result.inserted_id)
        
        logger.info(f"Google signup: {payload.email}")
        return user_dict