from pymongo import MongoClient
from pymongo.database import Database
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: MongoClient = None
    db: Database = None

db = MongoDB()

def connect_to_mongo():
    """Create database connection"""
    try:
        db.client = MongoClient(settings.MONGODB_URI)
        db.db = db.client[settings.MONGODB_DB_NAME]
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")

def get_database() -> Database:
    """Get database instance"""
    if db.db is None:
        connect_to_mongo()
    return db.db


