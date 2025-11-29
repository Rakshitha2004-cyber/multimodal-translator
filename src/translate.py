# translate.py  – use deep_translator only

from deep_translator import GoogleTranslator
from languages import lang_code_for_translation


def _normalize_code(code: str | None) -> str:
    """
    Normalize language codes so deep_translator accepts them.
    Handles Chinese variants and basic cleanup.
    """
    if not code:
        return ""

    code = code.strip()

    low = code.lower()
    if low == "zh-cn":
        return "zh-CN"
    if low == "zh-tw":
        return "zh-TW"

    # deep_translator also accepts full names like 'chinese (simplified)'
    if low in ("chinese (simplified)", "simplified chinese"):
        return "chinese (simplified)"
    if low in ("chinese (traditional)", "traditional chinese"):
        return "chinese (traditional)"

    return code


def translate_text(text: str, src_lang_name: str, tgt_lang_name: str) -> str:
    """
    Translate text from source language to target using deep_translator.GoogleTranslator.

    text:           input text
    src_lang_name:  e.g. "English"
    tgt_lang_name:  e.g. "Hindi"
    """
    if not text:
        return ""
    text = text.strip()
    if not text:
        return ""

    src_code = lang_code_for_translation(src_lang_name)
    tgt_code = lang_code_for_translation(tgt_lang_name)

    # If both languages are effectively the same, just return original
    if src_code == tgt_code:
        return text

    # Normalize codes for deep_translator
    src_code = _normalize_code(src_code)
    tgt_code = _normalize_code(tgt_code)

    # Allow auto-detect if we don't know the source
    if not src_code:
        src_code = "auto"

    if not tgt_code:
        tgt_code = "en"

    try:
        translator = GoogleTranslator(source=src_code, target=tgt_code)
        translated = translator.translate(text)
        return translated or ""
    except Exception as e:
        # Log to console so you can see issues, but don't crash app
        print(f"[TRANSLATE ERROR] ({src_code} -> {tgt_code}) {e}")
        return text
