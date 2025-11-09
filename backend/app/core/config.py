from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Azure AI Foundry - DeepSeek
    deepseek_endpoint: str = os.getenv("AZURE_DEEPSEEK_ENDPOINT", "")
    deepseek_key: str = os.getenv("AZURE_DEEPSEEK_KEY", "")
    deepseek_model: str = os.getenv("AZURE_DEEPSEEK_MODEL", "DeepSeek-V3.1")
    openai_api_version: str = os.getenv("OPENAI_API_VERSION", "2024-05-01-preview")
    
    # Azure Speech Services
    AZURE_SPEECH_KEY: str = os.getenv("AZURE_SPEECH_KEY", "")
    AZURE_SPEECH_REGION: str = os.getenv("AZURE_SPEECH_REGION", "eastus")
    
    # Azure Storage
    AZURE_STORAGE_CONNECTION_STRING: str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    AZURE_STORAGE_ACCOUNT_NAME: str = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "")
    STORAGE_CONTAINER_ARTICLES: str = os.getenv("STORAGE_CONTAINER_ARTICLES", "articles-raw")
    STORAGE_CONTAINER_TRANSCRIPTS: str = os.getenv("STORAGE_CONTAINER_TRANSCRIPTS", "transcripts")
    STORAGE_CONTAINER_SUMMARIES: str = os.getenv("STORAGE_CONTAINER_SUMMARIES", "audio-summaries")
    
    # Azure Key Vault
    AZURE_KEY_VAULT_URI: str = os.getenv("AZURE_KEY_VAULT_URI", "")
    
    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "pulseloop")
    
    # ElevenLabs
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    
    # YouTube
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    
    # Application
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    class Config:
        case_sensitive = True

settings = Settings()


