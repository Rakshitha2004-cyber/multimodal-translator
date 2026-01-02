# config.py
# Central, crash-safe configuration file

# --------------------------------------------------
# Translation backend (optional, never mandatory)
# --------------------------------------------------
try:
    from deep_translator import GoogleTranslator
except Exception:
    GoogleTranslator = None


# --------------------------------------------------
# MASTER SUPPORTED LANGUAGES
# IMPORTANT:
# - Value MUST always be a string language code
# - Other files assume: {"English": "en"}
# --------------------------------------------------
SUPPORTED_LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Tamil": "ta",
    "Telugu": "te",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Punjabi": "pa",
    "Urdu": "ur",

    # International (safe for text translation)
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese (Simplified)": "zh-cn",
    "Chinese (Traditional)": "zh-tw",
    "Arabic": "ar",
}

# --------------------------------------------------
# OPTIONAL: extended languages (TEXT-ONLY use)
# DO NOT use these for STT / TTS
# --------------------------------------------------
EXTENDED_TEXT_LANGUAGES = {
    "Afrikaans": "af",
    "Albanian": "sq",
    "Amharic": "am",
    "Armenian": "hy",
    "Assamese": "as",
    "Basque": "eu",
    "Bulgarian": "bg",
    "Catalan": "ca",
    "Croatian": "hr",
    "Czech": "cs",
    "Danish": "da",
    "Dutch": "nl",
    "Esperanto": "eo",
    "Estonian": "et",
    "Finnish": "fi",
    "Greek": "el",
    "Hebrew": "he",
    "Hungarian": "hu",
    "Indonesian": "id",
    "Irish": "ga",
    "Latin": "la",
    "Latvian": "lv",
    "Lithuanian": "lt",
    "Norwegian": "no",
    "Polish": "pl",
    "Romanian": "ro",
    "Slovak": "sk",
    "Slovenian": "sl",
    "Swedish": "sv",
    "Thai": "th",
    "Turkish": "tr",
    "Ukrainian": "uk",
    "Vietnamese": "vi",
}


# --------------------------------------------------
# SAFE ACCESS HELPERS
# --------------------------------------------------
def get_lang_code(lang_name: str) -> str:
    """
    Always return a valid language code.
    Never crash.
    """
    return SUPPORTED_LANGUAGES.get(lang_name, "en")
