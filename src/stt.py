# stt.py – final version using SpeechRecognition + Google Web Speech API

from __future__ import annotations

import speech_recognition as sr
import streamlit as st

from languages import lang_code_for_translation


def _stt_code_for_language(lang_name: str) -> str:
    """
    Map our language name to a code usable by Google's STT.

    We reuse lang_code_for_translation(). If it returns something
    empty or strange, we fall back to English ("en-US").
    """
    if not isinstance(lang_name, str):
        return "en-US"

    code = (lang_code_for_translation(lang_name) or "").strip().lower()

    # Google Web Speech API usually accepts simple ISO codes like "en", "hi", "ar".
    # If we don't get anything, fall back to English (US).
    if not code:
        return "en-US"

    return code


def speech_to_text(audio_path: str, language_name: str) -> str:
    """
    Convert speech audio file to text.

    Parameters
    ----------
    audio_path : str
        Path to a WAV audio file.
    language_name : str
        Human-readable language name (e.g. "English", "Hindi").

    Returns
    -------
    str
        Recognized text, or "" if recognition failed.
    """
    recognizer = sr.Recognizer()
    stt_lang = _stt_code_for_language(language_name)

    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)

        # You need internet for this to work
        text = recognizer.recognize_google(audio_data, language=stt_lang)
        return text or ""
    except sr.UnknownValueError:
        # Speech was not understood
        return ""
    except sr.RequestError as e:
        st.error(f"Speech recognition error (API): {e}")
        return ""
    except Exception as e:
        st.error(f"Speech recognition error: {e}")
        return ""
