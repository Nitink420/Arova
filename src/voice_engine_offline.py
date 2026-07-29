# src/voice_engine_offline.py

import os
import sys
import hashlib
import re
from pathlib import Path

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


def translate_to_hindi_devanagari(text: str) -> str:
    """
    Dynamically translate Roman script Hinglish sentences to Devanagari Hindi script.
    This ensures standard Hindi phonemization, producing a natural and polite Indian voice.
    """
    # If the text has ellipses, split it, translate each segment, and join back with natural pauses
    if "..." in text:
        parts = text.split("...")
        translated_parts = [translate_to_hindi_devanagari(p) for p in parts]
        return "... ".join(translated_parts)

    t = text.strip()
    if not t:
        return ""
    t_lower = t.lower()

    # Exact checks for cached lines to return optimal clean Hindi (ellipses-free matches)
    if "namaste" in t_lower and "main arova hoon" in t_lower:
        return (
            "नमस्ते। मैं अरोवा हूँ। मैं आपकी ग्रामीण स्वास्थ्य जांच में मदद करने के लिए यहाँ हूँ। "
            "मैं डॉक्टर नहीं हूँ, और कोई अंतिम निदान नहीं देती। बीमारी की पुष्टि के लिए क्लीनिकल हीमोग्लोबिन ब्लड टेस्ट ज़रूरी है। "
            "कृपया अपना नाम बताएं।"
        )

    if "apni age batayein" in t_lower:
        # Check if there is a name (e.g. "dhanyavaad ramesh ji")
        if "dhanyavaad" in t_lower and "ji" in t_lower:
            try:
                # Extract name between dhanyavaad and ji
                start = t_lower.find("dhanyavaad") + len("dhanyavaad")
                end = t_lower.find("ji")
                name = t[start:end].strip()
                if name:
                    return f"धन्यवाद {name} जी। कृपया अपनी उम्र बताएं।"
            except Exception:
                pass
        return "धन्यवाद। कृपया अपनी उम्र बताएं।"

    if "apne symptoms ya lakshan batayein" in t_lower:
        return (
            "अब कृपया अपने लक्षण या सिम्टम्स बताएं। "
            "जैसे कमजोरी, थकान, चक्कर आना, आँखों का पीलापन, सांस फूलना, सीने में दर्द, बेहोशी, या गंभीर कमजोरी।"
        )

    if "lower eyelid" in t_lower or "conjunctiva" in t_lower or "clear photo" in t_lower:
        return "लक्षण नोट कर लिए गए हैं। अब कृपया आँख के निचले हिस्से या कंजंक्टाइवा एरिया की साफ़ फोटो अपलोड या कैप्चर करें।"

    if "screening analysis kar rahi hoon" in t_lower or "screening analysis" in t_lower:
        return "धन्यवाद। मैं अब स्क्रीनिंग एनालिसिस कर रही हूँ। कृपया थोड़ा इंतज़ार करें।"

    if "din shubh ho" in t_lower and "dhyan rakhein" in t_lower:
        return "धन्यवाद। कृपया अपना ध्यान रखें। आपका दिन शुभ हो।"

    if "shaam shubh ho" in t_lower and "nearby clinic" in t_lower:
        return "धन्यवाद। आपकी शाम शुभ हो। ज़रूरत हो तो पास के क्लिनिक से सलाह लें।"

    # Dynamic translation replacement dictionary for report parts
    replacements = [
        # Named and priority details
        (r"(?i)(\w+)\s+ji\s*,\s*aapki\s+screening\s+complete\s+ho\s+gayi\s+hai", r"\1 जी, आपकी स्क्रीनिंग पूरी हो गई है"),
        (r"(?i)(\w+)\s+ji\s+aapki\s+screening\s+complete\s+ho\s+gayi\s+hai", r"\1 जी, आपकी स्क्रीनिंग पूरी हो गई है"),
        (r"(?i)yeh\s+final\s+diagnosis\s+nahi\s+hai", r"यह कोई अंतिम निदान यानी फाइनल डायग्नोसिस नहीं है"),
        (r"(?i)arova\s+doctor\s+nahi\s+hai", r"अरोवा डॉक्टर नहीं है"),
        (r"(?i)aapki\s+hb-test\s+priority\s+high\s+hai", r"आपकी हीमोग्लोबिन टेस्ट प्रायोरिटी उच्च यानी हाई है"),
        (r"(?i)aapki\s+hb-test\s+priority\s+medium\s+hai", r"आपकी हीमोग्लोबिन टेस्ट प्रायोरिटी मध्यम यानी मीडियम है"),
        (r"(?i)aapki\s+hb-test\s+priority\s+low\s+hai", r"आपकी हीमोग्लोबिन टेस्ट प्रायोरिटी कम यानी लो है"),
        (r"(?i)confirmation\s+ke\s+liye\s+clinical\s+hemoglobin\s+blood\s+test\s+karwana\s+recommended\s+hai", r"पुष्टि के लिए क्लिनिकल हीमोग्लोबिन ब्लड टेस्ट करवाना ज़रूरी है"),
        (r"(?i)confirmation\s+ke\s+liye\s+clinical\s+hemoglobin\s+blood\s+test\s+zaroori\s+hai", r"पुष्टि के लिए क्लिनिकल हीमोग्लोबिन ब्लड टेस्ट ज़रूरी है"),
        (r"(?i)general\s+care\s+ke\s+liye\s+aap\s+iron-rich\s+foods,\s+green\s+leafy\s+vegetables,\s+pulses,\s+beans,\s+dates,\s+jaggery,\s+nuts,\s+seasonal\s+fruits,\s+paani,\s+aur\s+proper\s+rest\s+ka\s+dhyan\s+rakh\s+sakte\s+hain", r"सामान्य देखभाल के लिए आप आयरन से भरपूर चीजें, हरी पत्तेदार सब्जियां, दालें, बीन्स, खजूर, गुड़, नट्स, मौसमी फल, पानी, और आराम का ध्यान रख सकते हैं"),
        (r"(?i)main\s+medicine\s+ya\s+dosage\s+recommend\s+nahi\s+karti", r"मैं कोई दवा या खुराक नहीं बताती"),
        (r"(?i)agar\s+breathlessness,\s+chest\s+pain,\s+fainting,\s+ya\s+severe\s+weakness\s+ho,\s+toh\s+kripya\s+doctor\s+ya\s+nearby\s+clinic\s+visit\s+karein", r"अगर सांस फूलना, सीने में दर्द, बेहोशी, या ज्यादा कमजोरी महसूस हो, तो कृपया तुरंत डॉक्टर या पास के क्लिनिक पर जाएं"),
        (r"(?i)report\s+ready\s+hai\.\s+aap\s+pdf\s+download\s+kar\s+sakte\s+hain", r"रिपोर्ट तैयार है। आप पीडीएफ डाउनलोड कर सकते हैं"),
        (r"(?i)dhanyavaad\s+(\w+)\s+ji\.\s+kripya\s+apna\s+dhyan\s+rakhein\.\s+aapka\s+din\s+shubh\s+ho", r"धन्यवाद \1 जी। कृपया अपना ध्यान रखें। आपका दिन शुभ हो"),
        (r"(?i)dhanyavaad\s+(\w+)\s+ji\.\s+kripya\s+paani\s+piyen,\s+aaram\s+karein,\s+aur\s+apna\s+dhyan\s+rakhein", r"धन्यवाद \1 जी। कृपया पानी पीयें, आराम करें, और अपना ध्यान रखें"),
        (r"(?i)dhanyavaad\s+(\w+)\s+ji\.\s+aapki\s+shaam\s+shubh\s+ho\.\s+zaroorat\s+ho\s+toh\s+nearby\s+clinic\s+se\s+salah\s+lein", r"धन्यवाद \1 जी। आपकी शाम शुभ हो। ज़रूरत हो तो पास के क्लिनिक से सलाह लें"),
        (r"(?i)dhanyavaad\s+(\w+)\s+ji\.\s+kripya\s+aaram\s+karein\.\s+agar\s+symptoms\s+severe\s+ho\s+rahe\s+hain,\s+toh\s+doctor\s+ya\s+clinic\s+visit\s+karein", r"धन्यवाद \1 जी। कृपया आराम करें। अगर लक्षण गंभीर हो रहे हैं, तो डॉक्टर या क्लिनिक पर तुरंत जाएं"),
        
        # Word-level polite equivalents
        (r"(?i)\bnamaste\b", "नमस्ते"),
        (r"(?i)\barova\b", "अरोवा"),
        (r"(?i)\bdoctor\b", "डॉक्टर"),
        (r"(?i)\bclinic\b", "क्लिनिक"),
        (r"(?i)\bmedicine\b", "मेडिसिन"),
        (r"(?i)\bdosage\b", "डोसेज"),
        (r"(?i)\btest\b", "टेस्ट"),
        (r"(?i)\bpdf\b", "पी डी एफ"),
        (r"(?i)\bdownload\b", "डाउनलोड"),
        (r"(?i)\bshubh\b", "शुभ"),
        (r"(?i)\bdhyan\b", "ध्यान")
    ]

    res = t
    for pattern, replacement in replacements:
        res = re.sub(pattern, replacement, res)

    return res


