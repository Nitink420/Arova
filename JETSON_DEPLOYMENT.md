# 🚀 AROVA — AIProff Jetson Deployment Guide

Complete step-by-step deployment guide specifically tailored for **AIProff Jetson Terminal**.

---

## ⚡ Fast Track — One-Line Copy-Paste Commands

Open your **AIProff Jetson Terminal** and paste these commands in sequence:

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

## 📖 Step-by-Step Detailed Breakdown

### Step 1: Clone Repository
```bash
git clone https://github.com/Nitink420/Arova.git
cd Arova
```

---

### Step 2: Install Jetson Dependencies
Run `install_jetson.sh` to install Gradio, OpenCV, NumPy, FPDF, and Kokoro/Whisper engines:
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
Save with `Ctrl+O`, `Enter`, and exit with `Ctrl+X`.

---

### Step 4: Launch AROVA
```bash
chmod +x run_jetson.sh
./run_jetson.sh
```

When AROVA starts up, the terminal will print:

```text
====================================================================
🚀 AROVA IS ONLINE & READY (JETSON MODE)
====================================================================
💻 Local PC Link (If running directly on this laptop):
   👉 http://127.0.0.1:7860

📱 Jetson SSH / Wi-Fi Network Link (Open this in your laptop browser):
   👉 http://10.217.190.66:7860  (Works 100% Offline!)

💡 Tip for Jetson SSH Users:
   If using SSH, paste 'http://10.217.190.66:7860' in your laptop browser
====================================================================
```

---

## 🌐 Opening the Dashboard in Your Browser

1. Copy the network link displayed in the terminal:  
   👉 **`http://<JETSON_IP>:7860`** *(Example: `http://10.217.190.66:7860`)*
2. Open **Chrome / Edge / Safari** on your laptop.
3. Paste the URL into the address bar and press **Enter**.
4. The full AROVA Multilingual Screening Dashboard will load!

---

## 🏎️ Performance Boost Commands (For Hackathon Demo)

To ensure maximum GPU speed and lowest latency during your demo:

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
| **Cannot open URL in browser** | Laptop not on same network | Connect laptop and Jetson to same Wi-Fi/Hotspot |
| **Ollama timeout** | Local/remote Ollama not started | Verify `OLLAMA_API_URL` in `.env` |
