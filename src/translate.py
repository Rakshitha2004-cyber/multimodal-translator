# translate.py

# translate.py

from deep_translator import GoogleTranslator
from languages import lang_code_for_translation


def translate_text(text: str, src_lang_name: str, tgt_lang_name: str) -> str:
    """
    Translate text from source language to target using GoogleTranslator.

    text:           input text
    src_lang_name:  e.g. "English"
    tgt_lang_name:  e.g. "Hindi"
    """
    # Clean empty text early
    if not text:
        return ""
    text = text.strip()
    if not text:
        return ""

    src_code = lang_code_for_translation(src_lang_name)
    tgt_code = lang_code_for_translation(tgt_lang_name)

    # Allow auto-detect for source language if needed
    if not src_code:
        src_code = "auto"

    translator = GoogleTranslator(source=src_code, target=tgt_code)
    try:
        translated = translator.translate(text)
        return translated or ""
    except Exception as e:
        # In case of any translation error, just return original text (safer than crashing)
        print(f"[TRANSLATE ERROR] {e}")
        return text
