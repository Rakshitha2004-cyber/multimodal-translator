# main_app.py – Premium Multimodal Medical Translator

from pathlib import Path
import tempfile

from PIL import Image
import streamlit as st

from utils import get_language_list
from themes import apply_theme
from homepage import show_homepage
from mic_ui import medical_mic
from conversation import show_conversation
from stt import speech_to_text
from translate import translate_text
from tts import text_to_speech_file, cleanup_temp_file
from ocr import ocr_image
from languages import has_sr_support  # (if used elsewhere)


# =========================================================
# PATHS / LOGO + PAGE CONFIG
# =========================================================

BASE_DIR = Path(__file__).resolve().parent          # .../src
LOGO_PATH = BASE_DIR / "assets" / "logo.png"        # src/assets/logo.png

st.set_page_config(
    page_title="Multimodal AI Medical Translator",
    page_icon=str(LOGO_PATH),
    layout="wide",
)

print("LOGO PATH:", LOGO_PATH)
print("EXISTS?:", LOGO_PATH.exists())
logo = Image.open(LOGO_PATH)


# =========================================================
# APP HEADER
# =========================================================

header_col_logo, header_col_text = st.columns([1, 5])

with header_col_logo:
    st.image(logo, width=80)

with header_col_text:
    st.markdown(
        """
        <div style="display:flex; flex-direction:column; justify-content:center;">
          <div style="font-size:1.6rem; font-weight:700; margin-bottom:0.2rem;">
            Multimodal AI Medical Translator
          </div>
          <div style="font-size:0.95rem; color:#888;">
            Premium speech · text · image translator for doctors and patients
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")


# =========================================================
# UI HELPERS
# =========================================================

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


# =========================================================
# TRANSLATOR – SPEECH TAB
# =========================================================

def show_speech_tab(languages: list[str]):
    col_src, col_tgt = st.columns(2)

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


# =========================================================
# TRANSLATOR – TEXT TAB
# =========================================================

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


# =========================================================
# TRANSLATOR – IMAGE TAB (Hybrid OCR + Editable Text)
# =========================================================

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
            Clear printed prescriptions and neat handwriting are recognized best.
            For very cursive doctor handwriting, you can correct the text before translation.
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

    # Show original image
    image = Image.open(uploaded_img).convert("RGB")
    st.image(image, caption="Uploaded image", use_column_width=True)

    # --- STEP 1: OCR BUTTON ---
    if st.button("📖 Extract Text from Image", type="primary", key="extract_img"):
        try:
            with st.spinner("Running OCR (printed + handwritten)..."):
                extracted_text, processed = ocr_image(image, src_lang_name)

            extracted_text = (extracted_text or "").strip()

            # Save in session_state so it persists for the next rerun
            st.session_state["ocr_extracted_text"] = extracted_text

            if processed is not None:
                st.markdown("**Image used by OCR (after preprocessing):**")
                st.image(processed, use_column_width=True)

            if not extracted_text:
                st.warning(
                    "OCR could not confidently read this image. "
                    "If it's very messy handwriting, you may need to type the text."
                )

        except Exception as e:
            st.error(f"Error while running OCR: {e}")

    # --- EDITABLE TEXT (always visible once OCR has run) ---
    current_ocr_text = st.session_state.get("ocr_extracted_text", "")

    editable_text = st.text_area(
        "Extracted text (you can edit or type manually):",
        value=current_ocr_text,
        height=180,
        key="ocr_edit_box",
    )

    # --- STEP 2: TRANSLATE BUTTON ---
    if st.button("🔁 Translate Above Text", type="primary", key="translate_img"):
        final_text = (editable_text or "").strip()
        if not final_text:
            st.error("Please enter or correct the text before translation.")
            return

        try:
            with st.spinner("Translating text..."):
                translated_text = translate_text(
                    final_text, src_lang_name, tgt_lang_name
                )

            _write_result_block("Final text to translate", final_text)
            _write_result_block("Translated text", translated_text)

            # TTS
            if translated_text and translated_text.strip():
                MAX_TTS_CHARS = 3000
                tts_text = translated_text[:MAX_TTS_CHARS]

                tts_path = text_to_speech_file(tts_text, tgt_lang_name)
                if tts_path:
                    with open(tts_path, "rb") as f:
                        audio_bytes = f.read()
                    st.markdown("**Translated audio:**")
                    st.audio(audio_bytes, format="audio/mp3")
                    cleanup_temp_file(tts_path)
                else:
                    st.warning(
                        "Could not generate audio for the translated text."
                    )
        except Exception as e:
            st.error(f"Error while translating OCR text: {e}")


# =========================================================
# MAIN APP LAYOUT
# =========================================================

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
        # These mics can be wired into your conversation logic as needed
        mic_audio_patient = medical_mic("Patient Microphone", key="conv_patient")
        mic_audio_doctor = medical_mic("Doctor Microphone", key="conv_doctor")


if __name__ == "__main__":
    main()
