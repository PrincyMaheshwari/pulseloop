import logging
from datetime import datetime
from typing import Optional

from azure.storage.blob import BlobServiceClient, ContentSettings
from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self) -> None:
        self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        self.account_name = settings.AZURE_STORAGE_ACCOUNT_NAME

        if not self.connection_string:
            logger.warning("Azure Storage connection string is not configured.")

        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self._ensure_containers()

    def _ensure_containers(self) -> None:
        """Ensure required containers exist"""
        containers = [
            settings.STORAGE_CONTAINER_ARTICLES,
            settings.STORAGE_CONTAINER_TRANSCRIPTS,
            settings.STORAGE_CONTAINER_SUMMARIES,
        ]
        for container_name in containers:
            try:
                container_client = self.blob_service_client.get_container_client(container_name)
                if not container_client.exists():
                    container_client.create_container()
                    logger.info("Created blob container '%s'", container_name)
            except Exception as exc:
                logger.error("Error ensuring container %s: %s", container_name, exc)

    def upload_bytes(
        self,
        container_name: str,
        blob_name: str,
        data: bytes,
        content_type: str,
    ) -> str:
        """Upload raw bytes to blob storage and return the blob URL"""
        try:
            blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            blob_client.upload_blob(
                data,
                overwrite=True,
                content_settings=ContentSettings(content_type=content_type),
            )
            return blob_client.url
        except Exception as exc:
            logger.error("Error uploading blob %s/%s: %s", container_name, blob_name, exc)
            raise

    def upload_text(
        self,
        container_name: str,
        blob_prefix: str,
        text: str,
        content_type: str = "text/plain",
    ) -> str:
        blob_name = self._build_blob_name(blob_prefix, "txt")
        return self.upload_bytes(container_name, blob_name, text.encode("utf-8"), content_type)

    def upload_json(
        self,
        container_name: str,
        blob_prefix: str,
        json_bytes: bytes,
        content_type: str = "application/json",
    ) -> str:
        blob_name = self._build_blob_name(blob_prefix, "json")
        return self.upload_bytes(container_name, blob_name, json_bytes, content_type)

    def upload_audio(
        self,
        container_name: str,
        blob_prefix: str,
        audio_bytes: bytes,
        extension: str = "mp3",
        content_type: str = "audio/mpeg",
    ) -> str:
        blob_name = self._build_blob_name(blob_prefix, extension)
        return self.upload_bytes(container_name, blob_name, audio_bytes, content_type)

    def download_blob(self, container_name: str, blob_name: str) -> bytes:
        """Download blob data"""
        try:
            blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            return blob_client.download_blob().readall()
        except Exception as exc:
            logger.error("Error downloading blob %s/%s: %s", container_name, blob_name, exc)
            raise

    def delete_blob(self, container_name: str, blob_name: str) -> None:
        """Delete a blob"""
        try:
            blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            blob_client.delete_blob()
        except Exception as exc:
            logger.error("Error deleting blob %s/%s: %s", container_name, blob_name, exc)
            raise

    @staticmethod
    def _build_blob_name(blob_prefix: str, extension: str) -> str:
        timestamp = datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")
        return f"{blob_prefix}_{timestamp}.{extension}"


storage_service = StorageService()
