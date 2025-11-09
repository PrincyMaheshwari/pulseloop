# PulseLoop - Project Summary

## Overview

PulseLoop is a B2B SaaS platform that keeps company employees or university students continuously updated on their industry through curated, AI-summarized content, live animated explainers, and gamified engagement metrics.

## Architecture

### Backend (FastAPI)
- **Location**: `backend/`
- **Framework**: FastAPI (Python 3.11+)
- **Database**: MongoDB Atlas
- **AI Services**: Azure AI Foundry (DeepSeek-V3.1)
- **Storage**: Azure Blob Storage
- **Voice**: ElevenLabs API
- **Speech-to-Text**: Azure Cognitive Services
- **Background Jobs**: Azure Functions

### Frontend (Next.js)
- **Location**: `frontend/`
- **Framework**: Next.js 14 (React 18)
- **Styling**: Tailwind CSS
- **Authentication**: Microsoft Entra ID (Azure AD) - TODO

### Key Features Implemented

1. **Smart Content Aggregation**
   - RSS feed ingestion
   - YouTube channel integration
   - Podcast RSS feed support
   - Role-based content filtering

2. **Multi-Format Daily Feed**
   - Articles, videos, and podcasts
   - Latest content first
   - Choice of content type for daily streak

3. **Dual Reading Options**
   - Full content viewing
   - Animated summary with voice narration
   - Storyboard-based visualizations

4. **Adaptive Interactive Quizzes**
   - AI-generated 5-question quizzes
   - Retry logic with targeted review hints
   - Paragraph indices for articles
   - Timestamps for videos/podcasts
   - Tech score penalties for retries

5. **Gamification**
   - Tech scores
   - Streak tracking
   - Badge system (structure in place)
   - First-try vs retry tracking

6. **Admin Dashboard**
   - Organization analytics
   - User participation metrics
   - Content source management
   - ROI reporting

## Project Structure

```
pulseloop/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── core/             # Configuration
│   │   ├── models/           # Data models
│   │   ├── services/         # Business logic
│   │   ├── scripts/          # Utility scripts
│   │   └── utils/            # Utilities
│   ├── functions/            # Azure Functions
│   ├── requirements.txt      # Python dependencies
│   └── startup.sh           # Startup script
├── frontend/
│   ├── app/                  # Next.js app directory
│   ├── lib/                  # Utilities
│   └── package.json         # Node dependencies
├── README.md                 # Main README
├── SETUP.md                  # Setup guide
├── DEPLOYMENT.md             # Deployment guide
├── API.md                    # API documentation
└── .gitignore               # Git ignore file
```

## Database Collections

- `users` - User accounts and profiles
- `organizations` - Organization settings
- `sources` - Content sources (RSS, YouTube, Podcasts)
- `content_items` - Articles, videos, podcasts
- `quizzes` - Quiz questions and versions
- `quiz_attempts` - User quiz submissions
- `events` - User activity events

## API Endpoints

### Public
- `GET /health` - Health check

### Feed
- `GET /api/feed` - Get user feed
- `GET /api/feed/today` - Get today's content

### Content
- `GET /api/content/{id}` - Get content item
- `GET /api/content/{id}/summary` - Get animated summary
- `POST /api/content/{id}/complete` - Mark as completed

### Quiz
- `GET /api/quiz/content/{id}` - Get quiz
- `POST /api/quiz/content/{id}/submit` - Submit answers
- `GET /api/quiz/content/{id}/retry` - Get retry quiz

### User
- `GET /api/me/dashboard` - User dashboard
- `GET /api/me/stats` - User statistics

### Admin
- `GET /api/admin/organizations` - List organizations
- `GET /api/admin/analytics` - Get analytics
- `POST /api/admin/sources` - Add source
- `GET /api/admin/reports` - Generate report

## Environment Variables

See `SETUP.md` for detailed environment variable documentation.

### Backend Required
- Azure AI Foundry DeepSeek credentials
- Azure Speech Services credentials
- Azure Blob Storage connection string
- MongoDB Atlas connection string
- ElevenLabs API key
- YouTube API key (optional)

### Frontend Required
- Backend API URL
- Azure AD credentials (for authentication)

## Setup Instructions

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Fill in .env with your credentials
   python app/scripts/init_db.py
   uvicorn app.main:app --reload
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   cp .env.example .env.local
   # Fill in .env.local with your credentials
   npm run dev
   ```

## Deployment

See `DEPLOYMENT.md` for detailed deployment instructions to Azure.

### Azure Resources
- App Service (backend)
- Static Web Apps (frontend)
- Azure Functions (background jobs)
- Azure Blob Storage
- Azure Key Vault
- Application Insights
- Azure AI Foundry (DeepSeek-V3.1)

## TODO / Future Enhancements

1. **Authentication**
   - Implement Microsoft Entra ID (Azure AD) integration
   - JWT token validation
   - Role-based access control

2. **Features**
   - Animated summary visualization component
   - Real-time transcript generation for videos/podcasts
   - Badge system implementation
   - Social features (sharing, comments)

3. **Improvements**
   - Better error handling
   - Rate limiting
   - Caching layer
   - Performance optimization
   - Comprehensive testing
   - CI/CD pipeline

4. **Monitoring**
   - Application Insights integration
   - Error tracking
   - Performance monitoring
   - Usage analytics

## License

MIT

## Support

For issues and questions, please refer to the documentation files:
- `SETUP.md` - Local development setup
- `DEPLOYMENT.md` - Azure deployment
- `API.md` - API documentation
- `README.md` - General information


