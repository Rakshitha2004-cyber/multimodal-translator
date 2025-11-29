# main_app.py – Final premium version

from __future__ import annotations

import tempfile

import streamlit as st
from PIL import Image

from utils import get_language_list
from themes import apply_theme
from homepage import show_homepage
from mic_ui import medical_mic
from conversation import show_conversation

from stt import speech_to_text
from translate import translate_text
from tts import text_to_speech_file, cleanup_temp_file
from ocr import ocr_image


# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Multimodal AI Medical Translator",
    page_icon="🩺",
    layout="wide",
)


# ---------- UI HELPERS ----------

def _section_header(title: str, subtitle: str | None = None, icon: str = ""):
    icon_html = (
        f"<span style='font-size:1.3rem; margin-right:0.4rem;'>{icon}</span>"
        if icon
        else ""
    )
    st.markdown(
        f"""
        <div style="margin-top:0.6rem; margin-bottom:0.4rem;">
          <div style="display:flex; align-items:center; gap:0.3rem;">
            {icon_html}
            <span style="font-size:1.2rem; font-weight:700; letter-spacing:0.02em;">
                {title}
            </span>
          </div>
          <div class="secondary-text">{subtitle or ""}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _write_result_block(title: str, text: str):
    if not text:
        return
    st.markdown(
        f"""
        <div class="app-card">
          <div class="pill-label">{title}</div>
          <div style="font-size:0.95rem; line-height:1.6;">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------- TRANSLATOR – SPEECH TAB ----------

def show_speech_tab(languages: list[str]):
    col_src, col_tgt = st.columns(2)

    # sensible defaults
    default_src = languages.index("English") if "English" in languages else 0
    default_tgt = (
        languages.index("Hindi")
        if "Hindi" in languages
        else (1 if len(languages) > 1 else 0)
    )

    with col_src:
        _section_header("Source (Patient)", "Patient speaks in their language", "🧑‍🌾")
        src_lang_name = st.selectbox(
            "Patient language",
            languages,
            key="speech_src_lang",
            index=default_src,
        )

    with col_tgt:
        _section_header(
            "Target (Doctor)", "Doctor hears translation in this language", "👩‍⚕️"
        )
        tgt_lang_name = st.selectbox(
            "Doctor language",
            languages,
            key="speech_tgt_lang",
            index=default_tgt,
        )

    st.markdown("---")

    col_file, col_mic = st.columns(2)

    # Option 1 – upload wav
    with col_file:
        st.markdown(
            """
            <div class="app-card">
              <h4>Option 1 – Upload audio file (WAV only)</h4>
              <p class="secondary-text">
                Use this if you already have a recorded patient audio sample.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded = st.file_uploader(
            "Upload patient audio file",
            type=["wav"],
            key="speech_file",
        )

    # Option 2 – mic
    mic_audio = None
    with col_mic:
        st.markdown(
            """
            <div class="app-card">
              <h4>Option 2 – Record using microphone</h4>
              <p class="secondary-text">
                Click the microphone, speak clearly, then click again to stop.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        mic_audio = medical_mic("Patient Microphone", key="translator_patient")

    st.markdown("")

    # Translate button
    btn_col = st.container()
    with btn_col:
        translate_clicked = st.button("🔁 Translate Speech", type="primary")

    if not translate_clicked:
        return

    # Choose source audio
    audio_bytes = None
    if uploaded is not None:
        audio_bytes = uploaded.read()
        st.success("Uploaded audio file received.")
        st.audio(audio_bytes, format="audio/wav")
    elif mic_audio is not None:
        audio_bytes = mic_audio
        st.audio(audio_bytes, format="audio/wav")
    else:
        st.error("Please upload an audio file **or** record using the microphone.")
        return

    # Save to temp WAV file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.write(audio_bytes)
    tmp.flush()
    tmp.close()
    audio_path = tmp.name

    try:
        # -------- STT --------
        with st.spinner("Recognizing patient speech..."):
            text_src = speech_to_text(audio_path, src_lang_name)

        if not text_src or not text_src.strip():
            st.error(
                "❗ I could not recognize any speech.\n\n"
                "Please record again, speaking clearly and closer to the microphone."
            )
            return

        # -------- Translation + TTS --------
        with st.spinner("Translating and generating doctor audio..."):
            text_tgt = translate_text(text_src, src_lang_name, tgt_lang_name)

            _write_result_block("Recognized patient speech", text_src)
            _write_result_block("Translated for doctor", text_tgt)

            if text_tgt and text_tgt.strip():
                tts_path = text_to_speech_file(text_tgt, tgt_lang_name)
                if tts_path:
                    with open(tts_path, "rb") as f:
                        tts_bytes = f.read()
                    st.markdown("**Doctor hears (audio):**")
                    st.audio(tts_bytes, format="audio/mp3")
                    cleanup_temp_file(tts_path)
                else:
                    st.warning(
                        "TTS could not generate audio for the translated text "
                        "(see any error message in the terminal)."
                    )
            else:
                st.warning("Translation text is empty, so TTS was skipped.")

    except Exception as e:
        st.error(f"Error while translating speech: {e}")
    finally:
        cleanup_temp_file(audio_path)


# ---------- TRANSLATOR – TEXT TAB ----------

def show_text_tab(languages: list[str]):
    col_src, col_tgt = st.columns(2)

    default_src = languages.index("English") if "English" in languages else 0
    default_tgt = (
        languages.index("Hindi")
        if "Hindi" in languages
        else (1 if len(languages) > 1 else 0)
    )

    with col_src:
        _section_header("Source Text", "Enter patient or doctor text", "💬")
        src_lang_name = st.selectbox(
            "Source language",
            languages,
            key="text_src_lang",
            index=default_src,
        )

    with col_tgt:
        _section_header("Target Text", "Output translation", "🌐")
        tgt_lang_name = st.selectbox(
            "Target language",
            languages,
            key="text_tgt_lang",
            index=default_tgt,
        )

    st.markdown("")

    st.markdown(
        """
        <div class="app-card">
          <h4>Enter text to translate</h4>
        </div>
        """,
        unsafe_allow_html=True,
    )

    text_input = st.text_area(
        "Type or paste text here",
        height=160,
        key="text_input_area",
    )

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        translate_clicked = st.button("🔁 Translate Text", type="primary")
    with col_btn2:
        tts_toggle = st.checkbox(
            "🔊 Also generate audio for translated text", value=True
        )

    if not translate_clicked:
        return

    if not text_input or not text_input.strip():
        st.error("Please enter some text to translate.")
        return

    try:
        with st.spinner("Translating text..."):
            translated = translate_text(text_input, src_lang_name, tgt_lang_name)

        _write_result_block("Original text", text_input)
        _write_result_block("Translated text", translated)

        if tts_toggle and translated and translated.strip():
            tts_path = text_to_speech_file(translated, tgt_lang_name)
            if tts_path:
                with open(tts_path, "rb") as f:
                    audio_bytes = f.read()
                st.markdown("**Translated audio:**")
                st.audio(audio_bytes, format="audio/mp3")
                cleanup_temp_file(tts_path)
            else:
                st.warning(
                    "TTS could not generate audio for the translated text "
                    "(see any error message in the terminal)."
                )
    except Exception as e:
        st.error(f"Error while translating text: {e}")


# ---------- TRANSLATOR – IMAGE TAB (FINAL) ----------

def show_image_tab(languages: list[str]):
    col_src, col_tgt = st.columns(2)

    default_src = languages.index("English") if "English" in languages else 0
    default_tgt = (
        languages.index("Hindi")
        if "Hindi" in languages
        else (1 if len(languages) > 1 else 0)
    )

    with col_src:
        _section_header(
            "Source (Image OCR)", "Upload prescription / note image", "🧾"
        )
        src_lang_name = st.selectbox(
            "Language in the image",
            languages,
            key="img_src_lang",
            index=default_src,
        )

    with col_tgt:
        _section_header("Target language", "Language for translated text/audio", "🌐")
        tgt_lang_name = st.selectbox(
            "Target language",
            languages,
            key="img_tgt_lang",
            index=default_tgt,
        )

    st.markdown("")

    st.markdown(
        """
        <div class="app-card">
          <h4>Upload image</h4>
          <p class="secondary-text">
            Clear photos of prescriptions or notes work best. Handwritten text is
            supported, but accuracy depends on legibility.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_img = st.file_uploader(
        "Upload image file",
        type=["png", "jpg", "jpeg"],
        key="img_uploader",
    )

    if not uploaded_img:
        return

    image = Image.open(uploaded_img)
    st.image(image, caption="Uploaded image", use_column_width=True)

    if st.button("📖 Read & Translate from Image", type="primary"):
        try:
            # -------- OCR --------
            with st.spinner("Running OCR on image..."):
                extracted_text, _ = ocr_image(image, src_lang_name)

            if not extracted_text or not extracted_text.strip():
                st.error("Could not extract any readable text from this image.")
                return

            # -------- Translation --------
            with st.spinner("Translating extracted text..."):
                translated_text = translate_text(
                    extracted_text, src_lang_name, tgt_lang_name
                )

            _write_result_block("Extracted text from image", extracted_text)
            _write_result_block("Translated text", translated_text)

            # -------- TTS for translated text --------
            if translated_text and translated_text.strip():
                # very long prescriptions: limit TTS length
                MAX_TTS_CHARS = 3000
                tts_text = translated_text

                if len(tts_text) > MAX_TTS_CHARS:
                    tts_text = tts_text[:MAX_TTS_CHARS]
                    st.info(
                        "Translated text is very long – audio is generated "
                        "for the first part only."
                    )

                tts_path = text_to_speech_file(tts_text, tgt_lang_name)
                if tts_path:
                    with open(tts_path, "rb") as f:
                        audio_bytes = f.read()
                    st.markdown("**Translated audio:**")
                    st.audio(audio_bytes, format="audio/mp3")
                    cleanup_temp_file(tts_path)
                else:
                    st.warning(
                        "Could not generate audio for the translated text. "
                        "If you see a red TTS error above, that explains why."
                    )

        except Exception as e:
            st.error(f"Error while processing image: {e}")


# ---------- MAIN APP LAYOUT ----------

def main():
    languages = get_language_list()

    # Sidebar – theme + navigation
    with st.sidebar:
        st.markdown("### 🎨 Theme")
        theme_choice = st.radio(
            "Choose theme", ["Light", "Dark"], index=0, key="theme_choice"
        )

        st.markdown("---")
        st.markdown("### 📍 Navigation")
        nav_choice = st.radio(
            "Go to",
            ["Home", "Translator", "Doctor–Patient Chat"],
            index=0,
            key="nav_choice",
        )

    # Apply theme styles
    apply_theme(theme_choice)

    # Route pages
    if nav_choice == "Home":
        show_homepage(theme_choice)

    elif nav_choice == "Translator":
        st.markdown(
            """
            <div class="app-card" style="margin-top:0.8rem;">
              <div class="pill-label">Translator mode</div>
              <div style="display:flex; align-items:center; gap:0.4rem;">
                <span style="font-size:1.2rem;">🌍</span>
                <div>
                  <div class="main-title" style="margin-bottom:0;">
                    Speech · Text · Image
                  </div>
                  <div class="main-subtitle">
                    Use this mode for one-way translation of patient/doctor content.
                  </div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tabs = st.tabs(["🎤 Speech", "⌨️ Text", "🖼️ Image"])

        with tabs[0]:
            show_speech_tab(languages)
        with tabs[1]:
            show_text_tab(languages)
        with tabs[2]:
            show_image_tab(languages)

    else:  # Doctor–Patient Chat
        show_conversation(theme_choice, languages)
        mic_audio_patient = medical_mic("Patient Microphone", key="conv_patient")
        mic_audio_doctor = medical_mic("Doctor Microphone", key="conv_doctor")



if __name__ == "__main__":
    main()
