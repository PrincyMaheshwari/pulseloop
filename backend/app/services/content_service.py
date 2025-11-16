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
    
    def _build_user_content_query(self, user: dict) -> dict:
        and_clauses: List[dict] = []

        job_role = (user.get("job_role") or user.get("role") or "").strip()
        organization_id = user.get("organization_id")
        org_document = None

        if organization_id:
            try:
                org_document = self.db.organizations.find_one({"_id": ObjectId(organization_id)})
            except Exception:
                logger.debug("Organization %s not found by ObjectId", organization_id)
                org_document = self.db.organizations.find_one({"slug": organization_id})

            if org_document:
                and_clauses.append({
                    "$or": [
                        {"organization_id": organization_id},
                        {"organization_id": {"$exists": False}},
                        {"organization_id": None},
                    ]
                })

        if job_role:
            normalized_role = job_role.lower()
            and_clauses.append({
                "$or": [
                    {"role_tags": {"$in": [job_role, normalized_role, job_role.title()]}},
                    {"role_tags": {"$size": 0}},
                    {"role_tags": {"$exists": False}},
                ]
            })
            role_keywords = {token for token in job_role.lower().replace("/", " ").replace("-", " ").split() if len(token) > 3}
            if role_keywords:
                and_clauses.append({
                    "$or": [
                        {"tags": {"$in": list(role_keywords)}},
                        {"tags": {"$exists": False}},
                    ]
                })
        else:
            and_clauses.append({
                "$or": [
                    {"role_tags": {"$size": 0}},
                    {"role_tags": {"$exists": False}},
                ]
            })

        source_ids = user.get("source_ids")
        if not source_ids and org_document:
            source_ids = org_document.get("sources")

        if source_ids:
            and_clauses.append({"source_id": {"$in": source_ids}})

        if and_clauses:
            return {"$and": and_clauses}
        return {}

    @staticmethod
    def _format_content_item(item: Optional[dict]) -> Optional[dict]:
        if not item:
            return None
        item["id"] = str(item.get("_id", ""))
        item.pop("_id", None)
        return item

    def get_user_feed(self, user_id: str, limit: int = 20) -> List[dict]:
        """Get personalized feed for user based on their role"""
        try:
            # Get user and their role
            user = self.db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return []

            query = self._build_user_content_query(user)

            content_items = (
                self.db.content_items.find(query)
                .sort([
                    ("priority_score", -1),
                    ("published_at", -1),
                    ("created_at", -1),
                ])
                .limit(limit)
            )
            
            # Convert to list of dicts
            feed = []
            for item in content_items:
                formatted = self._format_content_item(item)
                if formatted:
                    feed.append(formatted)
            
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

            summary_text = content_data.get("summary") or ""
            description_text = content_data.get("description") or ""

            # Generate descriptive tags
            if summary_text:
                generated_tags = ai_service.generate_tags(description_text, summary_text)
                if generated_tags:
                    existing_tags = content_data.get("tags") or []
                    content_data["tags"] = list(dict.fromkeys([tag.strip() for tag in (existing_tags + generated_tags) if tag]))

            # Normalise role tags
            if content_data.get("role_tags"):
                normalised_roles = []
                seen_roles = set()
                for role in content_data["role_tags"]:
                    if not role:
                        continue
                    role_text = role.strip()
                    if not role_text:
                        continue
                    key = role_text.lower()
                    if key not in seen_roles:
                        seen_roles.add(key)
                        normalised_roles.append(role_text)
                content_data["role_tags"] = normalised_roles

            # Derive role tags from generated tags if none provided
            if not content_data.get("role_tags") and content_data.get("tags"):
                inferred_roles = []
                seen_roles = set()
                for tag in content_data["tags"]:
                    key = tag.lower()
                    if key not in seen_roles:
                        seen_roles.add(key)
                        inferred_roles.append(tag)
                content_data["role_tags"] = inferred_roles[:5]

            # Calculate priority score
            priority_source = summary_text or description_text or content_data.get("transcript") or ""
            if priority_source:
                role_context = content_data.get("role_tags") or content_data.get("tags") or []
                content_data["priority_score"] = ai_service.calculate_priority_score(priority_source, role_context)
            
            # Ensure tags field exists
            if "tags" not in content_data:
                content_data["tags"] = []

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
        """Get daily feed with latest article and podcast options"""
        try:
            # Get user and their role
            user = self.db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return {"article": None, "podcast": None}
            
            query = self._build_user_content_query(user)
            
            # Get latest article
            article_query = {**query, "type": "article"}
            latest_article = self.db.content_items.find_one(
                article_query,
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
                "podcast": None
            }
            
            result["article"] = self._format_content_item(latest_article)
            result["podcast"] = self._format_content_item(latest_podcast)
            
            return result
        except Exception as e:
            logger.error(f"Error getting daily feed options: {e}")
            return {"article": None, "podcast": None}

# Singleton instance
content_service = ContentService()

