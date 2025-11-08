# Quick Start Guide

## Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] MongoDB Atlas account
- [ ] Azure account with:
  - [ ] Azure OpenAI access
  - [ ] Azure Cognitive Services Speech
  - [ ] Azure Blob Storage
- [ ] ElevenLabs API key
- [ ] YouTube Data API key (optional)

## 5-Minute Setup

### 1. Clone and Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_KEY=your-key
AZURE_SPEECH_KEY=your-speech-key
AZURE_SPEECH_REGION=eastus
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/db
ELEVENLABS_API_KEY=your-key
```

Initialize database:
```bash
python app/scripts/init_db.py
```

Start backend:
```bash
uvicorn app.main:app --reload
```

### 2. Setup Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start frontend:
```bash
npm run dev
```

### 3. Test the Application

1. Open `http://localhost:3000` in your browser
2. Navigate to `/dashboard` to see the feed
3. Click on a content item to view it
4. Take a quiz to test the quiz functionality

## Next Steps

1. **Add Content Sources**
   - Use the admin dashboard to add RSS feeds, YouTube channels, or podcasts
   - Content will be ingested automatically by Azure Functions

2. **Configure Authentication**
   - Set up Azure AD app registration
   - Update frontend and backend with Azure AD credentials
   - Implement JWT token validation

3. **Deploy to Azure**
   - Follow `DEPLOYMENT.md` for step-by-step Azure deployment
   - Set up Azure Functions for content ingestion
   - Configure monitoring and alerts

## Common Issues

### Backend won't start
- Check that all environment variables are set
- Verify MongoDB connection string is correct
- Ensure Azure credentials are valid

### Frontend can't connect to backend
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check that backend is running on port 8000
- Verify CORS settings in backend

### Database connection errors
- Check MongoDB Atlas IP whitelist
- Verify connection string format
- Ensure database user has correct permissions

## Getting Help

- Check `SETUP.md` for detailed setup instructions
- See `API.md` for API documentation
- Review `DEPLOYMENT.md` for deployment help
- Check `PROJECT_SUMMARY.md` for architecture overview

## Development Tips

1. **Backend Development**
   - Use `--reload` flag for auto-reload during development
   - Check logs in terminal for errors
   - Use MongoDB Compass to view database

2. **Frontend Development**
   - Use browser DevTools for debugging
   - Check Network tab for API calls
   - Use React DevTools for component debugging

3. **Testing APIs**
   - Use Postman or curl to test endpoints
   - Check `API.md` for endpoint documentation
   - Use `/health` endpoint to verify backend is running


