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

    if not diet:
        diet += [
            "Iron & Folic Acid Rich Vegetables: Palak (spinach), Chukandar (beetroot), Methi, Chana.",
            "Nutrient-Dense Fruits: Anar (pomegranate), Amrood (guava), Amla, Oranges.",
            "Vitamin C Boosters: Lemon (nimbu) & Amla to enhance iron absorption.",
            "Balanced light diet lein aur paani enough piyen."
        ]

    if not warnings:
        warnings.append("Agar symptoms badhein ya 2-3 din me improve na ho, doctor/clinic visit karein.")

    return {
        "care": list(dict.fromkeys(care)),
        "diet": list(dict.fromkeys(diet)),
        "warnings": list(dict.fromkeys(warnings)),
        "safety_note": "Yeh general health guidance hai, final diagnosis ya prescription nahi."
    }


if __name__ == "__main__":
    test_symptoms = ["fever", "weakness", "dizziness"]
    print(get_basic_care(test_symptoms))