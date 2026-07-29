import gradio as gr

from src.predict_mobilenet import load_model, predict_image


model = load_model()


def arova_photo_screening(image_path):
    if image_path is None:
        return "Please upload a lower eyelid / conjunctiva image."

    result = predict_image(image_path, model=model)

    if result.get("error"):
        return f"""
AROVA ERROR

Image read nahi ho paayi.

Reason:
{result.get("message")}

Please clear image upload karein.
"""

    response = f"""
AROVA PHOTO SCREENING RESULT

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

Safety Note:
{result["safety"]}

Important:
Arova anemia confirm nahi karta.
Final confirmation ke liye clinical hemoglobin blood test zaroori hai.
"""

    return response


demo = gr.Interface(
    fn=arova_photo_screening,
    inputs=[
        gr.Image(
            type="filepath",
            sources=["upload", "webcam"],
            label="Upload or take a photo of lower eyelid / conjunctiva"
        )
    ],
    outputs=[
        gr.Textbox(
            label="Arova Screening Result",
            lines=18
        )
    ],
    title="Arova Care - Photo Based Anemia Risk Screening",
    description=(
        "Upload lower eyelid / conjunctiva photo. "
        "Arova gives preliminary Hb-test priority, not final diagnosis."
    )
)


if __name__ == "__main__":
    demo.launch()