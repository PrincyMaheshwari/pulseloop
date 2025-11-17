# PulseLoop - Industry Trend Awareness Platform

A comprehensive B2B SaaS platform designed specifically for company employees and university students to stay continuously updated on their industry through curated, AI-summarized content, interactive quizzes, and gamified learning experiences. PulseLoop helps organizations keep their teams informed about the latest trends, technologies, and industry insights while making learning engaging and measurable.

## Features

### 🏠 Landing Page
- Modern, professional design optimized for enterprise use
- Clear value proposition for organizations and individual learners
- Responsive layout optimized for all devices
- Smooth navigation to dashboard and admin features
- Call-to-action to start the learning journey

### 📊 Learning Dashboard
- **Personalized Feed**: Role-based content curation showing articles and podcasts relevant to your job function
- **Tech Score Tracking**: Real-time display of your learning progress and knowledge score
- **Streak Monitoring**: Track consecutive days of active learning with current and longest streak metrics
- **Recent Activity Feed**: View recently consumed content and quiz performance
- **Content Type Selection**: Choose between articles or podcasts for daily learning
- **Quick Access Navigation**: Easy switching between feed, content view, quizzes, and admin dashboard
- **Progress Indicators**: Visual representation of learning milestones and achievements

### 📰 Multi-Format Content Consumption
- **Article Reading**: Full-text articles from curated sources with AI-generated summaries
- **Podcast Listening**: Audio content with key insight extraction
- **Content Filtering**: Role-based content filtering ensuring relevance to your industry and job function
- **Source Management**: Admin-configurable content sources from trusted industry publications
- **Publishing Date Tracking**: Chronological organization of content with latest-first sorting

### 🤖 AI-Powered Content Summarization
- **Intelligent Summaries**: DeepSeek-V3.1 powered summaries that extract key insights from articles and podcasts
- **Animated Summaries**: Flowchart-style visual summaries with step-by-step explanations
- **Voice Narration**: ElevenLabs text-to-speech integration for audio summaries
- **Content Analysis**: Automatic extraction of key concepts, trends, and actionable insights
- **Tag Generation**: AI-generated tags for content categorization and filtering
- **Priority Scoring**: Relevance scoring based on job role and organizational needs

### 🧪 Adaptive Interactive Quizzes
- **AI-Generated Questions**: DeepSeek-V3.1 creates 5-question multiple-choice quizzes based on content
- **Smart Retry Logic**: If you get 3+ questions wrong, the system generates a new quiz focusing on missed concepts
- **Targeted Review Hints**: 
  - For articles: Specific paragraph indices to re-read
  - For podcasts: Approximate timestamp ranges to re-listen
- **Concept-Based Learning**: Identifies specific concepts you struggled with and creates targeted retry questions
- **Explanation Feedback**: Detailed explanations for each correct answer to reinforce learning
- **Attempt Tracking**: Multiple attempt support with progressive difficulty adjustment

### 🎯 Gamified Engagement System
- **Tech Score Calculation**: Points awarded based on quiz performance and learning consistency
  - First-try success: +10 points
  - Second attempt: +6 points
  - Multiple retries: +3 points
  - Failed attempts: -2 points penalty
- **Streak Tracking**: Daily streak maintenance requires completing content and passing quizzes
- **Badge System**: Achievement badges for milestones (structure in place for future expansion)
- **Progress Visualization**: Visual dashboards showing learning journey and improvement over time
- **Leaderboard Ready**: Infrastructure for organization-wide learning competitions

### 👥 Admin Dashboard
- **Organization Analytics**: Comprehensive metrics on team learning engagement
- **ROI Metrics**: Track the impact of learning initiatives on organizational goals
- **Participation Rates**: Monitor user engagement and content consumption patterns
- **Content Source Management**: Add, configure, and manage RSS feeds and podcast sources
- **User Management**: View individual user progress and learning statistics
- **Report Generation**: Generate detailed reports on learning outcomes and engagement metrics
- **Role-Based Content Configuration**: Assign content sources to specific job roles and departments


## Technical Features

### 🤖 AI Integration
- **Azure AI Foundry (DeepSeek-V3.1)**: 
  - Content summarization and insight extraction
  - Quiz question generation with context awareness
  - Review hint generation with precise location targeting
  - Retry quiz creation focused on missed concepts
  - Tag generation and content categorization
  - Priority scoring for role-based relevance
- **ElevenLabs API**: 
  - High-quality text-to-speech for audio summaries
  - Natural-sounding voice narration
  - Multiple voice options for personalized experience
