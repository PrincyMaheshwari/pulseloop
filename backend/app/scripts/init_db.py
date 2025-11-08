"""
Database initialization script
Creates indexes and sample data for development
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import connect_to_mongo, get_database
from datetime import datetime
from bson import ObjectId

def create_indexes():
    """Create database indexes for better performance"""
    db = get_database()
    
    # Users indexes
    db.users.create_index("email", unique=True)
    db.users.create_index("organization_id")
    db.users.create_index("job_role")
    
    # Content items indexes
    db.content_items.create_index("source_id")
    db.content_items.create_index("published_at")
    db.content_items.create_index("role_tags")
    db.content_items.create_index([("organization_id", 1), ("published_at", -1)])
    
    # Quizzes indexes
    db.quizzes.create_index("content_id")
    db.quizzes.create_index([("content_id", 1), ("version", 1)])
    
    # Quiz attempts indexes
    db.quiz_attempts.create_index("user_id")
    db.quiz_attempts.create_index("content_id")
    db.quiz_attempts.create_index([("user_id", 1), ("content_id", 1)])
    db.quiz_attempts.create_index("created_at")
    
    # Events indexes
    db.events.create_index("user_id")
    db.events.create_index("organization_id")
    db.events.create_index("event_type")
    db.events.create_index("created_at")
    
    # Sources indexes
    db.sources.create_index("organization_id")
    db.sources.create_index("enabled")
    
    print("Indexes created successfully")

def create_sample_data():
    """Create sample data for development"""
    db = get_database()
    
    # Create sample organization
    org = {
        "name": "Sample Corporation",
        "domain": "sample.com",
        "sources": [],
        "roles": ["Data Analyst - Hospitality", "Software Engineer - FinTech"],
        "settings": {},
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    org_result = db.organizations.insert_one(org)
    org_id = str(org_result.inserted_id)
    
    # Create sample user
    user = {
        "email": "user@sample.com",
        "name": "John Doe",
        "organization_id": org_id,
        "role": "employee",
        "job_role": "Data Analyst - Hospitality",
        "tech_score": 0,
        "current_streak": 0,
        "longest_streak": 0,
        "badges": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    user_result = db.users.insert_one(user)
    user_id = str(user_result.inserted_id)
    
    # Create sample source
    source = {
        "name": "TechCrunch",
        "type": "rss",
        "url": "https://techcrunch.com/feed/",
        "role_tags": ["Data Analyst - Hospitality", "Software Engineer - FinTech"],
        "enabled": True,
        "organization_id": org_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    source_result = db.sources.insert_one(source)
    
    print(f"Sample data created:")
    print(f"  Organization ID: {org_id}")
    print(f"  User ID: {user_id}")
    print(f"  Source ID: {str(source_result.inserted_id)}")

if __name__ == "__main__":
    connect_to_mongo()
    create_indexes()
    create_sample_data()
    print("Database initialization complete")


