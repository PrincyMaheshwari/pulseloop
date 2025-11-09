from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.quiz_service import quiz_service
from app.services.user_service import user_service
from app.utils.auth import get_current_user

router = APIRouter()

class QuizSubmitRequest(BaseModel):
    answers: List[int]
    quiz_id: Optional[str] = None

@router.get("/content/{content_id}")
async def get_quiz(content_id: str, version: int = 1, current_user=Depends(get_current_user)):
    """Get quiz for content item"""
    try:
        quiz = quiz_service.get_or_create_quiz(content_id, version)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/content/{content_id}/submit")
async def submit_quiz(content_id: str, request: QuizSubmitRequest, current_user=Depends(get_current_user)):
    """Submit quiz answers"""
    try:
        from app.core.database import get_database
        from bson import ObjectId
        db = get_database()
        
        # Determine which quiz to use
        quiz = None
        attempt_number = 1
        
        # If quiz_id was provided in request, use it (for retries)
        if request.quiz_id:
            quiz = db.quizzes.find_one({"_id": ObjectId(request.quiz_id)})
            if quiz:
                quiz["id"] = str(quiz["_id"])
                attempt_count = db.quiz_attempts.count_documents(
                    {"user_id": current_user["id"], "content_id": content_id}
                )
                attempt_number = attempt_count + 1
            else:
                raise HTTPException(status_code=404, detail="Quiz not found")
        else:
            latest_attempt = db.quiz_attempts.find_one(
                {"user_id": current_user["id"], "content_id": content_id},
                sort=[("created_at", -1)]
            )

            if latest_attempt and latest_attempt.get("next_quiz_id") and not latest_attempt.get("passed"):
                quiz = db.quizzes.find_one({"_id": ObjectId(latest_attempt["next_quiz_id"])})
                if quiz:
                    quiz["id"] = str(quiz["_id"])
                    attempt_count = db.quiz_attempts.count_documents(
                        {"user_id": current_user["id"], "content_id": content_id}
                    )
                    attempt_number = attempt_count + 1
                else:
                    quiz = quiz_service.get_or_create_quiz(content_id, version=1)
                    attempt_number = 1
            else:
                quiz = quiz_service.get_or_create_quiz(content_id, version=1)
                attempt_number = 1
        
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Submit answers
        result = quiz_service.submit_quiz(
            current_user["id"],
            content_id,
            str(quiz["_id"]),
            request.answers,
            attempt_number=attempt_number
        )
        
        # If passed, update streak
        if result.get("status") == "passed":
            user_service.update_streak(current_user["id"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/{content_id}/retry")
async def get_retry_quiz(content_id: str, current_user=Depends(get_current_user)):
    """Get retry quiz after failure"""
    try:
        from app.core.database import get_database
        from bson import ObjectId
        db = get_database()
        
        # Get the latest attempt to find next_quiz_id
        latest_attempt = db.quiz_attempts.find_one(
            {"user_id": current_user["id"], "content_id": content_id},
            sort=[("created_at", -1)]
        )
        
        if not latest_attempt:
            raise HTTPException(status_code=404, detail="No previous attempt found")
        
        if latest_attempt.get("passed"):
            raise HTTPException(status_code=400, detail="Quiz already passed")
        
        next_quiz_id = latest_attempt.get("next_quiz_id")
        if not next_quiz_id:
            raise HTTPException(status_code=404, detail="Retry quiz not available")
        
        quiz = db.quizzes.find_one({"_id": ObjectId(next_quiz_id)})
        if not quiz:
            raise HTTPException(status_code=404, detail="Retry quiz not found")
        
        quiz["id"] = str(quiz["_id"])
        return quiz
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