- **Smart Prompting**: Industry and role-specific prompts for accurate content analysis and quiz generation

### 📱 Responsive Design
- **Mobile-First Approach**: Optimized for smartphones, tablets, and desktops
- **Touch-Friendly Interface**: Large touch targets and intuitive navigation
- **Adaptive Layout**: Seamless experience across all screen sizes and orientations
- **Modern UI Framework**: Next.js with Tailwind CSS for consistent, professional styling
- **Fast Load Times**: Optimized performance with server-side rendering and efficient data fetching

### 💾 Data Management
- **MongoDB Atlas**: Cloud-hosted NoSQL database for scalable data storage
- **Content Storage**: Azure Blob Storage for raw articles, transcripts, and audio summaries
- **User Data**: Persistent storage of learning progress, quiz attempts, and streaks
- **Content Metadata**: Rich metadata storage including tags, role assignments, and source information
- **Export Capabilities**: Infrastructure for generating and downloading learning reports
- **Data Privacy**: Secure data handling with proper authentication and authorization

### ⚙️ Backend Architecture
- **FastAPI Framework**: High-performance Python web framework with automatic API documentation
- **RESTful API Design**: Clean, consistent API endpoints for all features
- **Azure Functions**: Serverless background jobs for content ingestion and processing
- **Azure Key Vault**: Secure secrets management for API keys and credentials
- **CORS Configuration**: Proper cross-origin resource sharing for frontend integration
- **Error Handling**: Comprehensive error handling and logging throughout the application

### 🔄 Content Ingestion Pipeline
- **Automated RSS Feed Processing**: Scheduled ingestion of articles from configured RSS feeds
- **Podcast RSS Support**: Audio content processing
- **Role-Based Filtering**: Content automatically tagged and filtered by job role relevance
- **Duplicate Detection**: Prevents duplicate content ingestion
- **Source Management**: Admin-configurable content sources with enable/disable functionality

## Setup Instructions

### Prerequisites
- Python 3.11+ installed
- Node.js 18+ installed
- MongoDB Atlas account (or local MongoDB instance)
- Azure account with:
  - Azure AI Foundry project with DeepSeek-V3.1 deployment
  - Azure Blob Storage account
  - Azure Functions (optional, for background jobs)
  - Azure Key Vault (optional, for production)
- ElevenLabs API key

### Installation

#### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create `.env` file:**
```bash
cp .env.example .env
```

