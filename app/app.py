# app/app.py

import sys
import datetime
from pathlib import Path
import os
import threading
import hashlib
import gradio as gr

# Safely configure standard output to use UTF-8 to prevent encoding crashes on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Local app config
from config import APP_TITLE, APP_DESCRIPTION, SAFETY_NOTE

# Arova core modules
from src.predict_mobilenet import load_model, predict_image
from src.symptom_parser import parse_symptoms
from src.basic_care_engine import get_basic_care
from src.llm_assistant import ask_llama_stream, ensure_ollama_running
from src.voice_stt import transcribe_audio

# Cache systems
from src.voice_cache import ensure_voice_cache, get_cached_voice

# Flow modules
from src.consultation_flow import (
    start_consultation, submit_name, submit_age, submit_symptoms, get_time_based_closing_audio,
    GREETING, ASK_NAME, ASK_AGE, ASK_SYMPTOMS, ASK_IMAGE, READY_FOR_ANALYSIS, ANALYSIS, REPORT_READY, CLOSING
)
from src.voice_engine_offline import generate_arova_speech, generate_dynamic_ask_age, generate_dynamic_report_speech, DYNAMIC_DIR
from src.report_generator import build_professional_report
from src.pdf_report import create_pdf_report

# Load MobileNet model once when dashboard starts
model = load_model()

# Ensure Ollama server is running in the background on startup
ensure_ollama_running()

# Pre-generate and load cached audio files at startup
print("[INFO] Warm up voice cache at startup...")
ensure_voice_cache()


# -----------------------------
# Onboarding Guided Handlers
# -----------------------------

def handle_start_consultation(state):
    """
    Triggers when user clicks 'Start Arova Voice'.
    Resets the state, plays intro.wav, unlocks Name input, and locks all other inputs.
    """
    state["step"] = ASK_NAME
    state["patient"] = {"name": "", "age": "", "symptoms": ""}
    state["conversation"] = ""
    audio = get_cached_voice("intro")
    transcript_html = "<div class='transcript-box'>💬 AROVA: Namaste ji. Main Arova hoon... Main aapki rural health screening mein madad karne ke liye yahan hoon... Kripya apna naam batayein.</div>"
    return (
        audio,
        state,
        transcript_html,
        gr.update(value="", interactive=True), # name_input
        gr.update(interactive=True),           # submit_name_btn
        gr.update(value="", interactive=False),# age_input
        gr.update(interactive=False),          # submit_age_btn
        gr.update(value="", interactive=False),# text_input
        gr.update(interactive=False),          # voice_input (mic)
        gr.update(interactive=False),          # submit_symptoms_btn
        gr.update(value=None, interactive=False) # image_input
    )


def generate_name_audio_bg(name):
    """
    Synthesizes the name audio file with 'G' honorific in a background daemon thread
    so it is ready by the time screening executes (0s lag at report screen).
    """
    try:
        name_clean = name.strip()
        name_spoken = f"{name_clean} G" if not name_clean.lower().endswith(" g") else name_clean
        name_hash = hashlib.md5(name_spoken.encode('utf-8')).hexdigest()
        name_audio_path = DYNAMIC_DIR / f"name_{name_hash}.wav"
        if not name_audio_path.exists():
            generate_arova_speech(name_spoken, str(name_audio_path), cache=False)
            print(f"[BG-INFO] Background name synthesis completed for '{name_spoken}'")
    except Exception as e:
        print("[BG-ERROR] Background name synthesis failed:", e)


def handle_submit_name(name, state):
    """
    Saves patient name, plays ask_age.wav, locks Name input, and unlocks Age input.
    Launches a daemon thread to synthesize the name audio in the background.
    """
    name_clean = name.strip() if name else ""
    if not name_clean:
        return (
            None,
            state,
            "<div class='transcript-box'>💬 AROVA: Please provide a valid name. / कृपया नाम दर्ज करें।</div>",
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=False),
            gr.update(interactive=False)
        )
    state["patient"]["name"] = name_clean
    state["step"] = ASK_AGE
    audio = get_cached_voice("ask_age")
    transcript_html = f"<div class='transcript-box'>💬 AROVA: Dhanyavaad {name_clean} G. Kripya apni age batayein.</div>"

    # Start background name synthesis thread to avoid UI lag
    bg_thread = threading.Thread(target=generate_name_audio_bg, args=(name_clean,))
    bg_thread.daemon = True
    bg_thread.start()

    return (
        audio,
        state,
        transcript_html,
        gr.update(interactive=False), # lock name
        gr.update(interactive=False), # lock submit name
        gr.update(interactive=True),  # unlock age
        gr.update(interactive=True)   # unlock submit age
    )


