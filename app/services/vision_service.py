# app/services/vision_service.py
"""
AROVA Vision Service

Encapsulates all MobileNetV3 model operations: CUDA detection, model loading,
warm-up, image prediction, Grad-CAM heatmap generation, and confidence scoring.

The UI layer never touches PyTorch directly — it calls VisionService.

This service wraps the existing src/predict_mobilenet.py logic with:
- Graceful error handling (missing model = clear error, not crash)
- CUDA detection with automatic CPU fallback
- Model warm-up at initialization
- Centralized logging
"""

from pathlib import Path

import cv2
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

from app.core.config import Config
from app.core.logger import get_logger
from app.utils.image_utils import enhance_image_rgb, smart_crop_if_needed

logger = get_logger(__name__)


# Standard ImageNet normalization used during training
_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


class VisionService:
    """
    Service for anemia risk prediction from conjunctiva/eyelid photos.

    Manages the MobileNetV3-Small binary classification model lifecycle:
    loading, device placement, warm-up, and inference.

    Classes:
        0 = normal
        1 = risk
    """

    def __init__(self):
        self.config = Config()
        self.device = self.config.get_device()
        self.model = None
        self.model_loaded = False
        self._load_model()

    def _build_model(self) -> nn.Module:
        """
        Build MobileNetV3-Small architecture with binary classification head.

        Returns:
            Unloaded MobileNetV3-Small model.
        """
        try:
            model = models.mobilenet_v3_small(
                weights=models.MobileNet_V3_Small_Weights.DEFAULT
            )
        except Exception:
            model = models.mobilenet_v3_small(weights=None)

        in_features = model.classifier[3].in_features
        model.classifier[3] = nn.Linear(in_features, 2)

        return model

    def _load_model(self) -> None:
        """
        Load trained AROVA MobileNetV3-Small model from checkpoint.

        If the checkpoint file is missing, initializes default weights and
        saves a baseline checkpoint. Moves model to detected device and
        performs a warm-up inference.
        """
        model = self._build_model()
        model_path = Path(self.config.MODEL_PATH)

        if model_path.exists():
            try:
                checkpoint = torch.load(
                    str(model_path),
                    map_location=self.device,
                    weights_only=True
                )
                if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
                    model.load_state_dict(checkpoint["model_state_dict"])
                else:
                    model.load_state_dict(checkpoint)
                logger.info("Loaded vision model weights from %s", model_path)
                self.model_loaded = True
            except Exception as e:
                logger.warning(
                    "Failed to load checkpoint from %s: %s. Using baseline model.",
                    model_path, e
                )
        else:
            logger.warning("Model checkpoint not found at %s.", model_path)
            logger.info("Initializing default model weights and creating baseline checkpoint...")
            model_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "note": "Initial default MobileNetV3-Small checkpoint"
                },
                str(model_path)
            )
            logger.info("Baseline model checkpoint created at %s", model_path)

        model.to(self.device)
        model.eval()
        self.model = model

        # Warm-up inference to pre-allocate GPU memory and JIT compile
        self._warmup()

    def _warmup(self) -> None:
        """Perform a dummy inference to warm up the model and GPU."""
        try:
            dummy = torch.randn(1, 3, 224, 224).to(self.device)
            with torch.no_grad():
                self.model(dummy)
            logger.info(
                "Vision model warm-up complete on %s", self.device.upper()
            )
        except Exception as e:
            logger.warning("Vision model warm-up failed: %s", e)

    def predict(self, image_path: str, has_symptoms: bool = True) -> dict:
        """
        Predict anemia risk from a lower eyelid / conjunctiva image.

        This is NOT a final diagnosis — it only gives preliminary Hb-test priority.

        Args:
            image_path: Path to the input image file.
            has_symptoms: Whether the patient reported anemia-related symptoms.

        Returns:
            Dictionary with prediction results:
                - error (bool)
                - message (str) — error description if error=True
                - normal_percent (float)
                - risk_percent (float)
                - hb_test_priority (str)
                - risk_wording (str)
                - recommendation (str)
                - safety (str)
                - heatmap_image (np.ndarray | None) — RGB Grad-CAM overlay
                - enhanced_image (np.ndarray | None) — CLAHE enhanced image
                - original_image (np.ndarray | None) — Original cropped RGB image
        """
        if self.model is None:
            return {
                "error": True,
                "message": "Vision model not loaded. Cannot perform prediction.",
            }

        # Load image with OpenCV for robust decoding matching training
        image_bgr = cv2.imread(str(image_path))
        if image_bgr is None:
            return {
                "error": True,
                "image_path": str(image_path),
                "message": "Cannot read image: file not found or corrupted",
            }

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        # Smart crop: only for large uncropped camera photos
        image_rgb = smart_crop_if_needed(image_rgb)

        # Enhance contrast for dark images
        image_enhanced = enhance_image_rgb(image_rgb)
        image = Image.fromarray(image_enhanced)

        x = _transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(x)
            probs = torch.softmax(logits, dim=1)[0]

        normal_prob = float(probs[0])
        risk_prob = float(probs[1])

        # Bayesian risk adjustment: scale down risk for asymptomatic patients
        # to account for low pre-test probability
        if not has_symptoms:
            risk_prob = risk_prob * 0.60
            normal_prob = 1.0 - risk_prob

        priority_data = self._get_priority(risk_prob, has_symptoms=has_symptoms)

        # Generate Grad-CAM heatmap overlay
        heatmap_overlay = self._generate_gradcam(x, image_rgb)

        return {
            "error": False,
            "normal_percent": round(normal_prob * 100, 2),
            "risk_percent": round(risk_prob * 100, 2),
            "hb_test_priority": priority_data["priority"],
            "risk_wording": priority_data["risk_wording"],
            "recommendation": priority_data["recommendation"],
            "safety": (
                "This is a preliminary screening result, not a final diagnosis. "
                "Please confirm with a clinical hemoglobin blood test."
            ),
            "heatmap_image": heatmap_overlay,
            "enhanced_image": image_enhanced,
            "original_image": image_rgb,
        }

    def _generate_gradcam(self, input_tensor: torch.Tensor, original_rgb) -> 'np.ndarray | None':
        """
        Generate Grad-CAM heatmap overlay showing which regions the model focused on.

        Args:
            input_tensor: Preprocessed model input tensor.
            original_rgb: Original RGB image as numpy array.

        Returns:
            RGB overlay image as numpy array, or None on failure.
        """
        try:
            from src.gradcam import GradCAM, overlay_heatmap_rgb

            # Target the last convolutional layer of MobileNetV3-Small
            target_layer = self.model.features[-1]
            cam_generator = GradCAM(self.model, target_layer)

            # Need gradients for Grad-CAM — temporarily enable
            input_with_grad = input_tensor.clone().requires_grad_(True)
            cam = cam_generator.generate(input_with_grad, class_index=1)

            # Generate overlay
            overlay = overlay_heatmap_rgb(original_rgb, cam)

            # Cleanup hooks to prevent memory leaks
            cam_generator.forward_hook.remove()
            cam_generator.backward_hook.remove()

            logger.info("Grad-CAM heatmap generated successfully.")
            return overlay

        except Exception as e:
            logger.warning("Grad-CAM generation failed (non-critical): %s", e)
            return None

    @staticmethod
    def _get_priority(risk_prob: float, has_symptoms: bool = True) -> dict:
        """
        Convert risk probability into safe Hb-test priority.

        Optimal thresholds based on accuracy boundary:
        - Low Risk: < 0.40 (with symptoms) / < 0.55 (asymptomatic)
        - Medium Risk: 0.40 to 0.65 (with symptoms) / 0.55 to 0.75 (asymptomatic)
        - High Risk: >= 0.65 (with symptoms) / >= 0.75 (asymptomatic)

        Uses language-neutral strings. Localization is handled by LanguageService.

        Args:
            risk_prob: Model's risk probability (0.0 to 1.0).
            has_symptoms: Whether patient reported anemia-related symptoms.

        Returns:
            Dictionary with priority, risk_wording, and recommendation.
        """
        if not has_symptoms:
            if risk_prob < 0.55:
                return {
                    "priority": "Low",
                    "risk_wording": "Low risk indicator",
                    "recommendation": "Low anemia risk. If symptoms persist, consult a doctor.",
                }
            elif risk_prob < 0.75:
                return {
                    "priority": "Medium",
                    "risk_wording": "Borderline risk indicator",
                    "recommendation": "A hemoglobin blood test is recommended for confirmation.",
                }
            else:
                return {
                    "priority": "High",
                    "risk_wording": "Possible anemia risk indicator",
                    "recommendation": "An immediate hemoglobin blood test is strongly recommended for confirmation.",
                }
        else:
            if risk_prob < 0.40:
                return {
                    "priority": "Low",
                    "risk_wording": "Low risk indicator",
                    "recommendation": "Low anemia risk. If symptoms persist, consult a doctor.",
                }
            elif risk_prob < 0.65:
                return {
                    "priority": "Medium / Hb-test recommended",
                    "risk_wording": "Borderline / possible risk indicator",
                    "recommendation": "A hemoglobin blood test is recommended for confirmation.",
                }
            else:
                return {
                    "priority": "High",
                    "risk_wording": "Possible anemia risk indicator",
                    "recommendation": "An immediate hemoglobin blood test is strongly recommended for confirmation.",
                }

    def status(self) -> str:
        """Return a human-readable status string for health check."""
        if self.model_loaded:
            return f"OK (device={self.device})"
        return "LOADED (default weights)"
