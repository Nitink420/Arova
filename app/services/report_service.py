# app/services/report_service.py
"""
AROVA Report Service

Assembles professional screening reports (markdown display + data dict).
Delegates to the existing src/report_generator.py for backward compatibility.

Usage:
    from app.services.report_service import ReportService
    report = ReportService()
    report_dict, markdown = report.build(patient_data, vision_result, symptoms, care)
"""

from typing import List, Tuple, Optional

from app.core.logger import get_logger

logger = get_logger(__name__)


class ReportService:
    """
    Service for assembling professional clinical screening reports.

    Wraps src/report_generator.build_professional_report with error handling.
    """

    def __init__(self):
        logger.info("ReportService initialized.")

    def build(
        self,
        patient_data: dict,
        vision_result: Optional[dict],
        symptoms: List[str],
        care_result: dict,
    ) -> Tuple[dict, str]:
        """
        Build a professional clinical screening report.

        Args:
            patient_data: Patient info dict with 'name', 'age', 'symptoms'.
            vision_result: Vision model prediction result dict.
            symptoms: List of normalized symptom labels.
            care_result: Care/diet guidance dict from MedicalService.

        Returns:
            Tuple of (report_dict, display_markdown).
            report_dict is used for PDF generation.
            display_markdown is shown in the Gradio UI.
        """
        try:
            from src.report_generator import build_professional_report
            return build_professional_report(
                patient_data, vision_result, symptoms, care_result
            )
        except Exception as e:
            logger.error("Report assembly failed: %s", e)
            return self._fallback_report(patient_data, vision_result)

    @staticmethod
    def _fallback_report(
        patient_data: dict,
        vision_result: Optional[dict],
    ) -> Tuple[dict, str]:
        """
        Generate a minimal fallback report when the report generator fails.

        Returns:
            Tuple of (report_dict, display_markdown).
        """
        name = patient_data.get("name", "Patient")
        age = patient_data.get("age", "N/A")
        symptoms = patient_data.get("symptoms", "None reported")

        priority = "Low"
        risk_percent = 0.0
        if vision_result and not vision_result.get("error"):
            priority = vision_result.get("hb_test_priority", "Low")
            risk_percent = vision_result.get("risk_percent", 0.0)

        report_dict = {
            "name": name,
            "age": age,
            "symptoms": symptoms,
            "hb_test_priority": priority,
            "risk_percent": risk_percent,
            "risk_wording": "Screening completed.",
            "care_guidance": "- Please consult a healthcare professional.",
            "severe_present": False,
        }

        markdown = (
            f"# AROVA Clinical Screening Report\n\n"
            f"**Patient:** {name} | **Age:** {age}\n\n"
            f"**Symptoms:** {symptoms}\n\n"
            f"**Hb-Test Priority:** {priority}\n\n"
            f"**Risk Indicator:** {risk_percent:.1f}%\n\n"
            f"---\n\n"
            f"> ⚠️ This is a preliminary screening result, not a final diagnosis. "
            f"Please confirm with a clinical hemoglobin blood test."
        )

        return report_dict, markdown
