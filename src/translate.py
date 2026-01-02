from __future__ import annotations

from googletrans import Translator
from languages import lang_code_for_translation

translator = Translator()


def translate_text(
    text: str,
    source_language: str,
    target_language: str
) -> str:
    """
    Premium translation logic:
    - Auto-detects language
    - Forces translation even if same language is selected
    """
    if not text:
        return ""

    try:
        src_code = lang_code_for_translation(source_language)
        tgt_code = lang_code_for_translation(target_language)

        # Auto-detect if same language selected
        if src_code == tgt_code:
            result = translator.translate(text, dest=tgt_code)
        else:
            result = translator.translate(text, src=src_code, dest=tgt_code)

        return result.text

    except Exception as e:
        # Fallback: never break the app
        return text
