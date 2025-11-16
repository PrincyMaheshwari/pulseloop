import os
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env first (local development)
load_dotenv()


def load_key_vault_secrets() -> None:
    """Optionally load secrets from Azure Key Vault when ENABLE_AZURE_KEY_VAULT=true"""
    enable_key_vault = os.getenv("ENABLE_AZURE_KEY_VAULT", "false").lower() in ("1", "true", "yes")
    if not enable_key_vault:
        return

    key_vault_uri = os.getenv("AZURE_KEY_VAULT_URI")
    if not key_vault_uri:
        import logging
        logging.getLogger(__name__).warning(
            "ENABLE_AZURE_KEY_VAULT=true but AZURE_KEY_VAULT_URI is not set. "
            "Skipping Key Vault secret loading."
        )
        return

    try:
        # Conditional imports - only load Azure SDK when Key Vault is enabled
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient

        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=key_vault_uri, credential=credential)

        for secret_props in client.list_properties_of_secrets():
            secret_name = secret_props.name
            secret_value = client.get_secret(secret_name).value
            env_var = secret_name.upper().replace("-", "_")
            os.environ[env_var] = secret_value
        
        import logging
        logging.getLogger(__name__).info("Loaded secrets from Azure Key Vault")
    except Exception as exc:
        # Fail gracefully; fall back to .env/env vars only
        import logging
        logging.getLogger(__name__).warning("Key Vault secret load failed: %s", exc)


# Load Key Vault secrets if explicitly enabled (opt-in)
load_key_vault_secrets()


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

    # Azure Active Directory
    AZURE_AD_TENANT_ID: str = os.getenv("AZURE_AD_TENANT_ID", "")
    AZURE_AD_CLIENT_ID: str = os.getenv("AZURE_AD_CLIENT_ID", "")
    AZURE_AD_ALLOWED_AUDIENCES: str = os.getenv("AZURE_AD_ALLOWED_AUDIENCES", "")
    AZURE_AD_DEFAULT_ROLE: str = os.getenv("AZURE_AD_DEFAULT_ROLE", "employee")
    
    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "pulseloop")
    
    # ElevenLabs
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    
    # Application
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    AUTH_DEV_BYPASS: bool = bool(os.getenv("AUTH_DEV_BYPASS", "false").lower() in ("1", "true", "yes"))
    AUTH_DEV_BYPASS_USER_OID: str = os.getenv("AUTH_DEV_BYPASS_USER_OID", "00000000-0000-0000-0000-000000000001")
    AUTH_DEV_BYPASS_USER_EMAIL: str = os.getenv("AUTH_DEV_BYPASS_USER_EMAIL", "dev.user@example.com")
    AUTH_DEV_BYPASS_USER_NAME: str = os.getenv("AUTH_DEV_BYPASS_USER_NAME", "PulseLoop Dev User")
    AUTH_DEV_BYPASS_USER_ROLE: str = os.getenv("AUTH_DEV_BYPASS_USER_ROLE", "employee")
    AUTH_DEV_BYPASS_JOB_ROLE: str = os.getenv("AUTH_DEV_BYPASS_JOB_ROLE", "Software Engineer - Canva")
    AUTH_DEV_BYPASS_TENANT_ID: str = os.getenv("AUTH_DEV_BYPASS_TENANT_ID", "dev-tenant")
    
    class Config:
        case_sensitive = True

    @property
    def azure_ad_audiences(self) -> List[str]:
        audiences = []
        if self.AZURE_AD_CLIENT_ID:
            audiences.append(self.AZURE_AD_CLIENT_ID)
            audiences.append(f"api://{self.AZURE_AD_CLIENT_ID}")
        if self.AZURE_AD_ALLOWED_AUDIENCES:
            extra = [value.strip() for value in self.AZURE_AD_ALLOWED_AUDIENCES.split(",") if value.strip()]
            audiences.extend(extra)
        # Preserve order while removing duplicates
        seen = set()
        deduped = []
        for audience in audiences:
            if audience not in seen:
                seen.add(audience)
                deduped.append(audience)
        return deduped

settings = Settings()


