# src/voice_cache.py

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = PROJECT_ROOT / "outputs" / "audio" / "cache"

CACHED_LINES = {
    "intro": (
        "नमस्ते... मैं अरोवा हूँ... मैं आपकी रूरल हेल्थ स्क्रीनिंग में मदद करने के लिए यहाँ हूँ... "
        "मैं डॉक्टर नहीं हूँ, और फाइनल डायग्नोसिस नहीं देती... कन्फर्मेशन के लिए क्लीनिकल हीमोग्लोबिन ब्लड टेस्ट ज़रूरी है... "
        "कृपया अपना नाम बताएं।"
    ),
    "ask_age": "धन्यवाद... कृपया अपनी उम्र बताएं।",
    "ask_symptoms": (
        "अब कृपया अपने लक्षण या सिम्पटम्स बताएं... जैसे कमजोरी... थकान... चक्कर आना... आँखों का पीलापन... "
        "सांस फूलना... छाती में दर्द... बेहोशी... या बहुत अधिक कमजोरी।"
    ),
    "ask_image": (
        "लक्षण नोट कर लिए गए हैं... अब कृपया आँख के निचले हिस्से यानी कंजंक्टाइवा एरिया की साफ़ फोटो अपलोड या कैप्चर करें।"
    ),
    "analysis_started": "धन्यवाद... मैं अब स्क्रीनिंग एनालिसिस कर रही हूँ... कृपया थोड़ा इंतज़ार करें।",
    "closing_morning": "धन्यवाद... कृपया अपना ध्यान रखें... आपका दिन शुभ हो।",
    "closing_evening": "धन्यवाद... आपकी शाम शुभ हो... ज़रूरत हो तो पास के क्लिनिक से सलाह लें।",
    "dhanyavaad": "धन्यवाद",
    "ji_ask_age": "जी। कृपया अपनी उम्र बताएं।",
    "report_intro": "जी... आपकी स्क्रीनिंग पूरी हो गई है... यह फाइनल डायग्नोसिस नहीं है... अरोवा डॉक्टर नहीं है... आपकी हीमोग्लोबिन टेस्ट प्रायोरिटी",
    "priority_low": "कम यानी लो",
    "priority_medium": "मध्यम यानी मीडियम",
    "priority_high": "अधिक यानी हाई",
    "report_mid": "है... कन्फर्मेशन के लिए क्लीनिकल हीमोग्लोबिन ब्लड टेस्ट करवाना रेकमेंडेड है...",
    "report_care": "सामान्य देखभाल के लिए आप आयरन से भरपूर खाना, हरी पत्तेदार सब्जियां, दालें, खजूर, गुड़, ड्राई फ्रूट्स, मौसमी फल, पानी और आराम का ध्यान रख सकते हैं... मैं दवाई या खुराक की सलाह नहीं देती...",
    "report_severe": "अगर सांस फूलना, छाती में दर्द, बेहोशी या बहुत अधिक कमजोरी हो, तो कृपया तुरंत डॉक्टर या पास के क्लिनिक में जाएं...",
    "report_ready": "रिपोर्ट तैयार है। आप पीडीएफ डाउनलोड कर सकते हैं..."
}

def ensure_voice_cache() -> dict:
    """
    Create common cached voice files if missing.
    Return dict of audio names and file paths.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Import inside function to avoid circular imports
    from src.voice_engine_offline import generate_arova_speech
    
    cached_paths = {}
    for name, text in CACHED_LINES.items():
        filename = f"{name}.wav"
        output_path = CACHE_DIR / filename
        
        if not output_path.exists():
            print(f"[INFO] Pre-generating cached voice: {filename}...")
            # We call generate_arova_speech with cache=False here to bypass local caching logic
            # and directly run Kokoro/Piper model generation to save the file.
            generate_arova_speech(text, filename, cache=False)
            
        cached_paths[name] = str(output_path)
        
    return cached_paths

def get_cached_voice(name: str) -> str:
    """
    Return cached WAV file path immediately if exists.
    """
    output_path = CACHE_DIR / f"{name}.wav"
    if output_path.exists():
        return str(output_path)
    
    # Fallback to generating it if somehow missing (e.g. cache deleted during runtime)
    if name in CACHED_LINES:
        print(f"[WARNING] Cached voice '{name}' was missing at runtime. Generating now...")
        from src.voice_engine_offline import generate_arova_speech
        generate_arova_speech(CACHED_LINES[name], f"{name}.wav", cache=False)
        return str(output_path)
        
    raise ValueError(f"Unknown voice cache line: {name}")
