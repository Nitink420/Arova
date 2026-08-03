# app/services/language_service.py
"""
AROVA Centralized Language & Speech Script Service

Manages application localization, global session language state, localized dictionary
resources for all 11 supported languages, voice mappings, and speech-optimized prompts.

Reads speech scripts from app/resources/speech_scripts.py for easy user editing.
"""

import threading
from typing import Dict, Any, Optional, List
from app.core.config import Config
from app.core.logger import get_logger
from app.resources.speech_scripts import SPEECH_SCRIPTS

logger = get_logger(__name__)


# Supported Languages Catalog
SUPPORTED_LANGUAGES_CATALOG: Dict[str, Dict[str, str]] = {
    "en": {"code": "en", "flag": "🇬🇧", "name": "English", "native": "English"},
    "hi": {"code": "hi", "flag": "🇮🇳", "name": "Hindi", "native": "हिन्दी"},
    "bn": {"code": "bn", "flag": "🇧🇩", "name": "Bengali", "native": "বাংলা"},
    "mr": {"code": "mr", "flag": "🇮🇳", "name": "Marathi", "native": "मराठी"},
    "ta": {"code": "ta", "flag": "🇮🇳", "name": "Tamil", "native": "தமிழ்"},
    "te": {"code": "te", "flag": "🇮🇳", "name": "Telugu", "native": "తెలుగు"},
    "gu": {"code": "gu", "flag": "🇮🇳", "name": "Gujarati", "native": "ગુજરાતી"},
    "kn": {"code": "kn", "flag": "🇮🇳", "name": "Kannada", "native": "ಕನ್ನಡ"},
    "ml": {"code": "ml", "flag": "🇮🇳", "name": "Malayalam", "native": "മലയാളം"},
    "pa": {"code": "pa", "flag": "🇮🇳", "name": "Punjabi", "native": "ਪੰਜਾਬੀ"},
    "ur": {"code": "ur", "flag": "🇮🇳", "name": "Urdu", "native": "اردو"},
}


