# app/handlers.py
"""
AROVA Multilingual Gradio Event Handlers

All Gradio event handler functions for language selection and consultation flow.
Handlers manage UI state only — delegating business logic to services.
"""

import datetime
import threading
import hashlib
import urllib.parse
import gradio as gr

from app.core.logger import get_logger
from app.services.language_service import LanguageService, SUPPORTED_LANGUAGES_CATALOG
from app.services.quality_service import QualityService

logger = get_logger(__name__)

# Flow state constants
GREETING = "GREETING"
ASK_NAME = "ASK_NAME"
ASK_AGE = "ASK_AGE"
ASK_SYMPTOMS = "ASK_SYMPTOMS"
ASK_IMAGE = "ASK_IMAGE"
READY_FOR_ANALYSIS = "READY_FOR_ANALYSIS"
ANALYSIS = "ANALYSIS"
REPORT_READY = "REPORT_READY"
CLOSING = "CLOSING"


class Handlers:
    """
    Container for all Gradio event handler methods.
    """

    def __init__(
        self,
        vision_service,
        llm_service,
        voice_service,
        medical_service,
        pdf_service,
        report_service,
        language_service: LanguageService,
        config,
    ):
        self.vision = vision_service
        self.llm = llm_service
        self.voice = voice_service
        self.medical = medical_service
        self.pdf = pdf_service
        self.report = report_service
        self.lang_service = language_service
        self.quality = QualityService()
        self.config = config

    def handle_select_language(self, lang_code: str, state: dict):
        """
        Triggered when user selects a language card on the startup screen.

        1. Sets session language in LanguageService.
        2. Plays welcome voice automatically in chosen language.
        3. Hides language selection page and reveals main healthcare UI.
        4. Updates all UI strings to chosen language.
        """
        active_lang = self.lang_service.set_language(lang_code)

        # Get localized welcome voice and transcript
        welcome_audio = self.voice.get_cached_voice("intro", lang=active_lang)
        if not welcome_audio:
            welcome_text = self.lang_service.get_welcome_message(lang=active_lang)
            welcome_audio = self.voice.speak(welcome_text, f"welcome_{active_lang}.wav", cache=True, lang=active_lang)

        transcript_html = f"<div class='transcript-box'>{self.lang_service.get_welcome_text(lang=active_lang)}</div>"

        state["step"] = ASK_NAME
        state["patient"] = {"name": "", "age": "", "symptoms": ""}
        state["conversation"] = ""
        state["lang"] = active_lang

        # Return updates for hiding selection view, showing main view, playing audio, updating all components
        return [
            state,
            gr.update(visible=False),  # lang_selection_container
            gr.update(visible=True),   # main_app_container
            welcome_audio,             # intro_audio
            transcript_html,           # transcript_box
            gr.update(value=self.lang_service.t("app_title", lang=active_lang)),
            gr.update(value=f"🌐 {self.lang_service.get_language_info(active_lang)['flag']} {self.lang_service.get_language_info(active_lang)['native']}"),
            gr.update(value=self.lang_service.t("start_voice", lang=active_lang)),
            gr.update(value=f"<div class='step-header'><span class='step-badge'>0</span> {self.lang_service.t('step_patient', lang=active_lang)}</div>"),
            gr.update(label=self.lang_service.t("name_label", lang=active_lang), placeholder=self.lang_service.t("name_placeholder", lang=active_lang), value="", interactive=True),
            gr.update(value=self.lang_service.t("submit_name", lang=active_lang), interactive=True),
            gr.update(label=self.lang_service.t("age_label", lang=active_lang), placeholder=self.lang_service.t("age_placeholder", lang=active_lang), value="", interactive=False),
            gr.update(value=self.lang_service.t("submit_age", lang=active_lang), interactive=False),
            gr.update(value=f"<div class='step-header'><span class='step-badge'>1</span> {self.lang_service.t('step_symptoms', lang=active_lang)}</div>"),
            gr.update(placeholder=self.lang_service.t("symptoms_placeholder", lang=active_lang), value="", interactive=False),
            gr.update(value=self.lang_service.t("submit_symptoms", lang=active_lang), interactive=False),
            gr.update(value=f"<div class='step-header'><span class='step-badge'>2</span> {self.lang_service.t('step_eyelid', lang=active_lang)}</div>"),
            gr.update(value=f"<div class='warning-box'><span class='warning-icon'>⚠️</span><span>{self.lang_service.t('upload_warning', lang=active_lang)}</span></div>"),
            gr.update(value=f"<span style='font-size: 0.8rem; font-weight: 700; color: #64748b;'>{self.lang_service.t('config_header', lang=active_lang)}</span>"),
            gr.update(label=self.lang_service.t("use_llama", lang=active_lang)),
            gr.update(label=self.lang_service.t("voice_reply", lang=active_lang)),
            gr.update(value=f"<div style='display:flex; justify-content:space-between; align-items:center; border-bottom: 2px solid #e2e8f0; padding-bottom:12px; margin-bottom:20px;'><span style='font-size:1.25rem; font-weight:800; color:#1e3a8a;'>{self.lang_service.t('report_title', lang=active_lang)}</span><span style='font-size:0.8rem; color:#64748b; font-weight: 600; background: #f1f5f9; padding: 4px 8px; border-radius: 6px;'>{self.lang_service.t('report_ref', lang=active_lang)}</span></div>"),
            gr.update(label=self.lang_service.t("download_pdf", lang=active_lang)),
        ]

    def handle_start_consultation(self, state: dict):
        """Reset state and play localized intro voice."""
        active_lang = self.lang_service.get_language()
        state["step"] = ASK_NAME
        state["patient"] = {"name": "", "age": "", "symptoms": ""}
        state["conversation"] = ""

        audio = self.voice.get_cached_voice("intro", lang=active_lang)
        if not audio:
            audio = self.voice.speak(self.lang_service.get_welcome_message(lang=active_lang), f"intro_{active_lang}.wav", cache=True, lang=active_lang)

        transcript_html = f"<div class='transcript-box'>{self.lang_service.get_welcome_text(lang=active_lang)}</div>"
        return (
            audio,
            state,
            transcript_html,
            gr.update(value="", interactive=True),     # name_input
            gr.update(interactive=True),               # submit_name_btn
            gr.update(value="", interactive=False),    # age_input
            gr.update(interactive=False),              # submit_age_btn
            gr.update(value="", interactive=False),    # text_input
            gr.update(interactive=False),              # voice_input (mic)
            gr.update(interactive=False),              # submit_symptoms_btn
            gr.update(value=None, interactive=False),  # image_input
        )

    def _generate_name_audio_bg(self, name: str, lang: str):
        """Background thread for name audio synthesis."""
        try:
            self.voice.generate_name_audio(name, lang=lang)
        except Exception as e:
            logger.error("Background name synthesis failed: %s", e)

    def handle_submit_name(self, name: str, state: dict):
        """Save name and prompt for age in active language."""
        active_lang = self.lang_service.get_language()
        name_clean = name.strip() if name else ""
        if not name_clean:
            err_msg = self.lang_service.t("error_name", lang=active_lang)
            return (
                None,
                state,
                f"<div class='transcript-box'>💬 AROVA: {err_msg}</div>",
                gr.update(interactive=True),
                gr.update(interactive=True),
                gr.update(interactive=False),
                gr.update(interactive=False),
            )

        state["patient"]["name"] = name_clean
        state["step"] = ASK_AGE

        ask_age_text = self.lang_service.t("ask_age_voice", lang=active_lang, name=name_clean)
        audio = self.voice.get_cached_voice("ask_age", lang=active_lang)
        if not audio:
            audio = self.voice.speak(ask_age_text, f"ask_age_{active_lang}.wav", cache=True, lang=active_lang)

        transcript_html = f"<div class='transcript-box'>💬 AROVA: {ask_age_text}</div>"

        # Daemon thread for name synthesis
        bg_thread = threading.Thread(target=self._generate_name_audio_bg, args=(name_clean, active_lang))
        bg_thread.daemon = True
        bg_thread.start()

        return (
            audio,
            state,
            transcript_html,
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=True),
            gr.update(interactive=True),
        )

    def handle_submit_age(self, age: str, state: dict):
        """Save age and prompt for symptoms in active language."""
        active_lang = self.lang_service.get_language()
        age_clean = age.strip() if age else ""
        if not age_clean:
            err_msg = self.lang_service.t("error_age", lang=active_lang)
            return (
                None,
                state,
                f"<div class='transcript-box'>💬 AROVA: {err_msg}</div>",
                gr.update(interactive=True),
                gr.update(interactive=True),
                gr.update(interactive=False),
                gr.update(interactive=False),
                gr.update(interactive=False),
            )

        state["patient"]["age"] = age_clean
        state["step"] = ASK_SYMPTOMS

        ask_sym_text = self.lang_service.t("ask_symptoms_voice", lang=active_lang)
        audio = self.voice.get_cached_voice("ask_symptoms", lang=active_lang)
        if not audio:
            audio = self.voice.speak(ask_sym_text, f"ask_symptoms_{active_lang}.wav", cache=True, lang=active_lang)

        transcript_html = f"<div class='transcript-box'>💬 AROVA: {ask_sym_text}</div>"
        return (
            audio,
            state,
            transcript_html,
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=True),
        )

    def handle_submit_symptoms(self, symptoms: str, state: dict):
        """Save symptoms and prompt for eyelid photo in active language."""
        active_lang = self.lang_service.get_language()
        s_clean = symptoms.strip() if symptoms else ""
        state["patient"]["symptoms"] = s_clean
        state["step"] = ASK_IMAGE

        ask_img_text = self.lang_service.t("ask_image_voice", lang=active_lang)
        audio = self.voice.get_cached_voice("ask_image", lang=active_lang)
        if not audio:
            audio = self.voice.speak(ask_img_text, f"ask_image_{active_lang}.wav", cache=True, lang=active_lang)

        transcript_html = f"<div class='transcript-box'>💬 AROVA: {ask_img_text}</div>"
        return (
            audio,
            state,
            transcript_html,
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=True),
        )

    def transcribe_only(self, audio_path: str):
        """Transcribe mic audio into text."""
        if audio_path is None:
            return ""
        return self.voice.transcribe(audio_path)

    def make_gauge_html(self, priority: str, risk_percent: float, lang: str) -> str:
        """Generate localized SVG Gauge HTML."""
        p_upper = priority.upper()
        if "HIGH" in p_upper or "High" in priority:
            rotation = 60
            color = "#ef4444"
            status = self.lang_service.t("priority_high", lang=lang)
            wording = self.lang_service.t("wording_high", lang=lang)
        elif "MEDIUM" in p_upper or "Medium" in priority or "MED" in p_upper:
            rotation = 0
            color = "#2563eb"
            status = self.lang_service.t("priority_medium", lang=lang)
            wording = self.lang_service.t("wording_medium", lang=lang)
        else:
            rotation = -60
            color = "#10b981"
            status = self.lang_service.t("priority_low", lang=lang)
            wording = self.lang_service.t("wording_low", lang=lang)

        gauge_title = self.lang_service.t("gauge_title", lang=lang)

        return f"""
        <div class="gauge-container">
            <span class="gauge-title">{gauge_title}</span>
            <svg width="220" height="120" viewBox="0 0 220 120">
                <path d="M 30 110 A 80 80 0 0 1 190 110" fill="none" stroke="#e2e8f0" stroke-width="14" stroke-linecap="round"/>
                <path d="M 30 110 A 80 80 0 0 1 83.3 56.7" fill="none" stroke="#10b981" stroke-width="14"/>
                <path d="M 83.3 56.7 A 80 80 0 0 1 136.7 56.7" fill="none" stroke="#f59e0b" stroke-width="14"/>
                <path d="M 136.7 56.7 A 80 80 0 0 1 190 110" fill="none" stroke="#ef4444" stroke-width="14"/>
                <line x1="110" y1="110" x2="110" y2="50" stroke="#1e293b" stroke-width="4" stroke-linecap="round" style="transform-origin: 110px 110px; transform: rotate({rotation}deg); transition: transform 1s ease-out;"/>
                <circle cx="110" cy="110" r="8" fill="#1e293b"/>
                <text x="35" y="118" font-size="9" font-weight="700" fill="#64748b" text-anchor="middle">LOW</text>
                <text x="110" y="32" font-size="9" font-weight="700" fill="#64748b" text-anchor="middle">MED</text>
                <text x="185" y="118" font-size="9" font-weight="700" fill="#64748b" text-anchor="middle">HIGH</text>
            </svg>
            <h2 style="font-size: 2.2rem; font-weight: 800; color: {color}; margin-top: 12px; margin-bottom: 2px; text-align: center;">{status}</h2>
            <span style="font-size: 0.9rem; color: #64748b; font-weight: 600; text-align: center; display: block;">{wording}</span>
        </div>
        """

    def make_care_html(self, care_result: dict, lang: str) -> str:
        """Generate localized Care Guidance HTML."""
        if not care_result:
            return ""

        care_title = self.lang_service.t("care_title", lang=lang)
        care_list = care_result.get("care", [])

        html = f"""
        <div style="margin-top: 20px; border-top: 1px solid #e2e8f0; padding-top: 16px;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #1e3a8a; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                <span style="color: #2563eb; font-size: 1.2rem;">➕</span> {care_title}
            </div>
            <div class="care-item-green">
                <span class="care-item-icon" style="color: #10b981;">🍎</span>
                <div>
                    <p class="care-item-title">Fruits & Vegetables / पोषण से भरपूर आहार</p>
                    <p class="care-item-subtitle">Palak, Chukandar (beetroot), Methi, Anar (pomegranate), Amrood (guava), Nimbu, Amla, Oranges.</p>
                </div>
            </div>
            <div class="care-item-green">
                <span class="care-item-icon" style="color: #059669;">🥬</span>
                <div>
                    <p class="care-item-title">Iron Superfoods & Vitamin C Boosters</p>
                    <p class="care-item-subtitle">Chana, Rajma, Khajur (dates), Gud (jaggery). Nimbu & Amla enhance iron absorption.</p>
                </div>
            </div>
        """

        if care_list:
            items_str = ", ".join(care_list[:4])
            html += f"""
            <div class="care-item-blue">
                <span class="care-item-icon" style="color: #3b82f6;">💧</span>
                <div>
                    <p class="care-item-title">Rest & Hydration / आराम और जलपान</p>
                    <p class="care-item-subtitle">{items_str}</p>
                </div>
            </div>
            """

        html += "</div>"
        return html

    def make_quality_badge_html(self, quality_result: dict, lang: str) -> str:
        """Generate HTML badge for image quality assessment."""
        grade = quality_result.get("grade", "REJECTED")
        score = quality_result.get("score", 0)
        feedback = quality_result.get("feedback", "")
        details = quality_result.get("details", {})

        if grade == "GOOD":
            bg = "#f0fdf4"; border = "#10b981"; color = "#065f46"; icon = "✅"
        elif grade == "FAIR":
            bg = "#fffbeb"; border = "#f59e0b"; color = "#92400e"; icon = "⚠️"
        else:
            bg = "#fef2f2"; border = "#ef4444"; color = "#991b1b"; icon = "❌"

        detail_str = ""
        if details:
            detail_str = f"<span style='font-size:0.7rem; color:#94a3b8; margin-left:8px;'>Blur: {details.get('blur_score','?')} | Brightness: {details.get('avg_brightness','?')}</span>"

        return f"""
        <div style="background:{bg}; border:1px solid {border}; border-left:4px solid {border};
                    border-radius:10px; padding:10px 14px; margin-bottom:12px;
                    display:flex; align-items:center; gap:10px;">
            <span style="font-size:1.3rem;">{icon}</span>
            <div>
                <span style="font-weight:700; color:{color}; font-size:0.9rem;">{grade} — Quality Score: {score}/100</span>{detail_str}
                <p style="margin:2px 0 0 0; font-size:0.8rem; color:{color}; opacity:0.85;">{feedback}</p>
            </div>
        </div>
        """

    @staticmethod
    def make_whatsapp_html(name: str, priority: str, risk_percent: float) -> str:
        """Generate WhatsApp share link HTML."""
        share_text = (
            f"🩺 AROVA Screening Report\n"
            f"Patient: {name}\n"
            f"Hb-Test Priority: {priority}\n"
            f"Risk Indicator: {risk_percent:.1f}%\n\n"
            f"⚠️ This is a preliminary screening only. "
            f"Please confirm with a clinical Hb blood test."
        )
        encoded = urllib.parse.quote(share_text)
        return f"""
        <a href="https://wa.me/?text={encoded}" target="_blank"
           style="display:inline-flex; align-items:center; gap:8px;
                  background:#25D366; color:#ffffff; padding:10px 18px;
                  border-radius:30px; text-decoration:none; font-weight:700;
                  font-size:0.85rem; box-shadow:0 4px 12px rgba(37,211,102,0.25);
                  transition: all 0.2s ease; margin-top:12px;">
            <span style="font-size:1.2rem;">📱</span> Share on WhatsApp
        </a>
        """

    def _make_empty_visual_outputs(self):
        """Return empty outputs for all new visual UI components."""
        return (
            "",                          # quality_badge
            gr.update(visible=False),    # visual_analysis_container
            None,                        # original_img_display
            None,                        # enhanced_img_display
            None,                        # gradcam_img_display
            "",                          # whatsapp_share
        )

    def run_screening(
        self,
        image_path: str,
        symptoms_text: str,
        name_input: str,
        age_input: str,
        use_llama: bool,
        generate_voice: bool,
        state: dict,
    ):
        """
        Main Arova Screening Pipeline with Quality Gate, Grad-CAM, and Progress Steps.
        """
        active_lang = self.lang_service.get_language()

        if image_path is None:
            err_img = self.lang_service.t("error_image", lang=active_lang)
            rep_title = self.lang_service.t("report_title", lang=active_lang)
            pending_label = self.lang_service.t("priority_pending", lang=active_lang)
            return (
                None,
                f"### {rep_title}\n*{err_img}*",
                None,
                f"""
                <div class="gauge-container">
                    <h2 style="font-size: 2.2rem; font-weight: 800; color: #64748b; margin-top: 12px; text-align: center;">{pending_label}</h2>
                    <span style="font-size: 0.9rem; color: #64748b;">{err_img}</span>
                </div>
                """,
                "",
                state,
                f"<div class='transcript-box'>💬 AROVA: {err_img}</div>",
                *self._make_empty_visual_outputs(),
            )

        name = name_input.strip() if name_input else "Patient"
        age = age_input.strip() if age_input else "N/A"
        s_text = symptoms_text.strip() if symptoms_text else ""

        # ── Step 1/5: Image Quality Check ──
        proc_audio = self.voice.get_cached_voice("analysis_started", lang=active_lang)
        yield (
            proc_audio,
            f"### {self.lang_service.t('report_title', lang=active_lang)}\n*Step 1/5: 🔍 Checking image quality...*",
            None,
            """<div class="gauge-container"><h2 style="font-size:1.5rem; font-weight:800; color:#2563eb; margin-top:12px; text-align:center;">Step 1/5: 🔍 Quality Check</h2></div>""",
            "", state,
            "<div class='transcript-box'>🔍 Step 1/5: Checking image quality...</div>",
            *self._make_empty_visual_outputs(),
        )

        quality_result = self.quality.check(image_path, lang=active_lang)
        quality_badge_html = self.make_quality_badge_html(quality_result, active_lang)

        if not quality_result["pass"]:
            yield (
                None,
                f"### {self.lang_service.t('report_title', lang=active_lang)}\n*{quality_result['feedback']}*",
                None,
                """<div class="gauge-container"><h2 style="font-size:2rem; font-weight:800; color:#ef4444; margin-top:12px; text-align:center;">❌ Rejected</h2><span style="font-size:0.9rem; color:#64748b;">Image quality too low for screening.</span></div>""",
                "", state,
                f"<div class='transcript-box'>❌ {quality_result['feedback']}</div>",
                quality_badge_html,
                gr.update(visible=False), None, None, None, "",
            )
            return

        # ── Step 2/5: ROI Extraction & Enhancement ──
        yield (
            None,
            f"### {self.lang_service.t('report_title', lang=active_lang)}\n*Step 2/5: ✂️ ROI extraction & CLAHE enhancement...*",
            None,
            """<div class="gauge-container"><h2 style="font-size:1.5rem; font-weight:800; color:#2563eb; margin-top:12px; text-align:center;">Step 2/5: ✂️ Enhancement</h2></div>""",
            "", state,
            "<div class='transcript-box'>✂️ Step 2/5: Enhancing image...</div>",
            quality_badge_html,
            gr.update(visible=False), None, None, None, "",
        )

        # 1. Symptom parsing
        symptoms = self.medical.parse_symptoms(s_text)

        # ── Step 3/5: MobileNetV3 Inference ──
        yield (
            None,
            f"### {self.lang_service.t('report_title', lang=active_lang)}\n*Step 3/5: 🧠 MobileNetV3 AI inference...*",
            None,
            """<div class="gauge-container"><h2 style="font-size:1.5rem; font-weight:800; color:#2563eb; margin-top:12px; text-align:center;">Step 3/5: 🧠 AI Inference</h2></div>""",
            "", state,
            "<div class='transcript-box'>🧠 Step 3/5: Running MobileNetV3 inference...</div>",
            quality_badge_html,
            gr.update(visible=False), None, None, None, "",
        )

        # 2. MobileNetV3 photo prediction (includes Grad-CAM)
        photo_result = None
        priority = "Low"
        risk_percent = 0.0
        heatmap_img = None
        enhanced_img = None
        original_img = None

        if image_path is not None:
            has_anemia_symptoms = self.medical.has_anemia_symptoms(symptoms)
            photo_result = self.vision.predict(image_path, has_symptoms=has_anemia_symptoms)
            priority = photo_result.get("hb_test_priority", "Low")
            risk_percent = photo_result.get("risk_percent", 0.0)
            heatmap_img = photo_result.get("heatmap_image", None)
            enhanced_img = photo_result.get("enhanced_image", None)
            original_img = photo_result.get("original_image", None)

        # ── Step 4/5: Grad-CAM Analysis ──
        yield (
            None,
            f"### {self.lang_service.t('report_title', lang=active_lang)}\n*Step 4/5: 🔬 Grad-CAM visual explanation...*",
            None,
            """<div class="gauge-container"><h2 style="font-size:1.5rem; font-weight:800; color:#2563eb; margin-top:12px; text-align:center;">Step 4/5: 🔬 Grad-CAM</h2></div>""",
            "", state,
            "<div class='transcript-box'>🔬 Step 4/5: Generating Grad-CAM heatmap...</div>",
            quality_badge_html,
            gr.update(visible=True), original_img, enhanced_img, heatmap_img, "",
        )

        # ── Step 5/5: Report Generation ──
        yield (
            None,
            f"### {self.lang_service.t('report_title', lang=active_lang)}\n*Step 5/5: 📋 Generating clinical report...*",
            None,
            """<div class="gauge-container"><h2 style="font-size:1.5rem; font-weight:800; color:#2563eb; margin-top:12px; text-align:center;">Step 5/5: 📋 Report</h2></div>""",
            "", state,
            "<div class='transcript-box'>📋 Step 5/5: Generating clinical report...</div>",
            quality_badge_html,
            gr.update(visible=True), original_img, enhanced_img, heatmap_img, "",
        )

        # 3. Basic Care Guidance
        basic_care = self.medical.get_care(symptoms, lang=active_lang)

        # 4. Compile Report Dict
        patient_data = {"name": name, "age": age, "symptoms": s_text}
        report_dict, display_markdown = self.report.build(patient_data, photo_result, symptoms, basic_care)

        gauge_html = self.make_gauge_html(priority, risk_percent, lang=active_lang)
        care_html = self.make_care_html(basic_care, lang=active_lang)

        # 5. Generate PDF Report
        pdf_path = self.pdf.generate(report_dict, patient_name=name, lang=active_lang)

        spoken_summary = self.lang_service.t("report_spoken_summary", lang=active_lang, name=name, priority=priority)
        transcript_html = f"<div class='transcript-box'>💬 {spoken_summary}</div>"

        whatsapp_html = self.make_whatsapp_html(name, priority, risk_percent)

        # Yield initial report state
        yield (
            None,
            display_markdown,
            pdf_path,
            gauge_html,
            care_html,
            state,
            transcript_html,
            quality_badge_html,
            gr.update(visible=True),
            original_img, enhanced_img, heatmap_img,
            whatsapp_html,
        )

        # 6. LLM Stream (if requested)
        llama_explanation = ""
        if use_llama:
            report_with_llama = display_markdown + f"\n\n---\n\n### 5. AROVA ASSISTANT SUMMARY ({active_lang.upper()})\n\n"
            for partial_text in self.llm.explain_stream(report_dict, lang=active_lang):
                llama_explanation = partial_text
                yield (
                    None,
                    report_with_llama + partial_text,
                    pdf_path,
                    gauge_html,
                    care_html,
                    state,
                    transcript_html,
                    quality_badge_html,
                    gr.update(visible=True),
                    original_img, enhanced_img, heatmap_img,
                    whatsapp_html,
                )

        # 7. Generate Spoken Voice Summary
        audio_path = None
        if generate_voice:
            now = datetime.datetime.now()
            closing_key = "closing_morning" if 5 <= now.hour < 17 else "closing_evening"
            severe_present = bool(self.medical.get_severe_symptoms(symptoms))

            try:
                audio_path = self.voice.speak_dynamic_report(
                    name=name,
                    priority=priority,
                    generate_care=True,
                    severe_present=severe_present,
                    closing_key=closing_key,
                    lang=active_lang,
                )
            except Exception as e:
                logger.error("Failed to generate spoken report summary: %s", e)

        final_display = display_markdown
        if use_llama and llama_explanation:
            final_display += f"\n\n---\n\n### 5. AROVA ASSISTANT SUMMARY ({active_lang.upper()})\n\n{llama_explanation}"

        yield (
            audio_path,
            final_display,
            pdf_path,
            gauge_html,
            care_html,
            state,
            transcript_html,
            quality_badge_html,
            gr.update(visible=True),
            original_img, enhanced_img, heatmap_img,
            whatsapp_html,
        )
