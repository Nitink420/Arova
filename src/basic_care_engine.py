# src/basic_care_engine.py

def get_basic_care(symptoms):
    """
    Gives basic care + diet guidance based on detected symptoms.

    Safety:
    - No final diagnosis
    - No medicine prescription
    - No exact dosage
    """

    symptoms = symptoms or []

    care = []
    diet = []
    warnings = []

    if "fever" in symptoms:
        care += [
            "Rest karein aur temperature monitor karein.",
            "Paani aur fluids zyada lein.",
            "Body ko cool aur comfortable rakhein."
        ]
        diet += [
            "Khichdi, dal-rice, soup, daliya jaise halka food lein.",
            "Oily/spicy food avoid karein.",
            "Nimbu pani ya ORS jaise fluids helpful ho sakte hain."
        ]
        warnings += [
            "Fever 3 din se zyada rahe toh doctor/clinic visit karein.",
            "Very high fever, confusion, severe weakness, ya saans lene me dikkat ho toh urgent help lein."
        ]

    if "cold" in symptoms:
        care += [
            "Rest karein.",
            "Warm fluids lein.",
            "Dust/smoke se door rahein."
        ]
        diet += [
            "Garam pani, soup, herbal tea helpful ho sakti hai.",
            "Gala dard ho toh cold drinks/ice cream avoid karein."
        ]
        warnings += [
            "Cold ke saath saans lene me dikkat, chest pain, ya high fever ho toh doctor ko dikhayein."
        ]

    if "cough" in symptoms or "sore_throat" in symptoms:
        care += [
            "Warm fluids lein.",
            "Smoke/dust se door rahein.",
            "Voice ko rest dein agar gala dard hai."
        ]
        diet += [
            "Soup, garam pani, soft food helpful ho sakta hai.",
            "Spicy food avoid karein agar throat irritation ho."
        ]
        warnings += [
            "Cough bahut lamba chale, saans me dikkat ho, ya chest pain ho toh doctor ko dikhayein."
        ]

    if "diarrhea" in symptoms:
        care += [
            "ORS chhote-chhote sips me lein.",
            "Dehydration signs observe karein.",
            "Rest karein."
        ]
        diet += [
            "Banana, khichdi, curd-rice, plain rice, toast jaise light food lein.",
            "Spicy/oily food aur packaged juice avoid karein."
        ]
        warnings += [
            "Khoon, bahut kam urine, severe weakness, ya repeated loose motion ho toh doctor/clinic jaiye."
        ]

    if "vomiting" in symptoms:
        care += [
            "Paani/ORS chhote-chhote sips me lein.",
            "Ek saath zyada khana/paani na lein.",
            "Rest karein."
        ]
        diet += [
            "Vomiting kam ho toh light food: khichdi, toast, banana le sakte hain.",
            "Oily/spicy food avoid karein."
        ]
        warnings += [
            "Repeated vomiting, dehydration, blood, ya severe weakness ho toh doctor/clinic jaiye."
        ]

    if "weakness" in symptoms or "dizziness" in symptoms or "paleness" in symptoms:
        care += [
            "Rest karein aur hydration maintain karein.",
            "Sudden chakkar aaye toh turant baith/let jaayein.",
            "Agar chakkar/weakness zyada ho toh Hb blood test consider karein."
        ]
        diet += [
            "Iron & Folic Acid Rich Vegetables: Palak (spinach), Chukandar (beetroot), Methi, Chana, Rajma.",
            "Nutrient-Dense Fruits: Anar (pomegranate), Amrood (guava), Amla, Apple, Oranges.",
            "Vitamin C Boosters: Lemon (nimbu), Amla & Oranges to maximize iron absorption.",
            "Natural Superfoods: Khajur (dates), Gud (jaggery), soaked chana (chickpeas)."
        ]
        warnings += [
            "Saans phoolna, fainting, chest pain, ya severe weakness ho toh urgent medical help lein."
        ]

    if "headache" in symptoms:
        care += [
            "Paani piyen, rest karein, screen time kam karein.",
            "Neend aur stress observe karein."
        ]
        diet += [
            "Nutrient-dense light food: Khichdi, fruits (Anar, Apple), and vegetable soup.",
            "Dehydration avoid karein aur nimbu pani / coconut water lein."
        ]
        warnings += [
            "Severe headache, confusion, vomiting, fainting, ya vision problem ho toh doctor ko dikhayein."
        ]

    if "stomach_pain" in symptoms:
        care += [
            "Halka food lein aur rest karein.",
            "Spicy/oily food avoid karein."
        ]
        diet += [
            "Khichdi, curd-rice, banana, plain rice jaise light food lein."
        ]
        warnings += [
            "Severe pet dard, khoon, vomiting, ya fever ke saath pain ho toh doctor ko dikhayein."
        ]

    if "body_pain" in symptoms:
        care += [
            "Rest karein aur fever/body temperature check karein.",
            "Fluids maintain karein."
        ]
        diet += [
            "Soup, dal-rice, khichdi, and fresh fruits lein."
        ]
        warnings += [
            "Body pain ke saath high fever ya severe weakness ho toh doctor ko dikhayein."
        ]

    if "breathless" in symptoms:
        warnings.insert(0, "Saans lene me dikkat urgent sign ho sakta hai. Nearest clinic/hospital jaiye.")

    if "chest_pain" in symptoms:
        warnings.insert(0, "Seene me dard urgent sign ho sakta hai. Nearest clinic/hospital jaiye.")

    if "fainting" in symptoms:
        warnings.insert(0, "Behoshi/fainting urgent sign ho sakta hai. Nearest clinic/hospital jaiye.")

    if not care:
        care.append("Symptoms clear nahi hain. Rest karein, fluids lein, aur symptoms monitor karein.")

    # Rural Indian Affordable Superfood Guidance (Anemia Mukt Bharat aligned)
    rural_diet = [
        "🍠 Gud aur Bhuna Chana (Jaggery & Roasted Gram): Sabse sasta aur powerful natural iron source.",
        "🌿 Sahjan / Munaga ke Patte (Moringa leaves): Daal ya sabzi me pakayein, high iron & minerals.",
        "🥘 Lohe ki Kadhai me khana pakayein: Purana traditional tarika jo naturally bhojan me iron badhata hai.",
        "🍋 Nimbu Paani ya Amla: Vitamin C iron ko sharir me absorb (pachane) ke liye behad zaroori hai.",
        "🚫 Khane ke 1 ghante pehle ya baad Chai/Coffee na piyein: Chai iron ke absorption ko rok deti hai."
    ]

    if not diet:
        diet = rural_diet
    else:
        # Prepend top rural superfoods
        diet = rural_diet[:3] + diet

    if not warnings:
        warnings.append("Agar symptoms badhein ya 2-3 din me improve na ho, doctor/clinic visit karein.")

    return {
        "care": list(dict.fromkeys(care)),
        "diet": list(dict.fromkeys(diet)),
        "warnings": list(dict.fromkeys(warnings)),
        "safety_note": "Yeh general health guidance hai, final diagnosis ya prescription nahi."
    }


