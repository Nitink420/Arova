# AROVA BUILD AUDIT REPORT
**Generated:** 2026-10-11  
**Project Directory:** `E:\Arova`  
**Host Environment:** Windows 10/11 64-bit (AMD Ryzen 5 5500U, AMD Radeon Graphics, 8 GB RAM, 512 GB SSD)  
**Primary Python Environment:** `C:\Users\nitinkardam\anaconda3\envs\winning_project` (Python 3.10.20 x64)

---

## 1. Executive Summary & Verification Baseline

A full inspection and execution audit of the AROVA healthcare project was performed. Every core AI component, model checkpoint, voice engine, and local runtime was tested with actual commands and verified for local offline capability.

| Component | Status | Details & Metrics |
|---|---|---|
| **Python Runtime** | ✅ VERIFIED | Python 3.10.20 x64 (`winning_project`) |
| **PyTorch (CPU)** | ✅ VERIFIED | PyTorch 2.12.0+cpu, Torchvision 0.27.0+cpu (0 CUDA requirement) |
| **Vision Model** | ✅ VERIFIED | `mobilenetv3_small_arova_combined_binary.pth` (5.93 MB / 6,221,591 bytes) |
| **Voice TTS (Kokoro)** | ✅ VERIFIED | `kokoro-v1.0.onnx` (310.45 MB) + `voices-v1.0.bin` (26.91 MB) |
| **Voice STT (Whisper)** | ✅ VERIFIED | `tiny.pt` (72.0 MB) loaded & verified offline transcription |
| **Local LLM (Ollama)** | ✅ VERIFIED | `llama3.2:1b` (1.3 GB blob) running at `http://127.0.0.1:11434` |
| **Safety Architecture** | ✅ VERIFIED | Symptom parser, red flags, Anemia Mukt Bharat protocols intact |
| **PDF Report Generation** | ✅ VERIFIED | Offline PDF generation with medical QR code verified |
| **Gradio Web Interface** | ✅ VERIFIED | Gradio 6.16.0 local UI |

---

## 2. Directory Structure & Entry Points

- **Primary Entry Points:**
  - `E:\Arova\app\app.py`: Legacy wrapper adding project root to `sys.path` and delegating to `app.main.main()`.
  - `E:\Arova\app\main.py`: Modular application entry point configuring UTF-8, loading `.env`, initializing services, warming up voice cache, running health check, and launching Gradio server on `http://127.0.0.1:7860`.
- **Subdirectories:**
  - `app/core/`: Configuration (`config.py`), logger (`logger.py`), startup diagnostics (`health_check.py`).
  - `app/services/`: Services for language, vision, LLM, voice, medical rules, PDF reports.
  - `app/resources/`: Multilingual speech scripts and UI labels.
  - `src/`: Deep learning inference (`predict_mobilenet.py`), care engine (`basic_care_engine.py`), Kokoro TTS (`voice_tts_kokoro.py`), Whisper STT (`voice_stt.py`), PDF creation (`pdf_report.py`).
  - `models/`: Trained model weights and checkpoints.
  - `outputs/`: Generated reports and voice cache.

---

## 3. Discovered Model Assets & Checkpoints

### A. Vision Model (MobileNetV3-Small Binary Classifier)
- **Path:** `E:\Arova\models\vision\mobilenetv3_small_arova_combined_binary.pth`
- **File Size:** 6,221,591 bytes (~5.93 MB)
- **Architecture:** PyTorch `mobilenet_v3_small` with final classifier linear layer adapted for binary classification (0 = normal, 1 = anemia risk indicator).
- **Inference Verification:** Successfully loaded and evaluated with `src/predict_mobilenet.py` and `verify_fixes.py`.
- **Pre-processing:** Resize to (224, 224), ImageNet mean `[0.485, 0.456, 0.406]`, std `[0.229, 0.224, 0.225]`. Sclera white balance calibration & erythema index calculation active in `src/roi_utils.py`.

### B. Voice TTS Model (Kokoro-v1.0 ONNX Engine)
- **Model ONNX Path:** `E:\Arova\models\tts_stt\kokoro\kokoro-v1.0.onnx` (325,532,387 bytes / ~310.45 MB)
- **Voices Binary Path:** `E:\Arova\models\tts_stt\kokoro\voices-v1.0.bin` (28,214,398 bytes / ~26.91 MB)
- **Runtime Dependencies:** `kokoro-onnx` 0.5.0, `espeakng-loader` 0.2.4 (native `espeak-ng.dll` and `espeak-ng-data`), `phonemizer-fork` 3.3.2.
- **Inference Verification:** Synthesized English speech file (`outputs/audio/dynamic/7432732846ab592c3ad1347585a34142.wav`) offline in 1.4s on CPU.
- **Multilingual Support:** All 11 languages (English, Hindi, Bengali, Tamil, Telugu, Gujarati, Marathi, Kannada, Malayalam, Punjabi, Urdu) mapped in `src/voice_speech_engine.py`.

### C. Speech-to-Text Model (Whisper Tiny)
- **Model Weights Path:** `E:\Arova\models\tts_stt\whisper\tiny.pt` (75,541,760 bytes / ~72.0 MB)
- **Local User Cache:** `C:\Users\nitinkardam\.cache\whisper\tiny.pt`
- **Official Weights SHA256:** `65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9`
- **Transcription Verification:** Tested offline with `soundfile` decoding; successfully transcribed audio on CPU without internet.

### D. Local Large Language Model (Ollama & Llama 3.2 1B)
- **Ollama Executable:** `C:\Users\nitinkardam\AppData\Local\Programs\Ollama\ollama.exe`
- **Ollama API Endpoint:** `http://127.0.0.1:11434`
- **Active Model:** `llama3.2:1b` (ID: `baf6a787fdff`)
- **Manifest:** `C:\Users\nitinkardam\.ollama\models\manifests\registry.ollama.ai\library\llama3.2\1b`
- **Layers & Blobs:**
  - Model weights blob: `sha256:74701a8c35f6c8d9a4b91f3f3497643001d63e0c7a84e085bed452548fa88d45` (1,321,082,688 bytes ~ 1.3 GB)
  - Config: `sha256:4f659a1e86d7f5a33c389f7991e7224b7ee6ad0358b53437d54c02d2e1b1118d` (485 B)
  - Template: `sha256:966de95ca8a62200913e3f8bfbf84c8494536f1b94b49166851e76644e966396` (1,429 B)
  - License: `sha256:fcc5a6bec9daf9b561a68827b67ab6088e1dba9d1fa2a50d7bbcc8384e0a265d` (7,711 B)
  - License: `sha256:a70ff7e570d97baaf4e62ac6e6ad9975e04caa6d900d3742d37698494479e0cd` (6,016 B)
- **Inference Verification:** Responded HTTP 200 to prompt in <1.2s locally on CPU.
- **Redistribution & Licensing:** Llama 3.2 is subject to Meta's Llama 3.2 Community License Agreement. The bundled distribution includes automated Ollama deployment and model blob seeding so the target machine can run 100% offline.

### E. Piper TTS Status
- `models/tts_stt/piper/voice.onnx.json` is present (4.8 KB). No `.onnx` model weights are present.
- Piper is an optional fallback; Kokoro TTS is the primary and fully functional TTS engine. Piper is documented as optional and omitted from bulky packaging to save disk space.

---

## 4. Safety & Clinical Integrity Audit

- **Core Rule Engine:** `src/basic_care_engine.py` implements the Anemia Mukt Bharat (AMB) guideline triage (Mild, Moderate, Severe, Non-anemic).
- **Red Flag Interceptors:** Detects severe symptoms (chest pain, shortness of breath, severe fainting, high fever) and forces urgent medical consultation warnings.
- **Prescription Prohibition:** Enforced in `src/llm_assistant.py` (system prompt explicitly forbids drug dosages or prescriptions; enforces dietary guidance and blood test recommendation).
- **Data Privacy:** All inference and reports remain 100% on the local workstation (`127.0.0.1`); no cloud transmission occurs when in desktop offline mode.

---

## 5. Packaging & Distribution Plan

1. **Standalone Portable Bundle (`release\AROVA-Portable\`):**
   - Self-contained Python 3.10 runtime + compiled application launcher (`AROVA.exe`).
   - Bundled PyTorch CPU, Torchvision, ONNX Runtime, OpenCV, Kokoro, Whisper, Gradio, FPDF2.
   - Bundled model checkpoints:
     - `models\vision\mobilenetv3_small_arova_combined_binary.pth`
     - `models\tts_stt\kokoro\kokoro-v1.0.onnx`
     - `models\tts_stt\kokoro\voices-v1.0.bin`
     - `models\tts_stt\whisper\tiny.pt`
   - Bundled Ollama setup helper & `llama3.2:1b` model manifest/blobs.
2. **Windows Installer (`release\AROVA-Setup.exe`):**
   - Installs AROVA into `%LOCALAPPDATA%\AROVA` or Program Files.
   - Creates Start Menu & Desktop shortcuts.
   - Sets up local Ollama runtime and pre-provisions `llama3.2:1b` blobs without internet connection.
   - Uninstaller preserves patient reports and user database.