def handle_submit_age(age, state):
    """
    Saves patient age, plays ask_symptoms.wav, locks Age input, and unlocks Symptoms inputs.
    """
    age_clean = age.strip() if age else ""
    if not age_clean:
        return (
            None,
            state,
            "<div class='transcript-box'>💬 AROVA: Please provide a valid age. / कृपया उम्र दर्ज करें।</div>",
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=False)
        )
    state["patient"]["age"] = age_clean
    state["step"] = ASK_SYMPTOMS
    audio = get_cached_voice("ask_symptoms")
    transcript_html = "<div class='transcript-box'>💬 AROVA: Dhanyavaad. Ab kripya symptoms batayein. Jaise weakness, dizziness...</div>"
    return (
        audio,
        state,
        transcript_html,
        gr.update(interactive=False), # lock age
        gr.update(interactive=False), # lock submit age
        gr.update(interactive=True),  # unlock symptoms textbox
        gr.update(interactive=True),  # unlock symptoms mic recorder
        gr.update(interactive=True)   # unlock submit symptoms btn
    )


def handle_submit_symptoms(symptoms, state):
    """
    Saves symptoms, plays ask_image.wav, locks Symptoms inputs, and unlocks Image Upload.
    """
    s_clean = symptoms.strip() if symptoms else ""
    state["patient"]["symptoms"] = s_clean
    state["step"] = ASK_IMAGE
    audio = get_cached_voice("ask_image")
    transcript_html = "<div class='transcript-box'>💬 AROVA: Symptoms note kar liye gaye hain. Ab kripya lower eyelid ki clear photo upload karein.</div>"
    return (
        audio,
        state,
        transcript_html,
        gr.update(interactive=False), # lock symptoms textbox
        gr.update(interactive=False), # lock symptoms mic recorder
        gr.update(interactive=False), # lock submit symptoms btn
        gr.update(interactive=True)   # unlock image upload widget
    )


def transcribe_only(audio_path):
    """
    Transcribes audio to text for dynamic voice detection.
    """
    if audio_path is None:
        return ""
    transcription = transcribe_audio(audio_path)
    if transcription.startswith("VOICE_TRANSCRIPTION_ERROR"):
        print("Whisper transcription warning:", transcription)
        return ""
    return transcription


def make_gauge_html(priority, risk_percent):
    if "High" in priority:
        rotation = 60
        status = "High"
        color = "#ef4444"
        wording = "Immediate Hb-test strongly recommended"
    elif "Medium" in priority:
        rotation = 0
        status = "Medium"
        color = "#2563eb"  # Premium blue matching mockup
        wording = "Suggested Hb-test within 48 hours"
    else:
        rotation = -60
        status = "Low"
        color = "#10b981"
        wording = "No immediate Hb-test needed"

    return f"""
    <div class="gauge-container">
        <span class="gauge-title">Hb-Test Priority Gauge</span>
        <svg width="220" height="120" viewBox="0 0 220 120">
            <!-- Background Arc -->
            <path d="M 30 110 A 80 80 0 0 1 190 110" fill="none" stroke="#e2e8f0" stroke-width="14" stroke-linecap="round"/>
            <!-- Sectors (Low = Green, Med = Orange, High = Red) -->
            <path d="M 30 110 A 80 80 0 0 1 83.3 56.7" fill="none" stroke="#10b981" stroke-width="14"/>
            <path d="M 83.3 56.7 A 80 80 0 0 1 136.7 56.7" fill="none" stroke="#f59e0b" stroke-width="14"/>
            <path d="M 136.7 56.7 A 80 80 0 0 1 190 110" fill="none" stroke="#ef4444" stroke-width="14"/>
            
            <!-- Needle -->
            <line x1="110" y1="110" x2="110" y2="50" stroke="#1e293b" stroke-width="4" stroke-linecap="round" style="transform-origin: 110px 110px; transform: rotate({rotation}deg); transition: transform 1s ease-out;"/>
            <circle cx="110" cy="110" r="8" fill="#1e293b"/>
            
            <!-- Labels -->
            <text x="35" y="118" font-size="9" font-weight="700" fill="#64748b" text-anchor="middle">LOW</text>
            <text x="110" y="32" font-size="9" font-weight="700" fill="#64748b" text-anchor="middle">MED</text>
            <text x="185" y="118" font-size="9" font-weight="700" fill="#64748b" text-anchor="middle">HIGH</text>
        </svg>
        <h2 style="font-size: 2.6rem; font-weight: 800; color: {color}; margin-top: 12px; margin-bottom: 2px; text-align: center; text-transform: capitalize;">{status}</h2>
        <span style="font-size: 0.95rem; color: #64748b; font-weight: 600; text-align: center; display: block;">{wording}</span>
    </div>
    """


