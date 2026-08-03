# src/voice_cache.py
"""
AROVA Voice Cache Manager

Pre-generates and caches static voice prompts across all supported languages
to guarantee zero latency (0s lag) during interactive voice consultation.
All speech lines use clean spaces without periods '.', danda '।', or pipes '|'.
"""

import os
from pathlib import Path
from typing import Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = PROJECT_ROOT / "outputs" / "audio" / "cache"

CACHED_LINES = {
    # Default Hindi keys
    "intro": (
        "नमस्ते मैं अरोवा हूँ मैं आपकी रूरल हेल्थ स्क्रीनिंग में मदद करने के लिए यहाँ हूँ "
        "मैं डॉक्टर नहीं हूँ और फाइनल डायग्नोसिस नहीं देती कन्फर्मेशन के लिए क्लीनिकल हीमोग्लोबिन ब्लड टेस्ट ज़रूरी है "
        "कृपया अपना नाम बताएं"
    ),
    "ask_age": "धन्यवाद कृपया अपनी उम्र बताएं",
    "ask_symptoms": (
        "अब कृपया अपने लक्षण या सिम्पटम्स बताएं जैसे कमजोरी थकान चक्कर आना आँखों का पीलापन "
        "सांस फूलना छाती में दर्द बेहोशी या बहुत अधिक कमजोरी"
    ),
    "ask_image": (
        "लक्षण नोट कर लिए गए हैं अब कृपया आँख के निचले हिस्से यानी कंजंक्टाइवा एरिया की साफ़ फोटो अपलोड या कैप्चर करें"
    ),
    "analysis_started": "धन्यवाद मैं अब स्क्रीनिंग एनालिसिस कर रही हूँ कृपया थोड़ा इंतज़ार करें",
    "closing_morning": "धन्यवाद कृपया अपना ध्यान रखें आपका दिन शुभ हो",
    "closing_evening": "धन्यवाद आपकी शाम शुभ हो ज़रूरत हो तो पास के क्लिनिक से सलाह लें",

    # Language-specific cached welcome and onboarding lines (clean spaces only)
    "intro_en": "Hello Welcome to AROVA I am here to help you with your health screening today Whenever you are ready please tell me your name",
    "intro_hi": "नमस्ते मैं अरोवा हूँ आपका स्वागत है मैं आपकी स्वास्थ्य सहायता के लिए यहाँ हूँ कृपया अपना नाम बताएं",
    "intro_ur": "सलाम मैं अरोवा हूँ आपका इस्तक़बाल है मैं आपकी सेहत की सहायता के लिए यहाँ हूँ बराह-ए-करम अपना नाम बताएं",
    "intro_bn": "হ্যালো আমি আরোভা আপনাকে স্বাগতম আমি আপনার স্বাস্থ্য সহায়তার জন্য এখানে আছি দয়া করে আপনার নাম বলুন",
    "intro_mr": "नमस्कार मी अरोव्हा आहे आपले स्वागत आहे मी आपल्या आरोग्य मदतीसाठी येथे आहे कृपया आपले नाव सांगा",
    "intro_ta": "வணக்கம் நான் அரோவா உங்களை வரவேற்கிறேன் உங்கள் சுகாதார பரிசோதனைக்கு உதவ நான் தயார் உங்கள் பெயரைச் சொல்லுங்கள்",
    "intro_te": "నమస్కారం నేను అరోవా మీకు స్వాగతం మీ ఆరోగ్య సహాయం కోసం నేను ఇక్కడ ఉన్నాను దయచేసి మీ పేరు చెప్పండి",
    "intro_gu": "નમસ્તે હું અરોવા છું આપનું સ્વાગત છે હું તમારી આરોગ્ય સહાય માટે અહીં છું કૃપા કરીને તમારું નામ જણાવો",
    "intro_kn": "ನಮಸ್ಕಾರ ನಾನು ಅರೋವಾ ನಿಮಗೆ ಸ್ವಾಗತ ನಿಮ್ಮ ಆರೋಗ್ಯ ನೆರವಿಗಾಗಿ ನಾನು ಇಲ್ಲಿದ್ದೇನೆ ದಯವಿಟ್ಟು ನಿಮ್ಮ ಹೆಸರು ಹೇಳಿ",
    "intro_ml": "നമസ്കാരം ഞാൻ അരോവ ആണ് സ്വാഗതം നിങ്ങളുടെ ആരോഗ്യ സഹായത്തിനായി ഞാൻ ഇവിടെയുണ്ട് ദയവായി നിങ്ങളുടെ പേര് പറയുക",
    "intro_pa": "ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ ਮੈਂ ਅਰੋਵਾ ਹਾਂ ਤੁਹਾਡਾ ਸਵਾਗਤ ਹੈ ਮੈਂ ਤੁਹਾਡੀ ਸਿਹਤ ਸਹਾਇਤਾ ਲਈ ਇੱਥੇ ਹਾਂ ਕਿਰਪਾ ਕਰਕੇ ਆਪਣਾ ਨਾਮ ਦੱਸੋ",

    "ask_age_en": "Thank you Please tell me your age",
    "ask_age_hi": "धन्यवाद कृपया अपनी उम्र बताएं",
    "ask_age_ur": "शुक्रिया बराह-ए-करम अपनी उम्र बताएं",
    "ask_age_bn": "ধন্যবাদ দয়া করে আপনার বয়স বলুন",
    "ask_age_mr": "धन्यवाद कृपया आपले वय सांगा",
    "ask_age_ta": "நன்றி உங்கள் வயதைச் சொல்லுங்கள்",
    "ask_age_te": "ధన్యవాదాలు దయచేసి మీ వయస్సు చెప్పండి",
    "ask_age_gu": "આભાર કૃપા કરીને તમારી ઉંમર જણાવો",
    "ask_age_kn": "ಧನ್ಯವಾದಗಳು ದಯವಿಟ್ಟು ನಿಮ್ಮ ವಯಸ್ಸು ಹೇಳಿ",
    "ask_age_ml": "നന്ദി ദയവായി നിങ്ങളുടെ വയസ്സ് പറയുക",
    "ask_age_pa": "ਧੰਨਵਾਦ ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੀ ਉਮਰ ਦੱਸੋ",

    "ask_symptoms_en": "Thank you Please tell me your symptoms such as weakness dizziness or tiredness",
    "ask_symptoms_hi": "धन्यवाद अब अपने लक्षण बताएं जैसे कमजोरी चक्कर आना या थकान",
    "ask_symptoms_ur": "शुक्रिया अब अपनी अलामात बताएं जैसे कमज़ोरी चक्कर आना या थकान",
    "ask_symptoms_bn": "ধন্যবাদ এবার আপনার লক্ষণসমূহ বলুন যেমন দুর্বলতা বা মাথা ঘোরা",
    "ask_symptoms_mr": "धन्यवाद आता आपली लक्षणे सांगा जसे की अशक्तपणा किंवा चक्कर येणे",
    "ask_symptoms_ta": "நன்றி உங்கள் அறிகுறிகளைச் சொல்லுங்கள்",
    "ask_symptoms_te": "ధన్యవాదాలు మీ లక్షణాలు చెప్పండి",
    "ask_symptoms_gu": "આભાર હવે તમારા લક્ષણો જણાવો",
    "ask_symptoms_kn": "ಧನ್ಯವಾದಗಳು ನಿಮ್ಮ ಲಕ್ಷಣಗಳನ್ನು ತಿಳಿಸಿ",
    "ask_symptoms_ml": "നന്ദി നിങ്ങളുടെ ലക്ഷണങ്ങൾ പറയുക",
    "ask_symptoms_pa": "ਧੰਨਵਾਦ ਹੁਣ ਆਪਣੇ ਲੱਛਣ ਦੱਸੋ",

    "ask_image_en": "Symptoms recorded Please upload a clear photo of your lower eyelid conjunctiva",
    "ask_image_hi": "लक्षण नोट कर लिए गए हैं अब अपनी निचली पलक की साफ फोटो अपलोड करें",
    "ask_image_ur": "अलामात दर्ज कर ली गई हैं अब अपनी निचली पलक की साफ तस्वीर अपलोड करें",
    "ask_image_bn": "লক্ষণসমূহ নোট করা হয়েছে এবার চোখের নিচের অংশের পরিষ্কার ছবি আপলোড করুন",
    "ask_image_mr": "लक्षणे नोंदवली गेली आहेत आता डोळ्याच्या खालच्या भागाचा स्पष्ट फोटो अपलोड करा",
    "ask_image_ta": "அறிகுறிகள் பதிவு செய்யப்பட்டன கீழ் இமையின் தெளிவான புகைப்படத்தைப் பதிவேற்றவும்",
    "ask_image_te": "లక్షణాలు నమోదు చేయబడ్డాయి కంటి కింది భాగం ఫోటో అప్‌లోড చేయండి",
    "ask_image_gu": "લક્ષણો નોંધાઈ ગયા છે હવે આંખનો ફોટો અપલોડ કરો",
    "ask_image_kn": "ಲಕ್ಷಣಗಳನ್ನು ದಾಖಲಿಸಲಾಗಿದೆ ಕಣ್ಣಿನ ಕೆಳಗಿನ ಭಾಗದ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
    "ask_image_ml": "ലക്ഷണങ്ങൾ രേഖപ്പെടുത്തി കണ്ണിന്റെ ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുക",
    "ask_image_pa": "ਲੱਛਣ ਨੋਟ ਕਰ ਲਏ ਗਏ ਹਨ ਅੱਖ ਦੀ ਫੋਟੋ ਅੱਪਲੋਡ ਕਰੋ",

    "analysis_started_en": "Please wait Preparing your screening report",
    "analysis_started_hi": "कृपया प्रतीक्षा करें मैं आपकी रिपोर्ट तैयार कर रही हूँ",
    "analysis_started_ur": "बराह-ए-करम इंतजार करें आपकी रिपोर्ट तैयार की जा रही है",
    "analysis_started_bn": "দয়া করে অপেক্ষা করুন আপনার রিপোর্ট তৈরি করা হচ্ছে",
    "analysis_started_mr": "कृपया प्रतीक्षा करा तुमचा अहवाल तयार केला जात आहे",
    "analysis_started_ta": "தயவுசெய்து காத்திருக்கவும் அறிக்கை தயாராகிறது",
    "analysis_started_te": "దయచేసి వేచి ఉండండి నివేదిక సిద్ధమవుతోంది",
    "analysis_started_gu": "કૃપા કરીને રાહ જુઓ રિપોર્ટ તૈયાર થઈ રહ્યો છે",
    "analysis_started_kn": "ದಯವಿಟ್ಟು ನಿರೀಕ್ಷಿಸಿ ವರದಿ ಸಿದ್ಧವಾಗುತ್ತಿದೆ",
    "analysis_started_ml": "ദയവായി കാത്തിരിക്കൂ റിപ്പോർട്ട് തയ്യാറാകുന്നു",
    "analysis_started_pa": "ਕਿਰਪਾ ਕਰਕੇ ਇੰਤਜ਼ਾਰ ਕਰੋ ਰਿਪੋਰਟ ਤਿਆਰ ਹੋ ਰਹੀ ਹੈ",

    "report_intro": "जी आपकी स्क्रीनिंग पूरी हो गई है यह फाइनल डायग्नोसिस नहीं है अरोवा डॉक्टर नहीं है आपकी हीमोग्लोबिन टेस्ट प्रायोरिटी",
    "priority_low": "कम यानी लो",
    "priority_medium": "मध्यम यानी मीडियम",
    "priority_high": "अधिक यानी हाई",
    "report_mid": "है कन्फर्मेशन के लिए क्लीनिकल हीमोग्लोबिन ब्लड टेस्ट करवाना रेकमेंडेड है",
    "report_care": "सामान्य देखभाल के लिए आप आयरन से भरपूर खाना हरी पत्तेदार सब्जियां दालें खजूर गुड़ ड्राई फ्रूट्स मौसमी फल पानी और आराम का ध्यान रख सकते हैं मैं दवाई या खुराक की सलाह नहीं देती",
    "report_severe": "अगर सांस फूलना छाती में दर्द बेहोशी या बहुत अधिक कमजोरी हो तो कृपया तुरंत डॉक्टर या पास के क्लिनिक में जाएं",
    "report_ready": "रिपोर्ट तैयार है आप पीडीएफ डाउनलोड कर सकते हैं"
}


