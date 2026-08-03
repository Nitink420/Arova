# app/core/health_check.py
"""
AROVA Startup Health Check & Diagnostics

Performs comprehensive system checks at startup and displays a formatted
diagnostic summary. Helps operators quickly identify issues on Desktop
and Jetson deployments.

Usage:
    from app.core.health_check import run_health_check
    run_health_check()
"""

import sys
import time
import platform
from pathlib import Path

# Safely configure standard output to use UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.core.config import Config
from app.core.logger import get_logger

logger = get_logger(__name__)


def _check_torch():
    """Check PyTorch availability, version, CUDA status, and GPU name."""
    try:
        import torch
        torch_version = torch.__version__
        cuda_available = torch.cuda.is_available()
        gpu_name = torch.cuda.get_device_name(0) if cuda_available else "N/A"
        return {
            "torch_version": torch_version,
            "cuda_available": cuda_available,
            "gpu_name": gpu_name,
        }
    except ImportError:
        return {
            "torch_version": "NOT INSTALLED",
            "cuda_available": False,
            "gpu_name": "N/A",
        }
    except Exception as e:
        return {
            "torch_version": f"ERROR: {e}",
            "cuda_available": False,
            "gpu_name": "N/A",
        }


def _check_vision_model(config: Config):
    """Check if the vision model weights file exists."""
    model_path = Path(config.MODEL_PATH)
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        return f"OK ({size_mb:.1f} MB)"
    return "MISSING"


def _check_voice_engine():
    """Check which TTS engine is available (Kokoro → Piper → None)."""
    # Check Kokoro
    try:
        from kokoro_onnx import Kokoro  # noqa: F401
        return "Kokoro (ONNX)"
    except ImportError:
        pass

    # Check Piper
    try:
        from piper.voice import PiperVoice  # noqa: F401
        return "Piper"
    except ImportError:
        pass

    return "DISABLED (no TTS engine found)"


def _check_stt():
    """Check Whisper STT availability."""
    try:
        import whisper  # noqa: F401
        return "Whisper (available)"
    except ImportError:
        return "DISABLED (whisper not installed)"


def _check_ollama(config: Config):
    """Check Ollama API connectivity."""
    if not config.ENABLE_OLLAMA:
        return "DISABLED (ENABLE_OLLAMA=false)"

    try:
        import urllib.request
        url = config.OLLAMA_API_URL
        with urllib.request.urlopen(url, timeout=3) as response:
            if response.status == 200:
                return f"CONNECTED ({url})"
    except Exception:
        pass

    return f"UNREACHABLE ({config.OLLAMA_API_URL})"


def run_health_check() -> dict:
    """
    Execute all startup diagnostics and print a formatted summary.

    Returns:
        Dictionary containing all diagnostic results.
    """
    config = Config()
    start_time = time.time()

    # Gather diagnostics
    torch_info = _check_torch()
    vision_status = _check_vision_model(config)
    voice_status = _check_voice_engine()
    stt_status = _check_stt()
    ollama_status = _check_ollama(config)

    elapsed = time.time() - start_time
    app_url = f"http://{config.GRADIO_HOST}:{config.GRADIO_PORT}"

    # Build results dictionary
    results = {
        "python_version": platform.python_version(),
        "torch_version": torch_info["torch_version"],
        "cuda_available": torch_info["cuda_available"],
        "gpu_name": torch_info["gpu_name"],
        "device": config.get_device(),
        "vision_model": vision_status,
        "voice_engine": voice_status,
        "stt_status": stt_status,
        "ollama_status": ollama_status,
        "app_url": app_url,
        "environment": config.ENVIRONMENT,
        "startup_check_time": f"{elapsed:.2f}s",
    }

    # Format and print diagnostic table
    separator = "═" * 60
    print(f"\n{separator}")
    print("  🩺 AROVA STARTUP DIAGNOSTICS")
    print(separator)
    print(f"  Python Version     │ {results['python_version']}")
    print(f"  Torch Version      │ {results['torch_version']}")
    print(f"  CUDA Available     │ {'✅ Yes' if results['cuda_available'] else '❌ No'}")
    print(f"  GPU                │ {results['gpu_name']}")
    print(f"  Compute Device     │ {results['device'].upper()}")
    print(f"  ──────────────────────────────────────────────────────")
    print(f"  Vision Model       │ {results['vision_model']}")
    print(f"  Voice Engine       │ {results['voice_engine']}")
    print(f"  STT (Whisper)      │ {results['stt_status']}")
    print(f"  Ollama LLM         │ {results['ollama_status']}")
    print(f"  ──────────────────────────────────────────────────────")
    print(f"  Application URL    │ {results['app_url']}")
    print(f"  Public Link (Share)│ {'ENABLED (Gradio share=True)' if config.GRADIO_SHARE else 'DISABLED'}")
    print(f"  Environment        │ {results['environment'].upper()}")
    print(f"  Diagnostics Time   │ {results['startup_check_time']}")
    print(f"{separator}\n")

    logger.info("Startup diagnostics completed in %s", results["startup_check_time"])

    return results
