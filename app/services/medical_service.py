# app/services/medical_service.py
"""
AROVA Multilingual Medical Service

Owns all medical domain logic: safety rules, symptom parsing,
Hb priority interpretation, localized care/diet recommendations, and
fallback explanations.

No HTTP calls. No model inference. Pure medical domain logic.

Usage:
    from app.services.medical_service import MedicalService
    medical = MedicalService()
    symptoms = medical.parse_symptoms("weakness, chakkar, bukhar")
    care = medical.get_care(symptoms, lang="hi")
"""

from typing import List, Optional
from app.core.logger import get_logger
from app.services.language_service import LanguageService

logger = get_logger(__name__)


class MedicalService:
    """
    Service for medical safety rules, symptom interpretation,
    and localized care guidance generation.
    """

    ANEMIA_INDICATORS = [
        "weakness", "dizziness", "breathless", "chest_pain", "fainting", "paleness"
    ]

    SEVERE_INDICATORS = [
        "breathless", "chest_pain", "fainting", "weakness"
    ]

    def __init__(self):
        self.lang_service = LanguageService()
        logger.info("MedicalService initialized.")

    def parse_symptoms(self, text: str) -> List[str]:
        """
        Parse symptom free-text into normalized keyword labels.
        """
        try:
            from src.symptom_parser import parse_symptoms
            return parse_symptoms(text)
        except Exception as e:
            logger.error("Symptom parsing failed: %s", e)
            return []

    def get_care(self, symptoms: List[str], lang: Optional[str] = None) -> dict:
        """
        Generate localized care, diet, and warning guidance based on symptoms and session language.
        """
        target_lang = lang or self.lang_service.get_language()
        try:
            from src.basic_care_engine import get_basic_care
            care_res = get_basic_care(symptoms)
            care_res["safety_note"] = self.lang_service.t("disclaimer_text", lang=target_lang)
            return care_res
        except Exception as e:
            logger.error("Care engine failed: %s", e)
            return self._fallback_care(target_lang)

    def has_anemia_symptoms(self, symptoms: List[str]) -> bool:
        """Check if any reported symptoms are anemia indicators."""
        return any(s in symptoms for s in self.ANEMIA_INDICATORS)

    def get_severe_symptoms(self, symptoms: List[str]) -> List[str]:
        """Filter symptoms for severe/urgent indicators."""
        return [s for s in symptoms if s in self.SEVERE_INDICATORS]

    def should_use_llm(self, prediction_result: Optional[dict] = None) -> bool:
        """Decide whether the LLM should be consulted."""
        return True

    def get_fallback_explanation(
        self,
        priority: str = "Low",
        risk_percent: float = 0.0,
        lang: Optional[str] = None,
    ) -> str:
        """Generate a localized rule-based explanation when LLM is unavailable."""
        target_lang = lang or self.lang_service.get_language()
        p_label = self.lang_service.t(f"priority_{priority.lower()}", lang=target_lang)
        wording = self.lang_service.t(f"wording_{priority.lower()}", lang=target_lang)
        safety_text = self.lang_service.t("disclaimer_text", lang=target_lang)

        return (
            f"📊 Screening Summary: Risk signal {risk_percent:.1f}%, Priority = {p_label}.\n"
            f"⚠️ {safety_text}\n"
            f"🩸 {wording}\n"
            f"🍎 Nutrition: Spinach, beetroot, dates, pomegranate & guava for iron boost."
        )

    def _fallback_care(self, lang: str) -> dict:
        """Provide basic care guidance when care engine fails."""
        return {
            "care": [
                "Rest & maintain proper hydration.",
                "Visit a clinic if symptoms worsen.",
            ],
            "diet": [
                "Iron-rich foods: Spinach, Beetroot, Beans, Dates.",
                "Fruits: Pomegranate, Guava, Oranges.",
            ],
            "warnings": [
                "Consult a physician if feeling breathless or fainting.",
            ],
            "safety_note": self.lang_service.t("disclaimer_text", lang=lang),
        }
