# Deployment Guide

## Prerequisites

1. Azure subscription
2. MongoDB Atlas account
3. ElevenLabs API key
4. YouTube Data API key (optional, for YouTube integration)

## Azure Resources Setup

### 1. Create Resource Group

```bash
az group create --name rg-techpulse-dev --location eastus
```

### 2. Create App Service Plan

```bash
az appservice plan create \
  --name asp-techpulse-dev \
  --resource-group rg-techpulse-dev \
  --sku B1 \
  --is-linux
```

### 3. Create Web App (Backend)

```bash
az webapp create \
  --name app-techpulse-api \
  --resource-group rg-techpulse-dev \
  --plan asp-techpulse-dev \
  --runtime "PYTHON:3.11"
```

### 4. Create Storage Account

```bash
az storage account create \
  --name sttechpulsedev \
  --resource-group rg-techpulse-dev \
  --location eastus \
  --sku Standard_LRS
```

### 5. Create Key Vault

```bash
az keyvault create \
  --name kv-techpulse-dev \
  --resource-group rg-techpulse-dev \
  --location eastus
```

### 6. Create Application Insights

```bash
az monitor app-insights component create \
  --app app-techpulse-insights \
  --location eastus \
  --resource-group rg-techpulse-dev
```

### 7. Create Azure Functions App

```bash
az functionapp create \
  --name func-techpulse-jobs \
  --resource-group rg-techpulse-dev \
  --plan asp-techpulse-dev \
  --runtime python \
  --storage-account sttechpulsedev
```

### 8. Create Azure AI Foundry Project

1. Go to Azure Portal
2. Create an Azure AI Foundry project
3. Deploy GPT-4o-mini model
4. Note the endpoint and key

### 9. Create Static Web App (Frontend)

```bash
az staticwebapp create \
  --name app-techpulse-web \
  --resource-group rg-techpulse-dev \
  --location eastus2
```

## Configuration

### Backend App Service Configuration

Add the following Application Settings in Azure Portal:

```
AZURE_OPENAI_ENDPOINT=https://<your-endpoint>.openai.azure.com/
AZURE_OPENAI_KEY=<your-key>
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_SPEECH_KEY=<your-speech-key>
AZURE_SPEECH_REGION=eastus
AZURE_STORAGE_CONNECTION_STRING=<storage-connection-string>
AZURE_STORAGE_ACCOUNT_NAME=sttechpulsedev
MONGODB_URI=<atlas-connection-string>
MONGODB_DB_NAME=pulseloop
ELEVENLABS_API_KEY=<your-elevenlabs-key>
YOUTUBE_API_KEY=<your-youtube-key>
ENVIRONMENT=production
SECRET_KEY=<generate-a-secure-secret-key>
```

### Key Vault Secrets

Store sensitive values in Key Vault:

```bash
az keyvault secret set --vault-name kv-techpulse-dev --name azure-openai-key --value <your-key>
az keyvault secret set --vault-name kv-techpulse-dev --name mongodb-uri --value <atlas-connection-string>
az keyvault secret set --vault-name kv-techpulse-dev --name elevenlabs-api-key --value <your-key>
```

Reference in App Service:
```
AZURE_OPENAI_KEY=@Microsoft.KeyVault(SecretUri=https://kv-techpulse-dev.vault.azure.net/secrets/azure-openai-key/)
```

## Deployment

### Backend Deployment

1. **Using Azure CLI:**
```bash
cd backend
az webapp up --name app-techpulse-api --resource-group rg-techpulse-dev --runtime "PYTHON:3.11"
```

2. **Using GitHub Actions:**
   - Create `.github/workflows/deploy-backend.yml`
   - Configure Azure credentials
   - Push to trigger deployment

3. **Using VS Code Azure Extension:**
   - Right-click on backend folder
   - Select "Deploy to Web App"

### Frontend Deployment

1. **Using Static Web Apps:**
   - Connect GitHub repository
   - Configure build settings:
     - App location: `/frontend`
     - Api location: (leave empty)
     - Output location: `.next`

2. **Using GitHub Actions:**
   - Static Web Apps will automatically deploy on push to main

### Azure Functions Deployment

```bash
cd backend/functions
func azure functionapp publish func-techpulse-jobs
```

## MongoDB Atlas Setup

1. Create a cluster in MongoDB Atlas
2. Create a database user
3. Whitelist Azure IP addresses
4. Get connection string
5. Add to App Service configuration

## Monitoring

1. Enable Application Insights in App Service
2. Set up alerts for errors and performance
3. Monitor Azure Functions execution
4. Track API usage and costs

## Security

1. Enable HTTPS only in App Service
2. Configure CORS appropriately
3. Use managed identity for Key Vault access
4. Enable authentication with Azure AD
5. Regularly rotate secrets

## Scaling

- Scale App Service Plan based on traffic
- Enable auto-scaling for Functions
- Monitor and adjust based on usage

## Troubleshooting

### Backend Issues

1. Check Application Insights for errors
2. Review App Service logs:
```bash
az webapp log tail --name app-techpulse-api --resource-group rg-techpulse-dev
```

### Frontend Issues

1. Check Static Web Apps logs in Azure Portal
2. Verify environment variables
3. Check browser console for errors

### Functions Issues

1. Check Functions logs in Azure Portal
2. Verify timer trigger configuration
3. Check storage account connectivity


