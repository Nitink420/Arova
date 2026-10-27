# app/services/gemini_client.py
"""
AROVA Gemini API Client (Gemma 4, online backend)

Thin transport wrapper around the official ``google-genai`` SDK.
Single responsibility: send a prompt, return plain text.

Design rules:
- The SDK is imported lazily inside the class, so the app still starts
  when ``google-genai`` is not installed (offline / Jetson builds).
- ALL instructions live in the prompt text. No system_instruction and no
  JSON / response-schema mode, because Gemma models may not support them.
- Any leading "thought"/reasoning text is stripped from the output.
- Every failure raises ``GeminiClientError`` so LLMService can fall back.
- The API key is never logged (error messages are scrubbed).

Usage:
    from app.services.gemini_client import GeminiClient, GeminiClientError
    client = GeminiClient()
    if client.health_check():
        try:
            text = client.generate("Hello", max_output_tokens=200, temperature=0.2)
        except GeminiClientError:
            ...
"""

import re
from typing import Optional

from app.core.config import Config
from app.core.logger import get_logger

logger = get_logger(__name__)

DEFAULT_GEMINI_MODEL = "gemma-4-31b-it"  # alternative: "gemma-4-26b-a4b-it"

# Reasoning blocks some models emit before the real answer.
_THOUGHT_BLOCK_PATTERNS = [
    re.compile(r"^\s*<think>.*?</think>\s*", re.DOTALL | re.IGNORECASE),
    re.compile(r"^\s*<thought>.*?</thought>\s*", re.DOTALL | re.IGNORECASE),
    re.compile(r"^\s*<\|channel\|?>\s*thought.*?<\|?channel\|>\s*", re.DOTALL | re.IGNORECASE),
]


class GeminiClientError(Exception):
    """Raised for any Gemini failure (missing SDK/key, timeout, API error, empty output)."""


class GeminiClient:
    """Client for Gemma 4 models served through the Gemini API (google-genai SDK)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        config = Config()  # also loads .env into the environment
        self.api_key = (api_key if api_key is not None else config.GEMINI_API_KEY).strip()
        self.model_name = (model_name or config.GEMINI_MODEL or DEFAULT_GEMINI_MODEL).strip()
        self.timeout = int(timeout or config.GEMINI_TIMEOUT or 30)
        self._client = None  # created lazily on first generate()

    # ── Setup ────────────────────────────────────────────────────

    def update_key(self, api_key: str) -> None:
        """Update the API key at runtime (drops the cached SDK client)."""
        self.api_key = (api_key or "").strip()
        self._client = None

    @staticmethod
    def _sdk_importable() -> bool:
        try:
            from google import genai  # noqa: F401
            return True
        except Exception:
            return False

    def health_check(self) -> bool:
        """True if an API key is set and the SDK is importable. No network call."""
        if not self.api_key:
            logger.debug("Gemini health check: GEMINI_API_KEY is empty.")
            return False
        if not self._sdk_importable():
            logger.warning(
                "Gemini health check: google-genai not installed (pip install google-genai)."
            )
            return False
        return True

    # Backward-compatible alias used by older callers.
    is_available = health_check

    def _get_client(self):
        if self._client is None:
            from google import genai
            from google.genai import types

            self._client = genai.Client(
                api_key=self.api_key,
                # google-genai expects the HTTP timeout in milliseconds.
                http_options=types.HttpOptions(timeout=self.timeout * 1000),
            )
        return self._client

    # ── Generation ───────────────────────────────────────────────

    def generate(
        self,
        prompt: str,
        max_output_tokens: int = 400,
        temperature: float = 0.2,
    ) -> str:
        """
        Generate text for ``prompt``.

        Returns:
            The answer text with any leading reasoning removed.

        Raises:
            GeminiClientError: on missing key/SDK, timeout, API error, or empty output.
        """
        if not self.api_key:
            raise GeminiClientError("GEMINI_API_KEY is not set.")

        try:
            from google.genai import types
        except Exception as e:
            raise GeminiClientError("google-genai SDK is not installed.") from e

        try:
            client = self._get_client()
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=int(max_output_tokens),
                    temperature=float(temperature),
                ),
            )
        except Exception as e:
            msg = self._scrub(f"{type(e).__name__}: {e}")
            logger.warning("Gemini request failed (%s): %s", self.model_name, msg)
            raise GeminiClientError(msg) from None

        text = self._clean_output(self._extract_text(response))
        if not text:
            raise GeminiClientError("Gemini returned an empty response.")
        logger.info("Gemini generation successful (%s).", self.model_name)
        return text

    # ── Helpers ──────────────────────────────────────────────────

    @staticmethod
    def _extract_text(response) -> str:
        """Join answer parts, skipping parts the SDK marks as thoughts."""
        try:
            candidates = getattr(response, "candidates", None) or []
            if candidates:
                content = getattr(candidates[0], "content", None)
                parts = getattr(content, "parts", None) or []
                texts = [
                    p.text for p in parts
                    if getattr(p, "text", None) and not getattr(p, "thought", False)
                ]
                if texts:
                    return "".join(texts)
        except Exception:
            pass
        try:
            return getattr(response, "text", "") or ""
        except Exception:
            return ""

    @staticmethod
    def _clean_output(text: str) -> str:
        """Strip leading reasoning blocks / 'thought' preambles."""
        if not text:
            return ""
        out = text
        for pattern in _THOUGHT_BLOCK_PATTERNS:
            out = pattern.sub("", out, count=1)
        # Plain "Thought: ..." / "thought\n..." preamble followed by a blank line.
        out = re.sub(
            r"^\s*thoughts?\s*[:\n].*?\n\s*\n", "", out,
            count=1, flags=re.DOTALL | re.IGNORECASE,
        )
        return out.strip()

    def _scrub(self, message: str) -> str:
        """Remove the API key from any message before it is logged or raised."""
        if self.api_key:
            message = message.replace(self.api_key, "***")
        return re.sub(r"(key=)[^&\s]+", r"\1***", message)[:300]
