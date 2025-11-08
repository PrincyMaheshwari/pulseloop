from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional
from app.services.content_service import content_service

router = APIRouter()

# Placeholder for user authentication
# In production, extract user_id from JWT token
def get_user_id(authorization: Optional[str] = Header(None)) -> str:
    """Extract user_id from authorization header - placeholder"""
    # TODO: Validate JWT token and extract user_id
    # For now, return a placeholder
    if authorization:
        # In production: decode JWT and extract user_id
        return "user_placeholder_id"
    raise HTTPException(status_code=401, detail="Unauthorized")

@router.get("")
async def get_feed(user_id: str = Depends(get_user_id)):
    """Get personalized feed for user"""
    try:
        feed = content_service.get_user_feed(user_id)
        return {"feed": feed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/today")
async def get_todays_content(user_id: str = Depends(get_user_id)):
    """Get today's top content for streak"""
    try:
        content = content_service.get_todays_top_content(user_id)
        if not content:
            return {"content": None, "message": "No content available for today"}
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/daily-options")
async def get_daily_feed_options(user_id: str = Depends(get_user_id)):
    """Get daily feed with latest article, video, and podcast options"""
    try:
        options = content_service.get_daily_feed_options(user_id)
        return options
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


