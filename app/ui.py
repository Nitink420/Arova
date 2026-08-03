# app/ui.py
"""
AROVA Multilingual Gradio UI Layout & Styling

Implements the full-screen startup Language Selection Screen and the main
localized healthcare dashboard.

Features:
- Premium clinical light theme design system.
- Accessible full-screen language selection on application startup.
- Touch-friendly 11-language selection grid (English, Hindi, Bengali, Marathi,
  Tamil, Telugu, Gujarati, Kannada, Malayalam, Punjabi, Urdu).
- Dynamic real-time localization of all UI controls, headers, disclaimers, and audio.
"""

import gradio as gr
from app.core.config import Config
from app.services.language_service import SUPPORTED_LANGUAGES_CATALOG


def get_custom_css() -> str:
    """Return premium clinical light theme CSS styling."""
    return """
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

/* Fullscreen Language Selection Screen */
.lang-selection-hero {
    background: #ffffff !important;
    border: 1px solid #e0e7ff !important;
    border-radius: 24px !important;
    padding: 40px 30px !important;
    box-shadow: 0 12px 40px rgba(37, 99, 235, 0.06) !important;
    margin: 20px auto !important;
    max-width: 950px !important;
    text-align: center !important;
}

.lang-title {
    font-size: 2.5rem !important;
    font-weight: 900 !important;
    color: #1e3a8a !important;
    margin-bottom: 6px !important;
}

.lang-subtitle {
    font-size: 1.1rem !important;
    color: #475569 !important;
    font-weight: 600 !important;
    margin-bottom: 24px !important;
}

.lang-prompt {
    font-size: 1.4rem !important;
    font-weight: 800 !important;
    color: #2563eb !important;
    margin-bottom: 30px !important;
}

.lang-card-btn {
    background: #ffffff !important;
    border: 2px solid #cbd5e1 !important;
    border-radius: 16px !important;
    padding: 16px 20px !important;
    font-size: 1.25rem !important;
    font-weight: 800 !important;
    color: #1e293b !important;
    cursor: pointer !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
    transition: all 0.2s ease !important;
    height: 70px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.lang-card-btn:hover {
    border-color: #2563eb !important;
    background: #eff6ff !important;
    color: #1d4ed8 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.15) !important;
}

/* Transcript Box */
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


def create_ui(handlers):
    """
    Create the Gradio Blocks UI and wire all event handlers.
    """
    config = Config()
    custom_css = get_custom_css()

    with gr.Blocks(title=config.APP_TITLE) as demo:
        # State trackers
        consultation_state = gr.State(value={
            "step": "GREETING",
            "patient": {"name": "Patient", "age": "N/A", "symptoms": ""},
            "conversation": "",
            "lang": "en",
        })

        # Audio elements
        intro_audio = gr.Audio(
            label="AROVA Voice",
            type="filepath",
            autoplay=True,
            interactive=False,
            visible=True,
            elem_classes="hidden-audio",
        )
        report_audio = gr.Audio(
            label="Report Voice Summary",
            type="filepath",
            autoplay=True,
            interactive=False,
            visible=True,
            elem_classes="hidden-audio",
        )

        # ────────────────────────────────────────────────────────────────
        # SCREEN 1: Full-Screen Language Selection Page (Shown on Startup)
        # ────────────────────────────────────────────────────────────────
        with gr.Column(elem_classes="lang-selection-hero", visible=True) as lang_selection_container:
            gr.HTML("""
            <div>
                <h1 class="lang-title">🩺 AROVA</h1>
                <p class="lang-subtitle">Offline-First AI Healthcare Assistant for Rural Healthcare</p>
                <div style="width: 80px; height: 3px; background: #2563eb; margin: 16px auto 24px auto; border-radius: 2px;"></div>
                <h2 class="lang-prompt">🌐 Choose Your Language / अपनी भाषा चुनें</h2>
            </div>
            """)

            lang_btns = {}
            # Row 1: Hindi, English, Bengali
            with gr.Row():
                lang_btns["hi"] = gr.Button("🇮🇳 हिन्दी", elem_classes="lang-card-btn")
                lang_btns["en"] = gr.Button("🇬🇧 English", elem_classes="lang-card-btn")
                lang_btns["bn"] = gr.Button("🇧🇩 বাংলা", elem_classes="lang-card-btn")

            # Row 2: Marathi, Tamil, Telugu
            with gr.Row():
                lang_btns["mr"] = gr.Button("🇮🇳 मराठी", elem_classes="lang-card-btn")
                lang_btns["ta"] = gr.Button("🇮🇳 தமிழ்", elem_classes="lang-card-btn")
                lang_btns["te"] = gr.Button("🇮🇳 తెలుగు", elem_classes="lang-card-btn")

            # Row 3: Gujarati, Kannada, Malayalam
            with gr.Row():
                lang_btns["gu"] = gr.Button("🇮🇳 ગુજરાતી", elem_classes="lang-card-btn")
                lang_btns["kn"] = gr.Button("🇮🇳 ಕನ್ನಡ", elem_classes="lang-card-btn")
                lang_btns["ml"] = gr.Button("🇮🇳 മലയാളം", elem_classes="lang-card-btn")

            # Row 4: Punjabi, Urdu
            with gr.Row():
                lang_btns["pa"] = gr.Button("🇮🇳 ਪੰਜਾਬੀ", elem_classes="lang-card-btn")
                lang_btns["ur"] = gr.Button("🇮🇳 اردو", elem_classes="lang-card-btn")

        # ────────────────────────────────────────────────────────────────
        # SCREEN 2: Main Healthcare Assistant Interface (Unlocked after language)
        # ────────────────────────────────────────────────────────────────
        with gr.Column(visible=False) as main_app_container:

            # Header Banner
            with gr.Row(elem_classes="header-banner"):
                with gr.Column(scale=8):
                    brand_html = gr.HTML("""
                    <div>
                        <h1 class="brand-title">🩺 AROVA AI</h1>
                        <p class="brand-sub">Rural Health Screening Assistant</p>
                    </div>
                    """)
                with gr.Column(scale=2, min_width=150):
                    header_lang_btn = gr.Button(
                        "🌐 English",
                        variant="secondary",
                        elem_classes="lang-pill",
                    )
                with gr.Column(scale=2, min_width=250):
                    start_btn = gr.Button(
                        "🗣️ Start AROVA Voice Assistant",
                        variant="primary",
                        elem_classes="start-voice-btn",
                    )

            # Real-time Voice Transcript Box
            transcript_box = gr.HTML(
                value="<div class='transcript-box'>💬 Voice assistant ready.</div>",
                show_label=False,
            )

            # Main Grid Columns
            with gr.Row():
                # Column 1 (Left Input Panel)
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
                                interactive=True,
                            )
                            age_input = gr.Textbox(
                                label="Patient Age",
                                value="",
                                placeholder="Enter age (e.g. 42)...",
                                interactive=False,
                            )
                        with gr.Row():
                            submit_name_btn = gr.Button("Submit Name", variant="secondary")
                            submit_age_btn = gr.Button(
                                "Submit Age", variant="secondary", interactive=False
                            )

                    # Step 1: Symptoms
                    with gr.Column(elem_classes="section-card"):
                        step1_header = gr.HTML("""
                        <div class="step-header">
                            <span class="step-badge">1</span> Say or Type Symptoms
                        </div>
                        """)
                        voice_input = gr.Audio(
                            sources=["microphone"],
                            type="filepath",
                            label="Record symptoms",
                            show_label=False,
                            interactive=False,
                        )
                        text_input = gr.Textbox(
                            placeholder="Example: weakness, tiredness, feeling dizzy or short of breath...",
                            lines=3,
                            show_label=False,
                            interactive=False,
                        )
                        submit_symptoms_btn = gr.Button(
                            "Submit Symptoms", variant="secondary", interactive=False
                        )

                    # Step 2: Eyelid Photo Upload
                    with gr.Column(elem_classes="section-card"):
                        step2_header = gr.HTML("""
                        <div class="step-header">
                            <span class="step-badge">2</span> Lower Eyelid Photo Upload
                        </div>
                        """)
                        image_input = gr.Image(
                            type="filepath",
                            sources=["upload", "webcam"],
                            label="Upload photo",
                            interactive=False,
                            show_label=False,
                            height=200,
                        )
                        warning_html = gr.HTML("""
                        <div class="warning-box">
                            <span class="warning-icon">⚠️</span>
                            <span>Important: Please crop only the lower eyelid / conjunctiva area to ensure screening accuracy.</span>
                        </div>
                        """)

                    # Configuration
                    with gr.Column(elem_classes="section-card"):
                        config_header = gr.HTML(
                            "<span style='font-size: 0.8rem; font-weight: 700; color: #64748b;'>CONFIGURATION</span>"
                        )
                        with gr.Row():
                            use_llama_chk = gr.Checkbox(
                                label="Use Llama AI Summary (<5s)",
                                value=True,
                            )
                            generate_voice_chk = gr.Checkbox(
                                label="Voice Reply Summary", value=True
                            )

                # Column 2 (Right Output Report Panel)
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

                        # Image Quality Badge
                        quality_badge = gr.HTML(value="")

                        # Visual Analysis: Before/After + Grad-CAM
                        with gr.Column(visible=False) as visual_analysis_container:
                            gr.HTML("""
                            <div style="font-size: 1.05rem; font-weight: 700; color: #1e3a8a; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;">
                                <span style="color: #2563eb; font-size: 1.1rem;">🔬</span> Visual Analysis Pipeline
                            </div>
                            """)
                            with gr.Row():
                                original_img_display = gr.Image(
                                    label="📷 Original", type="numpy",
                                    interactive=False, height=160,
                                )
                                enhanced_img_display = gr.Image(
                                    label="✨ Enhanced (CLAHE)", type="numpy",
                                    interactive=False, height=160,
                                )
                                gradcam_img_display = gr.Image(
                                    label="🔥 Grad-CAM Heatmap", type="numpy",
                                    interactive=False, height=160,
                                )

                        # Markdown Report
                        report_output = gr.Markdown(
                            value="### AROVA Clinical Screening Report\n*Report will appear here after screening analysis.*"
                        )

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

                        # Safety Note Box
                        gr.HTML("""
                        <div class="disclaimer-card">
                            <span class="disclaimer-icon">⚠️</span>
                            <div>
                                <p style="font-weight: 800; color: #ef4444; margin-top: 0; margin-bottom: 4px; font-size: 0.85rem; text-transform: uppercase;">IMPORTANT SAFETY NOTES</p>
                                <p style="margin: 0; line-height: 1.4; color: #991b1b;">This AI screening is NOT a final medical diagnosis. It does not replace a doctor's consultation. A clinical blood test (Hb-Test) is mandatory for confirmed medical evaluation.</p>
                            </div>
                        </div>
                        """)

                        # PDF report downloader + WhatsApp Share
                        with gr.Row():
                            pdf_downloader = gr.File(
                                label="📥 Download PDF Clinical Report",
                                visible=True,
                                interactive=False,
                            )
                            whatsapp_share = gr.HTML(value="")

        # ────────────────────────────────────────────────────────────────
        # Event Wiring
        # ────────────────────────────────────────────────────────────────

        # Output list for language selection event
        lang_outputs = [
            consultation_state,
            lang_selection_container,
            main_app_container,
            intro_audio,
            transcript_box,
            brand_html,
            header_lang_btn,
            start_btn,
            patient_card_header,
            name_input,
            submit_name_btn,
            age_input,
            submit_age_btn,
            step1_header,
            text_input,
            submit_symptoms_btn,
            step2_header,
            warning_html,
            config_header,
            use_llama_chk,
            generate_voice_chk,
            report_card_header,
            pdf_downloader,
        ]

        # Bind all 11 language card buttons to language selection handler
        for code, btn in lang_btns.items():
            btn.click(
                fn=lambda state, c=code: handlers.handle_select_language(c, state),
                inputs=[consultation_state],
                outputs=lang_outputs,
            )

        # Header language switcher button (returns user to language selection view)
        header_lang_btn.click(
            fn=lambda: (gr.update(visible=True), gr.update(visible=False)),
            inputs=[],
            outputs=[lang_selection_container, main_app_container],
        )

        # 1. Start Consultation
        start_btn.click(
            fn=handlers.handle_start_consultation,
            inputs=[consultation_state],
            outputs=[
                intro_audio, consultation_state, transcript_box,
                name_input, submit_name_btn,
                age_input, submit_age_btn,
                text_input, voice_input, submit_symptoms_btn,
                image_input,
            ],
        )

        # 2. Submit Name
        submit_name_btn.click(
            fn=handlers.handle_submit_name,
            inputs=[name_input, consultation_state],
            outputs=[
                intro_audio, consultation_state, transcript_box,
                name_input, submit_name_btn,
                age_input, submit_age_btn,
            ],
        )

        # 3. Submit Age
        submit_age_btn.click(
            fn=handlers.handle_submit_age,
            inputs=[age_input, consultation_state],
            outputs=[
                intro_audio, consultation_state, transcript_box,
                age_input, submit_age_btn,
                text_input, voice_input, submit_symptoms_btn,
            ],
        )

        # 4. Transcribe mic audio
        voice_input.change(
            fn=handlers.transcribe_only,
            inputs=[voice_input],
            outputs=[text_input],
        )

        # 5. Submit Symptoms
        submit_symptoms_btn.click(
            fn=handlers.handle_submit_symptoms,
            inputs=[text_input, consultation_state],
            outputs=[
                intro_audio, consultation_state, transcript_box,
                text_input, voice_input, submit_symptoms_btn,
                image_input,
            ],
        )

        # 6. Run Screening & Generate Report automatically on image upload
        image_input.change(
            fn=handlers.run_screening,
            inputs=[
                image_input, text_input, name_input, age_input,
                use_llama_chk, generate_voice_chk, consultation_state,
            ],
            outputs=[
                report_audio, report_output, pdf_downloader,
                gauge_output, care_output, consultation_state,
                transcript_box, quality_badge,
                visual_analysis_container,
                original_img_display, enhanced_img_display, gradcam_img_display,
                whatsapp_share,
            ],
        )

    return demo, custom_css
