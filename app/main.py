# app/main.py
"""
AROVA Multilingual Application Entry Point

Clean startup sequence:
1. Configure UTF-8 output
2. Load .env configuration
3. Set up centralized logging
4. Initialize all services (Vision, LLM, Voice, Medical, PDF, Report, Language)
5. Warm up voice cache across supported languages
6. Run startup health check
7. Create Gradio UI with startup Language Selection screen
8. Launch application server

Usage:
    python app/main.py
"""

import sys
import time
import socket
from pathlib import Path

# ─── Step 0: UTF-8 Output ───────────────────────────────────────────────
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ─── Step 1: Python Path & Config Import ────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import Config


def main():
    """
    Main application entry point.
    """
    startup_start = time.time()

    # ─── Step 2: Configuration ───────────────────────────────────────
    from app.core.config import Config
    config = Config()

    # ─── Step 3: Logging ─────────────────────────────────────────────
    from app.core.logger import setup_logging, get_logger
    setup_logging()
    logger = get_logger("main")

    logger.info("=" * 60)
    logger.info("AROVA Multilingual AI Healthcare Assistant — Starting Up")
    logger.info("Environment: %s | Default Language: %s", config.ENVIRONMENT.upper(), config.DEFAULT_LANGUAGE.upper())
    logger.info("Supported Languages: %s", ", ".join(config.SUPPORTED_LANGUAGES))
    logger.info("=" * 60)

    # ─── Step 4: Initialize Services ─────────────────────────────────

    # 4a. Language Service
    logger.info("Initializing LanguageService...")
    from app.services.language_service import LanguageService
    language_service = LanguageService()

    # 4b. Vision Service (MobileNetV3 + CUDA)
    logger.info("Initializing VisionService...")
    try:
        from app.services.vision_service import VisionService
        vision_service = VisionService()
    except Exception as e:
        logger.error("VisionService failed to initialize: %s", e)
        vision_service = None

    # 4c. LLM Service (Ollama client + safety)
    logger.info("Initializing LLMService...")
    try:
        from app.services.llm_service import LLMService
        llm_service = LLMService()
    except Exception as e:
        logger.error("LLMService failed to initialize: %s", e)
        llm_service = None

    # 4d. Voice Service
    logger.info("Initializing VoiceService...")
    try:
        from app.services.voice_service import VoiceService
        voice_service = VoiceService()
    except Exception as e:
        logger.error("VoiceService failed to initialize: %s", e)
        voice_service = None

    # 4e. Medical Service
    logger.info("Initializing MedicalService...")
    from app.services.medical_service import MedicalService
    medical_service = MedicalService()

    # 4f. PDF Service
    logger.info("Initializing PDFService...")
    from app.services.pdf_service import PDFService
    pdf_service = PDFService()

    # 4g. Report Service
    logger.info("Initializing ReportService...")
    from app.services.report_service import ReportService
    report_service = ReportService()

    # ─── Step 5: Warm Up Multilingual Voice Cache ─────────────────────
    if voice_service is not None:
        voice_service.warm_up_cache()

    # ─── Step 6: Health Check ────────────────────────────────────────
    from app.core.health_check import run_health_check
    run_health_check()

    # ─── Step 7: Create Handlers & UI ────────────────────────────────
    from app.handlers import Handlers
    from app.ui import create_ui

    # Graceful degradation stubs if services failed
    if vision_service is None:
        logger.warning("VisionService unavailable. Creating stub.")
        class _StubVisionService:
            def predict(self, *args, **kwargs):
                return {"error": True, "message": "Vision model failed to load at startup."}
        vision_service = _StubVisionService()

    if llm_service is None:
        logger.warning("LLMService unavailable. Using stub with rule-based fallback.")
        class _StubLLMService:
            is_available = False
            def explain(self, report, lang="en"):
                return medical_service.get_fallback_explanation(lang=lang)
            def explain_stream(self, report, lang="en"):
                yield self.explain(report, lang=lang)
        llm_service = _StubLLMService()

    if voice_service is None:
        logger.warning("VoiceService unavailable. Creating disabled stub.")
        class _StubVoiceService:
            tts_available = False
            stt_available = False
            def get_cached_voice(self, name, lang="en"):
                return None
            def transcribe(self, audio_path):
                return ""
            def speak_dynamic_report(self, **kwargs):
                return None
            def generate_name_audio(self, name, lang="en"):
                return None
            def warm_up_cache(self):
                pass
            def speak(self, text, output_name, cache=True, lang="en"):
                return None
        voice_service = _StubVoiceService()

    handlers = Handlers(
        vision_service=vision_service,
        llm_service=llm_service,
        voice_service=voice_service,
        medical_service=medical_service,
        pdf_service=pdf_service,
        report_service=report_service,
        language_service=language_service,
        config=config,
    )

    demo, custom_css = create_ui(handlers)

    # ─── Step 8: Launch ──────────────────────────────────────────────
    startup_elapsed = time.time() - startup_start
    logger.info("Total startup time: %.2fs", startup_elapsed)
    logger.info(
        "Launching Multilingual AROVA at http://%s:%d (Public Link Sharing=%s)",
        config.GRADIO_HOST,
        config.GRADIO_PORT,
        config.GRADIO_SHARE,
    )

    demo.launch(
        server_name=config.GRADIO_HOST,
        server_port=config.GRADIO_PORT,
        share=config.GRADIO_SHARE,
        allowed_paths=[str(PROJECT_ROOT)],
        css=custom_css,
    )


def get_local_ip() -> str:
    """Get local network IP address (Wi-Fi/LAN) for offline device sharing."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


if __name__ == "__main__":
    local_ip = get_local_ip()
    port = Config().GRADIO_PORT
    env_name = Config().ENVIRONMENT.upper()

    print("\n" + "=" * 68)
    print(f"🚀 AROVA IS ONLINE & READY ({env_name} MODE)")
    print("=" * 68)
    print("💻 Local PC Link (If running directly on this laptop):")
    print(f"   👉 http://127.0.0.1:{port}\n")
    print("📱 Jetson SSH / Wi-Fi Network Link (Open this in your laptop browser):")
    print(f"   👉 http://{local_ip}:{port}  (Works 100% Offline!)\n")
    print("💡 Tip for Jetson SSH Users:")
    print(f"   If using SSH, paste 'http://{local_ip}:{port}' in your laptop browser,")
    print(f"   OR use SSH port forwarding: ssh -L {port}:localhost:{port} user@{local_ip}")
    print("=" * 68 + "\n")

    main()
