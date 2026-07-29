# src/voice_stt.py

import whisper

_model = None


def load_whisper_model():
    global _model

    if _model is None:
        import os
        import ssl
        import urllib.request

        cache_dir = os.path.expanduser("~/.cache/whisper")
        os.makedirs(cache_dir, exist_ok=True)
        model_path = os.path.join(cache_dir, "tiny.pt")

        if not os.path.exists(model_path):
            print(f"[INFO] Whisper model weights not found at {model_path}. Downloading...")
            url = "https://openaipublic.azureedge.net/main/whisper/models/65147635de6e866e1162d0dd0034f40933cd7f00f6ee4c1b4c68b941fd1a829f/tiny.pt"
            try:
                # Bypass local SSL proxy/handshake decryption block
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


def transcribe_audio(audio_path):
    """
    Audio file ko text me convert karta hai.
    """

    if audio_path is None:
        return ""

    import os
    if not os.path.exists(audio_path):
        return ""

    try:
        model = load_whisper_model()

        result = model.transcribe(
            audio_path,
            fp16=False,
            language="hi"
        )

        text = result.get("text", "").strip()
        return text

    except Exception as e:
        return f"VOICE_TRANSCRIPTION_ERROR: {e}"


if __name__ == "__main__":
    print("Whisper STT module ready.")