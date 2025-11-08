from fastapi import APIRouter, HTTPException
from app.services.user_service import user_service

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard(user_id: str):
    """Get user dashboard data"""
    try:
        dashboard = user_service.get_user_dashboard(user_id)
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_user_stats(user_id: str):
    """Get user statistics"""
    try:
        user = user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get additional stats
        from app.core.database import get_database
        db = get_database()
        
        total_completions = db.quiz_attempts.count_documents({
            "user_id": user_id,
            "passed": True
        })
        
        first_try_passes = db.quiz_attempts.count_documents({
            "user_id": user_id,
            "passed": True,
            "attempt_number": 1
        })
        
        return {
            "user": user,
            "total_completions": total_completions,
            "first_try_passes": first_try_passes,
            "retry_passes": total_completions - first_try_passes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


