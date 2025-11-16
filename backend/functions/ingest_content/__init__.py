import json
import logging
import os
import sys
import tempfile
from datetime import datetime
from typing import Dict, List, Optional

import azure.functions as func
import feedparser
import requests

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.database import get_database
from app.services.ai_service import ai_service
from app.services.content_service import content_service
from app.services.speech_service import speech_service
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)

def main(timer: func.TimerRequest) -> None:
    """Timer-triggered function to ingest content from various sources"""
    try:
        db = get_database()
        
        # Get all active sources
        sources = list(db.sources.find({"enabled": True}))
        
        for source in sources:
            source_type = source.get("type")
            
            if source_type == "rss":
                ingest_rss_source(source, db)
            elif source_type == "podcast":
                ingest_podcast_source(source, db)
        
        logger.info("Content ingestion completed")
    except Exception as e:
        logger.error(f"Error in content ingestion: {e}")

def ingest_rss_source(source: dict, db):
    """Ingest content from RSS feed"""
    try:
        url = source.get("url")
        if not url:
            return
        
        feed = feedparser.parse(url)
        role_tags = source.get("role_tags", [])
        
        for entry in feed.entries:
            # Check if content already exists
            existing = db.content_items.find_one({"url": entry.link})
            if existing:
                continue
            
            # Download article content
            try:
                response = requests.get(entry.link, timeout=10)
                article_text = response.text
                
                # Save to blob storage
                blob_uri = storage_service.upload_text(
                    settings.STORAGE_CONTAINER_ARTICLES,
                    f"article_{content_service.slugify(entry.title)}",
                    article_text,
                    content_type="text/html",
                )
            except Exception as e:
                logger.warning(f"Could not download article {entry.link}: {e}")
                blob_uri = None
            
            # Create content item
            content_data = {
                "title": entry.title,
                "type": "article",
                "source_id": str(source["_id"]),
                "url": entry.link,
                "description": entry.get("summary", ""),
                "published_at": datetime(*entry.published_parsed[:6]) if hasattr(entry, "published_parsed") else datetime.utcnow(),
                "role_tags": role_tags,
                "blob_uri": blob_uri,
                "organization_id": source.get("organization_id")
            }
            
            content_id = content_service.create_content_item(content_data)
            logger.info(f"Created content item: {content_id}")
    except Exception as e:
        logger.error(f"Error ingesting RSS source: {e}")

def ingest_podcast_source(source: dict, db):
    """Ingest content from podcast RSS feed"""
    try:
        url = source.get("url")
        if not url:
            return
        
        feed = feedparser.parse(url)
        role_tags = source.get("role_tags", [])
        
        for entry in feed.entries:
            # Get audio URL
            audio_url = None
            for link in entry.links:
                if link.get("type", "").startswith("audio"):
                    audio_url = link.href
                    break
            
            if not audio_url:
                continue
            
            # Check if content already exists
            existing = db.content_items.find_one({"url": entry.link})
            if existing:
                continue
            
            # Download and transcribe audio
            transcript = None
            transcript_segments: List[Dict] = []
            try:
                transcription_result = speech_service.transcribe_from_url(audio_url)
                transcript = transcription_result.get("full_text")
                transcript_segments = transcription_result.get("segments", [])
                logger.info(f"Generated transcript for podcast: {entry.title}")
            except Exception as e:
                logger.warning(f"Could not download/transcribe podcast audio: {e}")
            
            # Create content item
            slug_base = content_service.slugify(entry.title) or entry.id if hasattr(entry, "id") else "podcast"

            transcript_blob_uri = None
            transcript_segments_blob_uri = None

            if transcript:
                transcript_blob_uri = storage_service.upload_text(
                    settings.STORAGE_CONTAINER_TRANSCRIPTS,
                    f"{slug_base}_transcript",
                    transcript,
                )

            if transcript_segments:
                segments_json = json.dumps(transcript_segments).encode("utf-8")
                transcript_segments_blob_uri = storage_service.upload_json(
                    settings.STORAGE_CONTAINER_TRANSCRIPTS,
                    f"{slug_base}_segments",
                    segments_json,
                )

            content_data = {
                "title": entry.title,
                "type": "podcast",
                "source_id": str(source["_id"]),
                "url": entry.link,
                "description": entry.get("summary", ""),
                "published_at": datetime(*entry.published_parsed[:6]) if hasattr(entry, "published_parsed") else datetime.utcnow(),
                "role_tags": role_tags,
                "transcript": transcript,
                "transcript_segments": transcript_segments or None,
                "transcript_blob_uri": transcript_blob_uri,
                "transcript_segments_blob_uri": transcript_segments_blob_uri,
                "metadata": {
                    "audio_url": audio_url
                },
                "organization_id": source.get("organization_id")
            }
            
            content_id = content_service.create_content_item(content_data)
            logger.info(f"Created podcast content item: {content_id}")
    except Exception as e:
        logger.error(f"Error ingesting podcast source: {e}")

