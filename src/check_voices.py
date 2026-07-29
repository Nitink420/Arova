# src/check_voices.py

import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty("voices")

for i, voice in enumerate(voices):
    print("=" * 60)
    print("Index:", i)
    print("ID:", voice.id)
    print("Name:", voice.name)
    print("Languages:", voice.languages)