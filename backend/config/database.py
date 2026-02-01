from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

# Global database client
client: AsyncIOMotorClient = None
database: AsyncIOMotorDatabase = None

def get_db() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return database

async def init_db():
    """Initialize database connection"""
    global client, database
    
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME', 'autoshorts_ai')
    
    if not mongo_url:
        raise ValueError("MONGO_URL environment variable is not set")
    
    logger.info(f"Connecting to MongoDB: {db_name}")
    
    client = AsyncIOMotorClient(mongo_url)
    database = client[db_name]
    
    # Create indexes for better performance
    await create_indexes()
    
    logger.info("Database connection established")

async def create_indexes():
    """Create database indexes"""
    try:
        # Users collection
        await database.users.create_index("email", unique=True)
        
        # Connected accounts collection
        await database.connected_accounts.create_index("user_id")
        await database.connected_accounts.create_index([("user_id", 1), ("platform", 1)])
        
        # Videos collection
        await database.videos.create_index("user_id")
        await database.videos.create_index("status")
        await database.videos.create_index([("user_id", 1), ("created_at", -1)])
        
        # Analytics collection
        await database.analytics.create_index("video_id")
        await database.analytics.create_index("platform")
        await database.analytics.create_index([("video_id", 1), ("platform", 1)], unique=True)
        
        # Render queue collection
        await database.render_queue.create_index("job_id", unique=True)
        await database.render_queue.create_index("status")
        await database.render_queue.create_index([("user_id", 1), ("created_at", -1)])
        
        # Schedules collection
        await database.schedules.create_index("scheduled_time")
        await database.schedules.create_index("status")
        await database.schedules.create_index([("user_id", 1), ("scheduled_time", 1)])
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")

async def close_db():
    """Close database connection"""
    global client
    if client:
        client.close()
        logger.info("Database connection closed")