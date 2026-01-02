from __future__ import annotations

import os
import speech_recognition as sr


# --------------------------------------------------
# INTERNAL: map UI language → Google STT language code
# --------------------------------------------------
def _stt_code_for_language(lang_name: str) -> str:
    """
    Convert UI language name to Google Speech-to-Text code.
    Uses India-specific codes where applicable.
    Always returns a safe default.
    """
    if not isinstance(lang_name, str):
        return "en-IN"

    code_map = {
        "English": "en-IN",
        "Hindi": "hi-IN",
        "Tamil": "ta-IN",
        "Telugu": "te-IN",
        "Kannada": "kn-IN",
        "Malayalam": "ml-IN",
        "Marathi": "mr-IN",
        "Bengali": "bn-IN",
        "Gujarati": "gu-IN",
        "Punjabi": "pa-IN",
        "Urdu": "ur-IN",
    }

    return code_map.get(lang_name, "en-IN")


# --------------------------------------------------
# MAIN API
# --------------------------------------------------
def speech_to_text(audio_path: str, source_language_name: str) -> str:
    """
    Convert speech audio file (WAV) to text using Google Speech Recognition.

    This function is:
    - crash-safe
    - UI-independent
    - suitable for Streamlit Cloud

    Returns:
        Recognized text (str) or empty string on failure
    """
    # ---- basic validation ----
    if not audio_path or not os.path.exists(audio_path):
        return ""

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.pause_threshold = 0.8

    stt_lang = _stt_code_for_language(source_language_name)

    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)

        if audio_data is None:
            return ""

        text = recognizer.recognize_google(
            audio_data,
            language=stt_lang
        )

        return text.strip() if text else ""

    except sr.UnknownValueError:
        # Speech not understood (very common, not an error)
        return ""

    except sr.RequestError:
        # API/network error → fail silently, don't crash UI
        return ""

    except Exception:
        # Any unexpected issue → safe fallback
        return ""
