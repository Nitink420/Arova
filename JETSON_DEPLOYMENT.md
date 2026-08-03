# 🚀 AROVA — AIProff Jetson Simple Deployment Guide

Simple step-by-step terminal commands to deploy AROVA on AIProff Jetson.

---

## ⚡ 4-Step Quick Commands

Copy and paste these commands step-by-step into your terminal:

```bash
# Step 1: Clone repository & enter folder
git clone https://github.com/Nitink420/Arova.git
cd Arova

# Step 2: Install dependencies for Jetson
pip install -r requirements-jetson.txt

# Step 3: Create configuration file
cp .env.example .env

# Step 4: Run AROVA
python app/main.py
```

---

## 🌐 Opening AROVA in Your Browser

When `python app/main.py` finishes starting up, the terminal will print:

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

### Steps to open:
1. Copy the `https://xxxxxx.gradio.live` link from the terminal.
2. Open a **new tab** in your browser.
3. Paste the URL and press **Enter**.
4. The full AROVA Multilingual Healthcare Assistant will open!

---

## 💡 Notes for Jetson Deployment

- **`requirements-jetson.txt`** is specially designed for Jetson: it installs all packages (Gradio, OpenCV, Kokoro TTS, Whisper STT) **without touching NVIDIA's pre-installed CUDA PyTorch**.
- If port 7860 is busy, free it with: `fuser -k 7860/tcp`