def ensure_voice_cache() -> Dict[str, str]:
    """
    Create common cached voice files if missing.
    Returns dict of audio names and file paths.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    from src.voice_engine_offline import generate_arova_speech

    cached_paths = {}
    for name, text in CACHED_LINES.items():
        filename = f"{name}.wav"
        output_path = CACHE_DIR / filename

        if not output_path.exists():
            try:
                lang = name.split("_")[-1] if "_" in name and len(name.split("_")[-1]) == 2 else "hi"
                generate_arova_speech(text, filename, cache=False, lang=lang)
            except Exception as e:
                print(f"[WARNING] Could not pre-generate voice cache line '{name}': {e}")

        cached_paths[name] = str(output_path)

    return cached_paths


def get_cached_voice(name: str, lang: str = "en") -> str:
    """
    Return cached WAV file path immediately if exists.
    Checks language-specific key first, then generic fallback.
    """
    lang_key = f"{name}_{lang.lower()}"
    output_path_lang = CACHE_DIR / f"{lang_key}.wav"
    if output_path_lang.exists():
        return str(output_path_lang)

    output_path = CACHE_DIR / f"{name}.wav"
    if output_path.exists():
        return str(output_path)

    target_key = lang_key if lang_key in CACHED_LINES else (name if name in CACHED_LINES else None)
    if target_key:
        try:
            from src.voice_engine_offline import generate_arova_speech
            save_name = f"{target_key}.wav"
            generate_arova_speech(CACHED_LINES[target_key], save_name, cache=False, lang=lang)
            res_path = CACHE_DIR / save_name
            if res_path.exists():
                return str(res_path)
        except Exception as e:
            print(f"[WARNING] Runtime voice generation for '{target_key}' failed: {e}")

    return str(output_path) if output_path.exists() else None
