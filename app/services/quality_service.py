# app/services/quality_service.py
"""
AROVA Image Quality Validation Service

Validates uploaded eyelid/conjunctiva photos before model inference to prevent
false predictions from blurry, dark, overexposed, or invalid images.

Quality checks performed:
1. Blur detection (Laplacian variance)
2. Brightness analysis (too dark / overexposed)
3. Aspect ratio validation
4. Minimum resolution check
5. Skin-tone presence (HSV range filter)

Usage:
    from app.services.quality_service import QualityService
    quality = QualityService()
    result = quality.check(image_path)
    # result = {"pass": True, "grade": "GOOD", "score": 85, "issues": [], ...}
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional

from app.core.logger import get_logger

logger = get_logger(__name__)


class QualityService:
    """
    Service for validating image quality before anemia screening.

    Returns a quality grade (GOOD / FAIR / REJECTED) with actionable
    feedback for the user when quality is insufficient.
    """

    # Thresholds (tuned for eyelid/conjunctiva photos)
    BLUR_THRESHOLD_REJECT = 30.0      # Below = too blurry, reject
    BLUR_THRESHOLD_FAIR = 80.0        # Below = fair, warn
    BRIGHTNESS_MIN = 35               # Below = too dark
    BRIGHTNESS_MAX = 240              # Above = overexposed
    BRIGHTNESS_LOW_WARN = 60          # Below = dim warning
    MIN_RESOLUTION = 64               # Minimum width or height in pixels
    MAX_ASPECT_RATIO = 5.0            # Reject extreme aspect ratios
    SKIN_TONE_MIN_PERCENT = 5.0       # Minimum % of skin-tone pixels

    def check(self, image_path: str, lang: str = "en") -> dict:
        """
        Run all quality checks on an image.

        Args:
            image_path: Path to the image file.
            lang: Language code for localized feedback messages.

        Returns:
            Dictionary with:
                - pass (bool): Whether image passes quality gate
                - grade (str): "GOOD" | "FAIR" | "REJECTED"
                - score (int): Quality score 0-100
                - issues (list): List of detected issues
                - feedback (str): User-facing feedback message
                - details (dict): Detailed metric values
        """
        if image_path is None:
            return self._result(False, "REJECTED", 0, ["No image provided"],
                                self._msg("no_image", lang), {})

        path = Path(image_path)
        if not path.exists():
            return self._result(False, "REJECTED", 0, ["File not found"],
                                self._msg("file_missing", lang), {})

        # Load image
        image_bgr = cv2.imread(str(image_path))
        if image_bgr is None:
            return self._result(False, "REJECTED", 0, ["Cannot read image"],
                                self._msg("unreadable", lang), {})

        h, w = image_bgr.shape[:2]
        issues = []
        score = 100

        # 1. Resolution check
        if h < self.MIN_RESOLUTION or w < self.MIN_RESOLUTION:
            issues.append("resolution_too_low")
            score -= 40

        # 2. Aspect ratio check
        aspect = max(w, h) / max(min(w, h), 1)
        if aspect > self.MAX_ASPECT_RATIO:
            issues.append("extreme_aspect_ratio")
            score -= 20

        # 3. Blur detection (Laplacian variance)
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

        if blur_score < self.BLUR_THRESHOLD_REJECT:
            issues.append("too_blurry")
            score -= 35
        elif blur_score < self.BLUR_THRESHOLD_FAIR:
            issues.append("slightly_blurry")
            score -= 15

        # 4. Brightness analysis
        avg_brightness = float(gray.mean())
        if avg_brightness < self.BRIGHTNESS_MIN:
            issues.append("too_dark")
            score -= 30
        elif avg_brightness < self.BRIGHTNESS_LOW_WARN:
            issues.append("dim_lighting")
            score -= 10
        elif avg_brightness > self.BRIGHTNESS_MAX:
            issues.append("overexposed")
            score -= 25

        # 5. Skin-tone presence (HSV range for conjunctiva tissue)
        hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
        # Broad skin-tone range covering various skin colors and conjunctiva tissue
        lower_skin = np.array([0, 20, 50], dtype=np.uint8)
        upper_skin = np.array([25, 255, 255], dtype=np.uint8)
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)

        # Extended range for darker / redder tissue
        lower_skin2 = np.array([160, 20, 50], dtype=np.uint8)
        upper_skin2 = np.array([180, 255, 255], dtype=np.uint8)
        skin_mask2 = cv2.inRange(hsv, lower_skin2, upper_skin2)

        combined_mask = cv2.bitwise_or(skin_mask, skin_mask2)
        skin_percent = float(np.sum(combined_mask > 0)) / max(h * w, 1) * 100.0

        if skin_percent < self.SKIN_TONE_MIN_PERCENT:
            issues.append("no_tissue_detected")
            score -= 25

        # Clamp score
        score = max(0, min(100, score))

        # Determine grade
        if score >= 70:
            grade = "GOOD"
            passed = True
        elif score >= 40:
            grade = "FAIR"
            passed = True  # Allow with warning
        else:
            grade = "REJECTED"
            passed = False

        details = {
            "resolution": f"{w}x{h}",
            "aspect_ratio": round(aspect, 2),
            "blur_score": round(blur_score, 1),
            "avg_brightness": round(avg_brightness, 1),
            "skin_percent": round(skin_percent, 1),
        }

        feedback = self._build_feedback(grade, issues, lang)

        logger.info(
            "Image quality check: grade=%s score=%d issues=%s blur=%.1f bright=%.1f skin=%.1f%%",
            grade, score, issues, blur_score, avg_brightness, skin_percent
        )

        return self._result(passed, grade, score, issues, feedback, details)

    @staticmethod
    def _result(passed: bool, grade: str, score: int, issues: list,
                feedback: str, details: dict) -> dict:
        return {
            "pass": passed,
            "grade": grade,
            "score": score,
            "issues": issues,
            "feedback": feedback,
            "details": details,
        }

    def _build_feedback(self, grade: str, issues: list, lang: str) -> str:
        """Build user-facing feedback string based on detected issues."""
        if grade == "GOOD":
            return self._msg("quality_good", lang)

        parts = []
        issue_msgs = {
            "too_blurry": self._msg("fix_blur", lang),
            "slightly_blurry": self._msg("fix_blur_mild", lang),
            "too_dark": self._msg("fix_dark", lang),
            "dim_lighting": self._msg("fix_dim", lang),
            "overexposed": self._msg("fix_bright", lang),
            "resolution_too_low": self._msg("fix_resolution", lang),
            "extreme_aspect_ratio": self._msg("fix_crop", lang),
            "no_tissue_detected": self._msg("fix_tissue", lang),
        }
        for issue in issues:
            if issue in issue_msgs:
                parts.append(issue_msgs[issue])

        if grade == "REJECTED":
            header = self._msg("quality_rejected", lang)
        else:
            header = self._msg("quality_fair", lang)

        return header + " " + " ".join(parts)

    @staticmethod
    def _msg(key: str, lang: str) -> str:
        """Return localized quality feedback message."""
        messages = {
            "en": {
                "no_image": "Please upload an image.",
                "file_missing": "Image file not found.",
                "unreadable": "Cannot read the uploaded file. Please try a different image.",
                "quality_good": "✅ Image quality is good. Proceeding with analysis.",
                "quality_fair": "⚠️ Image quality is acceptable but could be better.",
                "quality_rejected": "❌ Image quality is too low for accurate screening.",
                "fix_blur": "Image is blurry — hold the camera steady.",
                "fix_blur_mild": "Image is slightly blurry — try holding steady.",
                "fix_dark": "Image is too dark — use better lighting.",
                "fix_dim": "Lighting is dim — try near a window.",
                "fix_bright": "Image is overexposed — reduce flash/light.",
                "fix_resolution": "Image resolution is too low.",
                "fix_crop": "Please crop to show only the lower eyelid area.",
                "fix_tissue": "No eyelid tissue detected — ensure lower eyelid is visible.",
            },
            "hi": {
                "no_image": "कृपया एक फोटो अपलोड करें।",
                "file_missing": "फोटो फ़ाइल नहीं मिली।",
                "unreadable": "फोटो पढ़ नहीं पा रहे। दूसरी फोटो लगाएं।",
                "quality_good": "✅ फोटो की गुणवत्ता अच्छी है। जांच शुरू हो रही है।",
                "quality_fair": "⚠️ फोटो ठीक है लेकिन बेहतर हो सकती है।",
                "quality_rejected": "❌ फोटो की गुणवत्ता बहुत कम है। सही फोटो लगाएं।",
                "fix_blur": "फोटो धुंधली है — कैमरा स्थिर रखें।",
                "fix_blur_mild": "फोटो थोड़ी धुंधली है।",
                "fix_dark": "फोटो बहुत अंधेरी है — अच्छी रोशनी में लें।",
                "fix_dim": "रोशनी कम है — खिड़की के पास लें।",
                "fix_bright": "फोटो बहुत चमकीली है — फ्लैश कम करें।",
                "fix_resolution": "फोटो का रेजोल्यूशन बहुत कम है।",
                "fix_crop": "केवल निचली पलक का हिस्सा दिखाएं।",
                "fix_tissue": "पलक का हिस्सा नहीं दिख रहा — निचली पलक दिखाएं।",
            },
        }
        lang_msgs = messages.get(lang, messages["en"])
        return lang_msgs.get(key, messages["en"].get(key, key))
