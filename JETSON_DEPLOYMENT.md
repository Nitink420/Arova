# 🚀 AROVA — AIProff Web Terminal Jetson Deployment Guide

Complete deployment guide for running AROVA inside **AIProff Browser-based Web Terminal**.

---

## ⚡ Fast Track — Copy-Paste Commands

Open your **AIProff Browser Terminal** tab and run these commands:

```bash
# 1. Clone AROVA Repository & enter project folder
git clone https://github.com/Nitink420/Arova.git && cd Arova

# 2. Run automated Jetson installer (Installs dependencies without overwriting JetPack CUDA PyTorch)
chmod +x install_jetson.sh && ./install_jetson.sh

# 3. Create configuration file (.env)
cp .env.example .env

# 4. Launch AROVA Healthcare Assistant
chmod +x run_jetson.sh && ./run_jetson.sh
```

---

## 🌐 How to Open the Dashboard on Your Browser

When running inside AIProff's Web Terminal, Gradio will print a **Gradio Live Public Link**:

```text
====================================================================
🚀 AROVA IS ONLINE & READY (JETSON MODE)
====================================================================
Running on local URL: http://0.0.0.0:7860
Running on public URL: https://a1b2c3d4e5f6.gradio.live

💡 Open the Public Link in a new tab on your browser:
   👉 https://a1b2c3d4e5f6.gradio.live
====================================================================
```

### 🎯 Steps to Open:
1. Look for the `https://xxxxxx.gradio.live` link in the terminal output.
2. Open a **new tab** in your browser.
3. Paste the `https://xxxxxx.gradio.live` URL and press **Enter**.
4. The full AROVA Multilingual Screening Dashboard will load!

---

## 📖 Step-by-Step Detailed Breakdown

### Step 1: Clone Repository
```bash
git clone https://github.com/Nitink420/Arova.git
cd Arova
```

---

### Step 2: Install Jetson Dependencies
Run `install_jetson.sh` to set up Gradio, OpenCV, NumPy, FPDF, Kokoro ONNX, and Whisper:
```bash
chmod +x install_jetson.sh
./install_jetson.sh
```

> ⚠️ **CRITICAL NOTE:** Do NOT run `pip install torch torchvision`. JetPack comes pre-installed with CUDA-accelerated PyTorch. `install_jetson.sh` safely preserves CUDA acceleration.

---

### Step 3: Setup Environment (`.env`)
Create the `.env` file from example:
```bash
cp .env.example .env
```

If you need to edit AIProff Ollama API URL or custom settings:
```bash
nano .env
```
Default configuration pre-configured in `.env`:
```env
ENVIRONMENT=jetson
DEVICE=cuda
OLLAMA_API_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:1b
GRADIO_HOST=0.0.0.0
GRADIO_PORT=7860
GRADIO_SHARE=true
```

---

### Step 4: Launch AROVA
```bash
chmod +x run_jetson.sh
./run_jetson.sh
```

---

## 🏎️ Performance Boost Commands (For Hackathon Demo)

To ensure maximum GPU speed during your demo:

```bash
# 1. Set Jetson to Maximum Performance Mode (MAXN)
sudo nvpmodel -m 0

# 2. Lock CPU and GPU clocks to maximum frequencies
sudo jetson_clocks
```

---

## ❓ Common Troubleshooting

| Problem | Cause | Solution |
|:---|:---|:---|
| **Port 7860 in use** | Previous instance still running | Run `fuser -k 7860/tcp` to free port |
| **CUDA not detected** | PyTorch imported incorrectly | Run `./install_jetson.sh` to verify CUDA |
| **Gradio share link slow** | Tunnel starting up | Wait 5 seconds for `gradio.live` link to appear |
| **Ollama timeout** | Local/remote Ollama not started | Verify `OLLAMA_API_URL` in `.env` |
