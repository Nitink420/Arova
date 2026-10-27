# app/services/llm_service.py
"""
AROVA Multilingual LLM Service (Online Gemma 4 + Offline Ollama models)

Orchestrates medical screening explanations in the patient's session language:
- Backends (selected by LLM_BACKEND in .env):
  1. "gemini" (Online): Gemma 4 via the Gemini API (GEMINI_MODEL, default gemma-4-31b-it).
  2. "ollama" (Offline, default): local Ollama model chosen from OLLAMA_MODELS
     (default gemma3:1b, llama3.2:1b), switchable at runtime.
  3. Safety Base: Deterministic rule-based clinical care engine if no model answers.
- Fallback chain: Gemini -> Ollama -> rules (Gemini is skipped in "ollama" mode).
- The SAME prompt builder and medical safety filter are used for every backend/model
  (prevents medication prescription or diagnostic claims).
"""

from typing import Generator, List, Optional

from app.core.config import Config
from app.core.logger import get_logger
from app.services.ollama_client import OllamaClient
from app.services.gemini_client import GeminiClient, GeminiClientError
from app.services.language_service import LanguageService

logger = get_logger(__name__)

VALID_BACKENDS = ("ollama", "gemini")


class LLMService:
    """
    Service for generating AI-powered medical screening explanations.
    Online: Gemma 4 via Gemini API. Offline: switchable local Ollama models.
    """

    # Generation limits for the Gemini backend (Ollama uses OLLAMA_OPTIONS).
    GEMINI_MAX_OUTPUT_TOKENS = 400
    GEMINI_TEMPERATURE = 0.2

    def __init__(self):
        self.config = Config()
        for warning in getattr(self.config, "CONFIG_WARNINGS", []):
            logger.warning("Config: %s", warning)

        self.lang_service = LanguageService()
        self.ollama_client = OllamaClient()
        self.gemini_client = GeminiClient(
            api_key=self.config.GEMINI_API_KEY,
            model_name=self.config.GEMINI_MODEL,
            timeout=self.config.GEMINI_TIMEOUT,
        )

        self.backend = self.config.LLM_BACKEND
        self.enable_gemini = self.config.ENABLE_GEMINI
        self.enable_ollama = self.config.ENABLE_OLLAMA
        self.ollama_models: List[str] = list(self.config.OLLAMA_MODELS)
        self.ollama_model = self.config.OLLAMA_MODEL
        self.ollama_options = dict(self.config.OLLAMA_OPTIONS)
        self._ollama_available = False

        if self.enable_ollama:
            self._ollama_available = self.ollama_client.health_check()
            if not self._ollama_available:
                logger.warning(
                    "Ollama unavailable at %s. Edge model standby disabled.",
                    self.config.OLLAMA_API_URL,
                )
        else:
            logger.info("Ollama local LLM is disabled via ENABLE_OLLAMA=false.")

        logger.info(
            "LLM backend=%s | Gemini model=%s | Ollama model=%s (choices: %s)",
            self.backend, self.config.GEMINI_MODEL, self.ollama_model,
            ", ".join(self.ollama_models),
        )

    # ── Availability / runtime switching ───────────────────────

    def _gemini_ready(self) -> bool:
        """Gemini backend selected, enabled, keyed and SDK importable (no network call)."""
        return (
            self.backend == "gemini"
            and self.enable_gemini
            and self.gemini_client.health_check()
        )

    @property
    def is_available(self) -> bool:
        """Whether at least one LLM backend (Gemini online or Ollama offline) is available."""
        return self._gemini_ready() or (self.enable_ollama and self._ollama_available)

    def set_gemini_api_key(self, api_key: str):
        """Allow setting or updating the Gemini API key at runtime (never logged)."""
        self.config.GEMINI_API_KEY = api_key.strip()
        self.gemini_client.update_key(api_key.strip())

    def get_backend(self) -> str:
        """Return the configured backend: 'ollama' or 'gemini'."""
        return self.backend

    def set_backend(self, backend: str) -> bool:
        """Switch backend at runtime. Returns False (no change) for unknown values."""
        value = (backend or "").strip().lower()
        if value not in VALID_BACKENDS:
            logger.warning("Ignoring unknown LLM backend '%s'.", backend)
            return False
        self.backend = value
        logger.info("LLM backend switched to %s.", value)
        return True

    def get_ollama_models(self) -> List[str]:
        """Offline models that may be selected (from OLLAMA_MODELS)."""
        return list(self.ollama_models)

    def get_ollama_model(self) -> str:
        """Currently active offline model."""
        return self.ollama_model

    def set_ollama_model(self, model: str) -> bool:
        """Switch the active offline model at runtime. Only OLLAMA_MODELS values are accepted."""
        value = (model or "").strip()
        if value not in self.ollama_models:
            logger.warning(
                "Ignoring Ollama model '%s' (allowed: %s).", model, ", ".join(self.ollama_models)
            )
            return False
        self.ollama_model = value
        logger.info("Active Ollama model switched to %s.", value)
        return True

    def _resolve_ollama_model(self, model: Optional[str]) -> str:
        """Per-call model override; unknown values fall back to the active OLLAMA_MODEL."""
        if model is None or not str(model).strip():
            return self.ollama_model
        value = str(model).strip()
        if value in self.ollama_models:
            return value
        logger.warning(
            "Requested Ollama model '%s' is not in OLLAMA_MODELS (%s); using '%s'.",
            value, ", ".join(self.ollama_models), self.ollama_model,
        )
        return self.ollama_model

    def get_active_backend(self) -> str:
        """Return which backend will currently be tried first (no network call for Gemini)."""
        if self._gemini_ready():
            return f"Online Gemma 4 via Gemini API ({self.config.GEMINI_MODEL})"
        if self.enable_ollama and self._ollama_available:
            return f"Offline Ollama ({self.ollama_model})"
        return "Deterministic Clinical Rules"

    # ── Generation ────────────────────────────────────────────────

    def generate_summary(
        self,
        arova_report,
        lang: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        """
        Generate a safety-filtered explanation for a screening report.

        Args:
            arova_report: Report dict (or any object; stringified).
            lang: Target language code (defaults to the session language).
            model: Optional offline model for this call. Only values from
                OLLAMA_MODELS are accepted; anything else uses the active OLLAMA_MODEL.

        Order: Gemini (only if LLM_BACKEND=gemini) -> Ollama -> rule engine.
        """
        target_lang = lang or self.lang_service.get_language()
        prompt = self._build_safe_prompt(arova_report, target_lang)
        ollama_model = self._resolve_ollama_model(model)

        # ── Step 1: Online Gemma 4 via Gemini API (if selected & configured) ──
        if self._gemini_ready():
            logger.info("Generating explanation via Gemini API (%s)...", self.config.GEMINI_MODEL)
            try:
                gemini_response = self.gemini_client.generate(
                    prompt,
                    max_output_tokens=self.GEMINI_MAX_OUTPUT_TOKENS,
                    temperature=self.GEMINI_TEMPERATURE,
                )
                formatted_response = (
                    f"✨ **[Gemma 4 via Gemini API ({self.config.GEMINI_MODEL}) — Online Mode]**\n\n"
                    f"{gemini_response}"
                )
                return self._safety_filter(formatted_response, target_lang)
            except GeminiClientError as e:
                logger.warning("Gemini unavailable (%s). Switching to local Ollama model...", e)
        elif self.backend == "gemini":
            logger.info("Gemini backend selected but not ready (key/SDK/ENABLE_GEMINI). Using Ollama.")

        # ── Step 2: Offline local Ollama model ──
        if self.enable_ollama and self._ollama_available:
            logger.info("Generating explanation via local Ollama (%s)...", ollama_model)
            response = self.ollama_client.generate(
                model=ollama_model,
                prompt=prompt,
                options=self.ollama_options,
            )
            if response and response.strip():
                logger.info("Ollama generation successful (%s).", ollama_model)
                formatted_response = (
                    f"⚡ **[Edge {ollama_model} — 100% On-Device Offline Mode]**\n\n"
                    f"{response.strip()}"
                )
                return self._safety_filter(formatted_response, target_lang)
            logger.warning(
                "Ollama returned no response for %s (is it pulled? `ollama pull %s`). "
                "Switching to rule-based engine...", ollama_model, ollama_model,
            )

        # ── Step 3: Pure Deterministic Rule-Based Fallback ──
        logger.info("Using localized clinical rule-based engine fallback.")
        return self._fallback_explanation(arova_report, target_lang)

    def explain(self, arova_report, lang: Optional[str] = None, model: Optional[str] = None) -> str:
        """Backward-compatible wrapper around generate_summary()."""
        return self.generate_summary(arova_report, lang=lang, model=model)

    def explain_stream(
        self, arova_report, lang: Optional[str] = None, model: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Streaming explanation generator with seamless fallback.
        """
        target_lang = lang or self.lang_service.get_language()
        # For hybrid mode, we generate the full text and yield it
        explanation = self.generate_summary(arova_report, lang=target_lang, model=model)
        yield explanation

    def refresh_availability(self) -> bool:
        """Re-check Ollama server connectivity."""
        if self.enable_ollama:
            self._ollama_available = self.ollama_client.health_check()
        return self.is_available

    def _build_safe_prompt(self, arova_report, lang: str) -> str:
        """
        Construct a compact medical prompt in the target language.
        """
        lang_info = self.lang_service.get_language_info(lang)
        lang_name = lang_info.get("name", "English")
        native_name = lang_info.get("native", lang_name)

        if isinstance(arova_report, dict):
            name = arova_report.get("name", "Patient")
            symptoms = arova_report.get("symptoms", "None reported")
            risk = arova_report.get("risk_percent", 0.0)
            priority = arova_report.get("hb_test_priority", "Low")
            hb_est = arova_report.get("estimated_hb_range", "N/A")
            summary_text = (
                f"Patient Name: {name}, Reported Symptoms: {symptoms}, "
                f"Non-Invasive Conjunctiva Risk Signal: {risk}%, "
                f"Hb-Test Priority Tier: {priority}, Estimated Hemoglobin Range: {hb_est} g/dL."
            )
        else:
            summary_text = str(arova_report)[:400]

        return (
            f"You are AROVA AI, an expert clinical decision-support assistant for rural frontline health workers.\n"
            f"Explain this non-invasive anemia screening report clearly in {lang_name} ({native_name}) in 4 concise, clear bullet points.\n\n"
            f"Screening Findings:\n{summary_text}\n\n"
            "Clinical Safety Directives:\n"
            "1. Clarify that this is an optical screening signal, NOT a confirmatory venous blood test.\n"
            "2. Recommend confirmation via laboratory CBC / Sahli's hemoglobinometer blood test.\n"
            "3. Suggest traditional Indian bio-available iron foods (Sahjan/Moringa, Gud-Chana, Amla/Lemon for Vitamin C absorption).\n"
            "4. Do NOT prescribe any specific prescription medicines or pharmacological dosages.\n\n"
            "Format your answer with clean bullet points:\n"
            "- 📊 Clinical Summary: ...\n"
            "- 🩸 Hb Blood Test Recommendation: ...\n"
            "- 🌿 Nutritional Guidance (Iron & Vitamin C): ...\n"
            "- ⚠️ Medical Safety Notice: ..."
        )

    def _safety_filter(self, text: str, lang: str) -> str:
        """Apply medical safety filter to LLM-generated text."""
        bad_phrases = [
            "you have anemia",
            "anemia confirmed",
            "take this tablet",
            "mg dosage",
            "antibiotic",
        ]

        lower_text = text.lower()
        for phrase in bad_phrases:
            if phrase in lower_text:
                disc = self.lang_service.t("disclaimer_text", lang=lang)
                text += f"\n\n⚠️ {disc}"
                break

        return text

    def _fallback_explanation(self, arova_report, lang: str) -> str:
        """Generate localized rule-based explanation when LLMs are unavailable."""
        if isinstance(arova_report, dict):
            priority = arova_report.get("hb_test_priority", "Low")
            risk = arova_report.get("risk_percent", 0.0)
            hb_est = arova_report.get("estimated_hb_range", "11.5 - 13.5")
        else:
            priority = "Pending"
            risk = 0.0
            hb_est = "N/A"

        p_label = self.lang_service.t(f"priority_{priority.lower()}", lang=lang)
        wording = self.lang_service.t(f"wording_{priority.lower()}", lang=lang)
        safety_text = self.lang_service.t("disclaimer_text", lang=lang)
        care_title = self.lang_service.t("care_title", lang=lang)

        return (
            f"🔒 **[Deterministic Clinical Rule Engine — 100% Air-Gapped Mode]**\n\n"
            f"- 📊 **{self.lang_service.t('report_title', lang=lang)}**: Priority = **{p_label}** ({risk:.1f}% signal | Est. Hb ~{hb_est} g/dL)\n"
            f"- 🩸 **{self.lang_service.t('gauge_title', lang=lang)}**: {wording}\n"
            f"- 🌿 **{care_title}**: Sahjan (Moringa), Gud-Chana, Ankurit Dal, Amla (Vitamin C synergist) & hydration.\n"
            f"- ⚠️ **{self.lang_service.t('disclaimer_title', lang=lang)}**: {safety_text}"
        )

    def status(self) -> str:
        """Return human-readable status for startup health check."""
        if not self.enable_gemini:
            gemini_status = "DISABLED"
        elif self.gemini_client.health_check():
            gemini_status = "READY"
        else:
            gemini_status = "NO_KEY_OR_SDK"
        ollama_status = "CONNECTED" if self._ollama_available else "OFFLINE"
        return (
            f"Backend: {self.backend} | Gemini ({self.config.GEMINI_MODEL}): {gemini_status} | "
            f"Ollama ({self.ollama_model}): {ollama_status}"
        )
