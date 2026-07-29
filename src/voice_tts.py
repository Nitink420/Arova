# src/voice_tts.py

import os
import wave
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PIPER_MODEL_PATH = PROJECT_ROOT / "models" / "tts_stt" / "piper" / "voice.onnx"
PIPER_CONFIG_PATH = PROJECT_ROOT / "models" / "tts_stt" / "piper" / "voice.onnx.json"

def generate_piper_tts(text: str, output_path: str) -> str:
    """
    Generate WAV using existing Piper model.
    Return output path.
    """
    if not PIPER_MODEL_PATH.exists() or not PIPER_CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Piper model files missing. Checked paths:\n"
            f"- Model: {PIPER_MODEL_PATH}\n"
            f"- Config: {PIPER_CONFIG_PATH}"
        )

    print(f"[INFO] Piper TTS Synthesizing: '{text[:40]}...' to {output_path}")

    # Ensure output parent directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    from piper.voice import PiperVoice

    try:
        # Load the voice model
        voice = PiperVoice.load(str(PIPER_MODEL_PATH), str(PIPER_CONFIG_PATH))
        
        with wave.open(output_path, "wb") as wav_file:
            initialized = False
            for chunk in voice.synthesize(text):
                if not initialized:
                    wav_file.setnchannels(chunk.sample_channels)
                    wav_file.setsampwidth(chunk.sample_width)
                    wav_file.setframerate(chunk.sample_rate)
                    initialized = True
                wav_file.writeframes(chunk.audio_int16_bytes)
        
        if os.path.exists(output_path):
            print(f"[INFO] Piper synthesis completed successfully.")
            return str(output_path)
        else:
            raise FileNotFoundError("Piper synthesis completed but output file was not found.")
    except Exception as e:
        print(f"[ERROR] Piper fallback synthesis failed: {e}")
        raise e

if __name__ == "__main__":
    sample_text = "नमस्ते जी... मैं अरोवा हूँ, आपकी हेल्थ असिस्टेंट।"
    test_output = PROJECT_ROOT / "outputs" / "audio" / "piper_test.wav"
    try:
        path = generate_piper_tts(sample_text, str(test_output))
        print("Piper test successful. Saved audio at:", path)
    except Exception as err:
        print("Piper test failed:", err)