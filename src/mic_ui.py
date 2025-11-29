# mic_ui.py – Mic with clear START / STOP style icons and status

from __future__ import annotations

import streamlit as st
from audio_recorder_streamlit import audio_recorder


def _status_box(text: str, mode: str = "info") -> None:
    """Show a clear status message with icons."""
    if mode == "ready":
        bg = "#e0f2fe"
        border = "#2563eb"
        emoji = "▶"   # start icon
    elif mode == "saved":
        bg = "#e8f5e9"
        border = "#22c55e"
        emoji = "⏹"  # stop icon / done
    else:
        bg = "#fef9c3"
        border = "#f59e0b"
        emoji = "🎙️"

    st.markdown(
        f"""
        <div style="
            margin-top:0.6rem;
            padding:0.45rem 0.8rem;
            border-radius:10px;
            background:{bg};
            border:1px solid {border};
            font-size:0.9rem;
            display:flex;
            align-items:center;
            gap:0.5rem;
        ">
            <span style="font-size:1.1rem;">{emoji}</span>
            <span>{text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def medical_mic(title: str, key: str) -> bytes | None:
    """
    Simple, clear mic widget:

    - The MIC ICON is the real Start/Stop button.
    - User clicks mic once → starts recording
    - User clicks mic again → stops and returns audio
    - We show:
        ▶ "Click the mic to START recording"
        ⏹ "Recording saved, you can TRANSLATE now"
    - Returns recorded audio bytes (or None if nothing yet).
    """

    last_audio_key = f"{key}_last_audio"

    if last_audio_key not in st.session_state:
        st.session_state[last_audio_key] = None

    st.markdown(
        f"""
        <div style="
            border-radius:18px;
            padding:1rem 1.2rem;
            background:rgba(255,255,255,0.96);
            box-shadow:0 8px 20px rgba(15,23,42,0.10);
            border:1px solid rgba(148,163,184,0.45);
            margin-bottom:0.5rem;
        ">
            <div style="font-weight:700; font-size:1.05rem; margin-bottom:0.2rem;">
                {title}
            </div>
            <div style="font-size:0.85rem; color:#64748b;">
                <b>How to use:</b><br/>
                ▶ Click the mic icon once to <b>start</b> recording.<br/>
                ⏹ Click the mic icon again to <b>stop</b> and save.<br/>
                The last saved recording will be used for translation.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Main mic widget (this is the real start/stop control)
    audio_bytes = audio_recorder(
        text="Click mic to START / STOP recording",
        recording_color="#ef4444",
        neutral_color="#2563eb",
        icon_name="microphone",
        icon_size="3x",
        sample_rate=16_000,
        key=key,
    )

    # If user just recorded new audio, store it
    if audio_bytes is not None:
        st.session_state[last_audio_key] = audio_bytes

    # Decide what to show based on whether we have audio
    if st.session_state[last_audio_key] is None:
        _status_box(
            "▶ Not recording yet. Click the mic once to START, then again to STOP.",
            mode="ready",
        )
        return None

    # We have a saved recording
    _status_box(
        "⏹ Recording saved. You can play it below or press TRANSLATE.",
        mode="saved",
    )
    st.audio(st.session_state[last_audio_key], format="audio/wav")

    return st.session_state[last_audio_key]
