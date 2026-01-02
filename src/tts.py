from __future__ import annotations

import os
import tempfile

import streamlit as st
from gtts import gTTS

from languages import lang_code_for_translation


def text_to_speech(text: str, language_name: str) -> None:
    """
    Convert text to speech and play audio directly in Streamlit.
    Used by conversation.py
    """
    if not text:
        return

    lang_code = (lang_code_for_translation(language_name) or "en").lower()

    try:
        tts = gTTS(text=text, lang=lang_code)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            audio_path = fp.name

        st.audio(audio_path)

    except Exception as e:
        st.error(f"TTS error: {e}")


def text_to_speech_file(text: str, language_name: str) -> str | None:
    """
    Convert text to speech and return the audio file path.
    Used by main_app.py
    """
    if not text:
        return None

    lang_code = (lang_code_for_translation(language_name) or "en").lower()

    try:
        tts = gTTS(text=text, lang=lang_code)

        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp_file.name)

        return tmp_file.name

    except Exception as e:
        st.error(f"TTS file generation error: {e}")
        return None


def cleanup_temp_file(file_path: str | None) -> None:
    """
    Safely delete temporary audio files.
    Used by main_app.py
    """
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass
