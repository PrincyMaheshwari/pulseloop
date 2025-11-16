import logging
import os
import tempfile
import time
from typing import Any, Dict, List, Optional

import requests
import azure.cognitiveservices.speech as speechsdk
from app.core.config import settings
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class SpeechService:
    def __init__(self) -> None:
        self.speech_key = settings.AZURE_SPEECH_KEY
        self.speech_region = settings.AZURE_SPEECH_REGION
        self._speech_config: Optional[speechsdk.SpeechConfig] = None

    def _get_speech_config(self) -> speechsdk.SpeechConfig:
        """Lazily create speech config on first use"""
        if self._speech_config is None:
            if not self.speech_key or not self.speech_region:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Azure Speech Services is not configured. Please set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables."
                )
            try:
                self._speech_config = speechsdk.SpeechConfig(
                    subscription=self.speech_key,
                    region=self.speech_region,
                )
                # Enable detailed output with word timestamps
                self._speech_config.output_format = speechsdk.OutputFormat.Detailed
                try:
                    self._speech_config.request_word_level_timestamps()
                except AttributeError:
                    # request_word_level_timestamps is not available in very old SDK versions
                    self._speech_config.set_property(
                        speechsdk.PropertyId.SpeechServiceResponse_RequestWordLevelTimestamps,
                        "true",
                    )

                # Optimise for long-form dictation scenarios
                self._speech_config.set_property(
                    speechsdk.PropertyId.Speech_SegmentationSilenceTimeoutMs,
                    "5000",
                )
            except Exception as exc:
                logger.error("Failed to initialize Azure Speech config: %s", exc)
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Failed to initialize Azure Speech Services: {exc}"
                ) from exc
        return self._speech_config

    @property
    def speech_config(self) -> speechsdk.SpeechConfig:
        """Property accessor for lazy config initialization"""
        return self._get_speech_config()

    def transcribe_from_url(self, audio_url: str, language: str = "en-US") -> Dict[str, Any]:
        """
        Download audio from a remote URL and transcribe it with Azure Speech.
        Returns a dict containing the full transcript and timestamped segments.
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=self._infer_extension(audio_url)) as tmp_file:
                response = requests.get(audio_url, timeout=60, stream=True)
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp_file.write(chunk)
                tmp_path = tmp_file.name

            return self.transcribe_file(tmp_path, language=language)
        except Exception as exc:
            logger.error("Error downloading or transcribing audio from %s: %s", audio_url, exc)
            raise
        finally:
            if "tmp_path" in locals() and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    logger.warning("Failed to remove temporary audio file %s", tmp_path)

    def transcribe_file(self, file_path: str, language: str = "en-US") -> Dict[str, Any]:
        """
        Transcribe a local audio file and return transcript plus segment timing metadata.
        """
        try:
            config = self._get_speech_config()
            audio_config = speechsdk.audio.AudioConfig(filename=file_path)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=config,
                audio_config=audio_config,
                language=language,
            )

            full_text_parts: List[str] = []
            segments: List[Dict[str, Any]] = []
            done = False

            def recognized_cb(evt) -> None:
                nonlocal full_text_parts, segments
                result = evt.result
                if result.reason == speechsdk.ResultReason.RecognizedSpeech and result.text:
                    segment_text = result.text.strip()
                    if segment_text:
                        start_ms = int(result.offset / 10_000) if result.offset else 0
                        duration_ms = int(result.duration / 10_000) if result.duration else 0
                        end_ms = start_ms + duration_ms
                        segments.append(
                            {
                                "text": segment_text,
                                "start_ms": start_ms,
                                "end_ms": end_ms,
                            }
                        )
                        full_text_parts.append(segment_text)
                elif result.reason == speechsdk.ResultReason.NoMatch:
                    logger.debug("Azure Speech could not match audio segment to speech.")

            def stop_cb(_) -> None:
                nonlocal done
                done = True

            recognizer.recognized.connect(recognized_cb)
            recognizer.session_stopped.connect(stop_cb)
            recognizer.canceled.connect(stop_cb)

            recognizer.start_continuous_recognition()

            start_time = time.time()
            timeout_seconds = 900  # 15 minutes
            while not done:
                time.sleep(0.5)
                if (time.time() - start_time) > timeout_seconds:
                    logger.warning("Azure Speech transcription timed out after %s seconds", timeout_seconds)
                    break

            recognizer.stop_continuous_recognition()

            full_text = " ".join(full_text_parts).strip()
            return {"full_text": full_text, "segments": segments}

        except Exception as exc:
            logger.error("Error transcribing audio file %s: %s", file_path, exc)
            raise

    @staticmethod
    def _infer_extension(url: str) -> str:
        for ext in (".mp3", ".wav", ".m4a", ".ogg"):
            if ext in url.lower():
                return ext
        return ".mp3"


speech_service = SpeechService()
