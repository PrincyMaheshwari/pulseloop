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
from googleapiclient.discovery import build
from yt_dlp import YoutubeDL

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
            
            transcript = None
            transcript_segments: List[Dict] = []

            # Prefer Azure Speech transcription
            try:
                transcription_result = _transcribe_youtube_audio(video_url)
                if transcription_result:
                    transcript = transcription_result.get("full_text")
                    transcript_segments = transcription_result.get("segments", [])
            except Exception as e:
                logger.warning(f"Azure Speech transcription failed for video {video_id}: {e}")

            # Fallback to YouTube captions if speech transcription is unavailable
            if not transcript:
                try:
                    transcript = _download_captions_as_text(youtube, video_id)
                except Exception as e:
                    logger.warning(f"Could not get captions for video {video_id}: {e}")
            
            # Create content item
            slug_base = content_service.slugify(snippet["title"]) or video_id

            transcript_blob_uri = None
            transcript_segments_blob_uri = None

            if transcript:
                transcript_blob_uri = storage_service.upload_text(
                    settings.STORAGE_CONTAINER_TRANSCRIPTS,
                    f"{slug_base}_{video_id}_transcript",
                    transcript,
                )

            if transcript_segments:
                segments_json = json.dumps(transcript_segments).encode("utf-8")
                transcript_segments_blob_uri = storage_service.upload_json(
                    settings.STORAGE_CONTAINER_TRANSCRIPTS,
                    f"{slug_base}_{video_id}_segments",
                    segments_json,
                )

            content_data = {
                "title": snippet["title"],
                "type": "video",
                "source_id": str(source["_id"]),
                "url": video_url,
                "description": snippet.get("description", ""),
                "published_at": datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00")),
                "role_tags": role_tags,
                "transcript": transcript,
                "transcript_segments": transcript_segments or None,
                "transcript_blob_uri": transcript_blob_uri,
                "transcript_segments_blob_uri": transcript_segments_blob_uri,
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


def _download_captions_as_text(youtube, video_id: str) -> Optional[str]:
    """
    Download English captions for a YouTube video and return plain text (no timing).
    """
    try:
        caption_request = youtube.captions().list(
            part="snippet",
            videoId=video_id
        )
        caption_response = caption_request.execute()

        for caption in caption_response.get("items", []):
            language = caption["snippet"].get("language", "")
            if language.lower().startswith("en"):
                from googleapiclient.http import MediaIoBaseDownload
                import io

                caption_download = youtube.captions().download(id=caption["id"], tfmt="srt")
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, caption_download)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
                caption_content = fh.getvalue().decode("utf-8")

                lines: List[str] = []
                for line in caption_content.splitlines():
                    stripped = line.strip()
                    if not stripped:
                        continue
                    if stripped.isdigit() or ("-->" in stripped and stripped.count(":") >= 2):
                        continue
                    lines.append(stripped)
                if lines:
                    return " ".join(lines)
    except Exception as exc:
        logger.debug(f"Failed to download captions for {video_id}: {exc}")
    return None


def _transcribe_youtube_audio(video_url: str) -> Optional[Dict[str, List]]:
    """
    Download the audio track for a YouTube video and run Azure Speech transcription.
    Returns the transcription payload or None on failure.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        outtmpl = os.path.join(tmp_dir, "%(id)s.%(ext)s")
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "ignoreerrors": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                if not info:
                    raise RuntimeError("Unable to retrieve video information.")

                base_filename = ydl.prepare_filename(info)
                possible_paths = [
                    base_filename,
                    f"{os.path.splitext(base_filename)[0]}.mp3",
                    f"{os.path.splitext(base_filename)[0]}.m4a",
                ]
                audio_path = next((p for p in possible_paths if os.path.exists(p)), None)
                if not audio_path:
                    raise FileNotFoundError("Audio download did not produce a usable file.")

                return speech_service.transcribe_file(audio_path)
        except Exception as exc:
            logger.warning(f"Could not download/transcribe audio for {video_url}: {exc}")
            return None

