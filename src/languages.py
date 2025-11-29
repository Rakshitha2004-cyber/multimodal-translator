# languages.py

from config import SUPPORTED_LANGUAGES


def get_all_languages() -> list[str]:
    """Return list of language names for dropdowns."""
    return list(SUPPORTED_LANGUAGES.keys())


def lang_code_for_translation(lang_name: str) -> str:
    """
    Return code used for translation / TTS.

    We store codes in SUPPORTED_LANGUAGES.
    If something is missing, fall back to English.
    """
    return SUPPORTED_LANGUAGES.get(lang_name, "en")


def has_sr_support(lang: str) -> bool:
    """
    For UI purposes, we will treat all SUPPORTED_LANGUAGES as supported.
    (In reality, SpeechRecognition/Google STT works for many of them,
    but not literally every single one. For your project demo, this is fine.)
    """
    return lang in SUPPORTED_LANGUAGES


def code_for_easyocr(lang_name: str) -> str:
    """
    Map UI language name to EasyOCR code for image OCR.
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
        "French": "fr",
        "Spanish": "es",
        "German": "de",
        "Chinese (Simplified)": "ch_sim",
        "Chinese (Traditional)": "ch_tra",
        "Japanese": "ja",
        "Korean": "ko",
        "Thai": "th",
    }
    return mapping.get(lang_name, "en")
