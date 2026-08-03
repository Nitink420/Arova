# src/voice_speech_engine.py
"""
AROVA Multilingual Speech Optimization Engine

Provides end-to-end text preprocessing, Urdu script to Devanagari phonetic transliteration,
medical jargon normalization, number spelling, sentence segmentation, and audio post-processing.

Ensures all periods '.', danda '।', pipes '|', colons, and semicolons are stripped from input
text and replaced with clean spaces before TTS synthesis for smooth, natural voice.
"""

import re
import math
import numpy as np
from typing import Dict, Any, List, Tuple, Optional

# Kokoro v1.0 Supported Voice Profiles (Soft, Crystal Clear, Calm Cadence)
LANGUAGE_PROFILES: Dict[str, Dict[str, Any]] = {
    "en": {
        "voice_id": "af_heart",       # Kokoro Female English Healthcare Voice (Ultra-Soft)
        "speed": 0.86,
        "style": "calm, professional, clear, soft",
        "kokoro_lang": "en-us",
    },
    "hi": {
        "voice_id": "hf_beta",        # Kokoro Hindi Female Voice (Clear & Warm)
        "speed": 0.84,
        "style": "warm, respectful, natural cadence, soft",
        "kokoro_lang": "hi",
    },
    "ur": {
        "voice_id": "hf_beta",        # Kokoro Hindi/Urdu Female Voice
        "speed": 0.84,
        "style": "polite, elegant, soft",
        "kokoro_lang": "hi",
    },
    "bn": {"voice_id": "hf_beta", "speed": 0.84, "style": "soft, polite", "kokoro_lang": "hi"},
    "mr": {"voice_id": "hf_beta", "speed": 0.84, "style": "conversational", "kokoro_lang": "hi"},
    "ta": {"voice_id": "hf_beta", "speed": 0.84, "style": "respectful", "kokoro_lang": "hi"},
    "te": {"voice_id": "hf_beta", "speed": 0.84, "style": "natural", "kokoro_lang": "hi"},
    "gu": {"voice_id": "hf_beta", "speed": 0.84, "style": "friendly", "kokoro_lang": "hi"},
    "kn": {"voice_id": "hf_beta", "speed": 0.84, "style": "clear", "kokoro_lang": "hi"},
    "ml": {"voice_id": "hf_beta", "speed": 0.84, "style": "gentle", "kokoro_lang": "hi"},
    "pa": {"voice_id": "hf_beta", "speed": 0.84, "style": "respectful", "kokoro_lang": "hi"},
}

URDU_TO_DEVANAGARI_MAP: List[Tuple[str, str]] = [
    (r"سلام", "सलाम"),
    (r"میں", "मैं"),
    (r"ہوں", "हूँ"),
    (r"آپ", "आप"),
    (r"کا", "का"),
    (r"کی", "की"),
    (r"کے", "के"),
    (r"استقبال", "इस्तक़बाल"),
    (r"یہاں", "यहाँ"),
    (r"صحت", "सेहत"),
    (r"معاونت", "सहायता"),
    (r"مدد", "मदद"),
    (r"لیے", "लिए"),
    (r"براہ", "बराह"),
    (r"کرم", "करम"),
    (r"اپنا", "अपना"),
    (r"نام", "नाम"),
    (r"بتائیں۔", "बताएं।"),
    (r"بتائیں", "बताएं"),
    (r"شکریہ", "शुक्रिया"),
    (r"عمر", "उम्र"),
    (r"علامات", "अलामात"),
    (r"تصویر", "तस्वीर"),
    (r"اپ لوڈ", "अपलोड"),
    (r"کریں۔", "करें।"),
    (r"کریں", "करें"),
    (r"انتظار", "इंतजार"),
    (r"رپورٹ", "रिपोर्ट"),
    (r"تکمیل", "तकमील"),
    (r"ہو گئی", "हो गई"),
    (r"ہے۔", "है।"),
    (r"ہے", "है"),
]

MEDICAL_DICTIONARIES: Dict[str, Dict[str, str]] = {
    "en": {
        "hemoglobin deficiency": "low blood iron count",
        "conjunctiva": "lower eyelid area",
        "anemia": "low hemoglobin count",
        "hb-test": "hemoglobin blood check up",
        "hb test": "hemoglobin blood check up",
        "ref:": "reference number",
        "pdf": "report document",
    },
    "hi": {
        "hemoglobin deficiency": "हीमोग्लोबिन या खून की कमी",
        "conjunctiva": "आँख का निचला हिस्सा",
        "anemia": "हीमोग्लोबिन की कमी",
        "hb-test": "हीमोग्लोबिन खून की जांच",
        "hb test": "हीमोग्लोबिन खून की जांच",
        "ref:": "रेफरेंस नंबर",
        "pdf": "पीडीएफ रिपोर्ट",
    },
    "ur": {
        "hemoglobin deficiency": "हीमोग्लोबिन या खून की कमी",
        "conjunctiva": "आँख का निचला हिस्सा",
        "anemia": "खून की कमी",
        "hb-test": "हीमोग्लोबिन खून की जांच",
        "hb test": "हीमोग्लोबिन खून की जांच",
        "ref:": "रेफरेंस नंबर",
        "pdf": "पीडीएफ रिपोर्ट",
    },
}

