# src/consultation_flow.py

import datetime
from src.voice_cache import get_cached_voice

# States
GREETING = "GREETING"
ASK_NAME = "ASK_NAME"
ASK_AGE = "ASK_AGE"
ASK_SYMPTOMS = "ASK_SYMPTOMS"
ASK_IMAGE = "ASK_IMAGE"
READY_FOR_ANALYSIS = "READY_FOR_ANALYSIS"
ANALYSIS = "ANALYSIS"
REPORT_READY = "REPORT_READY"
CLOSING = "CLOSING"


def start_consultation():
    """
    Return intro text, intro cached audio path, and initial state.
    """
    intro_text = (
        "Namaste . Main Arova hoon.   Main aapki rural health screening mein madad karne ke liye yahan hoon. "
        "Main doctor nahi hoon, aur final diagnosis nahi deti.  Confirmation ke liye clinical hemoglobin blood test zaroori hai. "
        "Kripya apna naam batayein."
    )
    audio_path = get_cached_voice("intro")
    state = {
        "step": ASK_NAME,
        "patient": {
            "name": "",
            "age": "",
            "symptoms": ""
        },
        "conversation": "AROVA: " + intro_text
    }
    return intro_text, audio_path, state


def submit_name(name, state):
    """
    Save name and return next question text + cached age question audio.
    """
    name_clean = name.strip() if name else "Patient"
    state["patient"]["name"] = name_clean
    state["step"] = ASK_AGE
    
    text = f"Dhanyavaad {name_clean} ji. Kripya apni age batayein."
    audio_path = get_cached_voice("ask_age")
    
    state["conversation"] += f"\n\nPatient: {name_clean}\nAROVA: {text}"
    return text, audio_path, state


def submit_age(age, state):
    """
    Save age and return next question text + cached symptoms question audio.
    """
    age_clean = age.strip() if age else "N/A"
    state["patient"]["age"] = age_clean
    state["step"] = ASK_SYMPTOMS
    
    text = (
        "Dhanyavaad. Ab kripya apne symptoms ya lakshan batayein. "
        "Jaise weakness, tiredness, dizziness, pale eyes, breathlessness, chest pain, fainting, ya severe weakness."
    )
    audio_path = get_cached_voice("ask_symptoms")
    
    state["conversation"] += f"\n\nPatient: {age_clean}\nAROVA: {text}"
    return text, audio_path, state


def submit_symptoms(symptoms, state):
    """
    Save symptoms and return next question text + cached image instruction audio.
    """
    symptoms_clean = symptoms.strip() if symptoms else "None reported"
    state["patient"]["symptoms"] = symptoms_clean
    state["step"] = ASK_IMAGE
    
    text = "Symptoms note kar liye gaye hain. Ab kripya lower eyelid ya conjunctiva area ki clear photo upload ya capture karein."
    audio_path = get_cached_voice("ask_image")
    
    state["conversation"] += f"\n\nPatient: {symptoms_clean}\nAROVA: {text}"
    return text, audio_path, state


def get_time_based_closing_audio():
    """
    Return closing text and cached closing audio according to time of day.
    """
    now = datetime.datetime.now()
    hour = now.hour
    
    # 5 AM to 5 PM is considered daytime/morning for closing_morning
    if 5 <= hour < 17:
        text = "Dhanyavaad. Kripya apna dhyan rakhein. Aapka din shubh ho."
        audio_path = get_cached_voice("closing_morning")
    else:
        text = "Dhanyavaad. Aapki shaam shubh ho. Zaroorat ho toh nearby clinic se salah lein."
        audio_path = get_cached_voice("closing_evening")
        
    return text, audio_path
