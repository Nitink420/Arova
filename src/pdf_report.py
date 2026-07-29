# src/pdf_report.py

import os
from datetime import datetime
from pathlib import Path
from fpdf import FPDF

class ArovaPDFReport(FPDF):
    def header(self):
        # Clinical blue top header block
        self.set_fill_color(37, 99, 235)  # Medical Blue #2563eb
        self.rect(0, 0, 210, 16, 'F')
        
        self.set_y(22)
        self.set_font('helvetica', 'B', 18)
        self.set_text_color(15, 23, 42)  # Slate 900
        self.cell(0, 8, 'AROVA CLINICAL SCREENING REPORT', border=0, align='L')
        self.ln(7)
        
        self.set_font('helvetica', 'I', 9)
        self.set_text_color(100, 116, 139)  # Slate 500
        self.cell(0, 5, 'Rural Healthcare Preliminary Screening Assistant (Offline Edge AI)', border=0, align='L')
        self.ln(6)
        
        # Divider Line
        self.set_draw_color(226, 232, 240)  # Slate 200
        self.set_line_width(0.5)
        self.line(10, 39, 200, 39)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(148, 163, 184)  # Slate 400
        self.cell(0, 10, 'Page %s | AROVA AI Screening Assistant | Preliminary Screening Only' % self.page_no(), 0, 0, 'C')


def sanitize_pdf_text(text: str) -> str:
    """Strip characters outside latin-1 character set (e.g. emojis) for FPDF compatibility."""
    if not text:
        return ""
    return "".join(c for c in str(text) if ord(c) < 256)


def create_pdf_report(report_data: dict, output_path: str = None) -> str:
    """
    Create a professional PDF report.
    Return PDF file path.
    """
    project_root = Path(__file__).resolve().parents[1]
    reports_dir = project_root / "outputs" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = str(reports_dir / f"arova_report_{timestamp}.pdf")
        
    pdf = ArovaPDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Reference and Date
    pdf.set_font('helvetica', '', 9)
    pdf.set_text_color(100, 116, 139)
    current_date = datetime.now().strftime("%d-%b-%Y %I:%M %p")
    pdf.cell(100, 5, f"Report Date: {current_date}")
    pdf.cell(0, 5, "Reference ID: #AR-8291-AI", align="R")
    pdf.ln(8)
    
    # 1. Patient Details Header
    pdf.set_fill_color(248, 250, 252) # Light slate #f8fafc
    pdf.set_font('helvetica', 'B', 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, "  1. PATIENT DETAILS", fill=True)
    pdf.ln(10)
    
    # Details Grid
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(35, 6, "  Patient Name:")
    pdf.set_font('helvetica', '', 9)
    pdf.cell(65, 6, str(report_data.get("name", "Unknown")))
    
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(30, 6, "Patient Age:")
    pdf.set_font('helvetica', '', 9)
    pdf.cell(0, 6, str(report_data.get("age", "N/A")))
    pdf.ln(6)
    
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(35, 6, "  Symptoms:")
    pdf.set_font('helvetica', '', 9)
    symptoms = str(report_data.get("symptoms", "None reported"))
    pdf.multi_cell(0, 6, symptoms)
    pdf.ln(6)
    
    # 2. Screening Summary Header
    pdf.set_fill_color(248, 250, 252)
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(0, 8, "  2. SCREENING SUMMARY", fill=True)
    pdf.ln(10)
    
    priority = report_data.get("hb_test_priority", "Low")
    risk_percent = report_data.get("risk_percent", 0.0)
    
    # Highlight priority color
    if "High" in priority:
        priority_color = (239, 68, 68)  # Red #ef4444
    elif "Medium" in priority:
        priority_color = (245, 158, 11) # Amber #f59e0b
    else:
        priority_color = (16, 185, 129) # Green #10b981
        
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(55, 6, "  Hb-Test Priority Recommendation:")
    pdf.set_font('helvetica', 'B', 9)
    pdf.set_text_color(*priority_color)
    pdf.cell(0, 6, f" {priority.upper()}")
    pdf.set_text_color(30, 41, 59)
    pdf.ln(6)
    
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(55, 6, "  Eye Image Risk Probability:")
    pdf.set_font('helvetica', '', 9)
    pdf.cell(0, 6, f" {risk_percent:.1f}% (Screening signal from lower eyelid conjunctiva)")
    pdf.ln(6)
    
    wording = report_data.get("risk_wording", "Screening completed successfully.")
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(55, 6, "  Screening Status Wording:")
    pdf.set_font('helvetica', '', 9)
    pdf.cell(0, 6, f" {wording}")
    pdf.ln(8)
    
    # 3. Care Guidance Section
    pdf.set_fill_color(248, 250, 252)
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(0, 8, "  3. GENERAL CARE & GUIDANCE", fill=True)
    pdf.ln(10)
    
    care_text = sanitize_pdf_text(report_data.get("care_guidance", ""))
    if not care_text:
        # Fallback standard bullet list
        care_text = (
            "- Iron-rich foods (green leafy vegetables, pulses, beans)\n"
            "- Dates, jaggery, nuts, and seasonal fruits\n"
            "- Maintain proper hydration (water) and rest"
        )
    
    pdf.set_font('helvetica', '', 9)
    pdf.multi_cell(0, 5, care_text)
    pdf.ln(8)
    
    # 4. Safety Disclaimer Box (Red Border / Light Red Background)
    pdf.set_fill_color(254, 242, 242) # Light Red #fef2f2
    pdf.set_draw_color(239, 68, 68)   # Red #ef4444
    pdf.set_line_width(0.8)
    
    pdf.set_font('helvetica', 'B', 9)
    pdf.set_text_color(220, 38, 38)   # Red #dc2626
    
    disclaimer_text = (
        "IMPORTANT SAFETY DISCLAIMER:\n"
        "AROVA is a preliminary rural health screening assistant. It is not a doctor and "
        "does not provide final diagnosis, medicine prescription, or dosage. A clinical hemoglobin blood test "
        "is required for confirmation. In case of severe symptoms (such as breathlessness, chest pain, "
        "fainting, or severe weakness), please visit a doctor or nearby clinic immediately."
    )
    
    # Generate rectangular warning block
    pdf.multi_cell(190, 5, disclaimer_text, border=1, fill=True, align="L")
    
    # Reset text and drawing properties
    pdf.set_text_color(30, 41, 59)
    pdf.set_draw_color(226, 232, 240)
    pdf.set_line_width(0.5)
    
    # Output to file
    pdf.output(output_path)
    return output_path


if __name__ == "__main__":
    test_data = {
        "name": "Ramesh Kumar",
        "age": "42",
        "symptoms": "fever, weakness, dizziness",
        "hb_test_priority": "Medium",
        "risk_percent": 76.5,
        "risk_wording": "Suggested Hb-test recommended within 48 hours",
        "care_guidance": "- iron-rich diet encouraged (green leafy vegetables like spinach, pulses, legumes)\n- stay hydrated (8-10 glasses of water)"
    }
    path = create_pdf_report(test_data)
    print("PDF generated successfully at:", path)
