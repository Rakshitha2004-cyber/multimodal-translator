
# utils.py

try:
    from config import SUPPORTED_LANGUAGES
except Exception:
    SUPPORTED_LANGUAGES = {"English": "en"}  # fallback


def get_language_list():
    """
    Return all languages sorted alphabetically.
    Never crash even if config is broken.
    """
    try:
        langs = list(SUPPORTED_LANGUAGES.keys())
        return sorted(langs) if langs else ["English"]
    except Exception:
        return ["English"]
