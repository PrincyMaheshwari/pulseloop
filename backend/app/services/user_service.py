import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from bson import ObjectId

from app.core.database import get_database
from app.core.config import settings

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self):
        self.db = get_database()
    
    def get_user(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        try:
            user = self.db.users.find_one({"_id": ObjectId(user_id)})
            return self._format_user(user)
        except Exception as e:
            logger.error("Error getting user: {0}".format(e))
            return None
    
    def get_or_create_user_from_claims(self, claims: Dict[str, Any]) -> dict:
        """Ensure a local user exists for the authenticated Azure AD identity."""
        external_id = claims.get("oid") or claims.get("sub")
        if not external_id:
            raise ValueError("Token did not include an object identifier (oid/sub)")

        email = claims.get("preferred_username") or claims.get("email")
        display_name = claims.get("name") or email or "PulseLoop User"
        organization_id = claims.get("tid") or claims.get("tenant_id")
        role = self._resolve_role(claims)

        user = self.db.users.find_one({"external_id": external_id})
        now = datetime.utcnow()

        if user:
            updates: Dict[str, Any] = {}
            if email and email != user.get("email"):
                updates["email"] = email
            if display_name and display_name != user.get("display_name"):
                updates["display_name"] = display_name
            if organization_id and organization_id != user.get("organization_id"):
                updates["organization_id"] = organization_id
            if role and role != user.get("role"):
                updates["role"] = role

            if updates:
                updates["updated_at"] = now
                self.db.users.update_one({"_id": user["_id"]}, {"$set": updates})
                user.update(updates)
            return self._format_user(user)

        user_doc: Dict[str, Any] = {
            "external_id": external_id,
            "email": email,
            "display_name": display_name,
            "organization_id": organization_id,
            "role": role or settings.AZURE_AD_DEFAULT_ROLE,
            "tech_score": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "created_at": now,
            "updated_at": now,
        }

        result = self.db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        return self._format_user(user_doc)
    
    def update_streak(self, user_id: str):
        """Update user streak based on today's activity"""
        try:
            user = self.db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return
            
            today = datetime.utcnow().date()
            last_activity = user.get("last_activity_date")
            
            if last_activity:
                last_activity_date = last_activity.date() if isinstance(last_activity, datetime) else last_activity
                days_diff = (today - last_activity_date).days
                
                if days_diff == 0:
                    # Already updated today
                    return
                elif days_diff == 1:
                    # Consecutive day - increment streak
                    new_streak = user.get("current_streak", 0) + 1
                    longest_streak = max(user.get("longest_streak", 0), new_streak)
                else:
                    # Streak broken - reset to 1
                    new_streak = 1
                    longest_streak = user.get("longest_streak", 0)
            else:
                # First activity
                new_streak = 1
                longest_streak = 1
            
            # Update user
            self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "current_streak": new_streak,
                        "longest_streak": longest_streak,
                        "last_activity_date": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error updating streak: {e}")
    
    def get_user_dashboard(self, user_id: str) -> Dict:
        """Get user dashboard data"""
        try:
            user = self.get_user(user_id)
            if not user:
                return {}
            
            # Get recent completions
            recent_completions = list(self.db.quiz_attempts.find({
                "user_id": user_id,
                "passed": True
            }).sort("created_at", -1).limit(10))
            
            for completion in recent_completions:
                completion["id"] = str(completion["_id"])
                completion["_id"] = str(completion["_id"])
            
            # Get stats by content type
            stats_by_type = {}
            for content_type in ["article", "video", "podcast"]:
                count = self.db.quiz_attempts.count_documents({
                    "user_id": user_id,
                    "passed": True,
                    # Note: Would need to join with content_items for type
                })
                stats_by_type[content_type] = count
            
            return {
                "user": user,
                "recent_completions": recent_completions,
                "stats_by_type": stats_by_type
            }
        except Exception as e:
            logger.error(f"Error getting user dashboard: {e}")
            return {}

    @staticmethod
    def _format_user(user: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not user:
            return None
        user["id"] = str(user["_id"])
        user["_id"] = str(user["_id"])
        return user

    @staticmethod
    def _resolve_role(claims: Dict[str, Any]) -> str:
        roles = claims.get("roles")
        if isinstance(roles, list) and roles:
            return roles[0].lower()
        if isinstance(roles, str) and roles:
            return roles.lower()

        groups = claims.get("groups")
        if isinstance(groups, list):
            for value in groups:
                text = value.lower()
                if "admin" in text:
                    return "admin"
        return settings.AZURE_AD_DEFAULT_ROLE

# Singleton instance
user_service = UserService()


