from fastapi import APIRouter, Depends, HTTPException

from app.services.content_service import content_service
from app.utils.auth import get_current_user

router = APIRouter()


@router.get("")
async def get_feed(current_user=Depends(get_current_user)):
    """Get personalized feed for the authenticated user."""
    try:
        feed = content_service.get_user_feed(current_user["id"])
        return {"feed": feed}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/today")
async def get_todays_content(current_user=Depends(get_current_user)):
    """Get today's top content for streak tracking."""
    try:
        content = content_service.get_todays_top_content(current_user["id"])
        if not content:
            return {"content": None, "message": "No content available for today"}
        return {"content": content}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/daily-options")
async def get_daily_feed_options(current_user=Depends(get_current_user)):
    """Get the latest article, video, and podcast options for the user."""
    try:
        options = content_service.get_daily_feed_options(current_user["id"])
        return options
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

