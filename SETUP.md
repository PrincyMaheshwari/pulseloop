# Setup Guide

## Local Development Setup

### Prerequisites

1. Python 3.11+
2. Node.js 18+
3. MongoDB Atlas account (or local MongoDB)
4. Azure account with:
   - Azure AI Foundry (DeepSeek-V3.1 deployment)
   - Azure Cognitive Services Speech
   - Azure Blob Storage
5. ElevenLabs API key
6. YouTube Data API key (optional)

### Backend Setup

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
   - Azure AI Foundry DeepSeek endpoint and key
   - Azure Speech key and region
   - Azure Storage connection string
   - MongoDB Atlas connection string
   - ElevenLabs API key
   - YouTube API key (optional)

6. **Initialize database:**
```bash
python app/scripts/init_db.py
```

7. **Run the development server:**
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Create `.env.local` file:**
```bash
cp .env.example .env.local
```

4. **Fill in your credentials:**
   - `NEXT_PUBLIC_API_URL`: Backend API URL (default: `http://localhost:8000`)
   - `NEXT_PUBLIC_AZURE_AD_CLIENT_ID`: Azure AD app client ID (for authentication)
   - `NEXT_PUBLIC_AZURE_AD_TENANT_ID`: Azure AD tenant ID

5. **Run the development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Azure Functions Setup (Optional)

1. **Install Azure Functions Core Tools:**
```bash
npm install -g azure-functions-core-tools@4
```

2. **Navigate to functions directory:**
```bash
cd backend/functions
```

3. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate
```

4. **Install dependencies:**
```bash
pip install -r ../requirements-functions.txt
```

5. **Run locally:**
```bash
func start
```

## Testing

### Backend API Testing

1. **Health check:**
```bash
curl http://localhost:8000/health
```

2. **Get feed (requires authentication):**
```bash
curl http://localhost:8000/api/feed \
  -H "Authorization: Bearer <token>"
```

### Frontend Testing

1. Open `http://localhost:3000` in your browser
2. Navigate to `/dashboard` to see the user dashboard
3. Navigate to `/admin` to see the admin dashboard

## Environment Variables Reference

### Backend (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_DEEPSEEK_ENDPOINT` | Azure AI Foundry DeepSeek endpoint URL | Yes |
| `AZURE_DEEPSEEK_KEY` | Azure AI Foundry DeepSeek API key | Yes |
| `AZURE_DEEPSEEK_DEPLOYMENT_NAME` | Deployment name (e.g., DeepSeek-V3.1) | Yes |
| `AZURE_SPEECH_KEY` | Azure Speech Services key | Yes |
| `AZURE_SPEECH_REGION` | Azure Speech region | Yes |
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Blob Storage connection string | Yes |
| `AZURE_STORAGE_ACCOUNT_NAME` | Azure Storage account name | Yes |
| `MONGODB_URI` | MongoDB Atlas connection string | Yes |
| `MONGODB_DB_NAME` | MongoDB database name | No (default: pulseloop) |
| `ELEVENLABS_API_KEY` | ElevenLabs API key | Yes |
| `YOUTUBE_API_KEY` | YouTube Data API key | Optional |
| `ENVIRONMENT` | Environment (development/production) | No (default: development) |
| `SECRET_KEY` | Secret key for JWT tokens | Yes |

### Frontend (.env.local)

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |
| `NEXT_PUBLIC_AZURE_AD_CLIENT_ID` | Azure AD app client ID | Yes (for auth) |
| `NEXT_PUBLIC_AZURE_AD_TENANT_ID` | Azure AD tenant ID | Yes (for auth) |

## Troubleshooting

### Backend Issues

1. **Import errors:**
   - Ensure virtual environment is activated
   - Check that all dependencies are installed
   - Verify Python version is 3.11+

2. **Database connection errors:**
   - Verify MongoDB URI is correct
   - Check network connectivity
   - Ensure IP is whitelisted in MongoDB Atlas

3. **Azure service errors:**
   - Verify all Azure credentials are correct
   - Check that services are enabled in Azure Portal
   - Verify region settings match

### Frontend Issues

1. **API connection errors:**
   - Verify `NEXT_PUBLIC_API_URL` is correct
   - Check that backend server is running
   - Verify CORS settings in backend

2. **Build errors:**
   - Clear `.next` directory: `rm -rf .next`
   - Reinstall dependencies: `rm -rf node_modules && npm install`
   - Check Node.js version (18+)

### Azure Functions Issues

1. **Import errors:**
   - Ensure dependencies are installed in virtual environment
   - Check that `sys.path` is configured correctly
   - Verify function.json is correct

2. **Timer trigger not firing:**
   - Check function.json schedule format
   - Verify function is deployed correctly
   - Check Azure Functions logs

## Next Steps

1. Set up Azure AD authentication (see DEPLOYMENT.md)
2. Configure content sources via admin dashboard
3. Deploy to Azure (see DEPLOYMENT.md)
4. Set up monitoring and alerts
5. Configure CI/CD pipeline


