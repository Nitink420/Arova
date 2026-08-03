# app/utils/text_utils.py
"""
AROVA Text Formatting & Sanitization Utilities

Provides text formatting helpers used across services and UI.
Extracted from the original app/utils.py and src/pdf_report.py.
"""


def make_bullets(items: list) -> str:
    """
    Format a list of strings as markdown bullet points.

    Args:
        items: List of strings.

    Returns:
        Markdown-formatted bullet list, or "- None" if empty.
    """
    if not items:
        return "- None"
    return "\n".join([f"- {item}" for item in items])


def sanitize_pdf_text(text: str) -> str:
    """
    Strip characters outside the latin-1 character set (e.g. emojis)
    for FPDF compatibility.

    FPDF's built-in fonts only support latin-1 encoding. This function
    removes characters that would cause encoding errors during PDF generation.

    Args:
        text: Input text that may contain Unicode characters.

    Returns:
        Sanitized text safe for FPDF output.
    """
    if not text:
        return ""
    return "".join(c for c in str(text) if ord(c) < 256)


def format_photo_result(result: dict) -> str:
    """
    Format a photo screening result dictionary into human-readable text.

    Args:
        result: Dictionary from VisionService prediction.

    Returns:
        Formatted text string.
    """
    if result.get("error"):
        return (
            f"PHOTO SCREENING ERROR\n\n"
            f"Image read nahi ho paayi.\n\n"
            f"Reason:\n{result.get('message')}\n\n"
            f"Please clear lower eyelid / conjunctiva image upload karein."
        )

    return (
        f"PHOTO-BASED ANEMIA RISK SCREENING\n\n"
        f"Normal Indicator:\n{result['normal_percent']}%\n\n"
        f"Anemia Risk Indicator:\n{result['risk_percent']}%\n\n"
        f"Hb-test Priority:\n{result['hb_test_priority']}\n\n"
        f"Risk Wording:\n{result['risk_wording']}\n\n"
        f"Recommendation:\n{result['recommendation']}\n\n"
        f"Safety:\n{result['safety']}"
    )


def format_final_response(symptoms: list, photo_section: str, basic_care: dict) -> str:
    """
    Format the complete AROVA care result into human-readable text.

    Args:
        symptoms: List of detected symptom strings.
        photo_section: Formatted photo screening text.
        basic_care: Dictionary with 'care', 'diet', 'warnings' lists.

    Returns:
        Formatted complete response string.
    """
    detected = ", ".join(symptoms) if symptoms else "No clear symptoms detected"

    return (
        f"AROVA CARE RESULT\n\n"
        f"DETECTED SYMPTOMS:\n{detected}\n\n"
        f"{photo_section}\n\n"
        f"BASIC CARE GUIDANCE:\n{make_bullets(basic_care['care'])}\n\n"
        f"DIET ADVICE:\n{make_bullets(basic_care['diet'])}\n\n"
        f"WARNING SIGNS:\n{make_bullets(basic_care['warnings'])}\n\n"
        f"FINAL SAFETY NOTE:\n"
        f"Arova final diagnosis nahi karta.\n"
        f"Arova medicine prescribe nahi karta.\n"
        f"Agar symptoms severe hain, nearest doctor/clinic visit karein."
    )
