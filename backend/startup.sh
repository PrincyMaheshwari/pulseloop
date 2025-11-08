#!/bin/bash
# Startup script for Azure App Service

# Install dependencies
pip install -r requirements.txt

# Run migrations or initialization if needed
# python app/scripts/init_db.py

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8000


