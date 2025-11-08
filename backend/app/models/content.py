from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, HttpUrl
from enum import Enum

class ContentType(str, Enum):
    ARTICLE = "article"
    VIDEO = "video"
    PODCAST = "podcast"

class SourceType(str, Enum):
    RSS = "rss"
    YOUTUBE = "youtube"
    PODCAST = "podcast"
    MANUAL = "manual"

class Source(BaseModel):
    id: Optional[str] = None
    name: str
    type: SourceType
    url: Optional[str] = None
    youtube_channel_id: Optional[str] = None
    role_tags: List[str] = []  # Which roles this source is relevant for
    enabled: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

class ContentItem(BaseModel):
    id: Optional[str] = None
    title: str
    type: ContentType
    source_id: str
    url: HttpUrl
    description: Optional[str] = None
    published_at: datetime
    role_tags: List[str] = []  # Which roles this content is relevant for
    blob_uri: Optional[str] = None  # Azure Blob Storage URI for raw content/transcript
    transcript: Optional[str] = None  # For videos/podcasts
    summary: Optional[str] = None  # AI-generated summary
    summary_blob_uri: Optional[str] = None  # Blob URI for cached summary
    animated_summary: Optional[Dict] = None  # Storyboard and audio URL
    priority_score: float = 0.0  # AI-generated relevance score
    metadata: Dict = {}  # Additional metadata (author, duration, etc.)
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Latest AI Trends in 2024",
                "type": "article",
                "source_id": "source1",
                "url": "https://example.com/article",
                "published_at": "2024-01-15T10:00:00Z",
                "role_tags": ["Data Analyst - Hospitality"],
                "priority_score": 0.85
            }
        }