class LanguageService:
    """
    Centralized Language & Localization Service for AROVA.
    Implemented as a thread-safe Singleton to maintain session language state.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.config = Config()

        self._current_language = self.config.DEFAULT_LANGUAGE
        if self._current_language not in SUPPORTED_LANGUAGES_CATALOG:
            self._current_language = "en"

        self._translations = self._load_translations()
        logger.info("LanguageService initialized. Active language: %s", self._current_language)

    def set_language(self, lang_code: str) -> str:
        """Set active session language cleanly."""
        code = lang_code.lower().strip()
        if code in SUPPORTED_LANGUAGES_CATALOG:
            self._current_language = code
            logger.info("Session language changed to: %s (%s)", code, SUPPORTED_LANGUAGES_CATALOG[code]["name"])
        else:
            logger.warning("Unsupported language requested '%s', defaulting to '%s'", lang_code, self._current_language)
        return self._current_language

    def get_language(self) -> str:
        """Get current session language code."""
        return self._current_language

    def get_language_info(self, lang_code: Optional[str] = None) -> Dict[str, str]:
        """Get dictionary with code, flag, name, and native label."""
        code = lang_code or self._current_language
        return SUPPORTED_LANGUAGES_CATALOG.get(code, SUPPORTED_LANGUAGES_CATALOG["en"])

    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get catalog list of all supported languages."""
        return list(SUPPORTED_LANGUAGES_CATALOG.values())

    def t(self, key: str, lang: Optional[str] = None, **kwargs) -> str:
        """
        Translate a key into target language with optional format parameters.
        """
        target_lang = lang or self._current_language

        # 1. Check custom speech scripts dictionary first
        script_dict = SPEECH_SCRIPTS.get(target_lang, SPEECH_SCRIPTS.get("en", {}))
        if key in script_dict:
            text = script_dict[key]
            if kwargs:
                try:
                    return text.format(**kwargs)
                except Exception:
                    return text
            return text

        # 2. Check general UI translations dictionary
        lang_dict = self._translations.get(target_lang, self._translations.get("en", {}))
        text = lang_dict.get(key)

        if text is None and target_lang != "en":
            text = self._translations.get("en", {}).get(key)

        if text is None:
            text = key.replace("_", " ").title()

        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text

        return text

    def get_welcome_message(self, lang: Optional[str] = None) -> str:
        """Return localized welcome audio spoken string."""
        return self.t("welcome_voice", lang=lang)

    def get_welcome_text(self, lang: Optional[str] = None) -> str:
        """Return localized welcome display transcript."""
        return self.t("welcome_text", lang=lang)

    def get_voice_config(self, lang: Optional[str] = None) -> Dict[str, Any]:
        """Return voice configuration parameters for chosen language."""
        target_lang = lang or self._current_language
        from src.voice_speech_engine import MultilingualSpeechEngine
        return MultilingualSpeechEngine.get_profile(target_lang)

    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Return general UI localization resource dictionary for all 11 supported languages."""
        return {
            "en": {
                "app_title": "AROVA AI Healthcare Assistant",
                "app_tagline": "Offline-First AI Healthcare Assistant for Rural Healthcare",
                "choose_language": "Choose Your Language",
                "start_voice": "🗣️ Start AROVA Voice Assistant",
                "step_patient": "Patient Details",
                "name_label": "Patient Name",
                "name_placeholder": "Enter full name...",
                "submit_name": "Submit Name",
                "age_label": "Patient Age",
                "age_placeholder": "Enter age (e.g. 42)...",
                "submit_age": "Submit Age",
                "step_symptoms": "Say or Type Symptoms",
                "symptoms_placeholder": "Example: weakness, tiredness, feeling dizzy or short of breath...",
                "submit_symptoms": "Submit Symptoms",
                "step_eyelid": "Lower Eyelid Photo Upload",
                "upload_warning": "Important: Please crop only the lower eyelid / conjunctiva area to ensure screening accuracy.",
                "upload_image": "Upload lower eyelid photo",
                "config_header": "CONFIGURATION",
                "use_llama": "Use Llama AI Summary (<5s)",
                "voice_reply": "Voice Reply Summary",
                "report_title": "📋 Clinical Screening Report",
                "report_ref": "REF: #AR-8291-AI",
                "gauge_title": "Hb-Test Priority Gauge",
                "priority_pending": "Pending",
                "priority_low": "LOW",
                "priority_medium": "MEDIUM",
                "priority_high": "HIGH",
                "wording_low": "No immediate hemoglobin blood test needed",
                "wording_medium": "Hemoglobin blood test suggested within 48 hours",
                "wording_high": "Immediate hemoglobin blood test strongly recommended",
                "care_title": "➕ Care & Nutrition Guidance",
                "disclaimer_title": "IMPORTANT SAFETY NOTES",
                "disclaimer_text": "This AI screening is NOT a final medical diagnosis. It does not replace a doctor's consultation. A clinical blood test (Hb-Test) is mandatory for confirmed medical evaluation.",
                "download_pdf": "📥 Download PDF Clinical Report",
                "error_name": "Please provide a valid name.",
                "error_age": "Please provide a valid age.",
                "error_image": "Please upload a clear lower eyelid photo.",
            },
            "hi": {
                "app_title": "अरोवा AI स्वास्थ्य सहायक",
                "app_tagline": "ग्रामीण स्वास्थ्य देखभाल के लिए ऑफलाइन-फर्स्ट AI स्वास्थ्य सहायक",
                "choose_language": "अपनी भाषा चुनें",
                "start_voice": "🗣️ AROVA की आवाज शुरू करें",
                "step_patient": "मरीज का विवरण",
                "name_label": "मरीज का नाम",
                "name_placeholder": "पूरा नाम दर्ज करें...",
                "submit_name": "नाम जमा करें",
                "age_label": "मरीज की उम्र",
                "age_placeholder": "उम्र दर्ज करें (उदा. 42)...",
                "submit_age": "उम्र जमा करें",
                "step_symptoms": "लक्षण बताएं या टाइप करें",
                "symptoms_placeholder": "उदाहरण: कमजोरी, थकान, चक्कर आना या सांस फूलना...",
                "submit_symptoms": "लक्षण जमा करें",
                "step_eyelid": "आँख के निचले हिस्से की फोटो अपलोड करें",
                "upload_warning": "महत्वपूर्ण: सटीक जांच के लिए केवल आँख के निचले हिस्से की फोटो अपलोड करें।",
                "upload_image": "निचली पलक की फोटो अपलोड करें",
                "config_header": "कॉन्फ़िगरेशन",
                "use_llama": "Llama AI सारांश का उपयोग करें (<5s)",
                "voice_reply": "आवाज में रिपोर्ट सारांश",
                "report_title": "📋 क्लीनिकल स्क्रीनिंग रिपोर्ट",
                "report_ref": "संदर्भ: #AR-8291-AI",
                "gauge_title": "हीमोग्लोबिन टेस्ट प्राथमिकता",
                "priority_pending": "लंबित",
                "priority_low": "कम (LOW)",
                "priority_medium": "मध्यम (MED)",
                "priority_high": "उच्च (HIGH)",
                "wording_low": "तत्काल हीमोग्लोबिन टेस्ट की आवश्यकता नहीं है",
                "wording_medium": "48 घंटे के भीतर हीमोग्लोबिन टेस्ट करवाने की सलाह दी जाती है",
                "wording_high": "तुरंत हीमोग्लोबिन टेस्ट करवाने की सख्त सलाह दी जाती है",
                "care_title": "➕ देखभाल और पोषण सलाह",
                "disclaimer_title": "महत्वपूर्ण सुरक्षा निर्देश",
                "disclaimer_text": "यह AI जांच कोई अंतिम चिकित्सीय निदान नहीं है। यह डॉक्टर की सलाह का विकल्प नहीं है। पुष्टि के लिए क्लीनिकल हीमोग्लोबिन ब्लड टेस्ट अनिवार्य है।",
                "download_pdf": "📥 पीडीएफ क्लीनिकल रिपोर्ट डाउनलोड करें",
                "error_name": "कृपया सही नाम दर्ज करें।",
                "error_age": "कृपया सही उम्र दर्ज करें।",
                "error_image": "कृपया आँख के निचले हिस्से की साफ फोटो अपलोड करें।",
            },
            "ur": {
                "app_title": "ارووا AI ہیلتھ کیئر اسسٹنٹ",
                "app_tagline": "دیہی صحت کی دیکھ بھال کے لیے آف لائن AI ہیلتھ اسسٹنٹ",
                "choose_language": "اپنی زبان کا انتخاب کریں",
                "start_voice": "🗣️ AROVA وائس شروع کریں",
                "step_patient": "مریض کی تفصیلات",
                "name_label": "مریض کا نام",
                "name_placeholder": "مکمل نام درج کریں...",
                "submit_name": "نام جمع کریں",
                "age_label": "مریض کی عمر",
                "age_placeholder": "عمر درج کریں...",
                "submit_age": "عمر جمع کریں",
                "step_symptoms": "علامات بتائیں",
                "symptoms_placeholder": "مثال: کمزوری، تھکاوٹ...",
                "submit_symptoms": "علامات جمع کریں",
                "step_eyelid": "آنکھ کے نچلے حصے کی تصویر",
                "upload_warning": "اہم: صرف آنکھ کے نچلے حصے کی تصویر اپ لوڈ کریں۔",
                "upload_image": "تصویر اپ لوڈ کریں",
                "config_header": "ترتیبات",
                "use_llama": "Llama AI خلاصہ استعمال کریں",
                "voice_reply": "وائس رپورٹ خلاصہ",
                "report_title": "📋 کلینیکل سکریننگ رپورٹ",
                "report_ref": "حوالہ: #AR-8291-AI",
                "gauge_title": "ہیموگلوبن ٹیسٹ ترجیح",
                "priority_pending": "زیر التواء",
                "priority_low": "کم (LOW)",
                "priority_medium": "درمیانہ (MED)",
                "priority_high": "زیادہ (HIGH)",
                "wording_low": "فوری بلڈ ٹیسٹ کی ضرورت نہیں ہے",
                "wording_medium": "48 گھنٹے کے اندر ہیموگلوبن ٹیسٹ کی سفارش کی جاتی ہے",
                "wording_high": "فوری طور پر ہیموگلوبن بلڈ ٹیسٹ کروائیں",
                "care_title": "➕ دیکھ بھال اور غذائی رہنمائی",
                "disclaimer_title": "اہم حفاظتی نوٹ",
                "disclaimer_text": "یہ AI سکریننگ حتمی طبی تشخیص نہیں ہے۔ تصدیق کے لیے لیبارٹری ٹیسٹ لازمی ہے۔",
                "download_pdf": "📥 PDF رپورٹ ڈاؤن لوڈ کریں",
                "error_name": "درست نام درج کریں۔",
                "error_age": "درست عمر درج کریں۔",
                "error_image": "تصویر اپ لوڈ کریں۔",
            },
            "bn": {
                "app_title": "আরোভা AI স্বাস্থ্য সহায়ক",
                "app_tagline": "গ্রামীণ স্বাস্থ্যের জন্য অফলাইন AI সহায়ক",
                "choose_language": "আপনার ভাষা বেছে নিন",
                "start_voice": "🗣️ AROVA ভয়েস শুরু করুন",
                "step_patient": "রোগীর তথ্য",
                "name_label": "রোগীর নাম",
                "name_placeholder": "পুরো নাম লিখুন...",
                "submit_name": "নাম জমা দিন",
                "age_label": "রোগীর বয়স",
                "age_placeholder": "বয়স লিখুন (যেমন ৪২)...",
                "submit_age": "বয়স জমা দিন",
                "step_symptoms": "উপসর্গ বলুন বা টাইপ করুন",
                "symptoms_placeholder": "উদাহরণ: দুর্বলতা, ক্লান্তি, মাথা ঘোরা...",
                "submit_symptoms": "উপসর্গ জমা দিন",
                "step_eyelid": "চোখের নিচের পাতার ছবি আপলোড",
                "upload_warning": "গুরুত্বপূর্ণ: সঠিক স্ক্রিনিংয়ের জন্য শুধু চোখের নিচের পাতার ছবি আপলোড করুন।",
                "upload_image": "নিচের পাতার ছবি আপলোড করুন",
                "config_header": "সেটিংস",
                "use_llama": "Llama AI সারাংশ ব্যবহার করুন",
                "voice_reply": "ভয়েস রিপোর্ট সারাংশ",
                "report_title": "📋 ক্লিনিক্যাল স্ক্রিনিং রিপোর্ট",
                "report_ref": "রেফ: #AR-8291-AI",
                "gauge_title": "হিমোগ্লোবিন টেস্ট অগ্রাধিকার",
                "priority_pending": "অপেক্ষমাণ",
                "priority_low": "কম (LOW)",
                "priority_medium": "মাঝারি (MED)",
                "priority_high": "উচ্চ (HIGH)",
                "wording_low": "তাৎক্ষণিক হিমোগ্লোবিন পরীক্ষার প্রয়োজন নেই",
                "wording_medium": "৪৮ ঘণ্টার মধ্যে হিমোগ্লোবিন পরীক্ষা করার পরামর্শ",
                "wording_high": "তাৎক্ষণিকভাবে হিমোগ্লোবিন পরীক্ষা করানো জরুরি",
                "care_title": "➕ যত্ন ও পুষ্টি পরামর্শ",
                "disclaimer_title": "গুরুত্বপূর্ণ নিরাপত্তা নোট",
                "disclaimer_text": "এটি কোনো চূড়ান্ত চিকিৎসা রোগনির্ণয় নয়। নিশ্চিতকরণের জন্য ক্লিনিক্যাল হিমোগ্লোবিন রক্ত পরীক্ষা আবশ্যক।",
                "download_pdf": "📥 PDF রিপোর্ট ডাউনলোড করুন",
                "error_name": "সঠিক নাম দিন।",
                "error_age": "সঠিক বয়স দিন।",
                "error_image": "চোখের নিচের পাতার পরিষ্কার ছবি আপলোড করুন।",
            },
            "mr": {
                "app_title": "अरोव्हा AI आरोग्य सहाय्यक",
                "app_tagline": "ग्रामीण आरोग्यासाठी ऑफलाइन AI सहाय्यक",
                "choose_language": "तुमची भाषा निवडा",
                "start_voice": "🗣️ AROVA व्हॉइस सुरू करा",
                "step_patient": "रुग्णाचा तपशील",
                "name_label": "रुग्णाचे नाव",
                "name_placeholder": "पूर्ण नाव टाका...",
                "submit_name": "नाव सबमिट करा",
                "age_label": "रुग्णाचे वय",
                "age_placeholder": "वय टाका (उदा. ४२)...",
                "submit_age": "वय सबमिट करा",
                "step_symptoms": "लक्षणे सांगा किंवा टाइप करा",
                "symptoms_placeholder": "उदाहरण: अशक्तपणा, थकवा, चक्कर येणे...",
                "submit_symptoms": "लक्षणे सबमिट करा",
                "step_eyelid": "डोळ्याच्या खालच्या भागाचा फोटो अपलोड करा",
                "upload_warning": "महत्त्वाचे: फक्त खालच्या पापणीचा फोटो अपलोड करा.",
                "upload_image": "खालच्या पापणीचा फोटो अपलोड करा",
                "config_header": "सेटिंग्ज",
                "use_llama": "Llama AI सारांश वापरा",
                "voice_reply": "व्हॉइस रिपोर्ट सारांश",
                "report_title": "📋 क्लिनिकल स्क्रीनिंग अहवाल",
                "report_ref": "संदर्भ: #AR-8291-AI",
                "gauge_title": "हिमोग्लोबिन चाचणी प्राधान्य",
                "priority_pending": "प्रलंबित",
                "priority_low": "कमी (LOW)",
                "priority_medium": "मध्यम (MED)",
                "priority_high": "उच्च (HIGH)",
                "wording_low": "तात्काळ हिमोग्लोबिन चाचणीची गरज नाही",
                "wording_medium": "४८ तासांत हिमोग्लोबिन चाचणी करून घ्या",
                "wording_high": "तात्काळ हिमोग्लोबिन चाचणी करणे अत्यंत महत्त्वाचे",
                "care_title": "➕ काळजी व पोषण मार्गदर्शन",
                "disclaimer_title": "महत्त्वाचे सुरक्षा नोट्स",
                "disclaimer_text": "ही AI तपासणी अंतिम वैद्यकीय निदान नाही. खात्रीसाठी क्लिनिकल हिमोग्लोबिन रक्त चाचणी अनिवार्य आहे.",
                "download_pdf": "📥 PDF अहवाल डाउनलोड करा",
                "error_name": "योग्य नाव टाका.",
                "error_age": "योग्य वय टाका.",
                "error_image": "डोळ्याच्या खालच्या भागाचा स्पष्ट फोटो अपलोड करा.",
            },
            "ta": {
                "app_title": "அரோவா AI சுகாதார உதவியாளர்",
                "app_tagline": "கிராமப்புற சுகாதாரத்திற்கான ஆஃப்லைன் AI உதவியாளர்",
                "choose_language": "உங்கள் மொழியைத் தேர்வுசெய்யவும்",
                "start_voice": "🗣️ AROVA குரல் தொடங்கவும்",
                "step_patient": "நோயாளி விவரங்கள்",
                "name_label": "நோயாளி பெயர்",
                "name_placeholder": "முழு பெயர் உள்ளிடவும்...",
                "submit_name": "பெயர் சமர்ப்பிக்கவும்",
                "age_label": "நோயாளி வயது",
                "age_placeholder": "வயது உள்ளிடவும் (எ.கா. 42)...",
                "submit_age": "வயது சமர்ப்பிக்கவும்",
                "step_symptoms": "அறிகுறிகளைச் சொல்லுங்கள்",
                "symptoms_placeholder": "உதாரணம்: பலவீனம், சோர்வு, தலைச்சுற்றல்...",
                "submit_symptoms": "அறிகுறிகள் சமர்ப்பிக்கவும்",
                "step_eyelid": "கீழ் இமை புகைப்படம் பதிவேற்றம்",
                "upload_warning": "முக்கியம்: துல்லியமான பரிசோதனைக்கு கீழ் இமையின் புகைப்படத்தை மட்டும் பதிவேற்றவும்.",
                "upload_image": "கீழ் இமை புகைப்படம் பதிவேற்றவும்",
                "config_header": "அமைப்புகள்",
                "use_llama": "Llama AI சுருக்கம் பயன்படுத்தவும்",
                "voice_reply": "குரல் அறிக்கை சுருக்கம்",
                "report_title": "📋 மருத்துவ பரிசோதனை அறிக்கை",
                "report_ref": "குறிப்பு: #AR-8291-AI",
                "gauge_title": "ஹீமோகுளோபின் பரிசோதனை முன்னுரிமை",
                "priority_pending": "நிலுவையில்",
                "priority_low": "குறைவு (LOW)",
                "priority_medium": "நடுத்தரம் (MED)",
                "priority_high": "அதிகம் (HIGH)",
                "wording_low": "உடனடி ஹீமோகுளோபின் பரிசோதனை தேவையில்லை",
                "wording_medium": "48 மணி நேரத்தில் ஹீமோகுளோபின் பரிசோதனை பரிந்துரைக்கப்படுகிறது",
                "wording_high": "உடனடியாக ஹீமோகுளோபின் பரிசோதனை செய்வது மிக முக்கியம்",
                "care_title": "➕ பராமரிப்பு & ஊட்டச்சத்து வழிகாட்டல்",
                "disclaimer_title": "முக்கிய பாதுகாப்பு குறிப்புகள்",
                "disclaimer_text": "இது இறுதி மருத்துவ நோயறிதல் அல்ல. உறுதிப்படுத்த மருத்துவ ஹீமோகுளோபின் இரத்தப் பரிசோதனை கட்டாயம்.",
                "download_pdf": "📥 PDF அறிக்கை பதிவிறக்கம்",
                "error_name": "சரியான பெயர் கொடுக்கவும்.",
                "error_age": "சரியான வயது கொடுக்கவும்.",
                "error_image": "கீழ் இமையின் தெளிவான புகைப்படத்தைப் பதிவேற்றவும்.",
            },
            "te": {
                "app_title": "అరోవా AI ఆరోగ్య సహాయకం",
                "app_tagline": "గ్రామీణ ఆరోగ్యానికి ఆఫ్‌లైన్ AI సహాయకం",
                "choose_language": "మీ భాషను ఎంచుకోండి",
                "start_voice": "🗣️ AROVA వాయిస్ ప్రారంభించండి",
                "step_patient": "రోగి వివరాలు",
                "name_label": "రోగి పేరు",
                "name_placeholder": "పూర్తి పేరు నమోదు చేయండి...",
                "submit_name": "పేరు సమర్పించండి",
                "age_label": "రోగి వయస్సు",
                "age_placeholder": "వయస్సు నమోదు చేయండి (ఉదా. 42)...",
                "submit_age": "వయస్సు సమర్పించండి",
                "step_symptoms": "లక్షణాలు చెప్పండి లేదా టైప్ చేయండి",
                "symptoms_placeholder": "ఉదాహరణ: బలహీనత, అలసట, తలతిరగడం...",
                "submit_symptoms": "లక్షణాలు సమర్పించండి",
                "step_eyelid": "కంటి కింది రెప్ప ఫోటో అప్‌లోడ్",
                "upload_warning": "ముఖ్యం: సరైన స్క్రీనింగ్ కోసం కంటి కింది రెప్ప ఫోటో మాత్రమే అప్‌లోడ్ చేయండి.",
                "upload_image": "కింది రెప్ప ఫోటో అప్‌లోడ్ చేయండి",
                "config_header": "సెట్టింగ్‌లు",
                "use_llama": "Llama AI సారాంశం వాడండి",
                "voice_reply": "వాయిస్ రిపోర్ట్ సారాంశం",
                "report_title": "📋 క్లినికల్ స్క్రీనింగ్ నివేదిక",
                "report_ref": "సూచన: #AR-8291-AI",
                "gauge_title": "హిమోగ్లోబిన్ టెస్ట్ ప్రాధాన్యత",
                "priority_pending": "పెండింగ్",
                "priority_low": "తక్కువ (LOW)",
                "priority_medium": "మధ్యస్థం (MED)",
                "priority_high": "ఎక్కువ (HIGH)",
                "wording_low": "తక్షణ హిమోగ్లోబిన్ టెస్ట్ అవసరం లేదు",
                "wording_medium": "48 గంటల్లో హిమోగ్లోబిన్ టెస్ట్ చేయించాలని సిఫార్సు",
                "wording_high": "వెంటనే హిమోగ్లోబిన్ టెస్ట్ చేయించడం చాలా ముఖ్యం",
                "care_title": "➕ సంరక్షణ & పోషణ మార్గదర్శకత్వం",
                "disclaimer_title": "ముఖ్యమైన భద్రతా గమనికలు",
                "disclaimer_text": "ఇది తుది వైద్య నిర్ధారణ కాదు. నిర్ధారణ కోసం క్లినికల్ హిమోగ్లోబిన్ రక్త పరీక్ష తప్పనిసరి.",
                "download_pdf": "📥 PDF నివేదిక డౌన్‌లోడ్",
                "error_name": "సరైన పేరు ఇవ్వండి.",
                "error_age": "సరైన వయస్సు ఇవ్వండి.",
                "error_image": "కంటి కింది రెప్ప స్పష్టమైన ఫోటో అప్‌లోడ్ చేయండి.",
            },
            "gu": {
                "app_title": "અરોવા AI આરોગ્ય સહાયક",
                "app_tagline": "ગ્રામીણ આરોગ્ય માટે ઑફલાઇન AI સહાયક",
                "choose_language": "તમારી ભાષા પસંદ કરો",
                "start_voice": "🗣️ AROVA વૉઇસ શરૂ કરો",
                "step_patient": "દર્દીની વિગતો",
                "name_label": "દર્દીનું નામ",
                "name_placeholder": "પૂરું નામ દાખલ કરો...",
                "submit_name": "નામ સબમિટ કરો",
                "age_label": "દર્દીની ઉંમર",
                "age_placeholder": "ઉંમર દાખલ કરો (દા.ત. ૪૨)...",
                "submit_age": "ઉંમર સબમિટ કરો",
                "step_symptoms": "લક્ષણો જણાવો અથવા ટાઇપ કરો",
                "symptoms_placeholder": "ઉદાહરણ: નબળાઈ, થાક, ચક્કર આવવા...",
                "submit_symptoms": "લક્ષણો સબમિટ કરો",
                "step_eyelid": "આંખના નીચેના ભાગનો ફોટો અપલોડ",
                "upload_warning": "મહત્વપૂર્ણ: ચોક્કસ સ્ક્રીનિંગ માટે ફક્ત નીચેની પાંપણનો ફોટો અપલોડ કરો.",
                "upload_image": "નીચેની પાંપણનો ફોટો અપલોડ કરો",
                "config_header": "સેટિંગ્સ",
                "use_llama": "Llama AI સારાંશ વાપરો",
                "voice_reply": "વૉઇસ રિપોર્ટ સારાંશ",
                "report_title": "📋 ક્લિનિકલ સ્ક્રીનિંગ રિપોર્ટ",
                "report_ref": "સંદર્ભ: #AR-8291-AI",
                "gauge_title": "હિમોગ્લોબિન ટેસ્ટ પ્રાથમિકતા",
                "priority_pending": "પ્રલંબિત",
                "priority_low": "ઓછી (LOW)",
                "priority_medium": "મધ્યમ (MED)",
                "priority_high": "ઉચ્ચ (HIGH)",
                "wording_low": "તાત્કાલિક હિમોગ્લોબિન ટેસ્ટ જરૂરી નથી",
                "wording_medium": "૪૮ કલાકમાં હિમોગ્લોબિન ટેસ્ટ કરાવવાની સલાહ",
                "wording_high": "તાત્કાલિક હિમોગ્લોબિન ટેસ્ટ કરાવવું ખૂબ જ મહત્વનું",
                "care_title": "➕ સંભાળ અને પોષણ માર્ગદર્શન",
                "disclaimer_title": "મહત્વપૂર્ણ સુરક્ષા નોંધો",
                "disclaimer_text": "આ AI સ્ક્રીનિંગ અંતિમ તબીબી નિદાન નથી. ખાતરી માટે ક્લિનિકલ હિમોગ્લોબિન રક્ત ટેસ્ટ ફરજિયાત છે.",
                "download_pdf": "📥 PDF રિપોર્ટ ડાઉનલોડ કરો",
                "error_name": "યોગ્ય નામ દાખલ કરો.",
                "error_age": "યોગ્ય ઉંમર દાખલ કરો.",
                "error_image": "આંખના નીચેના ભાગનો સ્પષ્ટ ફોટો અપલોડ કરો.",
            },
            "kn": {
                "app_title": "ಅರೋವಾ AI ಆರೋಗ್ಯ ಸಹಾಯಕ",
                "app_tagline": "ಗ್ರಾಮೀಣ ಆರೋಗ್ಯಕ್ಕಾಗಿ ಆಫ್‌ಲೈನ್ AI ಸಹಾಯಕ",
                "choose_language": "ನಿಮ್ಮ ಭಾಷೆ ಆಯ್ಕೆಮಾಡಿ",
                "start_voice": "🗣️ AROVA ವಾಯ್ಸ್ ಪ್ರಾರಂಭಿಸಿ",
                "step_patient": "ರೋಗಿಯ ವಿವರಗಳು",
                "name_label": "ರೋಗಿಯ ಹೆಸರು",
                "name_placeholder": "ಪೂರ್ಣ ಹೆಸರು ನಮೂದಿಸಿ...",
                "submit_name": "ಹೆಸರು ಸಲ್ಲಿಸಿ",
                "age_label": "ರೋಗಿಯ ವಯಸ್ಸು",
                "age_placeholder": "ವಯಸ್ಸು ನಮೂದಿಸಿ (ಉದಾ. ೪೨)...",
                "submit_age": "ವಯಸ್ಸು ಸಲ್ಲಿಸಿ",
                "step_symptoms": "ಲಕ್ಷಣಗಳನ್ನು ಹೇಳಿ ಅಥವಾ ಟೈಪ್ ಮಾಡಿ",
                "symptoms_placeholder": "ಉದಾಹರಣೆ: ದೌರ್ಬಲ್ಯ, ಬಳಲಿಕೆ, ತಲೆತಿರುಗುವಿಕೆ...",
                "submit_symptoms": "ಲಕ್ಷಣಗಳನ್ನು ಸಲ್ಲಿಸಿ",
                "step_eyelid": "ಕಣ್ಣಿನ ಕೆಳಭಾಗದ ಫೋಟೋ ಅಪ್‌ಲೋಡ್",
                "upload_warning": "ಮುಖ್ಯ: ನಿಖರ ಪರೀಕ್ಷೆಗಾಗಿ ಕಣ್ಣಿನ ಕೆಳರೆಪ್ಪೆಯ ಫೋಟೋ ಮಾತ್ರ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.",
                "upload_image": "ಕೆಳರೆಪ್ಪೆಯ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
                "config_header": "ಸೆಟ್ಟಿಂಗ್‌ಗಳು",
                "use_llama": "Llama AI ಸಾರಾಂಶ ಬಳಸಿ",
                "voice_reply": "ವಾಯ್ಸ್ ವರದಿ ಸಾರಾಂಶ",
                "report_title": "📋 ಕ್ಲಿನಿಕಲ್ ಸ್ಕ್ರೀನಿಂಗ್ ವರದಿ",
                "report_ref": "ಉಲ್ಲೇಖ: #AR-8291-AI",
                "gauge_title": "ಹಿಮೋಗ್ಲೋಬಿನ್ ಪರೀಕ್ಷೆ ಆದ್ಯತೆ",
                "priority_pending": "ಬಾಕಿ",
                "priority_low": "ಕಡಿಮೆ (LOW)",
                "priority_medium": "ಮಧ್ಯಮ (MED)",
                "priority_high": "ಹೆಚ್ಚು (HIGH)",
                "wording_low": "ತಕ್ಷಣದ ಹಿಮೋಗ್ಲೋಬಿನ್ ಪರೀಕ್ಷೆ ಅಗತ್ಯವಿಲ್ಲ",
                "wording_medium": "೪೮ ಗಂಟೆಗಳಲ್ಲಿ ಹಿಮೋಗ್ಲೋಬಿನ್ ಪರೀಕ್ಷೆ ಮಾಡಿಸಿ",
                "wording_high": "ತಕ್ಷಣ ಹಿಮೋಗ್ಲೋಬಿನ್ ಪರೀಕ್ಷೆ ಮಾಡಿಸುವುದು ಅತ್ಯಂತ ಮುಖ್ಯ",
                "care_title": "➕ ಆರೈಕೆ ಮತ್ತು ಪೌಷ್ಟಿಕ ಮಾರ್ಗದರ್ಶನ",
                "disclaimer_title": "ಮುಖ್ಯ ಸುರಕ್ಷತಾ ಟಿಪ್ಪಣಿಗಳು",
                "disclaimer_text": "ಇದು ಅಂತಿಮ ವೈದ್ಯಕೀಯ ರೋಗನಿರ್ಣಯವಲ್ಲ. ದೃಢೀಕರಣಕ್ಕಾಗಿ ಕ್ಲಿನಿಕಲ್ ಹಿಮೋಗ್ಲೋಬಿನ್ ರಕ್ತ ಪರೀಕ್ಷೆ ಕಡ್ಡಾಯ.",
                "download_pdf": "📥 PDF ವರದಿ ಡೌನ್‌ಲೋಡ್",
                "error_name": "ಸರಿಯಾದ ಹೆಸರು ನೀಡಿ.",
                "error_age": "ಸರಿಯಾದ ವಯಸ್ಸು ನೀಡಿ.",
                "error_image": "ಕಣ್ಣಿನ ಕೆಳಭಾಗದ ಸ್ಪಷ್ಟ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.",
            },
            "ml": {
                "app_title": "അരോവ AI ആരോഗ്യ സഹായി",
                "app_tagline": "ഗ്രാമീണ ആരോഗ്യത്തിനായി ഓഫ്‌ലൈൻ AI സഹായി",
                "choose_language": "നിങ്ങളുടെ ഭാഷ തിരഞ്ഞെടുക്കുക",
                "start_voice": "🗣️ AROVA വോയ്‌സ് ആരംഭിക്കുക",
                "step_patient": "രോഗിയുടെ വിവരങ്ങൾ",
                "name_label": "രോഗിയുടെ പേര്",
                "name_placeholder": "മുഴുവൻ പേര് നൽകുക...",
                "submit_name": "പേര് സമർപ്പിക്കുക",
                "age_label": "രോഗിയുടെ വയസ്സ്",
                "age_placeholder": "വയസ്സ് നൽകുക (ഉദാ. 42)...",
                "submit_age": "വയസ്സ് സമർപ്പിക്കുക",
                "step_symptoms": "ലക്ഷണങ്ങൾ പറയുക അല്ലെങ്കിൽ ടൈപ്പ് ചെയ്യുക",
                "symptoms_placeholder": "ഉദാഹരണം: ബലഹീനത, ക്ഷീണം, തലകറക്കം...",
                "submit_symptoms": "ലക്ഷണങ്ങൾ സമർപ്പിക്കുക",
                "step_eyelid": "കണ്ണിന്റെ താഴത്തെ ഭാഗം ഫോട്ടോ അപ്‌ലോഡ്",
                "upload_warning": "പ്രധാനം: കൃത്യമായ സ്ക്രീനിംഗിന് കണ്ണിന്റെ താഴത്തെ ഭാഗത്തിന്റെ ഫോട്ടോ മാത്രം അപ്‌ലോഡ് ചെയ്യുക.",
                "upload_image": "താഴത്തെ കൺപോളയുടെ ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുക",
                "config_header": "ക്രമീകരണങ്ങൾ",
                "use_llama": "Llama AI സംഗ്രഹം ഉപയോഗിക്കുക",
                "voice_reply": "വോയ്‌സ് റിപ്പോർട്ട് സംഗ്രഹം",
                "report_title": "📋 ക്ലിനിക്കൽ സ്ക്രീനിംഗ് റിപ്പോർട്ട്",
                "report_ref": "റഫറൻസ്: #AR-8291-AI",
                "gauge_title": "ഹീമോഗ്ലോബിൻ ടെസ്റ്റ് മുൻഗണന",
                "priority_pending": "തീർപ്പാകാത്ത",
                "priority_low": "കുറവ് (LOW)",
                "priority_medium": "മധ്യമം (MED)",
                "priority_high": "ഉയർന്നത് (HIGH)",
                "wording_low": "ഉടൻ ഹീമോഗ്ലോബിൻ ടെസ്റ്റ് ആവശ്യമില്ല",
                "wording_medium": "48 മണിക്കൂറിനുള്ളിൽ ഹീമോഗ്ലോബിൻ ടെസ്റ്റ് ശുപാർശ ചെയ്യുന്നു",
                "wording_high": "ഉടൻ ഹീമോഗ്ലോബിൻ ടെസ്റ്റ് നടത്തേണ്ടത് വളരെ പ്രധാനം",
                "care_title": "➕ പരിചരണ & പോഷകാഹാര മാർഗ്ഗനിർദ്ദേശം",
                "disclaimer_title": "പ്രധാന സുരക്ഷാ കുറിപ്പുകൾ",
                "disclaimer_text": "ഈ AI സ്ക്രീനിംഗ് അന്തിമ രോഗനിർണയമല്ല. സ്ഥിരീകരണത്തിന് ക്ലിനിക്കൽ ഹീമോഗ്ലോബിൻ രക്തപരിശോധന നിർബന്ധമാണ്.",
                "download_pdf": "📥 PDF റിപ്പോർട്ട് ഡൗൺലോഡ്",
                "error_name": "ശരിയായ പേര് നൽകുക.",
                "error_age": "ശരിയായ വയസ്സ് നൽകുക.",
                "error_image": "കണ്ണിന്റെ താഴത്തെ ഭാഗത്തിന്റെ വ്യക്തമായ ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുക.",
            },
            "pa": {
                "app_title": "ਅਰੋਵਾ AI ਸਿਹਤ ਸਹਾਇਕ",
                "app_tagline": "ਪੇਂਡੂ ਸਿਹਤ ਲਈ ਆਫਲਾਈਨ AI ਸਹਾਇਕ",
                "choose_language": "ਆਪਣੀ ਭਾਸ਼ਾ ਚੁਣੋ",
                "start_voice": "🗣️ AROVA ਵੌਇਸ ਸ਼ੁਰੂ ਕਰੋ",
                "step_patient": "ਮਰੀਜ਼ ਦੇ ਵੇਰਵੇ",
                "name_label": "ਮਰੀਜ਼ ਦਾ ਨਾਮ",
                "name_placeholder": "ਪੂਰਾ ਨਾਮ ਦਰਜ ਕਰੋ...",
                "submit_name": "ਨਾਮ ਜਮ੍ਹਾ ਕਰੋ",
                "age_label": "ਮਰੀਜ਼ ਦੀ ਉਮਰ",
                "age_placeholder": "ਉਮਰ ਦਰਜ ਕਰੋ (ਜਿਵੇਂ ੪੨)...",
                "submit_age": "ਉਮਰ ਜਮ੍ਹਾ ਕਰੋ",
                "step_symptoms": "ਲੱਛਣ ਦੱਸੋ ਜਾਂ ਟਾਈਪ ਕਰੋ",
                "symptoms_placeholder": "ਉਦਾਹਰਣ: ਕਮਜ਼ੋਰੀ, ਥਕਾਵਟ, ਚੱਕਰ ਆਉਣਾ...",
                "submit_symptoms": "ਲੱਛਣ ਜਮ੍ਹਾ ਕਰੋ",
                "step_eyelid": "ਅੱਖ ਦੇ ਹੇਠਲੇ ਹਿੱਸੇ ਦੀ ਫੋਟੋ ਅੱਪਲੋਡ",
                "upload_warning": "ਜ਼ਰੂਰੀ: ਸਹੀ ਸਕ੍ਰੀਨਿੰਗ ਲਈ ਸਿਰਫ਼ ਹੇਠਲੀ ਪਲਕ ਦੀ ਫੋਟੋ ਅੱਪਲੋਡ ਕਰੋ।",
                "upload_image": "ਹੇਠਲੀ ਪਲਕ ਦੀ ਫੋਟੋ ਅੱਪਲੋਡ ਕਰੋ",
                "config_header": "ਸੈਟਿੰਗਜ਼",
                "use_llama": "Llama AI ਸਾਰ ਵਰਤੋ",
                "voice_reply": "ਵੌਇਸ ਰਿਪੋਰਟ ਸਾਰ",
                "report_title": "📋 ਕਲੀਨਿਕਲ ਸਕ੍ਰੀਨਿੰਗ ਰਿਪੋਰਟ",
                "report_ref": "ਹਵਾਲਾ: #AR-8291-AI",
                "gauge_title": "ਹੀਮੋਗਲੋਬਿਨ ਟੈਸਟ ਤਰਜੀਹ",
                "priority_pending": "ਬਕਾਇਆ",
                "priority_low": "ਘੱਟ (LOW)",
                "priority_medium": "ਮੱਧਮ (MED)",
                "priority_high": "ਜ਼ਿਆਦਾ (HIGH)",
                "wording_low": "ਤੁਰੰਤ ਹੀਮੋਗਲੋਬਿਨ ਟੈਸਟ ਦੀ ਲੋੜ ਨਹੀਂ",
                "wording_medium": "੪੮ ਘੰਟਿਆਂ ਵਿੱਚ ਹੀਮੋਗਲੋਬਿਨ ਟੈਸਟ ਕਰਵਾਉਣ ਦੀ ਸਲਾਹ",
                "wording_high": "ਤੁਰੰਤ ਹੀਮੋਗਲੋਬਿਨ ਟੈਸਟ ਕਰਵਾਉਣਾ ਬਹੁਤ ਜ਼ਰੂਰੀ",
                "care_title": "➕ ਦੇਖਭਾਲ ਅਤੇ ਪੋਸ਼ਣ ਮਾਰਗਦਰਸ਼ਨ",
                "disclaimer_title": "ਜ਼ਰੂਰੀ ਸੁਰੱਖਿਆ ਨੋਟ",
                "disclaimer_text": "ਇਹ AI ਸਕ੍ਰੀਨਿੰਗ ਅੰਤਿਮ ਡਾਕਟਰੀ ਤਸ਼ਖ਼ੀਸ ਨਹੀਂ ਹੈ। ਪੁਸ਼ਟੀ ਲਈ ਕਲੀਨਿਕਲ ਹੀਮੋਗਲੋਬਿਨ ਖ਼ੂਨ ਟੈਸਟ ਜ਼ਰੂਰੀ ਹੈ।",
                "download_pdf": "📥 PDF ਰਿਪੋਰਟ ਡਾਊਨਲੋਡ ਕਰੋ",
                "error_name": "ਸਹੀ ਨਾਮ ਦਰਜ ਕਰੋ।",
                "error_age": "ਸਹੀ ਉਮਰ ਦਰਜ ਕਰੋ।",
                "error_image": "ਅੱਖ ਦੇ ਹੇਠਲੇ ਹਿੱਸੇ ਦੀ ਸਾਫ਼ ਫੋਟੋ ਅੱਪਲੋਡ ਕਰੋ।",
            },
        }

    def __repr__(self) -> str:
        return f"LanguageService(active_lang='{self._current_language}')"
