# languages.py
# Crash-safe language utilities

try:
    from config import SUPPORTED_LANGUAGES
except Exception:
    SUPPORTED_LANGUAGES = {"English": "en"}


def get_all_languages() -> list[str]:
    """
    Return list of language names for dropdowns.
    Never crashes even if config import fails.
    """
    try:
        return list(SUPPORTED_LANGUAGES.keys())
    except Exception:
        return ["English"]


def lang_code_for_translation(lang_name: str) -> str:
    """
    Return ISO code used for translation / TTS.
    Falls back to English safely.
    """
    if not lang_name:
        return "en"

    try:
        return SUPPORTED_LANGUAGES.get(lang_name, "en")
    except Exception:
        return "en"


def has_sr_support(lang: str) -> bool:
    """
    UI helper – assume supported if in language list.
    Safe fallback for demos.
    """
    if not lang:
        return False

    try:
        return lang in SUPPORTED_LANGUAGES
    except Exception:
        return False


def code_for_easyocr(lang_name: str) -> str:
    """
    Map UI language name to EasyOCR language code.
    Falls back to English if unsupported.
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

    if not lang_name:
        return "en"

    try:
        return mapping.get(lang_name, "en")
    except Exception:
        return "en"
