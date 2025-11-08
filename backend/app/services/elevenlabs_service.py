import logging
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)

class ElevenLabsService:
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default voice (Rachel)
    
    def text_to_speech(self, text: str, voice_id: str = None) -> bytes:
        """Convert text to speech and return audio bytes"""
        try:
            url = f"{self.base_url}/text-to-speech/{voice_id or self.voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            return response.content
        except Exception as e:
            logger.error(f"Error converting text to speech: {e}")
            raise
    
    def generate_narration_audio(self, storyboard: list) -> bytes:
        """Generate narration audio from storyboard steps"""
        try:
            # Combine all step descriptions into a narrative
            narration_parts = []
            for step in storyboard:
                title = step.get("title", "")
                description = step.get("description", "")
                narration_parts.append(f"{title}. {description}")
            
            narration_text = " ".join(narration_parts)
            return self.text_to_speech(narration_text)
        except Exception as e:
            logger.error(f"Error generating narration audio: {e}")
            raise

# Singleton instance
elevenlabs_service = ElevenLabsService()


