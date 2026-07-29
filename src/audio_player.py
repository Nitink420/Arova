import pygame
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUDIO_DIR = PROJECT_ROOT / "outputs" / "audio"


def get_latest_audio():
    audio_files = list(AUDIO_DIR.glob("*.wav")) + list(AUDIO_DIR.glob("*.mp3"))

    if not audio_files:
        raise FileNotFoundError(
            f"No audio files found in: {AUDIO_DIR}\n"
            "Pehle python src\\voice_tts.py chalao, phir audio play karo."
        )

    latest_file = max(audio_files, key=lambda file: file.stat().st_mtime)
    return latest_file


def play_audio(audio_path: str):
    audio_path = Path(audio_path)

    if not audio_path.is_absolute():
        audio_path = PROJECT_ROOT / audio_path

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    pygame.mixer.init()
    pygame.mixer.music.load(str(audio_path))
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.quit()


if __name__ == "__main__":
    latest_audio = get_latest_audio()
    print(f"Playing latest audio: {latest_audio}")
    play_audio(str(latest_audio))