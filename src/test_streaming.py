# src/test_streaming.py

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.predict_mobilenet import load_model, predict_image
from src.symptom_parser import parse_symptoms
from src.basic_care_engine import get_basic_care
from src.report_generator import build_professional_report
from src.llm_assistant import ask_llama_stream

def main():
    print("Testing streaming and measuring latency...")
    test_image = "data/raw/dataset_1/CP-AnemiC dataset/Anemic/Image_001.png"
    symptoms_text = "mujhe thakan, chakkar aur bukhar hai"

    # Simulate the pipeline steps that run_screening does
    model = load_model()

    t0 = time.time()

    # 1. Parse symptoms
    symptoms = parse_symptoms(symptoms_text)

    # 2. Photo-based screening
    photo_result = predict_image(test_image, model=model)

    # 3. Care engine
    basic_care = get_basic_care(symptoms)

    # 4. Build report
    patient_data = {"name": "Test Patient", "age": "30", "symptoms": symptoms_text}
    report_dict, display_markdown = build_professional_report(patient_data, photo_result, symptoms, basic_care)

    t_report = time.time() - t0
    print(f"\n[Step 1-4] Report generated in {t_report:.2f} seconds")
    print(f"Report length: {len(display_markdown)} characters")
    print("-" * 50)

    # 5. Stream Llama explanation
    yield_count = 0
    first_yield_time = None
    last_response = ""

    try:
        for partial_text in ask_llama_stream(display_markdown):
            yield_count += 1
            elapsed = time.time() - t0

            if yield_count == 1:
                first_yield_time = elapsed
                print(f"\n[Yield 1] First LLM token in {elapsed:.2f} seconds")
            elif yield_count % 15 == 0:
                print(f"[Yield {yield_count}] Streaming... Elapsed: {elapsed:.2f}s | Response length: {len(partial_text)} chars")

            last_response = partial_text

        elapsed_total = time.time() - t0
        print(f"\n[Final Yield {yield_count}] Completed pipeline in {elapsed_total:.2f} seconds!")
        print("-" * 50)
        print("Llama Explanation Sample Output:")
        print(last_response[-300:])
        print("-" * 50)

        print("\nStreaming test PASSED!")

    except Exception as e:
        print(f"\nStreaming test FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
