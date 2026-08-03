<p align="center">
  <h1 align="center">🩺 AROVA</h1>
  <p align="center"><strong>Offline-First Edge AI Healthcare Assistant for Anemia Screening</strong></p>
  <p align="center">
    <em>Empowering rural health workers with AI-driven preliminary anemia screening — no internet required.</em>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/PyTorch-MobileNetV3--Small-ee4c2c?logo=pytorch&logoColor=white" />
  <img src="https://img.shields.io/badge/Gradio-4.x-orange?logo=gradio" />
  <img src="https://img.shields.io/badge/TTS-Kokoro%20ONNX-green" />
  <img src="https://img.shields.io/badge/STT-Whisper-black" />
  <img src="https://img.shields.io/badge/LLM-Llama%203.2%3A1B-purple" />
  <img src="https://img.shields.io/badge/Languages-11-ff69b4" />
  <img src="https://img.shields.io/badge/License-MIT-lightgrey" />
</p>

---

## 🏥 Problem Statement

**Anemia affects over 50% of women and children in rural India** — yet access to clinical hemoglobin blood tests is limited in remote areas. Health workers need a fast, reliable, offline-capable tool to triage patients and prioritize who needs an Hb blood test most urgently.

**AROVA bridges this gap** by using the lower eyelid conjunctiva — a clinically recognized anemia indicator — analyzed by edge-deployed AI to provide instant Hb-test priority recommendations, even without internet access.

> ⚠️ **AROVA is NOT a diagnostic tool.** It provides preliminary screening support only. A clinical hemoglobin blood test is mandatory for confirmed evaluation.

---

## 🎯 What AROVA Does

| Capability | Description |
|:---|:---|
| 📸 **Conjunctiva Image Analysis** | MobileNetV3-Small binary classifier analyzes lower eyelid photos |
| 🔬 **Grad-CAM Explainability** | Visual heatmap showing WHERE the AI is focusing on the image |
| 🛡️ **Image Quality Gate** | Validates blur, brightness, resolution & skin-tone before analysis |
| 🧠 **Bayesian Risk Adjustment** | Combines image prediction with symptom data for calibrated risk |
| 🗣️ **Multilingual Voice Assistant** | Kokoro TTS + Whisper STT in 11 Indian languages |
| 📋 **Clinical PDF Reports** | Downloadable professional screening reports |
| 📱 **WhatsApp Share** | One-click sharing of screening results for health workers |
| 🤖 **LLM Summary** | Local Llama 3.2:1B generates natural language explanations |
| 🔌 **100% Offline** | No cloud dependency — runs on laptop, desktop, or Jetson |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AROVA SYSTEM                            │
│                                                                 │
│  ┌──────────────┐    ┌──────────────────────────────────────┐   │
│  │   Gradio UI   │◄──►│          Handlers (Coordinator)      │   │
│  │  (11 langs)   │    │  Orchestrates full screening flow    │   │
│  └──────────────┘    └─────────────┬────────────────────────┘   │
│                                    │                             │
│         ┌──────────────────────────┼──────────────────────┐     │
│         ▼                          ▼                      ▼     │
│  ┌──────────────┐    ┌──────────────────┐    ┌────────────────┐ │
│  │ QualityService│    │  VisionService   │    │  VoiceService  │ │
│  │ Blur/Bright/ │    │ MobileNetV3-Small│    │ Kokoro TTS     │ │
│  │ Skin-tone    │    │ + Grad-CAM       │    │ Whisper STT    │ │
│  └──────────────┘    └────────┬─────────┘    └────────────────┘ │
│                               │                                  │
│         ┌─────────────────────┼──────────────────────┐          │
│         ▼                     ▼                      ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │MedicalService│    │  LLMService  │    │ LanguageService  │   │
│  │ Symptom Parse│    │ Llama 3.2:1B │    │ 11 Languages     │   │
│  │ Care Engine  │    │ via Ollama   │    │ Full UI + Voice  │   │
│  └──────────────┘    └──────────────┘    └──────────────────┘   │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐                           │
│  │ ReportService│    │  PDFService  │                           │
│  │ Clinical Rpt │    │  fpdf2 Gen   │                           │
│  └──────────────┘    └──────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔬 AI Pipeline (5-Step Screening Flow)

```
Image Upload
     │
     ▼
┌─────────────────────────────┐
│ Step 1: 🔍 Quality Gate      │  Blur, brightness, resolution,
│                              │  skin-tone presence validation
└──────────────┬──────────────┘
               │ ✅ Pass / ❌ Reject
               ▼
┌─────────────────────────────┐
│ Step 2: ✂️ ROI + CLAHE       │  Smart crop (lower region)
│                              │  + CLAHE contrast enhancement
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ Step 3: 🧠 MobileNetV3      │  Binary classification:
│          Inference           │  Normal vs Risk
│                              │  + Bayesian symptom adjustment
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ Step 4: 🔬 Grad-CAM         │  Heatmap overlay showing
│          Explanation         │  which regions AI focused on
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ Step 5: 📋 Report + Voice    │  PDF report, LLM summary,
│          Generation          │  TTS voice readout, WhatsApp
└─────────────────────────────┘
```

