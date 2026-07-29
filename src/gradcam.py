import os
import cv2
import numpy as np
import torch
import torch.nn.functional as F


class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer

        self.gradients = None
        self.activations = None

        self.forward_hook = self.target_layer.register_forward_hook(self.save_activation)
        self.backward_hook = self.target_layer.register_full_backward_hook(self.save_gradient)

    def save_activation(self, module, input, output):
        self.activations = output.detach()

    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate(self, input_tensor, class_index=1):
        """
        class_index:
        0 = normal
        1 = risk
        """
        self.model.eval()

        output = self.model(input_tensor)

        self.model.zero_grad()

        score = output[:, class_index]
        score.backward()

        gradients = self.gradients
        activations = self.activations

        if gradients is None or activations is None:
            raise ValueError("Grad-CAM hooks did not capture gradients/activations.")

        weights = torch.mean(gradients, dim=(2, 3), keepdim=True)
        cam = torch.sum(weights * activations, dim=1)

        cam = F.relu(cam)
        cam = cam.squeeze().cpu().numpy()

        cam = cv2.resize(cam, (224, 224))

        cam = cam - np.min(cam)
        cam = cam / (np.max(cam) + 1e-8)

        return cam


def overlay_heatmap_rgb(rgb_image, cam, save_path=None):
    """
    Takes RGB image and Grad-CAM map.
    Returns RGB overlay image.
    """
    image = cv2.resize(rgb_image, (224, 224))

    heatmap = np.uint8(255 * cam)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    overlay_bgr = cv2.addWeighted(image_bgr, 0.55, heatmap, 0.45, 0)
    overlay_rgb = cv2.cvtColor(overlay_bgr, cv2.COLOR_BGR2RGB)

    if save_path is not None:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        cv2.imwrite(save_path, overlay_bgr)

    return overlay_rgb