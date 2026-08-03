# app/models/patient.py
"""
AROVA Patient Data Structures

Simple data containers for patient information, prediction results,
and report data used across services for type clarity.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PatientData:
    """Patient information collected during the onboarding consultation flow."""
    name: str = "Patient"
    age: str = "N/A"
    symptoms: str = ""


@dataclass
class PredictionResult:
    """Result from VisionService prediction."""
    error: bool = False
    message: str = ""
    normal_percent: float = 100.0
    risk_percent: float = 0.0
    hb_test_priority: str = "Low"
    risk_wording: str = ""
    recommendation: str = ""
    safety: str = (
        "This is a preliminary screening result, not a final diagnosis. "
        "Please confirm with a clinical hemoglobin blood test."
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for backward compatibility with existing code."""
        return {
            "error": self.error,
            "message": self.message,
            "normal_percent": self.normal_percent,
            "risk_percent": self.risk_percent,
            "hb_test_priority": self.hb_test_priority,
            "risk_wording": self.risk_wording,
            "recommendation": self.recommendation,
            "safety": self.safety,
        }


@dataclass
class ReportData:
    """Assembled report data for PDF and display."""
    name: str = "Unknown"
    age: str = "N/A"
    symptoms: str = ""
    hb_test_priority: str = "Low"
    risk_percent: float = 0.0
    risk_wording: str = ""
    care_guidance: str = ""
    severe_present: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for backward compatibility."""
        return {
            "name": self.name,
            "age": self.age,
            "symptoms": self.symptoms,
            "hb_test_priority": self.hb_test_priority,
            "risk_percent": self.risk_percent,
            "risk_wording": self.risk_wording,
            "care_guidance": self.care_guidance,
            "severe_present": self.severe_present,
        }


@dataclass
class ConsultationState:
    """
    State container for the guided consultation flow.

    Tracks the current step and accumulated patient data.
    Used as Gradio State value.
    """
    step: str = "GREETING"
    patient: PatientData = field(default_factory=PatientData)
    conversation: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for Gradio State compatibility."""
        return {
            "step": self.step,
            "patient": {
                "name": self.patient.name,
                "age": self.patient.age,
                "symptoms": self.patient.symptoms,
            },
            "conversation": self.conversation,
        }
