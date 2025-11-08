import logging
import sys
import os
import azure.functions as func

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import feedparser
import requests
from googleapiclient.discovery import build
from datetime import datetime
from app.core.database import get_database
from app.core.config import settings
from app.services.content_service import content_service
from app.services.speech_service import speech_service
from app.services.storage_service import storage_service
from app.services.ai_service import ai_service

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
            elif source_type == "youtube":
                ingest_youtube_source(source, db)
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
                blob_name = f"article_{datetime.utcnow().timestamp()}.html"
                blob_uri = storage_service.upload_blob(
                    "articles-raw",
                    blob_name,
                    article_text.encode("utf-8"),
                    "text/html"
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

def ingest_youtube_source(source: dict, db):
    """Ingest content from YouTube channel"""
    try:
        youtube = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)
        channel_id = source.get("youtube_channel_id")
        if not channel_id:
            return
        
        # Get latest videos
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            type="video",
            order="date",
            maxResults=10
        )
        response = request.execute()
        role_tags = source.get("role_tags", [])
        
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            
            # Check if content already exists
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            existing = db.content_items.find_one({"url": video_url})
            if existing:
                continue
            
            # Get video details
            video_request = youtube.videos().list(
                part="contentDetails,snippet",
                id=video_id
            )
            video_response = video_request.execute()
            video_details = video_response.get("items", [])[0] if video_response.get("items") else None
            
            # Try to get captions/transcript
            transcript = None
            try:
                # Get available captions
                caption_request = youtube.captions().list(
                    part="snippet",
                    videoId=video_id
                )
                caption_response = caption_request.execute()
                
                # Try to download English captions
                for caption in caption_response.get("items", []):
                    if caption["snippet"]["language"] in ["en", "en-US", "en-GB"]:
                        try:
                            from googleapiclient.http import MediaIoBaseDownload
                            import io
                            
                            caption_download = youtube.captions().download(
                                id=caption["id"],
                                tfmt="srt"  # or "vtt"
                            )
                            
                            # Download caption content
                            caption_content = caption_download.execute()
                            if isinstance(caption_content, bytes):
                                caption_content = caption_content.decode('utf-8')
                            
                            # Extract text from SRT format (simple extraction)
                            import re
                            # Remove SRT timing and index lines, keep text
                            lines = caption_content.split('\n')
                            text_lines = []
                            for line in lines:
                                # Skip index numbers and timestamps
                                if not re.match(r'^\d+$', line.strip()) and not re.match(r'^\d{2}:\d{2}:\d{2}', line.strip()) and line.strip():
                                    text_lines.append(line.strip())
                            transcript = ' '.join(text_lines)
                            break
                        except Exception as e:
                            logger.warning(f"Could not download caption {caption['id']}: {e}")
                            continue
                
                # If no captions found, try to transcribe using Azure Speech-to-Text
                if not transcript:
                    try:
                        # Download video audio (requires youtube-dl or similar)
                        # For now, we'll skip this and rely on captions
                        logger.info(f"No captions available for video {video_id}, skipping transcript")
                    except Exception as e:
                        logger.warning(f"Could not generate transcript for video {video_id}: {e}")
            except Exception as e:
                logger.warning(f"Could not get captions for video {video_id}: {e}")
            
            # Create content item
            content_data = {
                "title": snippet["title"],
                "type": "video",
                "source_id": str(source["_id"]),
                "url": video_url,
                "description": snippet.get("description", ""),
                "published_at": datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00")),
                "role_tags": role_tags,
                "transcript": transcript,
                "metadata": {
                    "video_id": video_id,
                    "channel_id": channel_id,
                    "duration": video_details.get("contentDetails", {}).get("duration") if video_details else None
                },
                "organization_id": source.get("organization_id")
            }
            
            content_id = content_service.create_content_item(content_data)
            logger.info(f"Created YouTube content item: {content_id}")
    except Exception as e:
        logger.error(f"Error ingesting YouTube source: {e}")

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
            try:
                import requests
                import tempfile
                import os
                
                # Download audio file
                logger.info(f"Downloading podcast audio from {audio_url}")
                audio_response = requests.get(audio_url, timeout=60, stream=True)
                audio_response.raise_for_status()
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                    for chunk in audio_response.iter_content(chunk_size=8192):
                        tmp_file.write(chunk)
                    tmp_path = tmp_file.name
                
                try:
                    # Transcribe using Azure Speech-to-Text
                    transcript = speech_service.transcribe_audio(tmp_path)
                    logger.info(f"Generated transcript for podcast: {entry.title}")
                except Exception as e:
                    logger.warning(f"Could not transcribe podcast audio: {e}")
                finally:
                    # Clean up temporary file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"Could not download/transcribe podcast audio: {e}")
            # transcript = speech_service.transcribe_audio(audio_url)
            
            # Create content item
            content_data = {
                "title": entry.title,
                "type": "podcast",
                "source_id": str(source["_id"]),
                "url": entry.link,
                "description": entry.get("summary", ""),
                "published_at": datetime(*entry.published_parsed[:6]) if hasattr(entry, "published_parsed") else datetime.utcnow(),
                "role_tags": role_tags,
                "transcript": transcript,
                "metadata": {
                    "audio_url": audio_url
                },
                "organization_id": source.get("organization_id")
            }
            
            content_id = content_service.create_content_item(content_data)
            logger.info(f"Created podcast content item: {content_id}")
    except Exception as e:
        logger.error(f"Error ingesting podcast source: {e}")

