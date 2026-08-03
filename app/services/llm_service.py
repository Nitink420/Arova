# app/services/llm_service.py
"""
AROVA Multilingual LLM Service

Orchestrates LLM-powered explanations for screening reports in the patient's chosen session language.
Handles prompt engineering, localized safety filtering, response validation,
and rule-based fallback when Ollama is unavailable.

Usage:
    from app.services.llm_service import LLMService
    llm = LLMService()
    explanation = llm.explain(report_data, lang="hi")
    for partial in llm.explain_stream(report_markdown, lang="bn"):
        update_ui(partial)
"""

from typing import Generator, Optional

from app.core.config import Config
from app.core.logger import get_logger
from app.services.ollama_client import OllamaClient
from app.services.language_service import LanguageService

logger = get_logger(__name__)


class LLMService:
    """
    Service for generating AI-powered medical screening explanations in the selected language.

    Uses OllamaClient for LLM inference, applies medical safety filtering,
    and falls back to localized rule-based explanations when LLM is unavailable.
    """

    def __init__(self):
        self.config = Config()
        self.client = OllamaClient()
        self.lang_service = LanguageService()
        self.enabled = self.config.ENABLE_OLLAMA
        self.model = self.config.OLLAMA_MODEL
        self.options = self.config.OLLAMA_OPTIONS
        self._available = False

        if self.enabled:
            self._available = self.client.health_check()
            if not self._available:
                logger.warning(
                    "Ollama unavailable at %s. LLM explanations will use rule-based fallback.",
                    self.config.OLLAMA_API_URL,
                )
        else:
            logger.info("Ollama LLM is disabled via ENABLE_OLLAMA=false.")

    @property
    def is_available(self) -> bool:
        """Whether the LLM backend is reachable and enabled."""
        return self.enabled and self._available

    def explain(self, arova_report, lang: Optional[str] = None) -> str:
        """
        Generate a non-streaming explanation for a screening report in target language.
        """
        target_lang = lang or self.lang_service.get_language()
        if not self.is_available:
            return self._fallback_explanation(arova_report, target_lang)

        prompt = self._build_safe_prompt(arova_report, target_lang)

        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            options=self.options,
        )

        if response is None:
            logger.warning("LLM returned no response. Using rule-based fallback.")
            return self._fallback_explanation(arova_report, target_lang)

        return self._safety_filter(response, target_lang)

    def explain_stream(
        self, arova_report, lang: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Generate a streaming explanation for a screening report in target language.
        """
        target_lang = lang or self.lang_service.get_language()
        if not self.is_available:
            yield self._fallback_explanation(arova_report, target_lang)
            return

        prompt = self._build_safe_prompt(arova_report, target_lang)

        last_text = ""
        received_any = False

        for accumulated_text in self.client.generate_stream(
            model=self.model,
            prompt=prompt,
            options=self.options,
        ):
            received_any = True
            last_text = accumulated_text
            yield accumulated_text

        # Apply safety filter to the final accumulated text
        if received_any and last_text:
            yield self._safety_filter(last_text, target_lang)
        elif not received_any:
            logger.warning("LLM stream produced no output. Using rule-based fallback.")
            yield self._fallback_explanation(arova_report, target_lang)

    def refresh_availability(self) -> bool:
        """Re-check Ollama server connectivity."""
        if self.enabled:
            self._available = self.client.health_check()
        return self._available

    def _build_safe_prompt(self, arova_report, lang: str) -> str:
        """
        Construct a compact prompt requesting response in the target language.
        """
        lang_info = self.lang_service.get_language_info(lang)
        lang_name = lang_info.get("name", "English")
        native_name = lang_info.get("native", lang_name)

        if isinstance(arova_report, dict):
            name = arova_report.get("name", "Patient")
            symptoms = arova_report.get("symptoms", "None")
            risk = arova_report.get("risk_percent", 0.0)
            priority = arova_report.get("hb_test_priority", "Low")
            summary_text = (
                f"Patient: {name}, Symptoms: {symptoms}, "
                f"Eye Risk Indicator: {risk}%, Priority: {priority}"
            )
        else:
            summary_text = str(arova_report)[:400]

        return (
            f"You are Arova AI Healthcare Assistant. Explain this screening report "
            f"clearly in {lang_name} ({native_name}) script in 4 short bullet points.\n\n"
            f"Screening Data:\n{summary_text}\n\n"
            "Safety Rules:\n"
            "1. 'Risk indicator' is an image-based screening signal, NOT final blood Hb level.\n"
            "2. Hb blood test is mandatory for clinical confirmation.\n"
            "3. Suggest iron-rich vegetables (Palak, Beetroot) & fruits (Anar, Guava).\n"
            "4. Do NOT prescribe any medicines or dosages.\n\n"
            "Write response in this clean bullet format:\n"
            "- 📊 Summary: ...\n"
            "- ⚠️ Important Safety: ...\n"
            "- 🩸 Hb Test Advice: ...\n"
            "- 🍎 Nutrition & Diet: ..."
        )

    def _safety_filter(self, text: str, lang: str) -> str:
        """Apply medical safety filter to LLM-generated text."""
        bad_phrases = [
            "you have anemia",
            "anemia confirmed",
            "hb level is",
            "prescribe",
            "dosage",
            "antibiotic",
        ]

        lower_text = text.lower()
        for phrase in bad_phrases:
            if phrase in lower_text:
                disc = self.lang_service.t("disclaimer_text", lang=lang)
                text += f"\n\n⚠️ {disc}"
                break

        if "hb" not in lower_text and "test" not in lower_text:
            text += f"\n- 🩸 {self.lang_service.t('wording_medium', lang=lang)}"

        return text

    def _fallback_explanation(self, arova_report, lang: str) -> str:
        """Generate localized rule-based explanation when LLM is unavailable."""
        if isinstance(arova_report, dict):
            priority = arova_report.get("hb_test_priority", "Low")
            risk = arova_report.get("risk_percent", 0.0)
        else:
            priority = "Pending"
            risk = 0.0

        p_label = self.lang_service.t(f"priority_{priority.lower()}", lang=lang)
        wording = self.lang_service.t(f"wording_{priority.lower()}", lang=lang)
        safety_text = self.lang_service.t("disclaimer_text", lang=lang)
        care_title = self.lang_service.t("care_title", lang=lang)

        return (
            f"- 📊 {self.lang_service.t('report_title', lang=lang)}: Priority = {p_label} ({risk:.1f}% signal)\n"
            f"- ⚠️ {self.lang_service.t('disclaimer_title', lang=lang)}: {safety_text}\n"
            f"- 🩸 {self.lang_service.t('gauge_title', lang=lang)}: {wording}\n"
            f"- 🍎 {care_title}: Iron-rich spinach, beetroot, pomegranate, guava & hydration."
        )

    def status(self) -> str:
        """Return human-readable status for health check."""
        if not self.enabled:
            return "DISABLED"
        if self._available:
            return f"CONNECTED ({self.config.OLLAMA_API_URL}, model={self.model})"
        return f"UNREACHABLE ({self.config.OLLAMA_API_URL}) — using fallback"
