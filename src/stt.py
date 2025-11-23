## stt.py
# stt.py

import speech_recognition as sr

# Map your UI language names to Google STT language codes
LANG_CODE_MAP = {
    "English": "en-IN",     # Indian English
    "Hindi": "hi-IN",
    "Kannada": "kn-IN",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Malayalam": "ml-IN",
    "Marathi": "mr-IN",
    # add more if you want: "French": "fr-FR", etc.
}

_recognizer = sr.Recognizer()


def _get_lang_code(source_language_name: str) -> str:
    """Return Google STT language code for the given language name."""
    return LANG_CODE_MAP.get(source_language_name, "en-IN")


def speech_to_text(audio_file_path: str, source_language_name: str = None) -> str:
    """
    Convert speech in an audio file to text using Google Web Speech API.

    - Expects a WAV file (which audio_recorder_streamlit creates).
    - Returns "" if nothing could be recognized or an error happened.
    """
    lang_code = _get_lang_code(source_language_name or "English")

    try:
        with sr.AudioFile(audio_file_path) as source:
            audio_data = _recognizer.record(source)

        # Try to recognize using Google's free web API
        text = _recognizer.recognize_google(audio_data, language=lang_code)
        return text.strip()

    except sr.UnknownValueError:
        # Speech was detected but not understood
        return ""
    except Exception as e:
        # Any other error (network, format, etc.)
        print(f"[STT ERROR] {e}")
        return ""
