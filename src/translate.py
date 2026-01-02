from deep_translator import GoogleTranslator


def translate_text(text: str, src_lang: str, tgt_lang: str) -> str:
    """
    Translate text using deep-translator (Google backend).
    Works on Streamlit Cloud (Python 3.13 safe).
    """
    if not text:
        return ""

    try:
        translated = GoogleTranslator(
            source="auto",
            target=tgt_lang.lower()[:2]
        ).translate(text)
        return translated
    except Exception:
        return ""
