# tts.py
# tts.py

import os
import tempfile
from gtts import gTTS

# Map your language names to gTTS language codes
TTS_LANG_CODE = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Tamil": "ta",
    "Telugu": "te",
    "Malayalam": "ml",
    "Marathi": "mr",
    # add more as needed
}


def _get_tts_code(language_name: str) -> str:
    return TTS_LANG_CODE.get(language_name, "en")


def text_to_speech_file(text: str, language_name: str) -> str | None:
    """
    Convert text to speech using gTTS.

    Returns:
        path to mp3 file, or None if text is empty.
    """
    text = (text or "").strip()
    if not text:
        # IMPORTANT: do NOT raise error – just skip audio.
        return None

    lang_code = _get_tts_code(language_name)

    tts = gTTS(text=text, lang=lang_code)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.write_to_fp(tmp)
    tmp.flush()
    tmp.close()
    return tmp.name


def cleanup_temp_file(path: str | None):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
