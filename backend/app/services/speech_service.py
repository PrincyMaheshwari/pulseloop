import logging
import azure.cognitiveservices.speech as speechsdk
from app.core.config import settings

logger = logging.getLogger(__name__)

class SpeechService:
    def __init__(self):
        self.speech_key = settings.AZURE_SPEECH_KEY
        self.speech_region = settings.AZURE_SPEECH_REGION
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key,
            region=self.speech_region
        )
        # Use the latest neural voice
        self.speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"
    
    def transcribe_audio_url(self, audio_url: str, language: str = "en-US") -> str:
        """Transcribe audio from URL to text"""
        try:
            import requests
            import tempfile
            import os
            
            # Download audio file
            response = requests.get(audio_url, timeout=30)
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name
            
            try:
                # Use temporary file for transcription
                audio_config = speechsdk.audio.AudioConfig(filename=tmp_path)
                speech_recognizer = speechsdk.SpeechRecognizer(
                    speech_config=self.speech_config,
                    audio_config=audio_config,
                    language=language
                )
                
                # Use continuous recognition for longer audio
                transcript_parts = []
                done = False
                
                def recognized_cb(evt):
                    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                        transcript_parts.append(evt.result.text)
                    elif evt.result.reason == speechsdk.ResultReason.NoMatch:
                        logger.warning("No speech could be recognized in this segment")
                
                def stop_cb(evt):
                    nonlocal done
                    done = True
                
                speech_recognizer.recognized.connect(recognized_cb)
                speech_recognizer.session_stopped.connect(stop_cb)
                speech_recognizer.canceled.connect(stop_cb)
                
                # Start continuous recognition
                speech_recognizer.start_continuous_recognition()
                
                # Wait for completion (with timeout)
                import time
                timeout = 300  # 5 minutes
                start_time = time.time()
                while not done and (time.time() - start_time) < timeout:
                    time.sleep(0.5)
                
                speech_recognizer.stop_continuous_recognition()
                
                return " ".join(transcript_parts)
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        except Exception as e:
            logger.error(f"Error transcribing audio from URL: {e}")
            raise
    
    def transcribe_audio(self, audio_file_path: str, language: str = "en-US") -> str:
        """Transcribe audio from local file path to text"""
        try:
            audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config,
                language=language
            )
            
            result = speech_recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return result.text
            elif result.reason == speechsdk.ResultReason.NoMatch:
                logger.warning("No speech could be recognized")
                return ""
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speechsdk.CancellationDetails(result)
                logger.error(f"Speech recognition canceled: {cancellation_details.reason}")
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    logger.error(f"Error details: {cancellation_details.error_details}")
                return ""
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    def transcribe_audio_stream(self, audio_stream, language: str = "en-US") -> str:
        """Transcribe audio from stream"""
        try:
            audio_config = speechsdk.audio.AudioInputStream(audio_stream)
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config,
                language=language
            )
            
            result = speech_recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return result.text
            elif result.reason == speechsdk.ResultReason.NoMatch:
                logger.warning("No speech could be recognized")
                return ""
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speechsdk.CancellationDetails(result)
                logger.error(f"Speech recognition canceled: {cancellation_details.reason}")
                return ""
        except Exception as e:
            logger.error(f"Error transcribing audio stream: {e}")
            raise

# Singleton instance
speech_service = SpeechService()


