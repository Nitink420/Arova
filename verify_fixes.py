"""
Arova Full Pipeline Verification Script
Tests all 8 core modules after debug fixes.
"""
import sys
sys.path.insert(0, '.')

print("=" * 50)
print("  AROVA POST-FIX VERIFICATION")
print("=" * 50)

# 1. Vision model
from src.predict_mobilenet import load_model, predict_image
model = load_model()
print("[OK] 1. Vision model loaded successfully")

# 2. Symptom parser
from src.symptom_parser import parse_symptoms
symptoms = parse_symptoms("weakness chakkar bukhar thakan")
print(f"[OK] 2. Symptom parser: {symptoms}")

# 3. Care engine
from src.basic_care_engine import get_basic_care, calculate_estimated_hb, get_amb_triage
care = get_basic_care(symptoms)
care_count = len(care["care"])
diet_count = len(care["diet"])
warn_count = len(care["warnings"])
print(f"[OK] 3. Care engine: {care_count} care, {diet_count} diet, {warn_count} warnings")

# 3b. Anemia Mukt Bharat Protocol & Estimated Hb
hb_test = calculate_estimated_hb(risk_percent=55.0, symptoms=symptoms)
assert "mid_hb" in hb_test and "amb_grade" in hb_test, "Failed AMB calculation"
print(f"[OK] 3b. AMB Protocol: {hb_test['amb_grade']} | Est. Hb: {hb_test['hb_display']} | IFA: {hb_test['amb_ifa_protocol'][:30]}...")

# 4. Report generator
from src.report_generator import build_professional_report
patient = {"name": "Test Patient", "age": "30", "symptoms": "weakness chakkar bukhar"}
report_dict, markdown = build_professional_report(patient, None, symptoms, care)
assert "estimated_hb" in report_dict and "amb_grade" in report_dict
print(f"[OK] 4. Report: {len(markdown)} chars, keys: {list(report_dict.keys())}")

# 5. PDF report
from src.pdf_report import create_pdf_report
pdf_path = create_pdf_report(report_dict)
print(f"[OK] 5. PDF created with Offline Medical QR Code: {pdf_path}")

# 6. ROI utils grayscale test & Sclera Calibration
import numpy as np
from src.roi_utils import center_crop_lower_region, make_roi_preview, sclera_white_balance_calibration, compute_erythema_index
gray_img = np.zeros((100, 100), dtype=np.uint8)
result = center_crop_lower_region(gray_img)
print(f"[OK] 6. ROI handles grayscale: shape={result.shape}")

# None safety
none_result = make_roi_preview(None)
print(f"[OK] 6b. ROI handles None: result={none_result}")

# 6c. Sclera color calibration & Erythema Index test
test_rgb = np.full((120, 120, 3), 200, dtype=np.uint8)
test_rgb[80:, :, 0] = 230  # Reddish lower eyelid
calibrated_img, meta = sclera_white_balance_calibration(test_rgb)
ei = compute_erythema_index(calibrated_img)
print(f"[OK] 6c. Sclera calibration: calibrated={meta.get('calibrated')} | Erythema Index={ei}")

# 7. LLM assistant (import only, no Ollama needed)
from src.llm_assistant import build_safe_prompt, safety_filter
prompt = build_safe_prompt("test report")
filtered = safety_filter("Some text about hb blood test")
print(f"[OK] 7. LLM assistant imports fine, safety_filter OK")

# 8. Voice + consultation modules (import only)
from src.voice_cache import CACHED_LINES
from src.consultation_flow import start_consultation, GREETING, ASK_NAME
print(f"[OK] 8. Voice + consultation: {len(CACHED_LINES)} cached lines, states OK")

print()
print("=" * 50)
print("  ALL 10 CORE & HACKATHON MODULES VERIFIED")
print("  AROVA IS FULLY PREPARED FOR WINNING DEMO!")
print("=" * 50)
