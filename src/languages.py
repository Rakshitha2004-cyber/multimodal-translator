# languages.py

from config import SUPPORTED_LANGUAGES


def get_all_languages() -> list[str]:
    """Return list of language names for dropdowns."""
    return list(SUPPORTED_LANGUAGES.keys())


def lang_code_for_translation(lang_name: str) -> str:
    """Return ISO language code for translation."""
    return SUPPORTED_LANGUAGES.get(lang_name, "en")


def has_sr_support(lang: str) -> bool:
    """
    Languages that our SpeechRecognition-based STT supports.
    (You can extend this list as you test.)
    """
    sr_supported = [
        "English",
        "Hindi",
        "Kannada",
        "Tamil",
        "Telugu",
        "Malayalam",
        "Marathi",
    ]
    return lang in sr_supported


def code_for_easyocr(lang_name: str) -> str:
    """
    Map UI language name to EasyOCR code.
    Only some languages are supported by EasyOCR; others fall back to 'en'.
    """
    mapping = {
        "English": "en",
        "Hindi": "hi",
        "Tamil": "ta",
        "Telugu": "te",
        "Kannada": "kn",
        "Malayalam": "ml",
        "Marathi": "mr",
        "Bengali": "bn",
        "Gujarati": "gu",
        "Urdu": "ur",
        # you can add more if EasyOCR supports them
    }
    return mapping.get(lang_name, "en")
