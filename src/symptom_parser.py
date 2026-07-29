# src/symptom_parser.py

def parse_symptoms(text):
    """
    Parse Hindi / Hinglish / English symptom text
    and return normalized symptom labels.
    """

    text = (text or "").lower()

    mapping = {
        "fever": [
            "fever", "bukhar", "बुखार", "temperature", "taap", "tap"
        ],
        "cold": [
            "cold", "sardi", "सरदी", "zukam", "जुकाम",
            "naak behna", "runny nose", "blocked nose", "naak band"
        ],
        "cough": [
            "cough", "khansi", "khaansi", "खांसी"
        ],
        "sore_throat": [
            "gala dard", "gale me dard", "throat pain", "sore throat",
            "gala kharab", "गला दर्द"
        ],
        "headache": [
            "headache", "sir dard", "sar dard", "सिर दर्द", "sir dukh"
        ],
        "vomiting": [
            "vomit", "vomiting", "ulti", "उल्टी"
        ],
        "diarrhea": [
            "loose motion", "diarrhea", "dast", "दस्त", "pet kharab"
        ],
        "stomach_pain": [
            "stomach pain", "pet dard", "पेट दर्द", "abdomen pain"
        ],
        "body_pain": [
            "body pain", "badan dard", "बदन दर्द", "body ache"
        ],
        "weakness": [
            "weakness", "kamzori", "कमजोरी", "thakan", "tired", "fatigue"
        ],
        "dizziness": [
            "dizziness", "chakkar", "चक्कर", "sir ghoomna"
        ],
        "breathless": [
            "breathless", "saans phoolna", "saans lene me dikkat",
            "breathing problem", "सांस लेने में दिक्कत"
        ],
        "chest_pain": [
            "chest pain", "seene me dard", "सीने में दर्द"
        ],
        "fainting": [
            "faint", "fainting", "behosh", "behoshi", "बेहोशी"
        ],
        "paleness": [
            "pale", "peela", "safedpan", "pila", "पीला", "paleness"
        ],
    }

    found = []

    for symptom, keywords in mapping.items():
        for keyword in keywords:
            if keyword in text:
                found.append(symptom)
                break

    return list(dict.fromkeys(found))


if __name__ == "__main__":
    sample = "mujhe thakan, chakkar aur bukhar hai"
    print(parse_symptoms(sample))