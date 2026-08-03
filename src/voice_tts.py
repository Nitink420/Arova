# src/voice_tts.py
"""
AROVA Piper Fallback TTS Driver

Synthesizes spoken audio using Piper ONNX offline voice engine with speech preprocessing
and peak loudness normalization.
"""

import os
import wave
from pathlib import Path
import numpy as np
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PIPER_MODEL_PATH = PROJECT_ROOT / "models" / "tts_stt" / "piper" / "voice.onnx"
PIPER_CONFIG_PATH = PROJECT_ROOT / "models" / "tts_stt" / "piper" / "voice.onnx.json"

from src.voice_speech_engine import MultilingualSpeechEngine


def generate_piper_tts(text: str, output_path: str, lang: str = "en") -> str:
    """
    Generate WAV using existing Piper model with full text preprocessing.
    """
    if not PIPER_MODEL_PATH.exists() or not PIPER_CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Piper model files missing. Checked paths:\n"
            f"- Model: {PIPER_MODEL_PATH}\n"
            f"- Config: {PIPER_CONFIG_PATH}"
        )

    clean_text = MultilingualSpeechEngine.preprocess_text(text, lang=lang)
    if not clean_text:
        clean_text = text

    print(f"[INFO] Piper TTS Synthesizing ({lang.upper()}): '{clean_text[:40]}...' to {output_path}")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    from piper.voice import PiperVoice

    try:
        voice = PiperVoice.load(str(PIPER_MODEL_PATH), str(PIPER_CONFIG_PATH))

        raw_pcm_bytes = bytearray()
        sample_rate = 22050
        sample_width = 2
        channels = 1

        for chunk in voice.synthesize(clean_text):
            sample_rate = chunk.sample_rate
            sample_width = chunk.sample_width
            channels = chunk.sample_channels
            raw_pcm_bytes.extend(chunk.audio_int16_bytes)

        # Convert to float32 numpy array for post-processing
        pcm_int16 = np.frombuffer(raw_pcm_bytes, dtype=np.int16)
        samples_float = pcm_int16.astype(np.float32) / 32768.0

        # Apply post-processing
        processed_samples, sample_rate = MultilingualSpeechEngine.post_process_audio(samples_float, sample_rate)

        # Write WAV file
        processed_int16 = (processed_samples * 32767.0).astype(np.int16)

        with wave.open(output_path, "wb") as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(processed_int16.tobytes())

        if os.path.exists(output_path):
            return str(output_path)
        else:
            raise FileNotFoundError("Piper synthesis completed but output file was not found.")

    except Exception as e:
        print(f"[ERROR] Piper fallback synthesis failed: {e}")
        raise e