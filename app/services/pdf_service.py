# app/services/pdf_service.py
"""
AROVA Multilingual PDF Service

Wraps localized PDF report generation with fault tolerance.
PDF generation failure never prevents the screening pipeline from completing.

Usage:
    from app.services.pdf_service import PDFService
    pdf = PDFService()
    path = pdf.generate(report_data, patient_name="Ramesh", lang="hi")
"""

import datetime
from pathlib import Path
from typing import Optional

from app.core.config import Config
from app.core.logger import get_logger
from app.services.language_service import LanguageService

logger = get_logger(__name__)


class PDFService:
    """
    Service for generating professional, localized PDF screening reports.

    Wraps src/pdf_report.create_pdf_report with error isolation.
    If PDF generation fails, the error is logged but the screening
    pipeline continues — the user still gets their on-screen report.
    """

    def __init__(self):
        self.config = Config()
        self.lang_service = LanguageService()
        self.reports_dir = self.config.REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        logger.info("PDFService initialized. Reports dir: %s", self.reports_dir)

    def generate(
        self,
        report_data: dict,
        patient_name: str = "Patient",
        output_path: Optional[str] = None,
        lang: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a localized PDF report from screening data.
        """
        target_lang = lang or self.lang_service.get_language()
        try:
            if output_path is None:
                safe_name = patient_name.replace(" ", "_").replace("/", "_")
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"arova_report_{safe_name}_{target_lang}_{timestamp}.pdf"
                output_path = str(self.reports_dir / filename)

            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            from src.pdf_report import create_pdf_report
            pdf_path = create_pdf_report(report_data, output_path, lang=target_lang)

            logger.info("Localized PDF report generated (%s): %s", target_lang, pdf_path)
            return pdf_path

        except Exception as e:
            logger.error(
                "PDF report generation failed for lang='%s': %s. "
                "Screening results are still available on-screen.",
                target_lang,
                e,
            )
            return None