def generate_arova_speech(text: str, output_name: str, cache: bool = True) -> str:
    """
    Generate AROVA voice.
    Use Kokoro first.
    If Kokoro fails, fallback to Piper.
    Save WAV and return file path.
    Do not call play_audio().
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    DYNAMIC_DIR.mkdir(parents=True, exist_ok=True)

    # 1. If caching is enabled
    if cache:
        # Check if the output_name maps to a known file in cache directory
        name_only = Path(output_name).name
        cached_file = CACHE_DIR / name_only
        if cached_file.exists():
            return str(cached_file)

        base_name = Path(output_name).stem
        cached_file_stem = CACHE_DIR / f"{base_name}.wav"
        if cached_file_stem.exists():
            return str(cached_file_stem)

        # Use text hashing cache for dynamic content
        text_hash = hashlib.md5(text.strip().encode('utf-8')).hexdigest()
        hash_path = DYNAMIC_DIR / f"{text_hash}.wav"
        if hash_path.exists():
            print(f"[INFO] Cache HIT for dynamic speech text -> {hash_path}")
            return str(hash_path)

    # Determine save path
    if cache:
        text_hash = hashlib.md5(text.strip().encode('utf-8')).hexdigest()
        save_path = DYNAMIC_DIR / f"{text_hash}.wav"
    else:
        if Path(output_name).is_absolute():
            save_path = Path(output_name)
        else:
            save_path = CACHE_DIR / output_name

    save_path.parent.mkdir(parents=True, exist_ok=True)
    output_path = str(save_path)

    # Translate Hinglish to clean Devanagari Hindi script
    hindi_text = translate_to_hindi_devanagari(text)

    # 1. Try Kokoro TTS
    try:
        from src.voice_tts_kokoro import generate_kokoro_tts
        path = generate_kokoro_tts(hindi_text, output_path)
        if path and os.path.exists(path):
            print(f"[INFO] Kokoro generated voice at: {path}")
            return path
    except Exception as e:
        print(f"[WARNING] Kokoro TTS failed: {e}. Trying Piper fallback...")

    # 2. Try Piper fallback
    try:
        from src.voice_tts import generate_piper_tts
        path = generate_piper_tts(hindi_text, output_path)
        if path and os.path.exists(path):
            print(f"[INFO] Piper fallback generated voice at: {path}")
            return path
    except Exception as e:
        print(f"[ERROR] Piper TTS fallback also failed: {e}")
        raise RuntimeError(f"All Offline TTS engines failed. Kokoro error and Piper error: {e}")


def generate_dynamic_ask_age(name: str) -> str:
    """
    Returns ask_age greeting instantly from cached voice file (0s lag).
    """
    return str(CACHE_DIR / "ask_age.wav")


def generate_dynamic_report_speech(name: str, priority: str, generate_care: bool, severe_present: bool, closing_key: str) -> str:
    """
    Assembles report speech dynamically using cached segments (0s lag if name pre-cached in BG).
    """
    import soundfile as sf
    import numpy as np

    name_clean = name.strip()
    name_spoken = f"{name_clean} G" if not name_clean.lower().endswith(" g") else name_clean
    name_hash = hashlib.md5(name_spoken.encode('utf-8')).hexdigest()
    name_audio_path = DYNAMIC_DIR / f"name_{name_hash}.wav"

    # Synthesize name on the fly if missing (fallback)
    if not name_audio_path.exists():
        generate_arova_speech(name_spoken, str(name_audio_path), cache=False)

    p_clean = priority.lower()
    if "high" in p_clean:
        priority_key = "priority_high"
    elif "medium" in p_clean:
        priority_key = "priority_medium"
    else:
        priority_key = "priority_low"

    segments = [
        str(name_audio_path),
        str(CACHE_DIR / "report_intro.wav"),
        str(CACHE_DIR / f"{priority_key}.wav"),
        str(CACHE_DIR / "report_mid.wav")
    ]

    if generate_care:
        segments.append(str(CACHE_DIR / "report_care.wav"))

    if severe_present:
        segments.append(str(CACHE_DIR / "report_severe.wav"))

    segments.append(str(CACHE_DIR / "report_ready.wav"))
    segments.append(str(CACHE_DIR / f"{closing_key}.wav"))

    try:
        combined_data = []
        sample_rate = 24000
        for idx, path in enumerate(segments):
            if os.path.exists(path):
                data, sr = sf.read(path)
                sample_rate = sr
                combined_data.append(data)
                # Add natural pause between sections (0.25s silence)
                if idx < len(segments) - 1:
                    silence = np.zeros(int(0.25 * sample_rate))
                    combined_data.append(silence)
        if combined_data:
            final_audio = np.concatenate(combined_data)
            output_path = DYNAMIC_DIR / f"arova_summary_{name_hash}.wav"
            sf.write(str(output_path), final_audio, sample_rate)
            return str(output_path)
    except Exception as e:
        print("[ERROR] Failed to concatenate report segments:", e)

    # Fallback to cached default
    return str(CACHE_DIR / "analysis_started.wav")


if __name__ == "__main__":
    test_text = "Namaste ji. Main Arova hoon, aapki rural health screening assistant. Kripya apna naam batayein."
    try:
        filepath = generate_arova_speech(test_text, "arova_engine_test.wav", cache=False)
        print("[SUCCESS] Offline Speech engine test passed. File:", filepath)
    except Exception as e:
        print("[ERROR] Offline Speech engine test failed:", e)
