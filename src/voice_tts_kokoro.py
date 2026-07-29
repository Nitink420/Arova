# src/voice_tts_kokoro.py

import sys
from pathlib import Path
import requests

# Safely configure standard output to use UTF-8 to prevent encoding crashes on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Define paths
MODEL_DIR = PROJECT_ROOT / "models" / "tts_stt" / "kokoro"
ONNX_PATH = MODEL_DIR / "kokoro-v1.0.onnx"
VOICES_PATH = MODEL_DIR / "voices-v1.0.bin"

# Model URLs (Public Hugging Face Mirror)
MODEL_URL = "https://huggingface.co/leonelhs/kokoro-thewh1teagle/resolve/main/kokoro-v1.0.onnx"
VOICES_URL = "https://huggingface.co/leonelhs/kokoro-thewh1teagle/resolve/main/voices-v1.0.bin"

_kokoro_instance = None

def download_file_with_progress(url, dest_path):
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"\nDownloading {dest_path.name}...")
    print(f"From: {url}")
    print("This might take a couple of minutes (ONNX model is ~340MB)...")

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
                        sys.stdout.write(f"\rProgress: {percent:.2f}% ({downloaded / (1024*1024):.1f}MB / {file_size / (1024*1024):.1f}MB)")
                        sys.stdout.flush()

        print(f"\n[SUCCESS] Saved {dest_path.name} successfully!")
        return True

    except Exception as e:
        print(f"\n[ERROR] Download failed: {e}")
        if dest_path.exists():
            dest_path.unlink()  # Clean up partial download
        return False

def load_kokoro_model():
    global _kokoro_instance
    if _kokoro_instance is not None:
        return _kokoro_instance

    # 1. Download weights if missing
    if not ONNX_PATH.exists():
        print(f"[INFO] ONNX model not found. Downloading...")
        success = download_file_with_progress(MODEL_URL, ONNX_PATH)
        if not success:
            raise FileNotFoundError("Could not find or download Kokoro ONNX model weights.")

    if not VOICES_PATH.exists():
        print(f"[INFO] Voice bin file not found. Downloading...")
        success = download_file_with_progress(VOICES_URL, VOICES_PATH)
        if not success:
            raise FileNotFoundError("Could not find or download Kokoro voices bin file.")

    # 2. Setup espeak-ng dynamically
    try:
        import espeakng_loader
        from phonemizer.backend.espeak.wrapper import EspeakWrapper
        EspeakWrapper.set_library(espeakng_loader.get_library_path())
        EspeakWrapper.set_data_path(espeakng_loader.get_data_path())
        print("[INFO] espeak-ng dynamically loaded using espeakng-loader.")
    except Exception as el_err:
        print(f"[WARNING] Could not initialize espeakng-loader dynamically: {el_err}")

    # 3. Load Kokoro ONNX engine
    from kokoro_onnx import Kokoro
    _kokoro_instance = Kokoro(str(ONNX_PATH), str(VOICES_PATH))
    print("[INFO] Kokoro model loaded successfully.")
    return _kokoro_instance

def generate_kokoro_tts(text: str, output_path: str) -> str:
    """
    Generate WAV using Kokoro TTS.
    Return output path.
    """
    import soundfile as sf
    
    # Load model
    kokoro = load_kokoro_model()
    
    # Setup female Hindi voice configuration
    voice_code = "hf_beta"  # Hindi female voice (more polite and clear)
    speed = 0.82             # Natural speaking speed
    
    print(f"[INFO] Kokoro TTS Synthesizing: '{text[:40]}...' to {output_path}")
    
    samples, sample_rate = kokoro.create(
        text,
        voice=voice_code,
        speed=speed,
        lang="hi"
    )
    
    # Ensure output parent directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Save output to wav
    sf.write(str(output_path), samples, sample_rate)
    return str(output_path)

def main():
    OUTPUT_DIR = PROJECT_ROOT / "outputs" / "audio" / "tts_tests"
    OUTPUT_AUDIO_PATH = OUTPUT_DIR / "kokoro_test.wav"
    
    text = "नमस्ते जी... मैं अरोवा हूँ। मैं आपकी हेल्थ स्क्रीनिंग में मदद करने के लिए यहाँ हूँ..."
    try:
        generate_kokoro_tts(text, str(OUTPUT_AUDIO_PATH))
        print(f"[SUCCESS] Generated test audio at: {OUTPUT_AUDIO_PATH}")
    except Exception as e:
        print(f"[ERROR] Failed to run test: {e}")

if __name__ == "__main__":
    main()
