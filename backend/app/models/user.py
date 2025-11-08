from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"

class User(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    name: str
    organization_id: str
    role: UserRole = UserRole.EMPLOYEE
    job_role: Optional[str] = None  # e.g., "Data Analyst - Hospitality"
    tech_score: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[datetime] = None
    badges: List[str] = []
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "organization_id": "org123",
                "role": "employee",
                "job_role": "Data Analyst - Hospitality",
                "tech_score": 150,
                "current_streak": 5,
                "longest_streak": 10,
                "badges": ["early-adopter", "week-warrior"]
            }
        }