---

## 🌐 Supported Languages (11)

| Language | Code | Script | Voice TTS | UI Translations |
|:---|:---|:---|:---|:---|
| 🇬🇧 English | `en` | Latin | ✅ Kokoro `af_heart` | ✅ Full |
| 🇮🇳 Hindi | `hi` | Devanagari | ✅ Kokoro `hf_beta` | ✅ Full |
| 🇵🇰 Urdu | `ur` | Nastaliq→Devanagari | ✅ Kokoro `hf_beta` | ✅ Full |
| 🇧🇩 Bengali | `bn` | Bengali | ✅ Kokoro `hf_beta` | ✅ Full |
| 🇮🇳 Marathi | `mr` | Devanagari | ✅ Kokoro `hf_beta` | ✅ Full |
| 🇮🇳 Tamil | `ta` | Tamil | ✅ Kokoro `hf_beta` | ✅ Full |
| 🇮🇳 Telugu | `te` | Telugu | ✅ Kokoro `hf_beta` | ✅ Full |
| 🇮🇳 Gujarati | `gu` | Gujarati | ✅ Kokoro `hf_beta` | ✅ Full |
| 🇮🇳 Kannada | `kn` | Kannada | ✅ Kokoro `hf_beta` | ✅ Full |
| 🇮🇳 Malayalam | `ml` | Malayalam | ✅ Kokoro `hf_beta` | ✅ Full |
| 🇮🇳 Punjabi | `pa` | Gurmukhi | ✅ Kokoro `hf_beta` | ✅ Full |

---

## 📊 Model & Dataset

### Model: MobileNetV3-Small (Binary Classifier)

| Property | Value |
|:---|:---|
| Architecture | MobileNetV3-Small (pretrained ImageNet) |
| Task | Binary classification: `Normal` vs `Risk` |
| Input Size | 224 × 224 RGB |
| Parameters | ~2.5M (edge-optimized) |
| Weight File | `mobilenetv3_small_arova_combined_binary.pth` (~6MB) |
| Inference Device | CPU / CUDA (auto-detected) |

### Combined Dataset (907 images)

| Source | Description | Images |
|:---|:---|:---|
| **CP-AnemiC** | Lower eyelid images with Hb values | 710 |
| **DS-anemia** | India/Italy data, filtered `forniceal_palpebral` | 197 |

| Split | Count |
|:---|:---|
| Train | 634 |
| Validation | 137 |
| Test | 136 |
| **Total** | **907** |

**Class Distribution:** Risk: 499 | Normal: 408

### Bayesian Risk Calibration

AROVA doesn't just use raw model probabilities — it applies **Bayesian risk adjustment**:
- If the patient reports anemia symptoms (weakness, dizziness, paleness) → full model probability used
- If asymptomatic → risk scaled by 0.60× to reduce false positives

---

## 🛡️ Image Quality Gate

Before running AI inference, AROVA validates image quality to prevent false predictions:

| Check | Method | Reject Threshold |
|:---|:---|:---|
| **Blur** | Laplacian variance | < 30.0 |
| **Brightness** | Grayscale mean | < 35 (dark) / > 240 (overexposed) |
| **Resolution** | Min dimension | < 64px |
| **Aspect Ratio** | Max ratio | > 5.0 |
| **Tissue Presence** | HSV skin-tone mask | < 5% coverage |

**Quality Grades:** ✅ GOOD (70+) → ⚠️ FAIR (40-69) → ❌ REJECTED (<40)

---

## 🔬 Grad-CAM Explainability

AROVA generates **Grad-CAM heatmap overlays** showing exactly which regions of the conjunctiva the model focused on during prediction.

- Targets the **last convolutional layer** of MobileNetV3-Small
- Generates class-specific activation maps for the "risk" class
- Overlays heatmap on original image with 55% image / 45% heatmap blend
- Displayed alongside Original and CLAHE-enhanced images in a **Visual Analysis Pipeline**

---

## 🗣️ Voice Assistant

AROVA's voice system supports both **Text-to-Speech** and **Speech-to-Text**:

| Component | Engine | Details |
|:---|:---|:---|
| **TTS** | Kokoro v1.0 ONNX | 325MB model, auto-downloaded on first run |
| **STT** | OpenAI Whisper | `tiny`/`base` model for fast transcription |
| **Fallback** | Piper TTS | Lightweight fallback if Kokoro unavailable |

**Audio Pipeline:** Text preprocessing → Medical term normalization → Urdu→Devanagari transliteration → TTS synthesis → DC offset removal → Silence trimming → Peak normalization → Anti-clipping fade

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/nitink420/Arova.git
cd Arova

