# medical_terms.py

MEDICAL_TERMS = [
    "paracetamol", "ibuprofen", "aspirin",
    "diabetes", "hypertension", "asthma",
    "blood pressure", "bp",
    "ecg", "mri", "ct scan",
    "covid", "covid-19"
]

def protect_medical_terms(text: str):
    """
    Replace medical terms with placeholders
    """
    protected = {}
    modified = text

    for i, term in enumerate(MEDICAL_TERMS):
        token = f"__MED_{i}__"
        if term.lower() in modified.lower():
            protected[token] = term
            modified = modified.replace(term, token)
            modified = modified.replace(term.capitalize(), token)

    return modified, protected


def restore_medical_terms(text: str, protected: dict):
    for token, term in protected.items():
        text = text.replace(token, term)
    return text
