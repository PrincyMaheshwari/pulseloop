import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
from bson import ObjectId
from app.core.database import get_database

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.db = get_database()
    
    def get_user(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        try:
            user = self.db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                user["id"] = str(user["_id"])
                user["_id"] = str(user["_id"])
            return user
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
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

# Singleton instance
user_service = UserService()


