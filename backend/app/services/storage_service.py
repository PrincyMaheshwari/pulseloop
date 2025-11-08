import logging
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from app.core.config import settings
import os

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        self.account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self._ensure_containers()
    
    def _ensure_containers(self):
        """Ensure required containers exist"""
        containers = ["articles-raw", "transcripts", "audio-summaries"]
        for container_name in containers:
            try:
                container_client = self.blob_service_client.get_container_client(container_name)
                if not container_client.exists():
                    container_client.create_container()
                    logger.info(f"Created container: {container_name}")
            except Exception as e:
                logger.error(f"Error ensuring container {container_name}: {e}")
    
    def upload_blob(self, container_name: str, blob_name: str, data: bytes, content_type: str = "text/plain") -> str:
        """Upload data to blob storage and return the blob URL"""
        try:
            blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            blob_client.upload_blob(data, overwrite=True, content_settings={"content_type": content_type})
            return blob_client.url
        except Exception as e:
            logger.error(f"Error uploading blob: {e}")
            raise
    
    def upload_file(self, container_name: str, blob_name: str, file_path: str) -> str:
        """Upload a file to blob storage"""
        try:
            with open(file_path, "rb") as data:
                return self.upload_blob(container_name, blob_name, data.read())
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise
    
    def download_blob(self, container_name: str, blob_name: str) -> bytes:
        """Download blob data"""
        try:
            blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            return blob_client.download_blob().readall()
        except Exception as e:
            logger.error(f"Error downloading blob: {e}")
            raise
    
    def delete_blob(self, container_name: str, blob_name: str):
        """Delete a blob"""
        try:
            blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            blob_client.delete_blob()
        except Exception as e:
            logger.error(f"Error deleting blob: {e}")
            raise
    
    def get_blob_url(self, container_name: str, blob_name: str) -> str:
        """Get the URL for a blob"""
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        return blob_client.url

# Singleton instance
storage_service = StorageService()


