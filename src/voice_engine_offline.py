# src/voice_engine_offline.py
"""
AROVA Multilingual Offline Voice Synthesis Engine

Orchestrates high-quality offline speech generation across all 11 supported languages
(English, Hindi, Bengali, Marathi, Tamil, Telugu, Gujarati, Kannada, Malayalam, Punjabi, Urdu)
using Kokoro TTS with Piper ONNX fallback.

Routes all text through MultilingualSpeechEngine for normalization, medical term expansion,
number spelling, and audio post-processing (peak loudness normalization, silence trimming, anti-clipping fade).
"""

import os
import sys
import hashlib
from pathlib import Path
from typing import Optional

# Safely configure standard output to use UTF-8 to prevent encoding crashes on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

CACHE_DIR = PROJECT_ROOT / "outputs" / "audio" / "cache"
DYNAMIC_DIR = PROJECT_ROOT / "outputs" / "audio" / "dynamic"

from src.voice_speech_engine import MultilingualSpeechEngine


def generate_arova_speech(
    text: str, output_name: str, cache: bool = True, lang: str = "en"
) -> Optional[str]:
    """
    Generate AROVA spoken audio for text in target language.

    Tries Kokoro TTS first, then Piper fallback.
    Applies full speech normalization and audio post-processing.
    Never crashes — returns file path on success, or None on failure.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    DYNAMIC_DIR.mkdir(parents=True, exist_ok=True)

    target_lang = lang.lower().strip()

    # 1. Caching lookup
    if cache:
        name_only = Path(output_name).name
        cached_file = CACHE_DIR / name_only
        if cached_file.exists():
            return str(cached_file)

        base_name = Path(output_name).stem
        cached_file_stem = CACHE_DIR / f"{base_name}.wav"
        if cached_file_stem.exists():
            return str(cached_file_stem)

        text_hash = hashlib.md5(f"{target_lang}_{text.strip()}".encode("utf-8")).hexdigest()
        hash_path = DYNAMIC_DIR / f"{text_hash}.wav"
        if hash_path.exists():
            return str(hash_path)

    # Determine save path
    if cache:
        text_hash = hashlib.md5(f"{target_lang}_{text.strip()}".encode("utf-8")).hexdigest()
        save_path = DYNAMIC_DIR / f"{text_hash}.wav"
    else:
        if Path(output_name).is_absolute():
            save_path = Path(output_name)
        else:
            save_path = CACHE_DIR / output_name

    save_path.parent.mkdir(parents=True, exist_ok=True)
    output_path = str(save_path)

    # 1. Try Kokoro TTS (with internal MultilingualSpeechEngine preprocessing and post-processing)
    try:
        from src.voice_tts_kokoro import generate_kokoro_tts
        path = generate_kokoro_tts(text, output_path, lang=target_lang)
        if path and os.path.exists(path):
            return path
    except Exception as e:
        print(f"[WARNING] Kokoro TTS failed for lang='{target_lang}': {e}. Trying Piper fallback...")

    # 2. Try Piper fallback (with internal MultilingualSpeechEngine preprocessing and post-processing)
    try:
        from src.voice_tts import generate_piper_tts
        path = generate_piper_tts(text, output_path, lang=target_lang)
        if path and os.path.exists(path):
            return path
    except Exception as e:
        print(f"[WARNING] Piper TTS fallback failed for lang='{target_lang}': {e}")

    return None


def generate_dynamic_ask_age(name: str, lang: str = "en") -> Optional[str]:
    """Return ask_age greeting instantly from cached voice file (0s lag)."""
    lang_key = f"ask_age_{lang.lower()}"
    p_lang = CACHE_DIR / f"{lang_key}.wav"
    if p_lang.exists():
        return str(p_lang)

    p_default = CACHE_DIR / "ask_age.wav"
    if p_default.exists():
        return str(p_default)

    return None


def generate_dynamic_report_speech(
    name: str,
    priority: str,
    generate_care: bool,
    severe_present: bool,
    closing_key: str,
    lang: str = "en",
) -> Optional[str]:
    """Assemble report speech dynamically using speech-optimized engine."""
    from app.services.language_service import LanguageService
    lang_service = LanguageService()
    summary_text = lang_service.t(
        "report_spoken_summary",
        lang=lang,
        name=name or "Patient",
        priority=priority,
    )
    safe_filename = f"report_summary_{lang}_{hashlib.md5(summary_text.encode('utf-8')).hexdigest()[:8]}.wav"
    return generate_arova_speech(summary_text, safe_filename, cache=True, lang=lang)
