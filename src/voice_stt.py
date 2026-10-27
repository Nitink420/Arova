# src/voice_stt.py

import whisper

_model = None


def load_whisper_model():
    global _model

    if _model is None:
        import os
        from pathlib import Path

        # Priority 1: Check bundled model path in project directory
        project_root = Path(__file__).resolve().parents[1]
        bundled_path = project_root / "models" / "tts_stt" / "whisper" / "tiny.pt"
        if bundled_path.exists():
            _model = whisper.load_model(str(bundled_path))
            return _model

        cache_dir = os.path.expanduser("~/.cache/whisper")
        os.makedirs(cache_dir, exist_ok=True)
        model_path = os.path.join(cache_dir, "tiny.pt")

        if not os.path.exists(model_path):
            print(f"[INFO] Whisper model weights not found at {model_path}. Downloading...")
            url = "https://openaipublic.azureedge.net/main/whisper/models/65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9/tiny.pt"
            try:
                import urllib.request
                import ssl
                context = ssl._create_unverified_context()
                req = urllib.request.Request(
                    url, 
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                with urllib.request.urlopen(req, context=context) as response, open(model_path, "wb") as out_file:
                    out_file.write(response.read())
                print(f"[INFO] Whisper model successfully downloaded to {model_path}")
            except Exception as e:
                print(f"[ERROR] Failed to download Whisper weights: {e}")

        # Load local pt file directly
        _model = whisper.load_model(model_path)

    return _model


def transcribe_audio(audio_path, lang=None):
    """
    Audio file ko text me convert karta hai.
    Supports offline execution without requiring external ffmpeg installation.
    """

    if audio_path is None:
        return ""

    import os
    if not os.path.exists(audio_path):
        return ""

    try:
        model = load_whisper_model()

        # Try loading with soundfile first for zero-ffmpeg dependency
        audio_input = audio_path
        try:
            import soundfile as sf
            import numpy as np
            data, sr = sf.read(audio_path, dtype="float32")
            if data.ndim > 1:
                data = data.mean(axis=1)  # Convert stereo to mono
            # Resample to 16000 Hz if needed
            if sr != 16000:
                import scipy.signal
                num_samples = int(len(data) * 16000 / sr)
                data = scipy.signal.resample(data, num_samples).astype(np.float32)
            audio_input = data
        except Exception:
            # Fall back to passing path directly to whisper (requires ffmpeg)
            audio_input = audio_path

        transcribe_args = {
            "fp16": False,
        }
        if lang:
            transcribe_args["language"] = lang

        result = model.transcribe(
            audio_input,
            **transcribe_args
        )

        text = result.get("text", "").strip()
        return text

    except Exception as e:
        return f"VOICE_TRANSCRIPTION_ERROR: {e}"


if __name__ == "__main__":
    print("Whisper STT module ready.")