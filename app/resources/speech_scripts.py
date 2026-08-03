# app/resources/speech_scripts.py
"""
AROVA Speech Scripts & Prompt Catalog

This single file contains all spoken voice scripts and UI display prompts for all 11 supported languages.

All spoken voice prompts ('_voice' keys) use natural punctuation (commas, periods)
to ensure Kokoro TTS synthesizes soft, calm, crystal-clear speech with natural pauses.

Supported Languages:
- en: English
- hi: Hindi (हिन्दी)
- ur: Urdu (اردو)
- bn: Bengali (বাংলা)
- mr: Marathi (मराठी)
- ta: Tamil (தமிழ்)
- te: Telugu (తెలుగు)
- gu: Gujarati (ગુજરાતી)
- kn: Kannada (ಕನ್ನಡ)
- ml: Malayalam (മലയാളം)
- pa: Punjabi (ਪੰਜਾਬੀ)
"""

SPEECH_SCRIPTS = {
    # 🇬🇧 ENGLISH
    "en": {
        "welcome_voice": "Hello, welcome to AROVA. I am here to help you with your health screening today. Whenever you are ready, please tell me your name.",
        "welcome_text": "💬 AROVA: Hello. Welcome to AROVA. I am here to help you with your health screening today. Whenever you are ready, please tell me your name.",
        "ask_name_voice": "Thank you, whenever you are ready, please tell me your name.",
        "ask_age_voice": "Thank you {name}, please tell me your age.",
        "ask_symptoms_voice": "Thank you, please tell me if you are feeling any symptoms, such as weakness, dizziness, or tiredness.",
        "ask_image_voice": "Thank you, symptoms recorded. Whenever you are ready, please upload a clear photo of your lower eyelid.",
        "processing_voice": "Please wait, preparing your screening report.",
        "processing_text": "💬 AROVA: Analyzing eyelid image and symptom inputs. Please wait...",
        "report_spoken_summary": "AROVA screening completed for {name}. Your hemoglobin test priority is {priority}. A clinical blood test is recommended for confirmation.",
    },

    # 🇮🇳 HINDI (हिन्दी)
    "hi": {
        "welcome_voice": "नमस्ते, मैं अरोवा हूँ. आपका स्वागत है. मैं आपकी स्वास्थ्य जांच में मदद करने के लिए यहाँ हूँ. कृपया अपना नाम बताएं.",
        "welcome_text": "💬 AROVA: नमस्ते। मैं अरोवा हूँ। आपका स्वागत है। मैं आपकी स्वास्थ्य जांच में मदद करने के लिए यहाँ हूँ। कृपया अपना नाम बताएं।",
        "ask_name_voice": "धन्यवाद, कृपया अपना नाम बताएं.",
        "ask_age_voice": "धन्यवाद {name} जी, कृपया अपनी उम्र बताएं.",
        "ask_symptoms_voice": "धन्यवाद, अब अपने लक्षण बताएं, जैसे कमजोरी, चक्कर आना, या थकान.",
        "ask_image_voice": "लक्षण नोट कर लिए गए हैं, अब अपनी निचली पलक की साफ फोटो अपलोड करें.",
        "processing_voice": "कृपया प्रतीक्षा करें, मैं आपकी रिपोर्ट तैयार कर रही हूँ.",
        "processing_text": "💬 AROVA: फोटो और लक्षणों का विश्लेषण किया जा रहा है। कृपया थोड़ा इंतजार करें...",
        "report_spoken_summary": "AROVA {name} जी, आपकी स्क्रीनिंग पूरी हो गई है. आपकी हीमोग्लोबिन टेस्ट प्राथमिकता {priority} है. पुष्टि के लिए ब्लड टेस्ट करवाएं.",
    },

    # 🇮🇳 URDU (اردو)
    "ur": {
        "welcome_voice": "नमस्ते, मैं अरोवा हूँ. आपका स्वागत है. मैं आपकी सेहत की सहायता के लिए यहाँ हूँ. बराह-ए-करम अपना नाम बताएं.",
        "welcome_text": "💬 AROVA: سلام। میں AROVA ہوں۔ آپ کا استقبال ہے۔ میں آپ کی صحت کی معاونت کے لیے یہاں ہوں۔ براہ کرم اپنا نام بتائیں۔",
        "ask_name_voice": "शुक्रिया, बराह-ए-करम अपना नाम बताएं.",
        "ask_age_voice": "शुक्रिया {name} जी, बराह-ए-करम अपनी उम्र बताएं.",
        "ask_symptoms_voice": "शुक्रिया, अब अपनी अलामात बताएं, जैसे कमज़ोरी, चक्कर आना, या थकान.",
        "ask_image_voice": "अलामात दर्ज कर ली गई हैं, अब अपनी निचली पलक की साफ तस्वीर अपलोड करें.",
        "processing_voice": "बराह-ए-करम इंतजार करें, आपकी रिपोर्ट तैयार की जा रही है.",
        "processing_text": "💬 AROVA: تجزئیہ جاری ہے...",
        "report_spoken_summary": "AROVA {name} जी, आपकी स्क्रीनिंग मुकम्मल हो गई है. आपकी हीमोग्लोबिन टेस्ट प्राथमिकता {priority} है.",
    },

    # 🇧🇩 BENGALI (বাংলা)
    "bn": {
        "welcome_voice": "হ্যালো, আমি আরোভা. আপনাকে স্বাগতম. আমি আপনার স্বাস্থ্য সহায়তার জন্য এখানে আছি. দয়া করে আপনার নাম বলুন.",
        "welcome_text": "💬 AROVA: হ্যালো। আমি আরোভা। আপনাকে স্বাগতম। আমি আপনার স্বাস্থ্য সহায়তার জন্য এখানে আছি। দয়া করে আপনার নাম বলুন।",
        "ask_name_voice": "ধন্যবাদ, দয়া করে আপনার নাম বলুন.",
        "ask_age_voice": "ধন্যবাদ {name}, দয়া করে আপনার বয়স বলুন.",
        "ask_symptoms_voice": "ধন্যবাদ, এবার আপনার লক্ষণসমূহ বলুন, যেমন দুর্বলতা বা মাথা ঘোরা.",
        "ask_image_voice": "লক্ষণসমূহ নোট করা হয়েছে, এবার চোখের নিচের অংশের পরিষ্কার ছবি আপলোড করুন.",
        "processing_voice": "দয়া করে অপেক্ষা করুন, আপনার রিপোর্ট তৈরি করা হচ্ছে.",
        "processing_text": "💬 AROVA: পরীক্ষা চলছে। দয়া করে অপেক্ষা করুন...",
        "report_spoken_summary": "AROVA {name}, আপনার স্ক্রিনিং সম্পন্ন হয়েছে. আপনার হিমোগ্লোবিন পরীক্ষার অগ্রাধিকার {priority}.",
    },

    # 🇮🇳 MARATHI (मराठी)
    "mr": {
        "welcome_voice": "नमस्कार, मी अरोव्हा आहे. आपले स्वागत आहे. मी आपल्या आरोग्य मदतीसाठी येथे आहे. कृपया आपले नाव सांगा.",
        "welcome_text": "💬 AROVA: नमस्कार. मी अरोव्हा आहे. आपले स्वागत आहे. मी आपल्या आरोग्य मदतीसाठी येथे आहे. कृपया आपले नाव सांगा.",
        "ask_name_voice": "धन्यवाद, कृपया आपले नाव सांगा.",
        "ask_age_voice": "धन्यवाद {name}, कृपया आपले वय सांगा.",
        "ask_symptoms_voice": "धन्यवाद, आता आपली लक्षणे सांगा.",
        "ask_image_voice": "लक्षणे नोंदवली गेली आहेत, डोळ्याच्या खालच्या भागाचा फोटो अपलोड करा.",
        "processing_voice": "कृपया प्रतीक्षा करा, तुमचा अहवाल तयार केला जात आहे.",
        "processing_text": "💬 AROVA: विश्लेषणाचे काम सुरू आहे...",
        "report_spoken_summary": "AROVA {name}, तुमची स्क्रीन चाचणी पूर्ण झाली आहे.",
    },

    # 🇮🇳 TAMIL (தமிழ்)
    "ta": {
        "welcome_voice": "வணக்கம், நான் அரோவா. உங்களை வரவேற்கிறேன். உங்கள் சுகாதார பரிசோதனைக்கு உதவ நான் தயார். உங்கள் பெயரைச் சொல்லுங்கள்.",
        "welcome_text": "💬 AROVA: வணக்கம். நான் அரோவா. உங்களை வரவேற்கிறேன். உங்கள் சுகாதார பரிசோதனைக்கு உதவ நான் தயார். உங்கள் பெயரைச் சொல்லுங்கள்.",
        "ask_name_voice": "நன்றி, உங்கள் பெயரைச் சொல்லுங்கள்.",
        "ask_age_voice": "நன்றி {name}, உங்கள் வயதைச் சொல்லுங்கள்.",
        "ask_symptoms_voice": "நன்றி, உங்கள் அறிகுறிகளைச் சொல்லுங்கள்.",
        "ask_image_voice": "அறிகுறிகள் பதிவு செய்யப்பட்டன, புகைப்படத்தைப் பதிவேற்றவும்.",
        "processing_voice": "தயவுசெய்து காத்திருக்கவும், அறிக்கை தயாராகிறது.",
        "processing_text": "💬 AROVA: பரிசோதனை நடைபெறுகிறது...",
        "report_spoken_summary": "AROVA {name}, பரிசோதனை முடிந்தது.",
    },

    # 🇮🇳 TELUGU (తెలుగు)
    "te": {
        "welcome_voice": "నమస్కారం, నేను అరోవా. మీకు స్వాగతం. మీ ఆరోగ్య సహాయం కోసం నేను ఇక్కడ ఉన్నాను. దయచేసి మీ పేరు చెప్పండి.",
        "welcome_text": "💬 AROVA: నమస్కారం. నేను అరోవా. మీకు స్వాగతం. మీ ఆరోగ్య సహాయం కోసం నేను ఇక్కడ ఉన్నాను. దయచేసి మీ పేరు చెప్పండి.",
        "ask_name_voice": "ధన్యవాదాలు, దయచేసి మీ పేరు చెప్పండి.",
        "ask_age_voice": "ధన్యవాదాలు {name}, మీ వయస్సు చెప్పండి.",
        "ask_symptoms_voice": "ధన్యవాదాలు, మీ లక్షణాలు చెప్పండి.",
        "ask_image_voice": "లక్షణాలు నమోదు చేయబడ్డాయి, ఫోటో అప్‌లోడ్ చేయండి.",
        "processing_voice": "దయచేసి వేచి ఉండండి, నివేదిక సిద్ధమవుతోంది.",
        "processing_text": "💬 AROVA: విశ్లేషణ జరుగుతోంది...",
        "report_spoken_summary": "AROVA {name}, స్క్రీనింగ్ పూర్తయింది.",
    },

    # 🇮🇳 GUJARATI (ગુજરાતી)
    "gu": {
        "welcome_voice": "નમસ્તે, હું અરોવા છું. આપનું સ્વાગત છે. હું તમારી આરોગ્ય સહાય માટે અહીં છું. કૃપા કરીને તમારું નામ જણાવો.",
        "welcome_text": "💬 AROVA: નમસ્તે. હું અરોવા છું. આપનું સ્વાગત છે. હું તમારી આરોગ્ય સહાય માટે અહીં છું. કૃપા કરીને તમારું નામ જણાવો.",
        "ask_name_voice": "આભાર, કૃપા કરીને તમારું નામ જણાવો.",
        "ask_age_voice": "આભાર {name}, કૃપા કરીને તમારી ઉંમર જણાવો.",
        "ask_symptoms_voice": "આભાર, હવે તમારા લક્ષણો જણાવો.",
        "ask_image_voice": "લક્ષણો નોંધાઈ ગયા છે, ફોટો અપલોડ કરો.",
        "processing_voice": "કૃપા કરીને રાહ જુઓ, રિપોર્ટ તૈયાર થઈ રહ્યો છે.",
        "processing_text": "💬 AROVA: તપાસ ચાલુ છે...",
        "report_spoken_summary": "AROVA {name}, તપાસ પૂર્ણ થઈ છે.",
    },

    # 🇮🇳 KANNADA (ಕನ್ನಡ)
    "kn": {
        "welcome_voice": "ನಮಸ್ಕಾರ, ನಾನು ಅರೋವಾ. ನಿಮಗೆ ಸ್ವಾಗತ. ನಿಮ್ಮ ಆರೋಗ್ಯ ನೆರವಿಗಾಗಿ ನಾನು ಇಲ್ಲಿದ್ದೇನೆ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಹೆಸರು ಹೇಳಿ.",
        "welcome_text": "💬 AROVA: ನಮಸ್ಕಾರ. ನಾನು ಅರೋವಾ. ನಿಮಗೆ ಸ್ವಾಗತ. ನಿಮ್ಮ ಆರೋಗ್ಯ ನೆರವಿಗಾಗಿ ನಾನು ಇಲ್ಲಿದ್ದೇನೆ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಹೆಸರು ಹೇಳಿ.",
        "ask_name_voice": "ಧನ್ಯವಾದಗಳು, ದಯವಿಟ್ಟು ನಿಮ್ಮ ಹೆಸರು ಹೇಳಿ.",
        "ask_age_voice": "ಧನ್ಯವಾದಗಳು {name}, ನಿಮ್ಮ ವಯಸ್ಸು ಹೇಳಿ.",
        "ask_symptoms_voice": "ಧನ್ಯವಾದಗಳು, ನಿಮ್ಮ ಲಕ್ಷಣಗಳನ್ನು ತಿಳಿಸಿ.",
        "ask_image_voice": "ಲಕ್ಷಣಗಳನ್ನು ದಾಖಲಿಸಲಾಗಿದೆ, ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.",
        "processing_voice": "ದಯವಿಟ್ಟು ನಿರೀಕ್ಷಿಸಿ, ವರದಿ ಸಿದ್ಧವಾಗುತ್ತಿದೆ.",
        "processing_text": "💬 AROVA: ವಿಶ್ಲೇಷಣೆ ನಡೆಯುತ್ತಿದೆ...",
        "report_spoken_summary": "AROVA {name}, ಪರೀಕ್ಷೆ ಪೂರ್ಣಗೊಂಡಿದೆ.",
    },

    # 🇮🇳 MALAYALAM (മലയാളം)
    "ml": {
        "welcome_voice": "നമസ്കാരം, ഞാൻ അരോവ ആണ്. സ്വാഗതം. നിങ്ങളുടെ ആരോഗ്യ സഹായത്തിനായി ഞാൻ ഇവിടെയുണ്ട്. ദയവായി നിങ്ങളുടെ പേര് പറയുക.",
        "welcome_text": "💬 AROVA: നമസ്കാരം. ഞാൻ അരോവ ആണ്. സ്വാഗതം. നിങ്ങളുടെ ആരോഗ്യ സഹായത്തിനായി ഞാൻ ഇവിടെയുണ്ട്. ദയവായി നിങ്ങളുടെ പേര് പറയുക.",
        "ask_name_voice": "നന്ദി, ദയവായി നിങ്ങളുടെ പേര് പറയുക.",
        "ask_age_voice": "നന്ദി {name}, നിങ്ങളുടെ വയസ്സ് പറയുക.",
        "ask_symptoms_voice": "നന്ദി, നിങ്ങളുടെ ലക്ഷണങ്ങൾ പറയുക.",
        "ask_image_voice": "ലക്ഷണങ്ങൾ രേഖപ്പെടുത്തി, ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുക.",
        "processing_voice": "ദയവായി കാത്തിരിക്കൂ, റിപ്പോർട്ട് തയ്യാറാകുന്നു.",
        "processing_text": "💬 AROVA: പരിശോധന നടക്കുന്നു...",
        "report_spoken_summary": "AROVA {name}, പരിശോധന പൂർത്തിയായി.",
    },

    # 🇮🇳 PUNJABI (ਪੰਜਾਬੀ)
    "pa": {
        "welcome_voice": "ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ, ਮੈਂ ਅਰੋਵਾ ਹਾਂ. ਤੁਹਾਡਾ ਸਵਾਗਤ ਹੈ. ਮੈਂ ਤੁਹਾਡੀ ਸਿਹਤ ਸਹਾਇਤਾ ਲਈ ਇੱਥੇ ਹਾਂ. ਕਿਰਪਾ ਕਰਕੇ ਆਪਣਾ ਨਾਮ ਦੱਸੋ.",
        "welcome_text": "💬 AROVA: ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ। ਮੈਂ ਅਰੋਵਾ ਹਾਂ। ਤੁਹਾਡਾ ਸਵਾਗਤ ਹੈ। ਮੈਂ ਤੁਹਾਡੀ ਸਿਹਤ ਸਹਾਇਤਾ ਲਈ ਇੱਥੇ ਹਾਂ। ਕਿਰਪਾ ਕਰਕੇ ਆਪਣਾ ਨਾਮ ਦੱਸੋ।",
        "ask_name_voice": "ਧੰਨਵਾਦ, ਕਿਰਪਾ ਕਰਕੇ ਆਪਣਾ ਨਾਮ ਦੱਸੋ.",
        "ask_age_voice": "ਧੰਨਵਾਦ {name}, ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੀ ਉਮਰ ਦੱਸੋ.",
        "ask_symptoms_voice": "ਧੰਨਵਾਦ, ਹੁਣ ਆਪਣੇ ਲੱਛਣ ਦੱਸੋ.",
        "ask_image_voice": "ਲੱਛਣ ਨੋਟ ਕਰ ਲਏ ਗਏ ਹਨ, ਅੱਖ ਦੀ ਫੋਟੋ ਅੱਪਲੋਡ ਕਰੋ.",
        "processing_voice": "ਕਿਰਪਾ ਕਰਕੇ ਇੰਤਜ਼ਾਰ ਕਰੋ, ਰਿਪੋਰਟ ਤਿਆਰ ਹੋ ਰਹੀ ਹੈ.",
        "processing_text": "💬 AROVA: ਜਾਂਚ ਜਾਰੀ ਹੈ...",
        "report_spoken_summary": "AROVA {name}, ਜਾਂਚ ਪੂਰੀ ਹੋ ਗਈ ਹੈ.",
    },
}
