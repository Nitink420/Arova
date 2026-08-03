# app/core/config.py
"""
AROVA Central Configuration

Loads all configurable values from .env file using python-dotenv.
Provides typed access via a singleton Config class.

Every service reads configuration from this module — no os.environ.get()
scattered across the codebase.

Usage:
    from app.core.config import Config
    config = Config()
    print(config.OLLAMA_API_URL)
"""

import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """
    Singleton configuration class for the entire AROVA application.

    Loads environment variables from .env file at project root.
    Falls back to sensible defaults if .env is missing or incomplete.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # Resolve project root (two levels up from app/core/config.py)
        self.PROJECT_ROOT = Path(__file__).resolve().parents[2]

        # Load .env from project root
        env_path = self.PROJECT_ROOT / ".env"
        if env_path.exists():
            load_dotenv(str(env_path), override=True)

        # ── Environment ─────────────────────────────────────────
        self.ENVIRONMENT = os.environ.get("ENVIRONMENT", "desktop").strip().lower()
        self.LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").strip().upper()

        # ── Device ───────────────────────────────────────────────
        self.DEVICE = os.environ.get("DEVICE", "auto").strip().lower()

        # ── Feature Toggles ──────────────────────────────────────
        self.ENABLE_OLLAMA = self._parse_bool("ENABLE_OLLAMA", True)
        self.ENABLE_STT = self._parse_bool("ENABLE_STT", True)
        self.ENABLE_TTS = self._parse_bool("ENABLE_TTS", True)
        self.ENABLE_MULTILINGUAL = self._parse_bool("ENABLE_MULTILINGUAL", True)

        # ── Multilingual Configuration ───────────────────────────
        self.DEFAULT_LANGUAGE = os.environ.get("DEFAULT_LANGUAGE", "en").strip().lower()
        supp_langs_raw = os.environ.get(
            "SUPPORTED_LANGUAGES", "en,hi,bn,ta,te,gu,mr,kn,ml,pa,ur"
        )
        self.SUPPORTED_LANGUAGES = [
            lang.strip().lower() for lang in supp_langs_raw.split(",") if lang.strip()
        ]
        self.AUTO_DETECT_LANGUAGE = self._parse_bool("AUTO_DETECT_LANGUAGE", False)

        # ── Ollama LLM Configuration ─────────────────────────────
        self.OLLAMA_API_URL = os.environ.get(
            "OLLAMA_API_URL", "http://127.0.0.1:11434"
        ).strip().rstrip("/")
        self.OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b").strip()
        self.OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "30"))

        # Ollama inference options
        self.OLLAMA_OPTIONS = {
            "num_ctx": int(os.environ.get("OLLAMA_NUM_CTX", "1024")),
            "num_gpu": int(os.environ.get("OLLAMA_NUM_GPU", "1")),
            "use_mmap": True,
            "temperature": float(os.environ.get("OLLAMA_TEMPERATURE", "0.1")),
            "top_p": float(os.environ.get("OLLAMA_TOP_P", "0.8")),
            "num_predict": int(os.environ.get("OLLAMA_NUM_PREDICT", "110")),
            "num_thread": int(os.environ.get("OLLAMA_NUM_THREAD", "8")),
        }

        # ── Vision Model ─────────────────────────────────────────
        model_path_raw = os.environ.get(
            "MODEL_PATH",
            "models/vision/mobilenetv3_small_arova_combined_binary.pth"
        ).strip()
        # Support both absolute and relative paths
        model_path = Path(model_path_raw)
        if not model_path.is_absolute():
            model_path = self.PROJECT_ROOT / model_path_raw
        self.MODEL_PATH = str(model_path)

        # ── Whisper STT ───────────────────────────────────────────
        self.WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "tiny").strip()

        # ── Gradio Server ─────────────────────────────────────────
        self.GRADIO_HOST = os.environ.get("GRADIO_HOST", "0.0.0.0").strip()
        self.GRADIO_PORT = int(os.environ.get("GRADIO_PORT", "7860"))
        self.GRADIO_SHARE = self._parse_bool("GRADIO_SHARE", True)

        # ── Derived Paths ─────────────────────────────────────────
        self.OUTPUTS_DIR = self.PROJECT_ROOT / "outputs"
        self.REPORTS_DIR = self.OUTPUTS_DIR / "reports"
        self.AUDIO_DIR = self.OUTPUTS_DIR / "audio"
        self.AUDIO_CACHE_DIR = self.AUDIO_DIR / "cache"
        self.AUDIO_DYNAMIC_DIR = self.AUDIO_DIR / "dynamic"
        self.ASSETS_DIR = self.PROJECT_ROOT / "assets"

        # ── App Metadata ──────────────────────────────────────────
        self.APP_TITLE = "Arova Care - Multilingual Anemia Risk & Basic Symptom Care"
        self.APP_DESCRIPTION = (
            "Upload lower eyelid / conjunctiva photo and enter symptoms. "
            "Arova gives preliminary Hb-test priority and general care/diet guidance. "
            "It is not a final diagnosis or prescription."
        )
        self.SAFETY_NOTE = (
            "This is a preliminary screening result, not a final diagnosis. "
            "Please confirm with a clinical hemoglobin blood test."
        )

    @staticmethod
    def _parse_bool(key: str, default: bool = True) -> bool:
        """Parse a boolean environment variable (true/false/1/0/yes/no)."""
        val = os.environ.get(key, str(default)).strip().lower()
        return val in ("true", "1", "yes", "on")

    def get_device(self) -> str:
        """
        Resolve the compute device to use.

        If DEVICE=auto, detect CUDA availability.
        Otherwise, use the explicitly configured value.
        """
        if self.DEVICE == "auto":
            try:
                import torch
                return "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                return "cpu"
        return self.DEVICE

    def __repr__(self) -> str:
        return (
            f"Config(environment={self.ENVIRONMENT}, device={self.DEVICE}, "
            f"default_lang={self.DEFAULT_LANGUAGE}, supported_langs={self.SUPPORTED_LANGUAGES})"
        )