5. **Fill in your credentials in `.env`:**
```env
# MongoDB Configuration (REQUIRED)
MONGODB_URI=mongodb://localhost:27017  # or your MongoDB Atlas connection string
MONGODB_DB_NAME=pulseloop

# Azure AI Foundry (DeepSeek) Configuration
AZURE_DEEPSEEK_ENDPOINT=https://<your-resource>.services.ai.azure.com/
AZURE_DEEPSEEK_KEY=<YOUR_DEEPSEEK_API_KEY>
AZURE_DEEPSEEK_MODEL=DeepSeek-V3.1
OPENAI_API_VERSION=2024-05-01-preview

# Azure Storage Configuration
AZURE_STORAGE_CONNECTION_STRING=<storage-connection-string>
AZURE_STORAGE_ACCOUNT_NAME=<account-name>
STORAGE_CONTAINER_ARTICLES=articles-raw
STORAGE_CONTAINER_TRANSCRIPTS=transcripts
STORAGE_CONTAINER_SUMMARIES=audio-summaries

# ElevenLabs Configuration
ELEVENLABS_API_KEY=<your-elevenlabs-key>

# Azure Active Directory (Azure AD) Configuration
# Required for production authentication, optional for local development
AZURE_AD_TENANT_ID=<your-azure-ad-tenant-id>
AZURE_AD_CLIENT_ID=<your-azure-ad-client-id>
AZURE_AD_ALLOWED_AUDIENCES=api://<your-client-id>
AZURE_AD_DEFAULT_ROLE=employee

# Development Authentication Bypass
# Set to 'true' for local development when Azure AD is not configured
# When Azure AD config is missing, this defaults to true automatically
AUTH_DEV_BYPASS=true
AUTH_DEV_BYPASS_USER_OID=00000000-0000-0000-0000-000000000001
AUTH_DEV_BYPASS_USER_EMAIL=dev.user@example.com
AUTH_DEV_BYPASS_USER_NAME=PulseLoop Dev User
AUTH_DEV_BYPASS_USER_ROLE=employee
AUTH_DEV_BYPASS_JOB_ROLE=Software Engineer - Canva
AUTH_DEV_BYPASS_TENANT_ID=dev-tenant

# Azure Key Vault (optional, disabled by default)
# Set ENABLE_AZURE_KEY_VAULT=true to load secrets from Key Vault instead of .env
# For local development, use .env file - Key Vault is not required
ENABLE_AZURE_KEY_VAULT=false
AZURE_KEY_VAULT_URI=<key-vault-uri>


# Application Configuration
ENVIRONMENT=development
SECRET_KEY=<your-secret-key-change-in-production>
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

**Important Notes:**

- **Local Development**: The application runs locally by default. You only need to configure `MONGODB_URI` to get started.
- **Azure Services**: All Azure services (Azure AI Foundry / DeepSeek, Azure Blob Storage) and ElevenLabs for text-to-speech are optional and consumed via their SDKs using API keys from `.env`. The app will gracefully report 503 errors if services are not configured, allowing you to test features incrementally.
- **Authentication**: The app automatically enables `AUTH_DEV_BYPASS=true` if Azure AD configuration is missing, making local development easier.
- **Key Vault**: Azure Key Vault is disabled by default. Set `ENABLE_AZURE_KEY_VAULT=true` only if you want to load secrets from Key Vault instead of `.env`. For local development, `.env` is recommended.

6. **Initialize database (creates indexes and a sample org/user):**
```bash
python app/scripts/init_db.py
```

   **Optional:** Insert demo content so `/api/feed` has data:
   ```bash
   python app/scripts/seed_content.py
   ```

7. **Seed role-aware content sources:**
   
   The feed relies on the ingestion pipeline, so you need to insert source documents with `role_tags` matching your desired job roles. For example, using MongoDB shell or a script:
   
   ```python
   from app.core.database import get_database
   from datetime import datetime
   
   db = get_database()
   
   # Insert an RSS source with role tags matching your job role
   source = {
       "name": "TechCrunch",
       "type": "rss",
       "url": "https://techcrunch.com/feed/",
       "role_tags": ["Software Engineer - Canva"],  # Match your AUTH_DEV_BYPASS_JOB_ROLE
       "enabled": True,
       "organization_id": "<your-org-id>",  # From init_db.py output
       "created_at": datetime.utcnow(),
       "updated_at": datetime.utcnow()
   }
   db.sources.insert_one(source)
   ```

8. **Run content ingestion (optional):**
   
   To populate content dynamically, run the Azure Functions ingestion locally:
   
   ```bash
   # Install Azure Functions Core Tools (if not already installed)
   npm install -g azure-functions-core-tools@4
   
   # Navigate to functions directory
   cd backend/functions
   
   # Install function dependencies
   pip install -r ../requirements-functions.txt
   
   # Start the function locally
   func start
   ```
   
   Ensure you have the required environment variables set in your `.env`:
   - `AZURE_STORAGE_CONNECTION_STRING` (for storing content)
   - `AZURE_DEEPSEEK_ENDPOINT` and `AZURE_DEEPSEEK_KEY` (for AI processing)
   
   The ingestion function will process enabled sources and populate `content_items` with content matching your `role_tags`.

9. **Run the development server:**
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

#### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Create `.env.local` file:**
```env
# Backend API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Development Authentication Bypass
# Set to 'true' to skip Azure AD authentication in local development
# This allows the app to work without Azure AD configuration
NEXT_PUBLIC_DEV_AUTH_BYPASS=true