def make_care_html(care_result):
    if not care_result:
        return ""
        
    care_list = care_result.get("care", [])
    diet_list = care_result.get("diet", [])
    
    html = """
    <div style="margin-top: 20px; border-top: 1px solid #e2e8f0; padding-top: 16px;">
        <div style="font-size: 1.1rem; font-weight: 700; color: #1e3a8a; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
            <span style="color: #2563eb; font-size: 1.2rem;">➕</span> Care & Nutrition Guidance / पोषण सलाह
        </div>
        <div class="care-item-green">
            <span class="care-item-icon" style="color: #10b981;">🍎</span>
            <div>
                <p class="care-item-title">Fruits & Vegetables / पोषण से भरपूर फल & सब्जियां</p>
                <p class="care-item-subtitle">Palak, Chukandar (beetroot), Methi, Anar (pomegranate), Amrood (guava), Nimbu, Amla, Apple, Oranges.</p>
            </div>
        </div>
        <div class="care-item-green">
            <span class="care-item-icon" style="color: #059669;">🥬</span>
            <div>
                <p class="care-item-title">Iron Superfoods & Vitamin C Boosters</p>
                <p class="care-item-subtitle">Chana, Rajma, Khajur (dates), Gud (jaggery). Nimbu aur Amla iron absorption me madad karte hain.</p>
            </div>
        </div>
    """
        
    if care_list:
        html += f"""
        <div class="care-item-blue">
            <span class="care-item-icon" style="color: #3b82f6;">💧</span>
            <div>
                <p class="care-item-title">Rest & Hydration / आराम और जलपान</p>
                <p class="care-item-subtitle">{", ".join(care_list[:4])}</p>
            </div>
        </div>
        """
        
    html += "</div>"
    return html


def run_screening(image_path, symptoms_text, name_input, age_input, use_llama, generate_voice, state):
    """
    Main Arova pipeline:
    Processes the uploaded eyelid image, clinical symptoms, and dynamic name/age onboarding.
    """
    if image_path is None:
        return (
            None,
            "### AROVA Clinical Screening Report\n*Report will appear here after screening analysis.*",
            None,
            """
            <div class="gauge-container">
                <h2 style="font-size: 2.2rem; font-weight: 800; color: #64748b; margin-top: 12px; margin-bottom: 4px; text-align: center;">Pending</h2>
                <span style="font-size: 0.9rem; color: #64748b;">Complete steps to run analysis</span>
            </div>
            """,
            "",
            state,
            "<div class='transcript-box'>💬 AROVA: Please upload eyelid photo / कृपया फोटो अपलोड करें।</div>"
        )

    name = name_input.strip() if name_input else "Patient"
    age = age_input.strip() if age_input else "N/A"
    s_text = symptoms_text.strip() if symptoms_text else ""
    
    # Yield initial progress state
    yield (
        get_cached_voice("analysis_started"),
        "### AROVA Clinical Screening Report\n*Analyzing conjunctiva photo and symptom inputs. Please wait...*",
        None,
        """
        <div class="gauge-container">
            <h2 style="font-size: 2.2rem; font-weight: 800; color: #2563eb; margin-top: 12px; margin-bottom: 4px; text-align: center;">Analyzing</h2>
            <span style="font-size: 0.9rem; color: #64748b;">Processing lower eyelid image...</span>
        </div>
        """,
        "",
        state,
        "<div class='transcript-box'>💬 AROVA: Dhanyavaad. Main ab screening analysis kar rahi hoon. Kripya thoda intezaar karein. / धन्यवाद। मैं अब स्क्रीनिंग एनालिसिस कर रही हूँ। कृपया थोड़ा इंतज़ार करें।</div>"
    )

    # 1. Parse symptoms
    symptoms = parse_symptoms(s_text)

    # 2. Photo-based anemia screening (dynamic threshold depending on symptoms)
    photo_result = None
    priority = "Low"
    risk_percent = 0.0
    if image_path is not None:
        has_anemia_symptoms = any(s in symptoms for s in ["weakness", "dizziness", "breathless", "chest_pain", "fainting", "paleness"])
        photo_result = predict_image(image_path, model=model, has_symptoms=has_anemia_symptoms)
        priority = photo_result.get("hb_test_priority", "Low")
        risk_percent = photo_result.get("risk_percent", 0.0)
    
    # 3. Rule-based care + diet engine
    basic_care = get_basic_care(symptoms)

    # 4. Compile professional report
    patient_data = {"name": name, "age": age, "symptoms": s_text}
    report_dict, display_markdown = build_professional_report(patient_data, photo_result, symptoms, basic_care)

    # Generate initial gauge & care HTML
    gauge_html = make_gauge_html(priority, risk_percent)
    care_html = make_care_html(basic_care)

    # Generate PDF report
    pdf_filename = f"arova_report_{name.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = create_pdf_report(report_dict, str(PROJECT_ROOT / "outputs" / "reports" / pdf_filename))

    # Construct dynamic transcript text matching spoken content
    transcript_text = f"Screening completed for {name}. Hb-test priority is {priority}."
    transcript_html = f"<div class='transcript-box'>💬 AROVA: {transcript_text} Please get a clinical blood test for confirmation.</div>"

    # Yield initial report immediately!
    yield (
        None,
        display_markdown,
        pdf_path,
        gauge_html,
        care_html,
        state,
        transcript_html
    )

    # 5. Llama explanation stream (if enabled)
    llama_explanation = ""
    if use_llama:
        report_with_llama = display_markdown + "\n\n---\n\n### 5. AROVA ASSISTANT EXPLANATION\n\n"
        for partial_text in ask_llama_stream(display_markdown):
            llama_explanation = partial_text
            yield (
                None,
                report_with_llama + partial_text,
                pdf_path,
                gauge_html,
                care_html,
                state,
                transcript_html
            )

    # 6. Generate dynamic voice report summary (cached segments, 0s latency)
    audio_path = None
    if generate_voice:
        now = datetime.datetime.now()
        closing_key = "closing_morning" if 5 <= now.hour < 17 else "closing_evening"
        severe_present = report_dict.get("severe_present", False)
        
        try:
            audio_path = generate_dynamic_report_speech(
                name=name,
                priority=priority,
                generate_care=True,
                severe_present=severe_present,
                closing_key=closing_key
            )
        except Exception as e:
            print("[ERROR] Failed to generate spoken summary:", e)
            audio_path = None

    final_display = display_markdown
    if use_llama and llama_explanation:
        final_display += f"\n\n---\n\n### 5. AROVA ASSISTANT EXPLANATION\n\n{llama_explanation}"

    # Output detailed report summary to transcript box
    final_spoken_content = (
        f"AROVA: {name} G, aapki screening complete ho gayi hai. "
        f"Aapki Hb-test priority {priority.lower()} hai. Confirmation ke liye hemoglobin blood test karwana recommended hai. "
        f"Report ready hai, aap PDF download kar sakte hain."
    )
    transcript_html = f"<div class='transcript-box'>💬 {final_spoken_content}</div>"

    yield (
        audio_path,
        final_display,
        pdf_path,
        gauge_html,
        care_html,
        state,
        transcript_html
    )


