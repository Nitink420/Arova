# src/profile_pipeline.py

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.predict_mobilenet import load_model, predict_image
from src.symptom_parser import parse_symptoms
from src.basic_care_engine import get_basic_care
from src.llm_assistant import ask_llama
from src.voice_engine_offline import generate_arova_speech
from src.report_generator import build_professional_report

def main():
    print("Starting profiling...")
    test_image = "data/raw/dataset_1/CP-AnemiC dataset/Anemic/Image_001.png"
    symptoms_text = "mujhe thakan, chakkar aur bukhar hai"

    # 1. Load Vision Model
    t0 = time.time()
    model = load_model()
    t_load_model = time.time() - t0
    print(f"1. Model loading: {t_load_model:.2f} seconds")

    # 2. Vision Inference
    t0 = time.time()
    photo_result = predict_image(test_image, model=model)
    t_vision = time.time() - t0
    print(f"2. Image classification: {t_vision:.2f} seconds")

    # 3. Parse Symptoms
    t0 = time.time()
    symptoms = parse_symptoms(symptoms_text)
    t_parse = time.time() - t0
    print(f"3. Symptom parsing: {t_parse:.2f} seconds")

    # 4. Care Engine
    t0 = time.time()
    basic_care = get_basic_care(symptoms)
    t_care = time.time() - t0
    print(f"4. Care recommendation logic: {t_care:.2f} seconds")

    # 5. Build professional report
    patient_data = {"name": "Test Patient", "age": "30", "symptoms": symptoms_text}
    report_dict, display_markdown = build_professional_report(patient_data, photo_result, symptoms, basic_care)

    # 6. LLM Call
    t0 = time.time()
    llama_explanation = ask_llama(display_markdown)
    t_llm = time.time() - t0
    print(f"5. LLM (Ollama Llama 1B): {t_llm:.2f} seconds")
    print(f"   (LLM Response size: {len(llama_explanation)} chars)")

    # 7. Voice TTS Generation
    spoken_text = (
        "Test Patient ji... aapki screening complete ho gayi hai... "
        "Yeh final diagnosis nahi hai... AROVA doctor nahi hai... "
        "Confirmation ke liye clinical hemoglobin blood test karwana recommended hai..."
    )
    
    t0 = time.time()
    try:
        audio_path = generate_arova_speech(spoken_text, "profile_test.wav", cache=False)
        t_tts = time.time() - t0
        print(f"6. Voice response (Offline TTS): {t_tts:.2f} seconds")
    except Exception as e:
        t_tts = time.time() - t0
        print(f"6. Voice response FAILED after {t_tts:.2f} seconds: {e}")

if __name__ == "__main__":
    main()
