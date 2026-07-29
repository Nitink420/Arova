# src/llm_assistant.py

import json
import requests
import subprocess
import urllib.request
import time
import os

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"

def ensure_ollama_running():
    """
    Checks if Ollama service is active. If not, auto-starts the Ollama server programmatically in the background.
    """
    print("[INFO] Checking if Ollama server is running...")
    try:
        # Check if Ollama is listening on localhost:11434
        with urllib.request.urlopen("http://localhost:11434", timeout=2) as response:
            if response.status == 200:
                print("[INFO] Ollama server is already running.")
                return True
    except Exception:
        print("[INFO] Ollama server is not running. Attempting to start it in the background...")
        try:
            # On Windows, start 'ollama serve' hidden in background
            popen_kwargs = {
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
            }
            if os.name == 'nt':
                # CREATE_NO_WINDOW = 0x08000000
                popen_kwargs["creationflags"] = 0x08000000
                
            subprocess.Popen(
                ["ollama", "serve"],
                **popen_kwargs
            )
            
            # Wait for Ollama to spin up
            for i in range(10):
                time.sleep(1)
                try:
                    with urllib.request.urlopen("http://localhost:11434", timeout=1) as resp:
                        if resp.status == 200:
                            print("[INFO] Ollama server started successfully in the background.")
                            return True
                except Exception:
                    pass
            print("[WARNING] Ollama serve command was sent, but port 11434 is not active yet.")
            return False
        except Exception as e:
            print(f"[ERROR] Failed to launch Ollama: {e}")
            return False



def build_safe_prompt(arova_report):
    """
    Constructs a highly compact, structured prompt for instant LLM inference (<5 seconds).
    """
    if isinstance(arova_report, dict):
        name = arova_report.get("name", "Patient")
        symptoms = arova_report.get("symptoms", "None")
        risk = arova_report.get("risk_percent", 0.0)
        priority = arova_report.get("hb_test_priority", "Low")
        summary_text = f"Patient: {name}, Symptoms: {symptoms}, Eye Risk Indicator: {risk}%, Priority: {priority}"
    else:
        # If markdown string passed, extract concise snippet
        summary_text = str(arova_report)[:400]

    return f"""You are Arova Healthcare Assistant. Explain this screening report in simple, polite, easy-to-understand Hinglish in 4 short bullet points.

Screening Data:
{summary_text}

Rules:
1. "Risk indicator" is an image-based screening signal, NOT final Hb blood level.
2. Hb blood test is mandatory for clinical confirmation.
3. Suggest iron-rich vegetables (Palak, Beetroot) & fruits (Anar, Amrood).
4. No medicine or dosage prescriptions.

Write response in this clean bullet format:
- 📊 Screening Summary: ...
- ⚠️ Important Safety: ...
- 🩸 Hb Test Advice: ...
- 🍎 Nutrition & Diet: ..."""


def safety_filter(text):
    bad_phrases = [
        "you have anemia",
        "anemia confirmed",
        "hb level is",
        "hb level:",
        "prescribe",
        "dosage",
        "antibiotic",
        "injection",
        "steroid"
    ]

    lower_text = text.lower()

    for phrase in bad_phrases:
        if phrase in lower_text:
            text += (
                "\n\nSafety correction: Risk percentage Hb level nahi hota. "
                "Yeh sirf photo-based screening signal hai. "
                "Hb blood test se confirmation zaroori hai."
            )
            break

    if "hb blood test" not in lower_text and "hb test" not in lower_text:
        text += "\n- 🩸 Hb blood test se confirmation zaroori hai."

    return text


def ask_llama(arova_report):
    ensure_ollama_running()
    prompt = build_safe_prompt(arova_report)

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.8,
            "num_predict": 110,
            "num_thread": 8
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()
        answer = data.get("response", "No response from Llama.")
        return safety_filter(answer)

    except requests.exceptions.ConnectionError:
        return (
            "Ollama server connect nahi ho paaya. "
            "Please ek PowerShell me run karo: ollama run llama3.2:1b"
        )

    except Exception as e:
        return f"Llama error: {e}"


def ask_llama_stream(arova_report):
    """
    High-speed Ollama streaming interface (<5 seconds execution).
    """
    ensure_ollama_running()
    prompt = build_safe_prompt(arova_report)

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": 0.1,
            "top_p": 0.8,
            "num_predict": 110,
            "num_thread": 8
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=30)
        response.raise_for_status()

        accumulated_text = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line.decode('utf-8'))
                token = chunk.get("response", "")
                accumulated_text += token
                done = chunk.get("done", False)
                if done:
                    yield safety_filter(accumulated_text)
                else:
                    yield accumulated_text

    except requests.exceptions.ConnectionError:
        yield (
            "Ollama server connect nahi ho paaya. "
            "Please ek PowerShell me run karo: ollama run llama3.2:1b"
        )

    except Exception as e:
        yield f"Llama error: {e}"


if __name__ == "__main__":
    test_report = """
Symptoms: fever, weakness, dizziness
Anemia Risk Indicator: 76.5%
Hb-test Priority: Medium / Hb-test recommended
Diet advice: iron-rich foods, fluids, light food
Warning signs: severe weakness or breathlessness ho toh doctor visit karein
Safety: This is preliminary screening, not final diagnosis.
"""
    print(ask_llama(test_report))