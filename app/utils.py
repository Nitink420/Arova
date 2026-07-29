# app/utils.py

def make_bullets(items):
    if not items:
        return "- None"
    return "\n".join([f"- {item}" for item in items])


def format_photo_result(result):
    if result.get("error"):
        return f"""
PHOTO SCREENING ERROR

Image read nahi ho paayi.

Reason:
{result.get("message")}

Please clear lower eyelid / conjunctiva image upload karein.
"""

    return f"""
PHOTO-BASED ANEMIA RISK SCREENING

Normal Indicator:
{result["normal_percent"]}%

Anemia Risk Indicator:
{result["risk_percent"]}%

Hb-test Priority:
{result["hb_test_priority"]}

Risk Wording:
{result["risk_wording"]}

Recommendation:
{result["recommendation"]}

Safety:
{result["safety"]}
"""


def format_final_response(symptoms, photo_section, basic_care):
    detected = ", ".join(symptoms) if symptoms else "No clear symptoms detected"

    return f"""
AROVA CARE RESULT

DETECTED SYMPTOMS:
{detected}

{photo_section}

BASIC CARE GUIDANCE:
{make_bullets(basic_care["care"])}

DIET ADVICE:
{make_bullets(basic_care["diet"])}

WARNING SIGNS:
{make_bullets(basic_care["warnings"])}

FINAL SAFETY NOTE:
Arova final diagnosis nahi karta.
Arova medicine prescribe nahi karta.
Agar symptoms severe hain, nearest doctor/clinic visit karein.
"""