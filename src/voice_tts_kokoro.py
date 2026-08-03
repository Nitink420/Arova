# src/voice_tts_kokoro.py
"""
AROVA Multilingual Kokoro TTS Driver

Synthesizes hospital-grade spoken audio using Kokoro-v1.0 ONNX engine.
Supports language-specific voice mappings, dynamic speed/prosody,
text normalization, and audio post-processing (peak normalization, silence trimming, anti-clipping fade).
Includes standard library 'wave' fallback for zero-dependency WAV file saving.
"""

import sys
import wave
from pathlib import Path
from typing import Optional
import requests
import numpy as np

# Safely configure standard output to use UTF-8 to prevent encoding crashes on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.voice_speech_engine import MultilingualSpeechEngine

# Define model paths
MODEL_DIR = PROJECT_ROOT / "models" / "tts_stt" / "kokoro"
ONNX_PATH = MODEL_DIR / "kokoro-v1.0.onnx"
VOICES_PATH = MODEL_DIR / "voices-v1.0.bin"

MODEL_URL = "https://huggingface.co/leonelhs/kokoro-thewh1teagle/resolve/main/kokoro-v1.0.onnx"
VOICES_URL = "https://huggingface.co/leonelhs/kokoro-thewh1teagle/resolve/main/voices-v1.0.bin"

_kokoro_instance = None


def download_file_with_progress(url: str, dest_path: Path) -> bool:
    """Download weights file with progress feedback."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"\nDownloading {dest_path.name}...")
    try:
        response = requests.get(url, stream=True, timeout=90)
        response.raise_for_status()

        file_size = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(dest_path, "wb") as out_file:
            for chunk in response.iter_content(chunk_size=32768):
                if chunk:
                    out_file.write(chunk)
                    downloaded += len(chunk)
                    if file_size > 0:
                        percent = downloaded * 100 / file_size
                        sys.stdout.write(
                            f"\rProgress: {percent:.2f}% ({downloaded / (1024*1024):.1f}MB / {file_size / (1024*1024):.1f}MB)"
                        )
                        sys.stdout.flush()

        print(f"\n[SUCCESS] Saved {dest_path.name} successfully!")
        return True
    except Exception as e:
        print(f"\n[ERROR] Download failed: {e}")
        if dest_path.exists():
            dest_path.unlink()
        return False


def load_kokoro_model():
    """Load Kokoro ONNX model singleton with espeak-ng backend."""
    global _kokoro_instance
    if _kokoro_instance is not None:
        return _kokoro_instance

    if not ONNX_PATH.exists():
        print(f"[INFO] ONNX model not found. Downloading...")
        if not download_file_with_progress(MODEL_URL, ONNX_PATH):
            raise FileNotFoundError("Could not find or download Kokoro ONNX model weights.")

    if not VOICES_PATH.exists():
        print(f"[INFO] Voice bin file not found. Downloading...")
        if not download_file_with_progress(VOICES_URL, VOICES_PATH):
            raise FileNotFoundError("Could not find or download Kokoro voices bin file.")

    try:
        import espeakng_loader
        from phonemizer.backend.espeak.wrapper import EspeakWrapper
        EspeakWrapper.set_library(espeakng_loader.get_library_path())
        EspeakWrapper.set_data_path(espeakng_loader.get_data_path())
    except Exception as el_err:
        print(f"[WARNING] espeakng-loader init note: {el_err}")

    from kokoro_onnx import Kokoro
    _kokoro_instance = Kokoro(str(ONNX_PATH), str(VOICES_PATH))
    print("[INFO] Kokoro model loaded successfully.")
    return _kokoro_instance


def save_wav_file(samples: np.ndarray, sample_rate: int, output_path: str):
    """Save audio array to WAV using soundfile or standard library wave fallback."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    try:
        import soundfile as sf
        sf.write(str(output_path), samples, sample_rate)
    except ImportError:
        # Standard library wave fallback
        int16_samples = (samples * 32767.0).clip(-32768, 32767).astype(np.int16)
        with wave.open(str(output_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(int16_samples.tobytes())


def generate_kokoro_tts(
    text: str,
    output_path: str,
    voice: Optional[str] = None,
    lang: str = "en",
    speed: Optional[float] = None,
) -> str:
    """
    Generate high-quality WAV audio using Kokoro TTS with full speech preprocessing
    and audio post-processing.
    """
    kokoro = load_kokoro_model()

    # 1. Preprocess text through multilingual speech engine
    clean_text = MultilingualSpeechEngine.preprocess_text(text, lang=lang)
    if not clean_text:
        clean_text = text

    # 2. Resolve language profile, voice, speed, and kokoro lang tag
    profile = MultilingualSpeechEngine.get_profile(lang)
    voice_code = voice or profile.get("voice_id", "af_heart")
    synth_speed = speed or profile.get("speed", 0.90)
    kokoro_lang = profile.get("kokoro_lang", "en-us")

    print(f"[INFO] Kokoro Synthesizing ({lang.upper()} / voice='{voice_code}'): '{clean_text[:40]}...' -> {output_path}")

    # 3. Kokoro inference
    try:
        samples, sample_rate = kokoro.create(
            clean_text,
            voice=voice_code,
            speed=synth_speed,
            lang=kokoro_lang,
        )
    except Exception as e:
        print(f"[WARNING] Kokoro synthesis failed with voice='{voice_code}', fallback to 'af_heart': {e}")
        samples, sample_rate = kokoro.create(
            clean_text,
            voice="af_heart",
            speed=synth_speed,
            lang="en-us",
        )

    # 4. Audio post-processing (Peak normalization, silence trimming, anti-clipping fade)
    processed_samples, sample_rate = MultilingualSpeechEngine.post_process_audio(samples, sample_rate)

    # 5. Save WAV
    save_wav_file(processed_samples, sample_rate, output_path)
    return str(output_path)
