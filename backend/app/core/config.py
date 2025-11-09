import os
from typing import List

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


def load_key_vault_secrets() -> None:
    key_vault_uri = os.getenv("AZURE_KEY_VAULT_URI")
    if not key_vault_uri:
        return

    try:
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=key_vault_uri, credential=credential)

        for secret_props in client.list_properties_of_secrets():
            secret_name = secret_props.name
            secret_value = client.get_secret(secret_name).value
            env_var = secret_name.upper().replace("-", "_")
            os.environ[env_var] = secret_value
    except Exception as exc:
        # Fail gracefully; fall back to .env/env vars only
        import logging

        logging.getLogger(__name__).warning("Key Vault secret load failed: %s", exc)


load_key_vault_secrets()
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