def calculate_estimated_hb(risk_percent: float = 0.0, symptoms: list = None) -> dict:
    """
    Calculate clinical Estimated Hemoglobin (Hb) Range calibrated against
    conjunctiva pallor risk percentage and reported symptoms.

    Reference standard:
    - Normal adult female/male baseline: 12.0 - 15.0 g/dL
    - Mild anemia: 11.0 - 11.9 g/dL
    - Moderate anemia: 8.0 - 10.9 g/dL
    - Severe anemia: < 8.0 g/dL
    """
    symptoms = symptoms or []
    has_severe = any(s in ["breathless", "chest_pain", "fainting"] for s in symptoms)
    has_general = any(s in ["weakness", "dizziness", "paleness"] for s in symptoms)

    # Symptom weight adjustment
    symptom_penalty = 0.0
    if has_severe:
        symptom_penalty = 0.8
    elif has_general:
        symptom_penalty = 0.4

    # Linear calibration from risk percentage
    # 0% risk -> ~13.8 g/dL, 100% risk -> ~6.5 g/dL
    base_hb = 13.8 - (float(risk_percent) / 100.0) * 7.0 - symptom_penalty
    base_hb = max(5.5, min(14.5, base_hb))

    margin = 0.6
    hb_low = max(5.0, round(base_hb - margin, 1))
    hb_high = min(15.0, round(base_hb + margin, 1))
    mid_hb = round(base_hb, 1)

    triage = get_amb_triage(mid_hb, symptoms)

    return {
        "mid_hb": mid_hb,
        "hb_low": hb_low,
        "hb_high": hb_high,
        "hb_display": f"{mid_hb} ± {margin} g/dL (Range: {hb_low} - {hb_high} g/dL)",
        "amb_grade": triage["grade"],
        "amb_badge": triage["badge"],
        "amb_action": triage["action"],
        "amb_color": triage["color"],
        "amb_ifa_protocol": triage["ifa_protocol"],
    }


def get_amb_triage(estimated_hb: float, symptoms: list = None) -> dict:
    """
    Map estimated Hb value to Government of India's 'Anemia Mukt Bharat' (AMB) protocol.
    """
    symptoms = symptoms or []
    is_critical_symptom = any(s in ["breathless", "chest_pain", "fainting"] for s in symptoms)

    if estimated_hb >= 12.0 and not is_critical_symptom:
        return {
            "grade": "NORMAL",
            "badge": "🟢 NORMAL (No Anemia Detected)",
            "color": "#10b981",
            "ifa_protocol": "Routine Nutrition & Dietary Iron Maintenance",
            "action": "Koi dawayi zaroori nahi. Gud-chana aur santulit poshtik aahar lein."
        }
    elif estimated_hb >= 11.0 and not is_critical_symptom:
        return {
            "grade": "MILD",
            "badge": "🟡 MILD ANEMIA (Anemia Mukt Bharat Tier 1)",
            "color": "#f59e0b",
            "ifa_protocol": "Weekly Blue IFA Tablet (Iron 60mg + Folic Acid 500mcg)",
            "action": "Hafte me ek baar Blue IFA goli lein. Nimbu/Amla ke sath Gud-Chana aur hari sabziyan lein."
        }
    elif estimated_hb >= 8.0 and not is_critical_symptom:
        return {
            "grade": "MODERATE",
            "badge": "🟠 MODERATE ANEMIA (Anemia Mukt Bharat Tier 2)",
            "color": "#f97316",
            "ifa_protocol": "Daily Red IFA Tablet (Iron 100mg + Folic Acid 500mcg) for 100 Days",
            "action": "Rojana ek Red IFA goli lein. 30 din baad ASHA worker se dubara screening karwayein."
        }
    else:
        return {
            "grade": "SEVERE",
            "badge": "🔴 SEVERE ANEMIA (🚨 Urgent Clinical Referral)",
            "color": "#ef4444",
            "ifa_protocol": "Immediate Referral to PHC/CHC for Parenteral Iron / Blood Transfusion Triage",
            "action": "TURANT paas ke Primary Health Centre (PHC) ya Hospital me Doctor ko dikhayein! Der na karein."
        }


if __name__ == "__main__":
    test_symptoms = ["weakness", "dizziness"]
    print("Care:", get_basic_care(test_symptoms))
    print("Estimated Hb:", calculate_estimated_hb(65.0, test_symptoms))