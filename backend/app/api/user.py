from fastapi import APIRouter, Depends, HTTPException
from app.services.user_service import user_service
from app.utils.auth import get_current_user

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard(current_user=Depends(get_current_user)):
    """Get user dashboard data"""
    try:
        dashboard = user_service.get_user_dashboard(current_user["id"])
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_user_stats(current_user=Depends(get_current_user)):
    """Get user statistics"""
    try:
        user = user_service.get_user(current_user["id"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get additional stats
        from app.core.database import get_database
        db = get_database()
        
        total_completions = db.quiz_attempts.count_documents({
            "user_id": current_user["id"],
            "passed": True
        })
        
        first_try_passes = db.quiz_attempts.count_documents({
            "user_id": current_user["id"],
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


