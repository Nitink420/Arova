SYMPTOM_KEYWORDS = {
    "fatigue": ["fatigue", "tired", "tiredness", "thakan", "thakawat"],
    "dizziness": ["dizziness", "chakkar", "sir ghumna"],
    "weakness": ["weakness", "kamzori", "weak"],
    "breathlessness": ["breathlessness", "saans phoolna", "shortness of breath"],
    "pale_skin": ["pale", "paleness", "peela", "safedpan"],
    "pregnancy": ["pregnant", "pregnancy", "garbhvati", "garbhwati"]
}


SAFETY_NOTE = (
    "This is a preliminary screening result, not a final diagnosis. "
    "Please confirm with a clinical hemoglobin blood test."
)


def parse_symptoms(symptom_text):
    """
    Find simple symptom keywords from Hindi/Hinglish/English text.
    """
    if symptom_text is None:
        symptom_text = ""

    text = symptom_text.lower().strip()
    found_symptoms = []

    for symptom_name, keywords in SYMPTOM_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                found_symptoms.append(symptom_name)
                break

    return found_symptoms


def make_recommendation(prediction, risk_probability, symptom_text):
    """
    Combine image prediction and symptoms into a safer screening message.
    """
    found_symptoms = parse_symptoms(symptom_text)
    has_symptoms = len(found_symptoms) > 0

    if prediction == "risk" and has_symptoms:
        recommendation = (
            "Anemia risk detected from the image, and symptoms were also reported. "
            "Please confirm with a clinical hemoglobin blood test."
        )
    elif prediction == "risk" and not has_symptoms:
        recommendation = (
            "Anemia risk detected from the image. "
            "Please confirm with a clinical hemoglobin blood test."
        )
    elif prediction == "normal" and has_symptoms:
        recommendation = (
            "The image shows low anemia risk, but symptoms were reported. "
            "Please confirm with a clinical hemoglobin blood test."
        )
    else:
        recommendation = (
            "The image shows low anemia risk. "
            "If symptoms are present later, please confirm with a clinical hemoglobin blood test."
        )

    return {
        "found_symptoms": found_symptoms,
        "has_symptoms": has_symptoms,
        "recommendation": recommendation,
        "safety_note": SAFETY_NOTE
    }