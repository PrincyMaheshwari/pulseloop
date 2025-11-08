# PulseLoop

A B2B SaaS platform that keeps company employees or university students continuously updated on their industry through curated, AI-summarized content, live animated explainers, and gamified engagement metrics.

## Features

- **Smart Content Aggregation**: AI imports tech and industry news from pre-curated, role-based content bundles (articles, YouTube videos, podcasts)
- **Multi-Format Daily Feed**: Users can choose between reading an article, watching a YouTube video, or listening to a podcast
- **Dual Reading Options**: Full content or animated summary with voice narration
- **Adaptive Interactive Quizzes**: AI-generated quizzes with retry logic and targeted review hints
- **Gamified Engagement**: Streaks, badges, and Tech Scores for consistent learning
- **Admin Dashboard**: ROI metrics, participation rates, and engagement analytics

## Tech Stack

### Backend
- **Python FastAPI** on Azure App Service
- **MongoDB Atlas** for database
- **Azure OpenAI** (GPT-4o-mini/GPT-4o) for AI features
- **Azure Cognitive Services Speech-to-Text** for transcripts
- **Azure Blob Storage** for content storage
- **Azure Functions** for background jobs
- **Azure Key Vault** for secrets management

### Frontend
- **Next.js/React** on Azure Static Web Apps or App Service
- **Microsoft Entra ID (Azure AD)** for authentication

### External APIs
- **ElevenLabs API** for text-to-speech
- **YouTube Data API** for video content
- **Podcast RSS feeds** for podcast content

## Project Structure

```
pulseloop/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── functions/          # Azure Functions
│   └── requirements.txt
├── frontend/               # Next.js frontend
│   ├── app/               # Next.js app directory
│   ├── components/        # React components
│   └── package.json
└── README.md
```

## Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://<your-endpoint>.openai.azure.com/
AZURE_OPENAI_KEY=<your-key>
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini

# Azure Speech Services
AZURE_SPEECH_KEY=<your-speech-key>
AZURE_SPEECH_REGION=<region>

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=<storage-connection-string>
AZURE_STORAGE_ACCOUNT_NAME=<account-name>

# Azure Key Vault (optional, for production)
AZURE_KEY_VAULT_URI=<key-vault-uri>

# MongoDB Atlas
MONGODB_URI=<atlas-connection-string>

# ElevenLabs
ELEVENLABS_API_KEY=<your-elevenlabs-key>

# YouTube
YOUTUBE_API_KEY=<your-youtube-key>

# Application
ENVIRONMENT=development
SECRET_KEY=<your-secret-key>
```

See `backend/.env.example` for a template.

## Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your credentials (see Environment Variables above)

5. Run the development server:
```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AZURE_AD_CLIENT_ID=<your-client-id>
NEXT_PUBLIC_AZURE_AD_TENANT_ID=<your-tenant-id>
```

4. Run the development server:
```bash
npm run dev
```

## API Endpoints

### Content Feed
- `GET /api/feed` - Get daily feed for user's role
- `GET /api/content/{id}` - Get specific content item
- `GET /api/content/{id}/summary` - Get animated summary
- `POST /api/content/{id}/complete` - Mark content as completed

### Quizzes
- `GET /api/content/{id}/quiz` - Get quiz for content
- `POST /api/content/{id}/quiz/submit` - Submit quiz answers
- `GET /api/content/{id}/quiz/retry` - Get retry quiz after failure

### User Dashboard
- `GET /api/me/dashboard` - Get user dashboard (streaks, scores, badges)
- `GET /api/me/stats` - Get user statistics

### Admin
- `GET /api/admin/organizations` - List organizations
- `GET /api/admin/analytics` - Get organization analytics
- `POST /api/admin/sources` - Add content sources
- `GET /api/admin/reports` - Generate reports

## Deployment

### Azure App Service (Backend)

1. Create an App Service Plan and Web App in Azure Portal
2. Configure Application Settings with all environment variables
3. Deploy using GitHub Actions or Azure DevOps

### Azure Static Web Apps (Frontend)

1. Create a Static Web App in Azure Portal
2. Connect to your GitHub repository
3. Configure build settings for Next.js

### Azure Functions (Background Jobs)

1. Create a Function App in Azure Portal
2. Deploy the functions from the `backend/functions` directory
3. Configure timer triggers for content ingestion

## License

MIT
