CRITICAL_MEDICAL_TERMS = {
    "bp": "blood pressure",
    "sugar": "blood glucose",
    "heart attack": "myocardial infarction",
    "stroke": "cerebrovascular accident",
    "fever": "pyrexia",
}

def sanitize_medical_text(text: str) -> str:
    text_lower = text.lower()
    for short, proper in CRITICAL_MEDICAL_TERMS.items():
        text_lower = text_lower.replace(short, proper)
    return text_lower
