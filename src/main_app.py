## main_app.py – Multimodal AI Medical Translator (Streamlit)

from pathlib import Path
import tempfile

import numpy as np
from PIL import Image
import streamlit as st

import easyocr  # OCR for printed + handwritten

from utils import get_language_list
from themes import apply_theme
from homepage import show_homepage
from mic_ui import medical_mic
from conversation import show_conversation
from stt import speech_to_text
from translate import translate_text          # your existing translator
from tts import text_to_speech_file, cleanup_temp_file
from languages import has_sr_support


# =========================================================
# PATHS / LOGO + PAGE CONFIG
# =========================================================

BASE_DIR = Path(__file__).resolve().parent          # .../src
LOGO_PATH = BASE_DIR / "assets" / "logo.png"        # src/assets/logo.png

# Use logo as tab icon if it exists, otherwise fall back to emoji
if LOGO_PATH.exists():
    page_icon = str(LOGO_PATH)
else:
    page_icon = "🩺"

st.set_page_config(
    page_title="Multimodal AI Medical Translator",
    page_icon=page_icon,
    layout="wide",
)


def load_logo():
    """Load logo safely; return None if it fails."""
    try:
        if LOGO_PATH.exists():
            return Image.open(LOGO_PATH)
    except Exception as e:
        print("Logo load failed:", e)
    return None


# =========================================================
# IMAGE OCR HELPERS (EasyOCR)
# =========================================================

@st.cache_resource(show_spinner=False)
def get_easyocr_reader(lang_code: str = "en"):
    """Create and cache EasyOCR reader for a language code."""
    try:
        return easyocr.Reader([lang_code])
    except Exception:
        # If a specific language is not supported, fall back to English
        return easyocr.Reader(["en"])


def extract_text_from_image(image_file, ocr_lang: str = "en") -> str:
    """
    Extract text from an uploaded image using EasyOCR.
    """
    try:
        image = Image.open(image_file).convert("RGB")
        image_np = np.array(image)

        reader = get_easyocr_reader(ocr_lang)
        result = reader.readtext(image_np, detail=0)  # detail=0 → only text

        text = "\n".join(result).strip()
        return text
    except Exception as e:
        return f"[OCR error: {e}]"


# =========================================================
# APP HEADER
# =========================================================

header_col_logo, header_col_text = st.columns([1, 5])
logo = load_logo()

with header_col_logo:
    if logo is not None:
        st.image(logo, width=80)
    else:
        st.markdown("🩺")  # simple fallback icon

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

    # Show SR support info if available
    try:
        if not has_sr_support(src_lang_name):
            st.warning(
                f"Speech recognition may not fully support **{src_lang_name}**. "
                "For best results, use English / Hindi / other supported languages."
            )
    except Exception:
        pass

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
# TRANSLATOR – IMAGE TAB  (OCR + manual text + TTS using translate_text)
# =========================================================

def show_image_tab(languages: list[str]):
    st.subheader("Image Translator (Printed + Handwritten)")

    st.write(
        """
        Upload an image containing **printed** or **handwritten** text.  
        The app will try to read it.  
        If OCR is not accurate, the patient/doctor can **edit or type the text manually**,  
        then translate it and listen to the audio.
        """
    )

    col1, col2 = st.columns(2)
    with col1:
        src_lang_name = st.selectbox(
            "Source language (text in image)",
            languages,
            index=0,
            key="img_src_lang",
        )
    with col2:
        tgt_lang_name = st.selectbox(
            "Target language (output)",
            languages,
            index=1 if len(languages) > 1 else 0,
            key="img_tgt_lang",
        )

    ocr_mode = st.radio(
        "Type of text in image",
        options=["Printed", "Handwritten"],
        index=0,
        horizontal=True,
        key="img_text_type",
    )

    uploaded_image = st.file_uploader(
        "Upload image",
        type=["png", "jpg", "jpeg"],
        key="img_uploader",
    )

    # --- keep a state for the editable text coming from OCR or manual typing ---
    if "img_text_input" not in st.session_state:
        st.session_state["img_text_input"] = ""

    if uploaded_image is not None:
        # Show preview
        st.image(uploaded_image, caption="Uploaded image", use_column_width=True)

        if st.button("📖 Extract Text from Image", key="btn_extract_img", type="primary"):
            # OCR language – we keep English here (EasyOCR Indian language support is limited)
            ocr_lang_code = "en"

            with st.spinner("Running OCR (this may take a few seconds)..."):
                extracted = extract_text_from_image(
                    uploaded_image,
                    ocr_lang=ocr_lang_code,
                )

            extracted = (extracted or "").strip()
            st.session_state["img_text_input"] = extracted

            if not extracted:
                st.warning(
                    "No text could be confidently extracted from the image.\n\n"
                    "You can type the content manually in the box below."
                )
            elif extracted.startswith("[OCR error"):
                st.error(
                    "There was an error while reading the text from the image. "
                    "You can type the text manually in the box below."
                )

    # --- Editable text area bound to session_state key ---
    editable_text = st.text_area(
        "Text from image (you can edit or type manually if OCR is wrong)",
        height=180,
        key="img_text_input",
    )

    # --- Translate whatever is currently in the text box + TTS ---
    if st.button("🔁 Translate Above Text", key="btn_translate_img", type="primary"):
        final_text = (editable_text or "").strip()

        if not final_text:
            st.error(
                "Please enter the text from the image (either by extracting or typing manually) before translating."
            )
            return

        with st.spinner("Translating text..."):
            translated = translate_text(final_text, src_lang_name, tgt_lang_name)

        st.subheader("Translated Text")
        st.text_area(
            "Translation",
            value=translated,
            height=180,
            key="img_translated_text",
        )

        # --- TTS for translated text ---
        if translated and translated.strip():
            try:
                MAX_TTS_CHARS = 3000
                tts_input = translated[:MAX_TTS_CHARS]
                tts_path = text_to_speech_file(tts_input, tgt_lang_name)
                if tts_path:
                    with open(tts_path, "rb") as f:
                        audio_bytes = f.read()
                    st.markdown("**Translated audio (from image text):**")
                    st.audio(audio_bytes, format="audio/mp3")
                    cleanup_temp_file(tts_path)
                else:
                    st.warning("Could not generate audio for the translated text.")
            except Exception as e:
                st.error(f"Error while generating TTS for image translation: {e}")


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
        # 👇 All mic + conversation UI is handled INSIDE show_conversation
        show_conversation(theme_choice, languages)


# =========================================================
# ENTRY POINT – show errors on the page instead of just "Oh no"
# =========================================================

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.title("App failed to start")
        st.error("An error happened while starting the app:")
        st.exception(e)
