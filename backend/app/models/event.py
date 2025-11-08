from typing import Optional, Dict
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

class EventType(str, Enum):
    CONTENT_VIEWED = "content_viewed"
    CONTENT_COMPLETED = "content_completed"
    QUIZ_ATTEMPTED = "quiz_attempted"
    QUIZ_PASSED = "quiz_passed"
    QUIZ_FAILED = "quiz_failed"
    STREAK_UPDATED = "streak_updated"
    BADGE_EARNED = "badge_earned"

class Event(BaseModel):
    id: Optional[str] = None
    user_id: str
    organization_id: str
    event_type: EventType
    content_id: Optional[str] = None
    quiz_id: Optional[str] = None
    metadata: Dict = {}
    created_at: datetime = datetime.utcnow()