# Azure Active Directory (Azure AD) Configuration
# Required for production authentication
# These can be left empty if using dev bypass mode
NEXT_PUBLIC_AZURE_AD_CLIENT_ID=<your-azure-ad-client-id>
NEXT_PUBLIC_AZURE_AD_TENANT_ID=<your-azure-ad-tenant-id>
NEXT_PUBLIC_AZURE_AD_REDIRECT_URI=http://localhost:3000
NEXT_PUBLIC_AZURE_AD_API_SCOPES=api://<your-client-id>/.default
```

**Note:** For local development with the backend using `AUTH_DEV_BYPASS=true`, set `NEXT_PUBLIC_DEV_AUTH_BYPASS=true` in the frontend as well. This skips MSAL authentication and uses a static dev bypass token.

4. **Run the development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## File Structure

```
pulseloop/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   │   ├── admin.py   # Admin dashboard endpoints
│   │   │   ├── auth.py    # Authentication endpoints
│   │   │   ├── content.py # Content management endpoints
│   │   │   ├── feed.py    # Feed and dashboard endpoints
│   │   │   ├── quiz.py    # Quiz endpoints
│   │   │   └── user.py    # User profile endpoints
│   │   ├── core/          # Core configuration
│   │   │   ├── config.py  # Environment settings
│   │   │   └── database.py # MongoDB connection
│   │   ├── models/        # Database models
│   │   │   ├── content.py # Content item models
│   │   │   ├── event.py   # Event tracking models
│   │   │   ├── organization.py # Organization models
│   │   │   ├── quiz.py    # Quiz models
│   │   │   └── user.py    # User models
│   │   ├── services/      # Business logic
│   │   │   ├── ai_service.py # AI content analysis
│   │   │   ├── content_service.py # Content management
│   │   │   ├── elevenlabs_service.py # Text-to-speech
│   │   │   ├── quiz_service.py # Quiz generation and scoring
│   │   │   ├── speech_service.py # Speech-to-text (for podcasts)
│   │   │   ├── storage_service.py # Blob storage
│   │   │   └── user_service.py # User management
│   │   ├── scripts/       # Utility scripts
│   │   │   └── init_db.py # Database initialization
│   │   ├── utils/         # Utilities
│   │   │   └── auth.py    # Authentication utilities
│   │   └── main.py        # FastAPI application
│   ├── functions/         # Azure Functions (optional - background content ingestion jobs)
│   │   └── ingest_content/ # Content ingestion function
│   ├── requirements.txt   # Python dependencies
│   ├── requirements-functions.txt # Function dependencies (optional)
│   └── .env.example       # Environment variable template
├── frontend/              # Next.js frontend
│   ├── app/              # Next.js app directory
│   │   ├── admin/        # Admin dashboard page
│   │   ├── content/      # Content viewing pages
│   │   ├── dashboard/    # User dashboard page
│   │   ├── globals.css   # Global styles
│   │   ├── layout.tsx    # Root layout
│   │   └── page.tsx      # Landing page
│   ├── lib/              # Utilities
│   │   └── api.ts        # API client
│   ├── next.config.js    # Next.js configuration
│   ├── package.json      # Node dependencies
│   ├── postcss.config.js # PostCSS configuration
│   ├── tailwind.config.js # Tailwind configuration
│   └── tsconfig.json     # TypeScript configuration
└── README.md             # This file
```

## Usage Guide

### Getting Started

1. **Landing Page**: Review platform features and navigate to dashboard
2. **Dashboard Overview**: View your current tech score, streak, and personalized content feed
3. **Content Consumption**: Click on any content item to view full article or podcast episode
4. **Quiz Taking**: After consuming content, take the AI-generated quiz to test your understanding
5. **Review and Retry**: If you struggle with the quiz, use review hints to revisit specific sections
6. **Track Progress**: Monitor your tech score and streak on the dashboard

### Content Consumption Flow

1. **Browse Feed**: Navigate to dashboard to see your personalized feed
2. **Select Content**: Choose an article or podcast episode that interests you
3. **Read/Watch/Listen**: Consume the full content or view the AI-generated summary
4. **Take Quiz**: Complete the 5-question quiz to test your understanding
5. **Review Results**: 
   - If passed (0-2 wrong): Earn points and maintain your streak
   - If failed (3+ wrong): Receive review hints and retry quiz
6. **Retry if Needed**: Use review hints to focus on missed concepts, then take the retry quiz

### Quiz System

1. **Initial Quiz**: AI generates 5 multiple-choice questions based on content
2. **Answer Submission**: Select your answers and submit
3. **Scoring**: 
   - Correct answers earn points toward tech score
   - Wrong answers trigger review hint generation
4. **Review Hints**: 
  - Articles: Paragraph indices to re-read
  - Podcasts: Approximate timestamp ranges to re-listen
5. **Retry Quiz**: New quiz focusing on concepts you missed
6. **Final Score**: Points awarded based on attempt number and performance

### Admin Dashboard

1. **Access Admin**: Navigate to admin dashboard (requires admin privileges)
2. **View Analytics**: Monitor organization-wide learning metrics
3. **Manage Sources**: Add RSS feeds or podcast sources
4. **Configure Roles**: Assign content sources to specific job roles
5. **Generate Reports**: Create detailed reports on learning outcomes
6. **User Management**: View individual user progress and engagement

### Content Source Management

1. **Add RSS Feed**: 
   - Provide RSS feed URL
   - Assign to relevant job roles
   - Configure update frequency
2. **Add Podcast**: 
   - Provide podcast RSS feed URL
   - Configure role assignments

## API Endpoints

### Content Feed
- `GET /api/feed` - Get personalized feed for user's role
- `GET /api/feed/today` - Get today's top content for streak
- `GET /api/feed/daily-options` - Get latest article and podcast options

### Content Management
- `GET /api/content/{id}` - Get specific content item
- `GET /api/content/{id}/summary` - Get AI-generated animated summary
- `POST /api/content/{id}/complete` - Mark content as completed

### Quizzes
- `GET /api/quiz/content/{id}` - Get quiz for content item
- `POST /api/quiz/content/{id}/submit` - Submit quiz answers
- `GET /api/quiz/content/{id}/retry` - Get retry quiz after failure

### User Dashboard
- `GET /api/me/dashboard` - Get user dashboard (streaks, scores, badges)
- `GET /api/me/stats` - Get user statistics

### Admin
- `GET /api/admin/organizations` - List organizations
- `GET /api/admin/analytics` - Get organization analytics
- `POST /api/admin/sources` - Add content sources
- `GET /api/admin/reports` - Generate reports

## Design Principles

Following modern web application design guidelines:

- **Consistent Navigation**: Clear information architecture with intuitive menu structure
- **Responsive Layout**: Seamless experience across desktop, tablet, and mobile devices
- **Visual Hierarchy**: Proper use of typography, spacing, and color to guide user attention
- **Performance Optimization**: Fast load times with efficient data fetching and caching
- **Accessibility**: WCAG-compliant design with proper contrast and keyboard navigation
- **User Feedback**: Clear success and error messages for all user actions
- **Professional Styling**: Clean, modern interface suitable for enterprise use

## Privacy & Security

- **Secure Authentication**: JWT token-based authentication (Azure AD integration planned)
- **Data Encryption**: All API communications use HTTPS
- **Secure Storage**: MongoDB Atlas with encrypted connections
- **API Key Management**: Azure Key Vault integration (optional, disabled by default - uses `.env` for local development)
- **User Privacy**: User data stored securely with proper access controls
- **Content Security**: Secure content ingestion and processing pipeline
- **CORS Configuration**: Proper cross-origin resource sharing settings

## Browser Compatibility

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Local Development

This application is designed to run locally by default. Both the FastAPI backend and Next.js frontend can be run on your local machine without any Azure infrastructure dependencies.

### Running the Stack Locally

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Both services will start and communicate via the configured `NEXT_PUBLIC_API_BASE_URL` (defaults to `http://localhost:8000`).

