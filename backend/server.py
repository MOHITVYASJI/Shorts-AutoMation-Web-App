from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from config.database import init_db, close_db
from config.settings import get_settings
from routes import auth, platforms, content

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    logger.info("Starting AutoShorts AI Backend...")
    await init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down...")
    await close_db()

# Create the main app
app = FastAPI(
    title="AutoShorts AI API",
    description="AI-powered Multi-Platform Short Video Automation & Analytics Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# Health check endpoint
@api_router.get("/")
async def root():
    return {
        "message": "AutoShorts AI API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@api_router.get("/health")
async def health_check():
    return {"status": "ok", "service": "autoshorts-ai"}

# Include route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(platforms.router, prefix="/platforms", tags=["Platforms"])
api_router.include_router(content.router, prefix="/content", tags=["Content Generation"])

# Include the API router in the main app
app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=settings.cors_origins.split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)