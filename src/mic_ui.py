# mic_ui.py

# mic_ui.py

import streamlit as st
from audio_recorder_streamlit import audio_recorder


def medical_mic(label: str, key: str):
    """
    Medical-style microphone UI with subtle pulse effect.
    Returns: audio bytes (or None if nothing/too short)
    """

    # Global CSS (only injected once)
    if "mic_css_loaded" not in st.session_state:
        st.markdown(
            """
            <style>
            .mic-card {
                border-radius: 18px;
                padding: 0.9rem 1.2rem;
                margin-bottom: 0.7rem;
                background: linear-gradient(135deg, #f9fafb 0%, #e0f2fe 60%, #eff6ff 100%);
                border: 1px solid rgba(148, 163, 184, 0.7);
                box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08);
            }
            .mic-title {
                margin: 0 0 0.25rem 0;
                font-size: 1.05rem;
                color: #0f172a;
                font-weight: 600;
            }
            .mic-subtitle {
                margin: 0;
                font-size: 0.9rem;
                color: #475569;
            }

            /* Pulse ring around mic button */
            .mic-pulse {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                padding: 0.6rem;
                border-radius: 999px;
                background: radial-gradient(circle, rgba(248,250,252,1) 40%, rgba(59,130,246,0.28) 100%);
                animation: mic-pulse 2.2s infinite;
            }

            @keyframes mic-pulse {
                0%   { box-shadow: 0 0 0 0 rgba(14,165,233,0.45); }
                70%  { box-shadow: 0 0 0 18px rgba(14,165,233,0); }
                100% { box-shadow: 0 0 0 0 rgba(14,165,233,0); }
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.session_state["mic_css_loaded"] = True

    st.markdown(
        f"""
        <div class="mic-card">
          <h4 class="mic-title">{label}</h4>
          <p class="mic-subtitle">
            Tap the microphone once to <b>start</b>, and again to <b>stop</b> recording.
            Speak clearly and close to the mic.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Wrap recorder in pulse ring
    with st.container():
        st.markdown('<div class="mic-pulse">', unsafe_allow_html=True)
        audio_bytes = audio_recorder(
            text="🎤 Start Recording / Stop Recording",
            recording_color="#dc2626",   # red while recording
            neutral_color="#0ea5e9",     # medical blue idle
            icon_name="microphone-lines",
            icon_size="3x",
            key=f"{key}_mic",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # If user has just recorded something
    if audio_bytes is not None:
        if len(audio_bytes) > 500:
            st.success("💾 Recording saved.")
            return audio_bytes
        else:
            st.warning("Recording was too short. Please try again.")
            return None

    # No new recording this run
    return None