### Azure Services (Optional)

The application can connect to Azure services (Azure AI Foundry / DeepSeek, Azure Blob Storage) and ElevenLabs for text-to-speech using API keys from your `.env` file. These services are:
- **Optional**: The app gracefully handles missing configurations
- **Consumed via SDKs**: No Azure infrastructure deployment required
- **Configurable**: Set API keys in `.env` to enable specific features

### Background Jobs (Optional)

The `backend/functions` directory contains Azure Functions code for background content ingestion. This is optional and not required for local development. The functions are designed to run as scheduled background jobs in Azure, but can also be adapted to run locally as standalone Python scripts if needed.

## Future Enhancements

- **Authentication**: Microsoft Entra ID (Azure AD) integration for enterprise SSO
- **Advanced Analytics**: More detailed learning analytics and predictive recommendations
- **Social Features**: Content sharing and team collaboration features
- **Mobile App**: Native mobile applications for iOS and Android
- **Integration with Wearable Devices**: Track learning during commutes and breaks
- **Community Support**: Discussion forums and peer learning features
- **Real-time Notifications**: Push notifications for new content and quiz reminders
- **Offline Mode**: Download content for offline consumption
- **Advanced Badge System**: Comprehensive achievement and milestone tracking
- **Learning Paths**: Structured learning paths for career development
- **Video Annotations**: Interactive video annotations and highlights
- **AI Tutor**: Personalized AI tutor for concept clarification
- **Email Reports**: Automated weekly learning summaries and progress reports
- **AI Chatbot**: 24/7 support chatbot for learning assistance

## Support

For technical support or feature requests, please refer to the API documentation or contact the development team. The API includes comprehensive error handling and logging for troubleshooting.

## License

This project is created for educational and commercial use. Please ensure compliance with Azure AI Foundry, OpenAI, and other third-party service usage policies when deploying.

---

**PulseLoop - Empowering continuous learning and industry awareness through AI and gamification.** 🚀