def toggle_lang(lang):
    """
    Toggles dashboard language between English and Hindi.
    Returns gr.update() updates for all visual text elements.
    """
    new_lang = "hi" if lang == "en" else "en"
    
    if new_lang == "hi":
        return [
            new_lang,
            gr.update(value="🌐 English / हिंदी (हिंदी)"),
            gr.update(value="🗣️ Arova की आवाज शुरू करे / Start AROVA Voice"),
            gr.update(value="<div class='step-header'><span class='step-badge'>0</span> मरीज का विवरण (Patient Details)</div>"),
            gr.update(label="मरीज का नाम (Patient Name)", placeholder="मरीज का नाम दर्ज करें..."),
            gr.update(value="नाम जमा करें (Submit Name)"),
            gr.update(label="मरीज की उम्र (Patient Age)", placeholder="मरीज की उम्र दर्ज करें (उदा. 42)..."),
            gr.update(value="उम्र जमा करें (Submit Age)"),
            gr.update(value="<div class='step-header'><span class='step-badge'>1</span> लक्षण बताएं या टाइप करें (Say or Type Symptoms)</div>"),
            gr.update(placeholder="उदाहरण: कमजोरी, थकान, चक्कर आना या सांस फूलना..."),
            gr.update(value="लक्षण जमा करें (Submit Symptoms)"),
            gr.update(value="<div class='step-header'><span class='step-badge'>2</span> आँख के नीचे की फोटो अपलोड (Lower Eyelid Photo Upload)</div>"),
            gr.update(value="<div class='warning-box'><span class='warning-icon'>⚠️</span><span>महत्वपूर्ण: कृपया केवल पलक के निचले हिस्से / कंजंक्टाइवा एरिया को ही क्रॉप करें ताकि जांच सटीक हो।</span></div>"),
            gr.update(value="<span style='font-size: 0.8rem; font-weight: 700; color: #64748b; letter-spacing: 0.05em;'>कॉन्फ़िगरेशन (CONFIGURATION)</span>"),
            gr.update(label="Llama स्पष्टीकरण का उपयोग करें (Use Llama Explanation)"),
            gr.update(label="आवाज में रिपोर्ट सारांश (Voice Reply Summary)"),
            gr.update(value="<div style='display:flex; justify-content:space-between; align-items:center; border-bottom: 2px solid #e2e8f0; padding-bottom:12px; margin-bottom:20px;'><span style='font-size:1.25rem; font-weight:800; color:#1e3a8a;'>📋 क्लीनिकल स्क्रीनिंग रिपोर्ट</span><span style='font-size:0.8rem; color:#64748b; font-weight: 600; background: #f1f5f9; padding: 4px 8px; border-radius: 6px;'>REF: #AR-8291-AI</span></div>"),
            gr.update(label="📥 क्लीनिकल रिपोर्ट (PDF) डाउनलोड करें"),
            gr.update(value="<div class='transcript-box'>💬 वॉइस असिस्टेंट तैयार है। शुरू करने के लिए 'Start AROVA Voice' पर क्लिक करें।</div>")
        ]
    else:
        return [
            new_lang,
            gr.update(value="🌐 English / हिंदी (English)"),
            gr.update(value="🗣️ Start AROVA Voice / Arova की आवाज शुरू करे"),
            gr.update(value="<div class='step-header'><span class='step-badge'>0</span> Patient Details</div>"),
            gr.update(label="Patient Name", placeholder="Enter full name..."),
            gr.update(value="Submit Name"),
            gr.update(label="Patient Age", placeholder="Enter age (e.g. 42)..."),
            gr.update(value="Submit Age"),
            gr.update(value="<div class='step-header'><span class='step-badge'>1</span> Say or Type Symptoms</div>"),
            gr.update(placeholder="Example: weakness, tiredness, feeling dizzy or short of breath..."),
            gr.update(value="Submit Symptoms"),
            gr.update(value="<div class='step-header'><span class='step-badge'>2</span> Lower Eyelid Photo Upload</div>"),
            gr.update(value="<div class='warning-box'><span class='warning-icon'>⚠️</span><span>Important: Please crop only the lower eyelid / conjunctiva area to ensure screening accuracy.</span></div>"),
            gr.update(value="<span style='font-size: 0.8rem; font-weight: 700; color: #64748b; letter-spacing: 0.05em;'>CONFIGURATION</span>"),
            gr.update(label="Use Llama Explanation"),
            gr.update(label="Voice Reply Summary"),
            gr.update(value="<div style='display:flex; justify-content:space-between; align-items:center; border-bottom: 2px solid #e2e8f0; padding-bottom:12px; margin-bottom:20px;'><span style='font-size:1.25rem; font-weight:800; color:#1e3a8a;'>📋 Clinical Screening Report</span><span style='font-size:0.8rem; color:#64748b; font-weight: 600; background: #f1f5f9; padding: 4px 8px; border-radius: 6px;'>REF: #AR-8291-AI</span></div>"),
            gr.update(label="📥 Download PDF Clinical Report"),
            gr.update(value="<div class='transcript-box'>💬 Voice assistant ready. Click 'Start AROVA Voice' to begin.</div>")
        ]


