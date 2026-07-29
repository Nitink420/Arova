# Arova

## Offline Edge AI Hb-Test Prioritization Assistan

Arova is an offline Edge AI-powered healthcare screening assistant for preliminary anemia screening support using lower eyelid / conjunctiva images.

It helps estimate:

- Hb-test priority: Low / Medium / High
- Anemia risk indicator percentage
- Image quality status
- Symptom-based safety recommendation
- Grad-CAM visual explanation
- Simple screening report

> Important: Arova is not a diagnostic tool.  
> It does not confirm or rule out anemia.  
> Please confirm with a clinical hemoglobin blood test.

---

## Team

Team Name: Edge 柱 Hashiras

---

## Problem Statement

Anemia is a common health issue, especially in low-resource areas where quick hemoglobin testing may not always be available.

Arova aims to support early screening workflows by helping health workers prioritize people for clinical hemoglobin blood test confirmation.

Arova does not replace doctors, labs, or clinical blood tests.

---

## Project Goal

The goal of Arova is to create an offline AI assistant that can:

1. Analyze lower eyelid / conjunctiva images
2. Estimate anemia risk indicator score
3. Suggest Hb-test priority
4. Combine image result with symptom input
5. Generate safe recommendation
6. Show Grad-CAM heatmap for visual explanation
7. Work locally without cloud dependency

---

## Current Features

- Image upload support
- Optional manual ROI / cropped lower eyelid image upload
- Automatic ROI crop support
- CLAHE image enhancement
- Image quality check
- MobileNetV3-Small binary classifier
- Combined Dataset 1 + Dataset 2 training
- Normal indicator percentage
- Anemia risk indicator percentage
- Hb-test priority: Low / Medium / High
- Symptom input support
- Hindi / Hinglish symptom keyword support
- Grad-CAM heatmap preview
- Arova screening report output
- Safe medical wording

---

## Safety Statement

Arova provides preliminary screening support only.

It should always show this safety note:

> This is a preliminary screening result, not a final diagnosis.  
> Please confirm with a clinical hemoglobin blood test.

Arova must never claim to diagnose anemia.

---

## Dataset Summary

### Dataset 1: CP-AnemiC

Dataset 1 contains lower eyelid images with hemoglobin and severity information.

Class distribution:

- Normal: 286
- Mild: 144
- Moderate: 232
- Severe: 48

For binary classification:

- Normal = normal
- Mild + Moderate + Severe = risk

Total images: 710

### Dataset 2: DS-anemia

Dataset 2 contains India and Italy data with Hgb values and multiple image variants.

Useful columns:

- Number
- Hgb
- Gender
- Age
- Note

Filtered Dataset 2:

- Used only `forniceal_palpebral` images
- Removed duplicate paths
- Final filtered images: 197

Class distribution after filtering:

- Normal: 122
- Risk: 75

---

## Combined Dataset

Dataset 1 and filtered Dataset 2 were merged.

Final combined dataset:

- Total rows: 907
- Risk: 499
- Normal: 408

Split:

- Train: 634
- Validation: 137
- Test: 136

---

## Model

Model used:

```text
MobileNetV3-Small
```

---

## 🚀 Quick Start & Deployment Guide

This project is built to work fully offline at the edge. Follow these simple steps to deploy and run it locally:

### 1. Clone the Repository
```bash
git clone https://github.com/nitink420/Arova.git
cd Arova
```

### 2. Install Dependencies
Create a virtual environment (Python 3.10 recommended) and install the packages listed in `requirements.txt`:
```bash
# Using Conda
conda create -n arova python=3.10 -y
conda activate arova

# Install pip requirements
pip install -r requirements.txt
```

### 3. Setup Ollama (Llama Assistant)
To run the dynamic explanation summary card, install **Ollama** on your machine ([ollama.com](https://ollama.com/)), and run the following command to download the 1.8GB language model:
```bash
ollama run llama3.2:1b
```
*(Note: Arova will automatically detect and start your local Ollama server in the background at runtime).*

### 4. Run the Dashboard
Simply execute the Gradio application script:
```bash
python app/app.py
```

---

## ⚡ Automatic Bootstrap (No manual models needed!)
- **TTS Weights Auto-Download**: The large 325MB Kokoro ONNX weights are excluded from Git to keep cloning fast. On the very first launch, Arova's built-in bootstrapper will **automatically download** the model weights (`kokoro-v1.0.onnx` and `voices-v1.0.bin`) from a secure mirror with progress logs.
- **Audio Cache Auto-Generation**: At first startup, Arova compiles and pre-caches the 17 Devanagari Hindi vocal segments dynamically on your machine.
- All folders (such as output audios and reports PDFs) are created programmatically at startup. No folders will fail due to Git exclusions.