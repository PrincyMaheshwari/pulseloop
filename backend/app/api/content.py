from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.services.content_service import content_service
from app.services.ai_service import ai_service
from app.services.elevenlabs_service import elevenlabs_service
from app.services.storage_service import storage_service
from app.core.database import get_database
from bson import ObjectId
import json

router = APIRouter()

@router.get("/{content_id}")
async def get_content(content_id: str):
    """Get specific content item"""
    try:
        content = content_service.get_content_item(content_id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{content_id}/summary")
async def get_animated_summary(content_id: str):
    """Get or generate animated summary for content"""
    try:
        db = get_database()
        content = content_service.get_content_item(content_id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Check if animated summary already exists
        if content.get("animated_summary"):
            return content["animated_summary"]
        
        # Generate storyboard
        summary = content.get("summary", "")
        if not summary:
            raise HTTPException(status_code=400, detail="Content summary not available")
        
        storyboard = ai_service.generate_storyboard(summary)
        
        # Generate narration audio
        audio_bytes = elevenlabs_service.generate_narration_audio(storyboard)
        
        # Upload audio to blob storage
        blob_name = f"summary_{content_id}.mp3"
        audio_url = storage_service.upload_blob(
            "audio-summaries",
            blob_name,
            audio_bytes,
            "audio/mpeg"
        )
        
        # Save animated summary
        animated_summary = {
            "storyboard": storyboard,
            "audio_url": audio_url
        }
        
        # Update content item
        db.content_items.update_one(
            {"_id": ObjectId(content_id)},
            {"$set": {"animated_summary": animated_summary}}
        )
        
        return animated_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{content_id}/complete")
async def mark_content_complete(content_id: str, user_id: str):
    """Mark content as completed by user (viewed, not streak-eligible)"""
    try:
        from datetime import datetime
        db = get_database()
        # Create event for tracking views
        event = {
            "user_id": user_id,
            "content_id": content_id,
            "event_type": "content_viewed",
            "created_at": datetime.utcnow()
        }
        db.events.insert_one(event)
        
        # Note: Streak is ONLY updated after a passed quiz, not on content completion
        # This endpoint just tracks that the user viewed the content
        
        return {"status": "completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


