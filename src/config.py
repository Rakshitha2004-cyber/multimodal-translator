# config.py
# config.py

from deep_translator import GoogleTranslator


def build_supported_languages():
    """
    Ask deep_translator (Google Translate) for ALL supported languages
    and convert them into our internal format.

    Result example:
    {
        "English": {"code": "en"},
        "Hindi":   {"code": "hi"},
        ...
    }
    """
    # returns dict like {"english": "en", "hindi": "hi", ...}
    langs = GoogleTranslator().get_supported_languages(as_dict=True)

    supported = {}
    for name_lower, code in langs.items():
        # Title-case the name for display, e.g. "english" -> "English"
        display_name = name_lower.title()
        supported[display_name] = {"code": code}

    return supported


# This now contains 100+ languages supported by Google Translate
# config.py

# Master list of supported languages for the UI and translation.
# Key = label shown to user, Value = ISO code used for translation.
SUPPORTED_LANGUAGES = {
    # India / local
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Tamil": "ta",
    "Telugu": "te",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Punjabi": "pa",
    "Bengali": "bn",
    "Urdu": "ur",

    # Popular world languages
    "Arabic": "ar",
    "Chinese (Simplified)": "zh-cn",
    "Chinese (Traditional)": "zh-tw",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Portuguese": "pt",
    "Russian": "ru",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Thai": "th",
    "Indonesian": "id",
    "Turkish": "tr",
    "Dutch": "nl",
    "Swedish": "sv",
    "Polish": "pl",
    "Czech": "cs",
    "Greek": "el",
    "Vietnamese": "vi",
    "Swahili": "sw",
    "Filipino": "tl",
    "Romanian": "ro",
    "Hungarian": "hu",
    "Finnish": "fi",
    "Danish": "da",
    "Norwegian": "no",
    "Hebrew": "he",
    "Persian (Farsi)": "fa",
}