# Premium clinical light theme CSS styling - forces light theme on every block
custom_css = """
:root {
    --body-background-fill: #f4f6fc !important;
    --container-background-fill: #ffffff !important;
    --block-background-fill: #ffffff !important;
    --input-background-fill: #ffffff !important;
    --background-fill-primary: #ffffff !important;
    --background-fill-secondary: #f8fafc !important;
    --border-color-primary: #e0e7ff !important;
    --text-color: #1e293b !important;
    --input-text-color: #1e293b !important;
}

body, .gradio-container {
    background: linear-gradient(135deg, #f4f6fc 0%, #eef2ff 100%) !important;
    font-family: 'Outfit', 'Inter', -apple-system, sans-serif !important;
    color: #1e293b !important;
}

/* Force dark text inside textareas, inputs, and selections on light background */
.prose, .prose *, p, span, h1, h2, h3, h4, h5, h6, label, .label, .chatbot, .textbox, .markdown {
    color: #1e293b !important;
}

textarea, input[type="text"], input[type="number"], select {
    background-color: #ffffff !important;
    color: #1e293b !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 12px !important;
}

textarea:focus, input[type="text"]:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15) !important;
}

/* Header style */
.header-banner {
    background: linear-gradient(90deg, #ffffff 0%, #f1f5f9 100%) !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 20px !important;
    padding: 16px 24px !important;
    margin-bottom: 20px !important;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.02) !important;
    align-items: center !important;
}

.brand-title {
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    color: #1e3a8a !important;
    margin: 0 !important;
}

.brand-sub {
    font-size: 0.85rem !important;
    color: #64748b !important;
    margin: 2px 0 0 0 !important;
}

/* Transcript Box styled exactly as requested */
.transcript-box {
    background: #ffffff !important;
    border: 1px solid #e0e7ff !important;
    border-radius: 16px !important;
    padding: 18px 24px !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.015) !important;
    color: #1e3a8a !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    text-align: center !important;
    line-height: 1.4 !important;
    margin-bottom: 20px !important;
}

/* Card layout wrapper */
.section-card {
    background: #ffffff !important;
    border: 1px solid #e0e7ff !important;
    border-radius: 20px !important;
    padding: 24px !important;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.02) !important;
    margin-bottom: 20px !important;
}

/* Badge index indicator */
.step-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #dbeafe !important;
    color: #2563eb !important;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    font-weight: 800;
    font-size: 0.9rem;
    margin-right: 12px;
}

.step-header {
    display: flex;
    align-items: center;
    font-size: 1.15rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 16px;
}

/* Pill language button */
.lang-pill {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 20px !important;
    padding: 6px 14px !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    color: #475569 !important;
    cursor: pointer !important;
}

/* Header Start voice button */
.start-voice-btn {
    background: #2563eb !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 30px !important;
    padding: 10px 24px !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    cursor: pointer !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
    transition: all 0.2s ease !important;
}

.start-voice-btn:hover {
    background: #1d4ed8 !important;
    transform: translateY(-1px) !important;
}

/* Warning box under uploader */
.warning-box {
    background-color: #fff5f5 !important;
    border: 1px solid #fed7d7 !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    margin-top: 14px !important;
    color: #9b2c2c !important;
    font-size: 0.85rem !important;
    display: flex !important;
    align-items: flex-start !important;
    gap: 8px !important;
    line-height: 1.4 !important;
}

.warning-icon {
    font-size: 1.1rem !important;
    color: #e53e3e !important;
}

/* SVG Gauge container */
.gauge-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 20px 0;
}

.gauge-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #64748b;
    margin-bottom: 12px;
}

/* Care Guidance Cards */
.care-item-green {
    background-color: #f0fdf4 !important;
    border: 1px solid #dcfce7 !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    margin-bottom: 10px !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    border-left: 4px solid #10b981 !important;
}

.care-item-blue {
    background-color: #f0f9ff !important;
    border: 1px solid #e0f2fe !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    margin-bottom: 10px !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    border-left: 4px solid #3b82f6 !important;
}

.care-item-icon {
    font-size: 1.4rem !important;
}

.care-item-title {
    font-weight: 700 !important;
    color: #0f294a !important;
    font-size: 0.95rem !important;
    margin: 0 !important;
}

.care-item-subtitle {
    color: #475569 !important;
    font-size: 0.8rem !important;
    margin: 2px 0 0 0 !important;
}

/* Red disclaimer box inside report */
.disclaimer-card {
    background-color: #fef2f2 !important;
    border: 1px solid #fecaca !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    margin-top: 16px !important;
    color: #991b1b !important;
    font-size: 0.85rem !important;
    line-height: 1.4 !important;
    border-left: 4px solid #ef4444 !important;
    display: flex !important;
    gap: 10px !important;
}

.disclaimer-icon {
    font-size: 1.2rem !important;
    color: #ef4444 !important;
}

/* Off-screen audio elements to preserve background play */
.hidden-audio {
    position: absolute !important;
    left: -9999px !important;
    top: -9999px !important;
    opacity: 0 !important;
    height: 0 !important;
    width: 0 !important;
    overflow: hidden !important;
    pointer-events: none !important;
}
"""

