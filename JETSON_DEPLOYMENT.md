# 🚀 AROVA — NVIDIA Jetson Orin / Nano Deployment Guide

Complete step-by-step guide to deploy AROVA on an **NVIDIA Jetson Orin / Nano** edge device over SSH.

---

## 📋 Prerequisites

| Requirement | Specification |
|:---|:---|
| **Hardware** | NVIDIA Jetson Orin Nano / Orin NX / AGX Orin |
| **OS / JetPack** | NVIDIA JetPack 6.x / 5.x (Ubuntu 22.04 LTS / 20.04 LTS) |
| **CUDA PyTorch** | Pre-installed via NVIDIA JetPack wheels |
| **Network** | Same Wi-Fi / Hotspot network as your laptop |
| **SSH Access** | SSH credentials (e.g. `nvidia@192.168.x.x`) |

---

## ⚡ Step-by-Step Deployment Flow

```
Laptop (Browser)                       NVIDIA Jetson Orin (Edge AI)
┌────────────────┐                    ┌────────────────────────────┐
│ Chrome / Edge  │                    │ AROVA Backend              │
│                │ ── SSH Connect ──► │  ├── PyTorch CUDA          │
│ Open URL:      │                    │  ├── MobileNetV3 + Grad-CAM│
│ http://IP:7860 │ ◄── HTTP Server ── │  └── Kokoro ONNX + Whisper │
└────────────────┘                    └────────────────────────────┘
```

---

## 🛠️ Step 1: Connect to Jetson via SSH

From your laptop terminal (macOS/Linux/Windows PowerShell):

```bash
# Replace <JETSON_IP> with your Jetson's local IP address
ssh nvidia@<JETSON_IP>
```

> **Tip:** To find your Jetson's IP address, run `ifconfig` or `ip a` on the Jetson, or check your Wi-Fi router dashboard / hotspot connected devices list.

---

## 📥 Step 2: Clone AROVA Repository

Once logged into your Jetson terminal:

```bash
cd ~
git clone https://github.com/Nitink420/Arova.git
cd Arova
```

---

## ⚙️ Step 3: Run Jetson Automated Installer

Execute the built-in Jetson installer script. This script verifies CUDA PyTorch and installs all Python dependencies without overwriting JetPack's CUDA drivers:

```bash
chmod +x install_jetson.sh
./install_jetson.sh
```

> ⚠️ **CRITICAL NOTE:** DO NOT run `pip install torch torchvision`. JetPack comes pre-installed with CUDA-accelerated PyTorch. Running standard `pip install torch` will overwrite it with a CPU-only version.

---

## 📝 Step 4: Configure Environment (`.env`)

Copy `.env.example` to `.env` and set Jetson configuration:

```bash
cp .env.example .env
nano .env
```

Ensure the following variables are configured in `.env`:

```env
# Set environment to Jetson mode
ENVIRONMENT=jetson

# Force CUDA GPU acceleration (or auto)
DEVICE=cuda

# Configure AIProff Ollama API Server (or local Jetson Ollama)
OLLAMA_API_URL=http://<AIPROFF_SERVER_IP>:11434
OLLAMA_MODEL=llama3.2:1b

# Bind to 0.0.0.0 for network access across laptops/mobiles
GRADIO_HOST=0.0.0.0
GRADIO_PORT=7860
GRADIO_SHARE=true
```

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

---

## 🚀 Step 5: Launch AROVA on Jetson

Run the Jetson launcher script:

```bash
chmod +x run_jetson.sh
./run_jetson.sh
```

Upon launching, the terminal will display a clear startup banner:

```text
====================================================================
🚀 AROVA IS ONLINE & READY (JETSON MODE)
====================================================================
💻 Local PC Link (If running directly on this laptop):
   👉 http://127.0.0.1:7860

📱 Jetson SSH / Wi-Fi Network Link (Open this in your laptop browser):
   👉 http://192.168.1.50:7860  (Works 100% Offline!)

💡 Tip for Jetson SSH Users:
   If using SSH, paste 'http://192.168.1.50:7860' in your laptop browser
====================================================================
```

---

## 🌐 Step 6: Access Dashboard on Laptop Browser

1. Open **Chrome / Edge / Safari** on your laptop.
2. Enter your Jetson's IP address:
   ```text
   http://<JETSON_IP>:7860
   ```
   *(Example: `http://192.168.1.50:7860`)*
3. The full AROVA Multilingual Screening Dashboard will load instantly!

---

## 🔑 SSH Port Forwarding (Alternative Method)

If direct IP browsing is restricted by firewall, use **SSH Port Forwarding** from your laptop:

```bash
# Run this on your laptop terminal:
ssh -L 7860:localhost:7860 nvidia@<JETSON_IP>
```

Now open **`http://127.0.0.1:7860`** directly in your laptop browser!

---

## 🏎️ Jetson Performance Tuning

To maximize inference speed during demo:

```bash
# 1. Set Jetson to Maximum Performance Mode (MAXN)
sudo nvpmodel -m 0

# 2. Lock GPU/CPU clocks to maximum frequencies
sudo jetson_clocks
```

---

## ❓ Troubleshooting

| Issue | Cause | Solution |
|:---|:---|:---|
| `CUDA available: False` | Standard PyTorch installed | Re-install NVIDIA PyTorch wheel for JetPack |
| Browser shows `Site can't be reached` | `GRADIO_HOST` set to `127.0.0.1` | Set `GRADIO_HOST=0.0.0.0` in `.env` |
| Ollama timeout | Remote server IP unreachable | Check ping to `OLLAMA_API_URL` server |
| Out of memory (OOM) | Memory exhausted | Close unused processes or run `sudo jetson_clocks` |
