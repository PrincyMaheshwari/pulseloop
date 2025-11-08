from fastapi import APIRouter, HTTPException
from app.services.user_service import user_service

router = APIRouter()

@router.get("/organizations")
async def list_organizations():
    """List all organizations"""
    try:
        from app.core.database import get_database
        db = get_database()
        orgs = list(db.organizations.find())
        for org in orgs:
            org["id"] = str(org["_id"])
        return {"organizations": orgs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def get_analytics(organization_id: str):
    """Get organization analytics"""
    try:
        from app.core.database import get_database
        from datetime import datetime, timedelta
        db = get_database()
        
        # Get organization users
        users = list(db.users.find({"organization_id": organization_id}))
        user_ids = [str(user["_id"]) for user in users]
        
        # Calculate metrics
        total_users = len(users)
        active_users = db.events.count_documents({
            "organization_id": organization_id,
            "created_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
        })
        
        # Average tech score
        avg_tech_score = sum(user.get("tech_score", 0) for user in users) / total_users if total_users > 0 else 0
        
        # Participation rate
        users_with_activity = db.quiz_attempts.distinct("user_id", {
            "user_id": {"$in": user_ids},
            "created_at": {"$gte": datetime.utcnow() - timedelta(days=30)}
        })
        participation_rate = len(users_with_activity) / total_users if total_users > 0 else 0
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "avg_tech_score": avg_tech_score,
            "participation_rate": participation_rate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sources")
async def add_source(source_data: dict):
    """Add content source"""
    try:
        from app.core.database import get_database
        from datetime import datetime
        db = get_database()
        
        source_data["created_at"] = datetime.utcnow()
        source_data["updated_at"] = datetime.utcnow()
        
        result = db.sources.insert_one(source_data)
        return {"id": str(result.inserted_id), "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports")
async def generate_report(organization_id: str):
    """Generate organization report"""
    try:
        from app.core.database import get_database
        from datetime import datetime, timedelta
        db = get_database()
        
        # Get organization users
        users = list(db.users.find({"organization_id": organization_id}))
        user_ids = [str(user["_id"]) for user in users]
        
        # Get weekly stats
        week_ago = datetime.utcnow() - timedelta(days=7)
        completions = list(db.quiz_attempts.find({
            "user_id": {"$in": user_ids},
            "passed": True,
            "created_at": {"$gte": week_ago}
        }))
        
        return {
            "organization_id": organization_id,
            "period": "last_7_days",
            "total_completions": len(completions),
            "users": len(user_ids)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


