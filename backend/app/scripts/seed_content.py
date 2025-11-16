"""
Content seeding script
Inserts sample content items for development/testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from app.core.database import connect_to_mongo, get_database

def main():
    connect_to_mongo()
    db = get_database()
    now = datetime.utcnow()
    db.content_items.insert_one({
        "title": "Platform engineering patterns at Canva",
        "type": "article",
        "source_id": "manual-demo",
        "url": "https://example.com/platform-engineering",
        "description": "Deep dive into Canva's internal platform stack.",
        "published_at": now,
        "role_tags": ["Software Engineer - Canva"],
        "tags": ["platform", "infrastructure"],
        "priority_score": 0.9,
        "created_at": now,
        "updated_at": now,
    })
    print("Inserted sample content.")

if __name__ == "__main__":
    main()



