from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from .content import Source

class Organization(BaseModel):
    id: Optional[str] = None
    name: str
    domain: Optional[str] = None
    sources: List[str] = []  # List of source IDs
    roles: List[str] = []  # List of job roles
    settings: dict = {}
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Acme Corp",
                "domain": "acme.com",
                "sources": ["source1", "source2"],
                "roles": ["Data Analyst - Hospitality", "Software Engineer - FinTech"]
            }
        }


