# app/services/voice_service.py
"""
AROVA Voice Service

Orchestrates text-to-speech (TTS) and speech-to-text (STT) functionality across all
11 supported languages with graceful degradation.

Voice is treated as an OPTIONAL feature — failures never crash the application.

Usage:
    from app.services.voice_service import VoiceService
    voice = VoiceService()
    audio_path = voice.speak("Hello patient", "hello.wav", lang="en")
    text = voice.transcribe("/path/to/audio.wav")
"""

import os
import hashlib
from pathlib import Path
from typing import Optional

from app.core.config import Config
from app.core.logger import get_logger
from app.services.language_service import LanguageService

logger = get_logger(__name__)


class VoiceService:
    """
    Service for Multilingual TTS and STT with Kokoro → Piper → Disabled fallback chain.

    All TTS/STT operations are wrapped in try/except — voice is optional
    and must never prevent the application from starting or screening from completing.
    """

    def __init__(self):
        self.config = Config()
        self.lang_service = LanguageService()
        self.tts_engine = None    # "kokoro" | "piper" | None
        self.stt_available = False
        self._whisper_model = None

        # Cached voice lines and directory paths
        self.cache_dir = self.config.AUDIO_CACHE_DIR
        self.dynamic_dir = self.config.AUDIO_DYNAMIC_DIR

        # Ensure output directories exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.dynamic_dir.mkdir(parents=True, exist_ok=True)

        # Initialize TTS engine (Kokoro → Piper → Disabled)
        if self.config.ENABLE_TTS:
            self._init_tts()
        else:
            logger.info("TTS is disabled via ENABLE_TTS=false.")

        # Initialize STT engine (Whisper)
        if self.config.ENABLE_STT:
            self._init_stt()
        else:
            logger.info("STT is disabled via ENABLE_STT=false.")

    def _init_tts(self) -> None:
        """
        Initialize TTS engine with Kokoro → Piper → Disabled fallback.
        """
        # Try Kokoro
        try:
            from src.voice_tts_kokoro import load_kokoro_model
            load_kokoro_model()
            self.tts_engine = "kokoro"
            logger.info("TTS engine initialized: Kokoro (ONNX Multilingual)")
            return
        except Exception as e:
            logger.warning("Kokoro TTS initialization failed: %s", e)

        # Try Piper
        try:
            from piper.voice import PiperVoice  # noqa: F401
            piper_model = self.config.PROJECT_ROOT / "models" / "tts_stt" / "piper" / "voice.onnx"
            if piper_model.exists():
                self.tts_engine = "piper"
                logger.info("TTS engine initialized: Piper (fallback)")
                return
            else:
                logger.warning("Piper model file not found at %s", piper_model)
        except Exception as e:
            logger.warning("Piper TTS initialization failed: %s", e)

        # All engines failed
        self.tts_engine = None
        logger.warning(
            "All TTS engines unavailable. Voice output is DISABLED. "
            "Application will continue without voice."
        )

    def _init_stt(self) -> None:
        """Initialize Whisper STT."""
        try:
            import whisper  # noqa: F401
            self.stt_available = True
            logger.info("STT engine available: Whisper (%s)", self.config.WHISPER_MODEL)
        except ImportError:
            self.stt_available = False
            logger.warning(
                "Whisper not installed. STT is DISABLED. "
                "Application will continue without speech-to-text."
            )

    @property
    def tts_available(self) -> bool:
        """Whether any TTS engine is available."""
        return self.tts_engine is not None

    def speak(
        self, text: str, output_name: str, cache: bool = True, lang: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate speech audio from text in chosen target language.
        """
        if not self.tts_available:
            return None

        target_lang = lang or self.lang_service.get_language()
        try:
            from src.voice_engine_offline import generate_arova_speech
            path = generate_arova_speech(text, output_name, cache=cache, lang=target_lang)
            return path
        except Exception as e:
            logger.error("TTS generation failed for lang='%s': %s", target_lang, e)
            return None

    def speak_dynamic_report(
        self,
        name: str,
        priority: str,
        generate_care: bool,
        severe_present: bool,
        closing_key: str,
        lang: Optional[str] = None,
    ) -> Optional[str]:
        """Assemble dynamic report speech in target language."""
        if not self.tts_available:
            return None

        target_lang = lang or self.lang_service.get_language()
        try:
            from src.voice_engine_offline import generate_dynamic_report_speech
            return generate_dynamic_report_speech(
                name=name,
                priority=priority,
                generate_care=generate_care,
                severe_present=severe_present,
                closing_key=closing_key,
                lang=target_lang,
            )
        except Exception as e:
            logger.error("Dynamic report speech generation failed: %s", e)
            return None

    def transcribe(self, audio_path: str) -> str:
        """Transcribe audio file to text using Whisper STT."""
        if not self.stt_available:
            return ""

        if audio_path is None or not os.path.exists(audio_path):
            return ""

        try:
            from src.voice_stt import transcribe_audio
            result = transcribe_audio(audio_path)
            if result.startswith("VOICE_TRANSCRIPTION_ERROR"):
                logger.warning("Whisper transcription warning: %s", result)
                return ""
            return result
        except Exception as e:
            logger.error("STT transcription failed: %s", e)
            return ""

    def get_cached_voice(self, name: str, lang: Optional[str] = None) -> Optional[str]:
        """
        Return cached WAV file path for a pre-generated voice line in target language.
        """
        target_lang = lang or self.lang_service.get_language()
        try:
            from src.voice_cache import get_cached_voice
            res = get_cached_voice(name, lang=target_lang)
            if res and os.path.exists(res):
                return res
        except Exception as e:
            logger.warning("Cached voice fetch failed for '%s' (%s): %s", name, target_lang, e)

        # Direct disk check fallback
        output_path = self.cache_dir / f"{name}_{target_lang}.wav"
        if output_path.exists():
            return str(output_path)

        default_path = self.cache_dir / f"{name}.wav"
        if default_path.exists():
            return str(default_path)

        return None

    def warm_up_cache(self) -> None:
        """Pre-generate all cached voice files across supported languages."""
        if not self.tts_available:
            logger.info("Skipping voice cache warm-up (TTS disabled).")
            return

        try:
            from src.voice_cache import ensure_voice_cache
            logger.info("Warming up multilingual voice cache at startup...")
            ensure_voice_cache()
            logger.info("Voice cache warm-up complete.")
        except Exception as e:
            logger.error("Voice cache warm-up failed: %s. Continuing without cache.", e)

    def generate_name_audio(self, name: str, lang: Optional[str] = None) -> Optional[str]:
        """Synthesize a name audio segment for report speech."""
        if not self.tts_available:
            return None

        target_lang = lang or self.lang_service.get_language()
        try:
            from src.voice_engine_offline import generate_arova_speech, DYNAMIC_DIR
            name_clean = name.strip()
            name_spoken = (
                f"{name_clean} G"
                if target_lang == "hi" and not name_clean.lower().endswith(" g")
                else name_clean
            )
            name_hash = hashlib.md5(f"{target_lang}_{name_spoken}".encode("utf-8")).hexdigest()
            name_audio_path = DYNAMIC_DIR / f"name_{name_hash}.wav"

            if not name_audio_path.exists():
                generate_arova_speech(name_spoken, str(name_audio_path), cache=False, lang=target_lang)
                logger.info("Background name synthesis completed for '%s'", name_spoken)

            return str(name_audio_path)
        except Exception as e:
            logger.error("Background name synthesis failed: %s", e)
            return None

    def status(self) -> str:
        """Return human-readable status for health check."""
        parts = []
        if self.tts_engine:
            parts.append(f"TTS={self.tts_engine.capitalize()}")
        else:
            parts.append("TTS=DISABLED")

        if self.stt_available:
            parts.append(f"STT=Whisper({self.config.WHISPER_MODEL})")
        else:
            parts.append("STT=DISABLED")

        return ", ".join(parts)
