# src/report_generator.py

import datetime

def build_professional_report(patient_data: dict, vision_result: dict, symptom_result: list, care_result: dict) -> tuple:
    """
    Build a professional clinical screening report.
    Returns:
        (report_dict, display_markdown)
    """
    name = patient_data.get("name", "Unknown")
    age = patient_data.get("age", "N/A")
    symptoms_raw = patient_data.get("symptoms", "")
    
    # 1. Process Vision Result
    if vision_result and not vision_result.get("error"):
        risk_percent = vision_result.get("risk_percent", 0.0)
        normal_percent = vision_result.get("normal_percent", 100.0)
        hb_test_priority = vision_result.get("hb_test_priority", "Low")
        risk_wording = vision_result.get("risk_wording", "Screening completed successfully.")
    else:
        risk_percent = 0.0
        normal_percent = 100.0
        hb_test_priority = "Low (No Image)"
        risk_wording = "No lower eyelid photo uploaded."

    # 2. Process Symptoms
    symptoms_list = symptom_result if isinstance(symptom_result, list) else []
    symptoms_str = ", ".join(symptoms_list) if symptoms_list else str(symptom_result)
    if not symptoms_str:
        symptoms_str = "None reported"

    # Check for severe symptoms
    severe_indicators = ["breathless", "chest_pain", "fainting", "weakness"]
    severe_symptoms = [s for s in symptoms_list if s in severe_indicators]

    # 3. Assemble Care Guidance Text
    care_list = []
    diet_list = []
    
    if care_result:
        care_list = care_result.get("care", [])
        diet_list = care_result.get("diet", [])
        
    # Standard nutrient-rich food items requested
    standard_foods = [
        "🥬 Iron & Folic Acid Rich Vegetables: Palak (spinach), Chukandar (beetroot), Methi, Chana, and Rajma.",
        "🍎 Nutrient-Dense Fruits: Anar (pomegranate), Amrood (guava), Amla, Apple, and Oranges.",
        "🍋 Vitamin C Boosters: Lemon (nimbu) & Amla (helps body absorb iron effectively).",
        "🍯 Natural Minerals & Superfoods: Khajur (dates), Gud (jaggery), soaked chickpeas & nuts."
    ]
    
    # Combine standard list with engine results
    combined_diet = standard_foods.copy()
    if diet_list:
        combined_diet.extend(diet_list)
        
    # Filter out duplicate guidance points
    unique_diet = []
    for item in combined_diet:
        if item not in unique_diet:
            unique_diet.append(item)

    unique_care = []
    if care_list:
        unique_care.extend(care_list)
    else:
        unique_care.append("Ensure regular sleep cycles and rest.")
        unique_care.append("Stay hydrated by drinking 8-10 glasses of clean water daily.")

    # 3b. Calculate Estimated Hb & Anemia Mukt Bharat Protocol
    from src.basic_care_engine import calculate_estimated_hb
    hb_data = calculate_estimated_hb(risk_percent=risk_percent, symptoms=symptoms_list)

    # 4. Assemble report dictionary for PDF and other files
    report_dict = {
        "name": name,
        "age": age,
        "symptoms": symptoms_raw if symptoms_raw else symptoms_str,
        "hb_test_priority": hb_test_priority,
        "risk_percent": risk_percent,
        "risk_wording": risk_wording,
        "estimated_hb": hb_data["hb_display"],
        "amb_grade": hb_data["amb_grade"],
        "amb_badge": hb_data["amb_badge"],
        "amb_action": hb_data["amb_action"],
        "amb_ifa_protocol": hb_data["amb_ifa_protocol"],
        "amb_color": hb_data["amb_color"],
        "care_guidance": "\n".join([f"- {c}" for c in unique_care] + [f"- {d}" for d in unique_diet]),
        "severe_present": len(severe_symptoms) > 0
    }

    # 5. Build Display Markdown (Clinical White Theme Aesthetics)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    priority_badge_color = "#10b981" # Green
    if "High" in hb_test_priority:
        priority_badge_color = "#ef4444" # Red
    elif "Medium" in hb_test_priority:
        priority_badge_color = "#f59e0b" # Amber
        
    markdown = f"""
# AROVA Clinical Screening Report

**Reference ID:** `#AR-8291-AI`  
**Date & Time:** `{current_time}`

---

### 1. Patient Details
| Detail | Value |
| :--- | :--- |
| **Patient Name** | {name} |
| **Patient Age** | {age} |
| **Symptoms Reported** | {symptoms_raw if symptoms_raw else symptoms_str} |

---

### 2. Screening Summary & AMB Clinical Triage
* **Eye Image Risk Probability:** **`{risk_percent:.1f}%`** (Based on lower eyelid conjunctiva photo)
* **Estimated Hemoglobin (Hb):** **`{hb_data['hb_display']}`**
* **National AMB Protocol Grade:** <span style="background-color:{hb_data['amb_color']}; color:#ffffff; padding:4px 10px; border-radius:4px; font-weight:bold; font-size: 0.9em;">{hb_data['amb_badge']}</span>
* **Hb-Test Recommendation Priority:** <span style="background-color:{priority_badge_color}; color:#ffffff; padding:4px 10px; border-radius:4px; font-weight:bold; font-size: 0.9em;">{hb_test_priority.upper()}</span>
* **Recommended Clinical Action:** {hb_data['amb_action']}
* **IFA Protocol:** *{hb_data['amb_ifa_protocol']}*
* **Screening Explanation:** {risk_wording}

---

### 3. General Care Guidance
#### 🥗 Nutrition & Diet Advice:
"""
    for d in unique_diet:
        markdown += f"- {d}\n"
        
    markdown += """
#### 🛌 Rest & Recovery Advice:
"""
    for c in unique_care:
        markdown += f"- {c}\n"

    markdown += """
---

### 4. Safety Notes
> [!IMPORTANT]
> * **AROVA is a preliminary screening assistant, NOT a doctor.** It does not provide medical treatment, diagnoses, prescriptions, or dosages.
> * **This report is NOT a final medical diagnosis.** A clinical hemoglobin blood test (Hb-Test) is mandatory for confirmed medical evaluation.
"""

    if severe_symptoms:
        markdown += """
> [!WARNING]
> * **SEVERE SYMPTOMS DETECTED:** Breathlessness, chest pain, fainting, or severe weakness were reported.
> * **ACTION REQUIRED:** Please consult a qualified medical professional or visit the nearest healthcare clinic immediately.
"""
    else:
        markdown += """
> [!NOTE]
> * In case of worsening symptoms or if tiredness persists, please seek advice from a doctor.
"""

    markdown += """
---
*Disclaimer: Arova is designed for edge screening purposes only and is not intended to confirm or rule out any pathology.*
"""

    return report_dict, markdown.strip()