# Build Gradio Blocks UI
with gr.Blocks(title=APP_TITLE) as demo:
    # State trackers
    consultation_state = gr.State(value={
        "step": "GREETING",
        "patient": {"name": "Patient", "age": "N/A", "symptoms": ""},
        "conversation": ""
    })
    lang_state = gr.State(value="en")

    # Header Banner
    with gr.Row(elem_classes="header-banner"):
        with gr.Column(scale=8):
            gr.HTML("""
            <div>
                <h1 class="brand-title">🩺 AROVA AI</h1>
                <p class="brand-sub">Rural Health Screening Assistant</p>
            </div>
            """)
        with gr.Column(scale=2, min_width=150):
            lang_btn = gr.Button("🌐 English / हिंदी (English)", variant="secondary", elem_classes="lang-pill")
        with gr.Column(scale=2, min_width=250):
            start_btn = gr.Button(
                "🗣️ Start AROVA Voice / Arova की आवाज शुरू करे",
                variant="primary",
                elem_classes="start-voice-btn"
            )

    # Real-time Voice Transcript Screen/Box (styled exactly as the user requested)
    transcript_box = gr.HTML(
        value="<div class='transcript-box'>💬 Voice assistant ready. Click 'Start AROVA Voice' to begin.</div>",
        show_label=False
    )

    # Invisible players for background play
    intro_audio = gr.Audio(
        label="AROVA Voice",
        type="filepath",
        autoplay=True,
        interactive=False,
        visible=True,
        elem_classes="hidden-audio"
    )
    report_audio = gr.Audio(
        label="Report Voice Summary",
        type="filepath",
        autoplay=True,
        interactive=False,
        visible=True,
        elem_classes="hidden-audio"
    )

    # Main Columns
    with gr.Row():
        # Column 1 (Left, 60% Scale)
        with gr.Column(scale=7):
            # Step 0: Patient Details
            with gr.Column(elem_classes="section-card"):
                patient_card_header = gr.HTML("""
                <div class="step-header">
                    <span class="step-badge">0</span> Patient Details
                </div>
                """)
                with gr.Row():
                    name_input = gr.Textbox(
                        label="Patient Name",
                        value="",
                        placeholder="Enter full name...",
                        interactive=True
                    )
                    age_input = gr.Textbox(
                        label="Patient Age",
                        value="",
                        placeholder="Enter age (e.g. 42)...",
                        interactive=False
                    )
                with gr.Row():
                    submit_name_btn = gr.Button("Submit Name", variant="secondary")
                    submit_age_btn = gr.Button("Submit Age", variant="secondary", interactive=False)

            # Step 1: Symptoms (moved before photo upload)
            with gr.Column(elem_classes="section-card"):
                step1_header = gr.HTML("""
                <div class="step-header">
                    <span class="step-badge">1</span> Say or Type Symptoms
                </div>
                """)
                voice_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="Record or speak symptoms",
                    show_label=False,
                    interactive=False
                )
                text_input = gr.Textbox(
                    placeholder="Example: weakness, tiredness, feeling dizzy or short of breath...",
                    lines=3,
                    show_label=False,
                    interactive=False
                )
                submit_symptoms_btn = gr.Button("Submit Symptoms", variant="secondary", interactive=False)

            # Step 2: Eyelid upload (moved after symptoms)
            with gr.Column(elem_classes="section-card"):
                step2_header = gr.HTML("""
                <div class="step-header">
                    <span class="step-badge">2</span> Lower Eyelid Photo Upload
                </div>
                """)
                image_input = gr.Image(
                    type="filepath",
                    sources=["upload", "webcam"],
                    label="Upload conjunctiva or eyelid photo",
                    interactive=False,
                    show_label=False,
                    height=200
                )
                warning_html = gr.HTML("""
                <div class="warning-box">
                    <span class="warning-icon">⚠️</span>
                    <span>Important: Please crop only the lower eyelid / conjunctiva area to ensure screening accuracy.</span>
                </div>
                """)

            # Configuration
            with gr.Column(elem_classes="section-card"):
                config_header = gr.HTML("<span style='font-size: 0.8rem; font-weight: 700; color: #64748b; letter-spacing: 0.05em;'>CONFIGURATION</span>")
                with gr.Row():
                    use_llama_chk = gr.Checkbox(label="Use Llama Explanation (Fast <5s AI Summary)", value=True)
                    generate_voice_chk = gr.Checkbox(label="Voice Reply Summary", value=True)

        # Column 2 (Right, 40% Scale)
        with gr.Column(scale=5):
            with gr.Column(elem_classes="section-card"):
                report_card_header = gr.HTML("""
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 2px solid #e2e8f0; padding-bottom:12px; margin-bottom:20px;">
                    <span style="font-size:1.25rem; font-weight:800; color:#1e3a8a;">📋 Clinical Screening Report</span>
                    <span style="font-size:0.8rem; color:#64748b; font-weight: 600; background: #f1f5f9; padding: 4px 8px; border-radius: 6px;">REF: #AR-8291-AI</span>
                </div>
                """)
                
                # Gauge HTML
                gauge_output = gr.HTML(value="""
                <div class="gauge-container">
                    <span class="gauge-title">Hb-Test Priority Gauge</span>
                    <svg width="220" height="120" viewBox="0 0 220 120">
                        <path d="M 30 110 A 80 80 0 0 1 190 110" fill="none" stroke="#e2e8f0" stroke-width="14" stroke-linecap="round"/>
                        <path d="M 30 110 A 80 80 0 0 1 83.3 56.7" fill="none" stroke="#10b981" stroke-width="14"/>
                        <path d="M 83.3 56.7 A 80 80 0 0 1 136.7 56.7" fill="none" stroke="#f59e0b" stroke-width="14"/>
                        <path d="M 136.7 56.7 A 80 80 0 0 1 190 110" fill="none" stroke="#ef4444" stroke-width="14"/>
                        <line x1="110" y1="110" x2="110" y2="50" stroke="#1e293b" stroke-width="4" stroke-linecap="round" style="transform-origin: 110px 110px; transform: rotate(-60deg); transition: transform 1s ease-out;"/>
                        <circle cx="110" cy="110" r="8" fill="#1e293b"/>
                        <text x="35" y="118" font-size="9" font-weight="700" fill="#64748b" text-anchor="middle">LOW</text>
                        <text x="110" y="32" font-size="9" font-weight="700" fill="#64748b" text-anchor="middle">MED</text>
                        <text x="185" y="118" font-size="9" font-weight="700" fill="#64748b" text-anchor="middle">HIGH</text>
                    </svg>
                    <h2 style="font-size: 2.2rem; font-weight: 800; color: #64748b; margin-top: 12px; margin-bottom: 4px;">Pending</h2>
                    <span style="font-size: 0.9rem; color: #64748b;">Complete steps to run analysis</span>
                </div>
                """)

                # Detailed text report (Markdown)
                report_output = gr.Markdown(value="### AROVA Clinical Screening Report\n*Report will appear here after screening analysis.*")
                
                # Care Recommendations Panel
                care_output = gr.HTML(value="""
                <div style="margin-top: 20px; border-top: 1px solid #e2e8f0; padding-top: 16px;">
                    <div style="font-size: 1.1rem; font-weight: 700; color: #1e3a8a; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                        <span style="color: #2563eb; font-size: 1.2rem;">➕</span> Care Guidance Section
                    </div>
                    <div class="care-item-blue">
                        <span class="care-item-icon">🍽️</span>
                        <div>
                            <p class="care-item-title">Balanced Nutrition Guidance</p>
                            <p class="care-item-subtitle">General iron-rich food and recovery advice is generated post-screening.</p>
                        </div>
                    </div>
                </div>
                """)

                # Safety Note Box (styled exactly like the mockup)
                gr.HTML("""
                <div class="disclaimer-card">
                    <span class="disclaimer-icon">⚠️</span>
                    <div>
                        <p style="font-weight: 800; color: #ef4444; margin-top: 0; margin-bottom: 4px; font-size: 0.85rem; text-transform: uppercase;">IMPORTANT SAFETY NOTES</p>
                        <p style="margin: 0; line-height: 1.4; color: #991b1b;">This AI screening is NOT a final medical diagnosis. It does not replace a doctor's consultation. A clinical blood test (Hb-Test) is mandatory for confirmed medical evaluation.</p>
                    </div>
                </div>
                """)
                
                # PDF report download
                pdf_downloader = gr.File(
                    label="📥 Download PDF Clinical Report",
                    visible=True,
                    interactive=False
                )

    # -----------------------------
    # Event Bindings
    # -----------------------------
    
    # 1. Start Consultation / Restart Reset
    start_btn.click(
        fn=handle_start_consultation,
        inputs=[consultation_state],
        outputs=[
            intro_audio, consultation_state, transcript_box,
            name_input, submit_name_btn,
            age_input, submit_age_btn,
            text_input, voice_input, submit_symptoms_btn,
            image_input
        ]
    )

    # 2. Submit Name
    submit_name_btn.click(
        fn=handle_submit_name,
        inputs=[name_input, consultation_state],
        outputs=[
            intro_audio, consultation_state, transcript_box,
            name_input, submit_name_btn,
            age_input, submit_age_btn
        ]
    )

    # 3. Submit Age
    submit_age_btn.click(
        fn=handle_submit_age,
        inputs=[age_input, consultation_state],
        outputs=[
            intro_audio, consultation_state, transcript_box,
            age_input, submit_age_btn,
            text_input, voice_input, submit_symptoms_btn
        ]
    )
    
    # 4. English/Hindi Language Toggle
    lang_btn.click(
        fn=toggle_lang,
        inputs=[lang_state],
        outputs=[
            lang_state, lang_btn, start_btn,
            patient_card_header, name_input, submit_name_btn, age_input, submit_age_btn,
            step1_header, text_input, submit_symptoms_btn,
            step2_header, warning_html,
            config_header, use_llama_chk, generate_voice_chk,
            report_card_header, pdf_downloader, transcript_box
        ]
    )
    
    # 5. Bind voice recording change directly to instant auto-transcription
    voice_input.change(
        fn=transcribe_only,
        inputs=[voice_input],
        outputs=[text_input]
    )

    # 6. Submit Symptoms
    submit_symptoms_btn.click(
        fn=handle_submit_symptoms,
        inputs=[text_input, consultation_state],
        outputs=[
            intro_audio, consultation_state, transcript_box,
            text_input, voice_input, submit_symptoms_btn,
            image_input
        ]
    )
    
    # 7. Run Screening & Generate Report automatically on image upload
    image_input.change(
        fn=run_screening,
        inputs=[image_input, text_input, name_input, age_input, use_llama_chk, generate_voice_chk, consultation_state],
        outputs=[
            report_audio, report_output, pdf_downloader, gauge_output, care_output, consultation_state, transcript_box
        ]
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, allowed_paths=[str(PROJECT_ROOT)], css=custom_css)