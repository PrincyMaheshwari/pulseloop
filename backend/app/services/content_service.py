import logging
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from app.core.database import get_database
from app.models.content import ContentItem, ContentType
from app.models.user import User
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)

class ContentService:
    def __init__(self):
        self.db = get_database()
    
    @staticmethod
    def slugify(value: str) -> str:
        import re
        value = value or "content"
        value = value.lower()
        value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
        return value or "content"
    
    def get_user_feed(self, user_id: str, limit: int = 20) -> List[dict]:
        """Get personalized feed for user based on their role"""
        try:
            # Get user and their role
            user = self.db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return []
            
            job_role = user.get("job_role")
            organization_id = user.get("organization_id")
            
            # Get organization sources
            org = self.db.organizations.find_one({"_id": ObjectId(organization_id)})
            if not org:
                return []
            
            # Build query for content relevant to user's role
            # Note: organization_id might not be stored directly on content items
            # Content is linked via sources which have organization_id
            query = {
                "$or": [
                    {"role_tags": {"$in": [job_role]}},
                    {"role_tags": {"$size": 0}}  # General content
                ]
            }
            
            # If organization has specific sources, filter by them
            source_ids = org.get("sources", [])
            if source_ids:
                query["source_id"] = {"$in": source_ids}
            
            # Get content items sorted by published_at (latest first)
            content_items = self.db.content_items.find(query).sort("published_at", -1).limit(limit)
            
            # Convert to list of dicts
            feed = []
            for item in content_items:
                item["id"] = str(item["_id"])
                item["_id"] = str(item["_id"])
                feed.append(item)
            
            return feed
        except Exception as e:
            logger.error(f"Error getting user feed: {e}")
            return []
    
    def get_content_item(self, content_id: str) -> Optional[dict]:
        """Get a specific content item"""
        try:
            item = self.db.content_items.find_one({"_id": ObjectId(content_id)})
            if item:
                item["id"] = str(item["_id"])
                item["_id"] = str(item["_id"])
            return item
        except Exception as e:
            logger.error(f"Error getting content item: {e}")
            return None
    
    def create_content_item(self, content_data: dict) -> str:
        """Create a new content item"""
        try:
            # Generate summary if not provided
            transcript_segments = content_data.get("transcript_segments") or []
            if not content_data.get("summary"):
                content_text = content_data.get("transcript") or content_data.get("description", "")
                if content_text:
                    content_data["summary"] = ai_service.generate_summary(
                        content_text,
                        content_data.get("type", "article"),
                        transcript_segments=transcript_segments,
                    )
            
            # Generate tags if not provided
            if not content_data.get("role_tags") and content_data.get("summary"):
                content_data["role_tags"] = ai_service.generate_tags(
                    content_data.get("description", ""),
                    content_data["summary"]
                )
            
            # Set timestamps
            content_data["created_at"] = datetime.utcnow()
            content_data["updated_at"] = datetime.utcnow()
            
            result = self.db.content_items.insert_one(content_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating content item: {e}")
            raise
    
    def get_todays_top_content(self, user_id: str) -> Optional[dict]:
        """Get the top content item for today's streak (latest overall)"""
        try:
            feed = self.get_user_feed(user_id, limit=1)
            if feed:
                return feed[0]
            return None
        except Exception as e:
            logger.error(f"Error getting today's top content: {e}")
            return None
    
    def get_daily_feed_options(self, user_id: str) -> dict:
        """Get daily feed with latest article, video, and podcast options"""
        try:
            # Get user and their role
            user = self.db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return {"article": None, "video": None, "podcast": None}
            
            job_role = user.get("job_role")
            organization_id = user.get("organization_id")
            
            # Get organization sources
            org = self.db.organizations.find_one({"_id": ObjectId(organization_id)})
            if not org:
                return {"article": None, "video": None, "podcast": None}
            
            # Build query for content relevant to user's role
            query = {
                "$or": [
                    {"role_tags": {"$in": [job_role]}},
                    {"role_tags": {"$size": 0}}  # General content
                ]
            }
            
            # If organization has specific sources, filter by them
            source_ids = org.get("sources", [])
            if source_ids:
                query["source_id"] = {"$in": source_ids}
            
            # Get latest article
            article_query = {**query, "type": "article"}
            latest_article = self.db.content_items.find_one(
                article_query,
                sort=[("published_at", -1)]
            )
            
            # Get latest video
            video_query = {**query, "type": "video"}
            latest_video = self.db.content_items.find_one(
                video_query,
                sort=[("published_at", -1)]
            )
            
            # Get latest podcast
            podcast_query = {**query, "type": "podcast"}
            latest_podcast = self.db.content_items.find_one(
                podcast_query,
                sort=[("published_at", -1)]
            )
            
            result = {
                "article": None,
                "video": None,
                "podcast": None
            }
            
            if latest_article:
                latest_article["id"] = str(latest_article["_id"])
                result["article"] = latest_article
            
            if latest_video:
                latest_video["id"] = str(latest_video["_id"])
                result["video"] = latest_video
            
            if latest_podcast:
                latest_podcast["id"] = str(latest_podcast["_id"])
                result["podcast"] = latest_podcast
            
            return result
        except Exception as e:
            logger.error(f"Error getting daily feed options: {e}")
            return {"article": None, "video": None, "podcast": None}

# Singleton instance
content_service = ContentService()