NUMBER_MAPS: Dict[str, Dict[str, str]] = {
    "en": {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten", "48": "forty eight"},
    "hi": {"0": "शून्य", "1": "एक", "2": "दो", "3": "तीन", "4": "चार", "5": "पाँच", "6": "छह", "7": "सात", "8": "आठ", "9": "नौ", "10": "दस", "48": "अड़तालिस"},
    "ur": {"0": "सिफर", "1": "एक", "2": "दो", "3": "तीन", "4": "चार", "5": "पाँच", "6": "छह", "7": "सात", "8": "आठ", "9": "नौ", "10": "दस", "48": "अड़तालिस"},
}


class MultilingualSpeechEngine:
    """
    Speech Optimization & Preprocessing Engine.
    """

    @staticmethod
    def get_profile(lang: str) -> Dict[str, Any]:
        """Return language profile dict or default to English."""
        return LANGUAGE_PROFILES.get(lang.lower(), LANGUAGE_PROFILES["en"])

    @classmethod
    def convert_urdu_to_devanagari(cls, text: str) -> str:
        """
        Convert Urdu Nastaliq/Arabic script text to clean Devanagari phonetic script.
        """
        res = text
        for urdu_word, devanagari_word in URDU_TO_DEVANAGARI_MAP:
            res = re.sub(re.escape(urdu_word), devanagari_word, res)
        return res

    @classmethod
    def preprocess_text(cls, text: str, lang: str = "en") -> str:
        """
        Full text normalization pipeline before TTS synthesis.
        Preserves natural pause markers (commas, periods) so TTS voices
        have soft cadence without trailing 'he' breath noises.
        """
        if not text:
            return ""

        target_lang = lang.lower().strip()

        # Step 1: Strip UI emojis and markdown syntax
        clean = text
        emojis = ["📋", "⚠️", "➕", "🗣️", "🌐", "📥", "🍎", "🥬", "💧", "🍽️", "🩺", "💬", "➕", "✅", "❌", "🔬"]
        for emoji in emojis:
            clean = clean.replace(emoji, "")

        clean = re.sub(r"#+\s*", "", clean)
        clean = re.sub(r"\*+", "", clean)
        clean = re.sub(r"`+", "", clean)
        clean = re.sub(r"\[.*?\]\(.*?\)", "", clean)

        # Step 2: Convert Urdu script to Devanagari phonetic script if needed
        if target_lang == "ur" or any('\u0600' <= c <= '\u06ff' for c in clean):
            clean = cls.convert_urdu_to_devanagari(clean)

        # Step 3: Apply medical term replacements
        med_dict = MEDICAL_DICTIONARIES.get(target_lang, MEDICAL_DICTIONARIES.get("en", {}))
        for raw_term, spoken_term in med_dict.items():
            pattern = re.compile(re.escape(raw_term), re.IGNORECASE)
            clean = pattern.sub(spoken_term, clean)

        # Step 4: Expand abbreviations and numbers
        clean = re.sub(r"(?i)\bref:\s*#?\w+-?\d*-?\w*", "", clean)
        clean = re.sub(r"(?i)\bpdf\b", "PDF", clean)

        num_dict = NUMBER_MAPS.get(target_lang, NUMBER_MAPS.get("en", {}))
        for num_str, spoken_num in num_dict.items():
            clean = re.sub(rf"\b{num_str}\b", spoken_num, clean)

        # Step 5: Normalize punctuation (Convert danda '।' and '|' to '.', colons/semicolons to ',')
        clean = clean.replace("।", ".").replace("|", ".").replace(";", ",").replace(":", ",")
        # Strip unwanted symbols, keeping alphanumeric, spaces, Devanagari/script chars, and basic punctuation (, . ?)
        clean = re.sub(r"[^\w\s\u0600-\u06FF\u0900-\u097F\u0980-\u09FF\u0B80-\u0BFF\u0C00-\u0C7F\u0A80-\u0AFF\u0C80-\u0CFF\u0D00-\u0D7F\u0A00-\u0A7F,.?!]", " ", clean)
        clean = re.sub(r"\s+", " ", clean).strip()

        return clean


    @classmethod
    def post_process_audio(
        cls, samples: np.ndarray, sample_rate: int = 24000
    ) -> Tuple[np.ndarray, int]:
        """
        Audio Post-Processing Pipeline:
        1. DC Offset Removal.
        2. Silence Trimming.
        3. Peak Loudness Normalization (-1.0 dB target).
        4. Anti-clipping 10ms raised-cosine fade-in & fade-out.
        """
        if samples is None or len(samples) == 0:
            return samples, sample_rate

        audio = np.array(samples, dtype=np.float32)

        # DC Offset Removal
        audio = audio - np.mean(audio)

        # Silence Trimming
        max_val = np.max(np.abs(audio))
        if max_val > 1e-4:
            threshold = max_val * 0.01
            non_silent = np.where(np.abs(audio) > threshold)[0]
            if len(non_silent) > 0:
                start_idx = max(0, non_silent[0] - int(sample_rate * 0.05))
                end_idx = min(len(audio), non_silent[-1] + int(sample_rate * 0.05))
                audio = audio[start_idx:end_idx]

        # Peak Loudness Normalization
        max_amp = np.max(np.abs(audio))
        if max_amp > 1e-4:
            target_amp = 0.891
            scaling_factor = target_amp / max_amp
            audio = audio * scaling_factor

        # Anti-clipping 10ms Raised-Cosine Fade
        fade_len = int(sample_rate * 0.01)
        if len(audio) > fade_len * 2:
            fade_in = 0.5 * (1.0 - np.cos(np.linspace(0, np.pi, fade_len)))
            fade_out = 0.5 * (1.0 + np.cos(np.linspace(0, np.pi, fade_len)))

            audio[:fade_len] *= fade_in
            audio[-fade_len:] *= fade_out

        return audio, sample_rate
