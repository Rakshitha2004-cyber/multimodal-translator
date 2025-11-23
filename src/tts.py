# tts.py – final version using gTTS

from __future__ import annotations

import os
import tempfile

import streamlit as st
from gtts import gTTS

from languages import lang_code_for_translation


def _tts_code_for_language(lang_name: str) -> str:
    """
    Get a language code for gTTS based on the language name.
    We reuse lang_code_for_translation and fall back to 'en'.
    """
    if not isinstance(lang_name, str):
        return "en"

    code = lang_code_for_translation(lang_name) or ""
    code = code.strip().lower()

    if not code:
        return "en"

    return code


def text_to_speech_file(text: str, language_name: str) -> str | None:
    """
    Convert text to speech using gTTS and return path to a temp MP3 file.

    Returns:
        str path to MP3, or None if TTS failed.
    """
    if not text or not text.strip():
        return None

    tts_lang = _tts_code_for_language(language_name)

    try:
        tts_obj = gTTS(text=text, lang=tts_lang)

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp_path = tmp.name
        tmp.close()

        tts_obj.save(tmp_path)

        if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
            return tmp_path

        st.error("TTS error: generated audio file is empty.")
        return None

    except Exception as e:
        st.error(f"TTS error: {e}")
        return None


def cleanup_temp_file(path: str | None) -> None:
    """Safely delete a temporary file."""
    if not path:
        return
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