# Create environment (Python 3.10 recommended)
conda create -n arova python=3.10 -y
conda activate arova

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup LLM API Endpoint (AIProff Server / Local)

Arova connects directly to the **AIProff Ollama REST API** server via HTTP. No local LLM installation is required if you are using AIProff's server!

#### Option A: AIProff Server API (Default for Hackathon)
Simply set the AIProff server URL in your `.env` file:
```env
OLLAMA_API_URL=http://<AIPROFF_SERVER_IP>:11434
OLLAMA_MODEL=llama3.2:1b
```

#### Option B: Local Offline Engine (Standalone Setup)
If running standalone without the AIProff server:
```bash
ollama run llama3.2:1b
```

> 🛡️ **Graceful Fallback:** If the API server is unreachable, AROVA automatically switches to localized rule-based summary generation — ensuring 100% crash-free operation.

### 4. NVIDIA Jetson Deployment
For deploying on **NVIDIA Jetson Orin / Nano** over SSH:
- Follow the step-by-step [JETSON_DEPLOYMENT.md](file:///e:/Arova/JETSON_DEPLOYMENT.md) guide.
- Quick setup: `chmod +x install_jetson.sh && ./install_jetson.sh && ./run_jetson.sh`


### ⚡ Auto-Bootstrap
- **TTS weights** (325MB Kokoro ONNX) auto-download on first launch
- **Audio cache** auto-generated for all voice segments
- **All folders** created programmatically — no manual setup needed

---

## 📁 Project Structure

```
Arova/
├── app/                          # Main application
│   ├── main.py                   # Entry point & service initialization
│   ├── ui.py                     # Gradio UI layout & CSS
│   ├── handlers.py               # Event coordination & screening pipeline
│   ├── core/
│   │   ├── config.py             # Central configuration
│   │   ├── logger.py             # Logging setup
│   │   └── health_check.py       # System diagnostics
│   ├── services/
│   │   ├── vision_service.py     # MobileNetV3 + Grad-CAM
│   │   ├── quality_service.py    # Image quality validation
│   │   ├── llm_service.py        # Ollama/Llama integration
│   │   ├── voice_service.py      # TTS/STT orchestrator
│   │   ├── medical_service.py    # Symptom parsing & care engine
│   │   ├── language_service.py   # 11-language localization
│   │   ├── report_service.py     # Clinical report builder
│   │   ├── pdf_service.py        # PDF generation
│   │   └── ollama_client.py      # Ollama HTTP client
│   ├── models/
│   │   └── patient.py            # Data classes
│   ├── resources/
│   │   └── speech_scripts.py     # Voice scripts for 11 languages
│   └── utils/
│       ├── image_utils.py        # CLAHE, ROI cropping
│       └── text_utils.py         # Text utilities
├── src/                          # Core ML & processing modules
│   ├── gradcam.py                # Grad-CAM implementation
│   ├── predict_mobilenet.py      # Model loading & inference
│   ├── symptom_parser.py         # Hindi/English symptom parser
│   ├── basic_care_engine.py      # Care & diet recommendations
│   ├── report_generator.py       # Report compilation
│   ├── pdf_report.py             # PDF layout engine
│   ├── voice_tts_kokoro.py       # Kokoro TTS driver
│   └── voice_speech_engine.py    # Audio preprocessing engine
├── models/
│   ├── vision/                   # MobileNetV3 weights (.pth)
│   └── tts_stt/                  # Kokoro ONNX + Whisper models
├── data/                         # Training data & labels
├── requirements.txt              # Python dependencies
└── README.md
```

---

## 🔑 Key Technical Highlights

| Feature | Implementation |
|:---|:---|
| **Edge-Optimized** | MobileNetV3-Small (~2.5M params, ~6MB weights) |
| **Graceful Degradation** | All services fail safely with stub fallbacks |
| **Privacy-First** | Zero data leaves the device — fully offline |
| **Medical Safety** | Disclaimers embedded at every output level |
| **Explainable AI** | Grad-CAM heatmaps show model focus regions |
| **Quality Assurance** | 5-check image quality gate prevents false predictions |
| **Accessible** | Voice-first design for low-literacy users |
| **Multilingual** | 11 Indian languages with native script UI + TTS |

---

## 👥 Team

**Team Name:** Edge 柱 Hashiras

---

## ⚖️ Safety & Disclaimer

> **AROVA is a preliminary screening assistant, NOT a doctor.**
> - It does not provide medical treatment, diagnoses, prescriptions, or dosages.
> - This screening is NOT a final medical diagnosis.
> - A clinical hemoglobin blood test (Hb-Test) is **mandatory** for confirmed evaluation.
> - In case of severe symptoms (breathlessness, chest pain, fainting), visit a doctor immediately.

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.