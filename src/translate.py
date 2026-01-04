from deep_translator import GoogleTranslator
from languages import lang_code_for_translation


def translate_text(text: str, src_lang: str, tgt_lang: str) -> str:
    """
    Translate text using deep-translator (Google backend).
    Correctly maps UI language names to ISO codes.
    """
    if not text:
        return ""

    try:
        # Convert UI language name → correct ISO code (e.g., Kannada → kn)
        target_code = lang_code_for_translation(tgt_lang)

        translated = GoogleTranslator(
            source="auto",
            target=target_code
        ).translate(text)

        return translated

    except Exception as e:
        # Optional: log for debugging
        print("Translation error:", e)
        return ""
