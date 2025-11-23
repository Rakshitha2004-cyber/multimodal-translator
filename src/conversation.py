# conversation.py

import streamlit as st
import tempfile
from datetime import datetime

from stt import speech_to_text
from translate import translate_text
from tts import text_to_speech_file, cleanup_temp_file
from languages import has_sr_support
from themes import apply_theme
from mic_ui import medical_mic   # premium mic UI


def _init_conversation_state():
    if "conversation" not in st.session_state:
        st.session_state.conversation = []   # list of dicts
    if "conv_css_loaded" not in st.session_state:
        st.markdown(
            """
            <style>
            .bubble-patient {
                background: #eff6ff;
                border-radius: 16px;
                padding: 0.6rem 0.9rem;
                margin-bottom: 0.4rem;
                border: 1px solid rgba(37, 99, 235, 0.35);
            }
            .bubble-doctor {
                background: #ecfdf5;
                border-radius: 16px;
                padding: 0.6rem 0.9rem;
                margin-bottom: 0.4rem;
                border: 1px solid rgba(16, 185, 129, 0.4);
            }
            .bubble-meta {
                font-size: 0.75rem;
                color: #6b7280;
                margin-bottom: 0.2rem;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.session_state["conv_css_loaded"] = True


def _record_and_process(role_label: str, src_lang: str, tgt_lang: str):
    """Handle one side speaking (Patient or Doctor)."""
    if not has_sr_support(src_lang):
        st.error(f"Speech recognition for '{src_lang}' is not configured. Please choose another language.")
        return

    wav_bytes = medical_mic(f"{role_label} Microphone", key=role_label.lower())

    if wav_bytes is None:
        st.info("Record audio above, then click the button to process.")
        return

    st.audio(wav_bytes, format="audio/wav")

    if st.button(f"Process {role_label} Speech", key=f"process_{role_label}"):
        with st.spinner("Translating..."):
            # Save to temp wav
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            tmp.write(wav_bytes)
            tmp.flush()
            tmp.close()
            audio_path = tmp.name

            try:
                src_text = speech_to_text(audio_path, source_language_name=src_lang)

                if not src_text or not src_text.strip():
                    st.error(
                        f"❗ I could not recognize {role_label.lower()}'s speech.\n\n"
                        "Please record again, speaking clearly and closer to the microphone."
                    )
                    cleanup_temp_file(audio_path)
                    return

                translated = translate_text(src_text, src_lang, tgt_lang)
                tts_path = text_to_speech_file(translated, tgt_lang)

                st.markdown(f"**{role_label} said (recognized):**")
                st.write(src_text)

                st.markdown("**Translated message:**")
                st.write(translated)

                if tts_path:
                    with open(tts_path, "rb") as f:
                        audio_bytes = f.read()
                    st.markdown("**Play translated audio:**")
                    st.audio(audio_bytes, format="audio/mp3")

                # Save in conversation history
                st.session_state.conversation.append({
                    "speaker": role_label,
                    "src_lang": src_lang,
                    "tgt_lang": tgt_lang,
                    "text": src_text,
                    "translated": translated,
                    "time": datetime.now().strftime("%H:%M"),
                    "tts_path": tts_path,
                })

            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                cleanup_temp_file(audio_path)


def show_conversation(theme: str, languages: list[str]):
    apply_theme(theme)
    _init_conversation_state()

    st.title("🤝 Doctor–Patient Conversation Mode")

    st.markdown("""
    This mode allows back-and-forth conversation:
    - Patient speaks in their language  
    - Doctor hears + sees translation in their language  
    - Doctor replies in their language  
    - Patient hears the translated reply  
    """)

    col_lang1, col_lang2 = st.columns(2)
    with col_lang1:
        patient_lang = st.selectbox(
            "Patient Language",
            languages,
            index=languages.index("English") if "English" in languages else 0,
            key="conv_patient_lang"
        )
    with col_lang2:
        doctor_lang = st.selectbox(
            "Doctor Language",
            languages,
            index=languages.index("Hindi") if "Hindi" in languages else 0,
            key="conv_doctor_lang"
        )

    st.markdown("---")

    col_patient, col_doctor = st.columns(2)

    with col_patient:
        st.subheader("🧑‍🌾 Patient Speaks")
        _record_and_process("Patient", patient_lang, doctor_lang)

    with col_doctor:
        st.subheader("👩‍⚕️ Doctor Speaks")
        _record_and_process("Doctor", doctor_lang, patient_lang)

    st.markdown("---")
    st.subheader("📝 Conversation History")

    if not st.session_state.conversation:
        st.info("No messages yet. Start the conversation using the microphones above.")
    else:
        for i, msg in enumerate(st.session_state.conversation, start=1):
            css_class = "bubble-patient" if msg["speaker"] == "Patient" else "bubble-doctor"
            st.markdown(
                f"""
                <div class="{css_class}">
                  <div class="bubble-meta">
                    <b>{i}. {msg['speaker']}</b>
                    · {msg['src_lang']} → {msg['tgt_lang']}
                    · {msg['time']}
                  </div>
                  <div>{msg['translated']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
