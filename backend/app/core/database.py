from pymongo.mongo_client import MongoClient
from pymongo.database import Database
from pymongo.server_api import ServerApi
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: MongoClient = None
    db: Database = None

db = MongoDB()

def connect_to_mongo():
    """Create database connection"""
    if not settings.MONGODB_URI:
        raise RuntimeError(
            "MongoDB connection string (MONGODB_URI) is not configured. "
            "Please set MONGODB_URI environment variable to connect to MongoDB."
        )
    try:
        uri = settings.MONGODB_URI
        db.client = MongoClient(uri, server_api=ServerApi("1"))
        
        # Ping the database to test connection
        try:
            db.client.admin.command("ping")
            logger.info("Pinged MongoDB deployment. Connection successful.")
        except Exception as exc:
            logger.error("MongoDB ping failed: %s", exc)
            raise RuntimeError("Unable to connect to MongoDB. Check your MONGODB_URI, network whitelist, and TLS configuration.") from exc
        
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
    """Get database instance - lazily creates connection on first use"""
    if db.db is None:
        connect_to_mongo()
    return db.db


