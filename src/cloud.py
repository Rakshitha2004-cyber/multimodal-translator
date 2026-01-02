# cloud_app.py – Light-weight Streamlit app for Cloud
# Focus: Text + Image translation with OCR (no microphone)

from pathlib import Path
import tempfile

from PIL import Image
import streamlit as st

from utils import get_language_list
from themes import apply_theme
from homepage import show_homepage
from translate import translate_text
from tts import text_to_speech_file, cleanup_temp_file
from ocr import ocr_image


# =========================================================
# PATHS / LOGO + PAGE CONFIG
# =========================================================

BASE_DIR = Path(__file__).resolve().parent          # .../src
LOGO_PATH = BASE_DIR / "assets" / "logo.png"        # src/assets/logo.png

if LOGO_PATH.exists():
    page_icon = str(LOGO_PATH)
else:
    page_icon = "🩺"

st.set_page_config(
    page_title="Multimodal AI Medical Translator (Cloud)",
    page_icon=page_icon,
    layout="wide",
)


def load_logo():
    try:
        if LOGO_PATH.exists():
            return Image.open(LOGO_PATH)
    except Exception as e:
        print("Logo load failed:", e)
    return None


# =========================================================
# HEADER
# =========================================================

header_col_logo, header_col_text = st.columns([1, 5])
logo = load_logo()

with header_col_logo:
    if logo is not None:
        st.image(logo, width=80)
    else:
        st.markdown("🩺")

with header_col_text:
    st.markdown(
        """
        <div style="display:flex; flex-direction:column; justify-content:center;">
          <div style="font-size:1.6rem; font-weight:700; margin-bottom:0.2rem;">
            Multimodal AI Medical Translator
          </div>
          <div style="font-size:0.95rem; color:#888;">
            Cloud version – Text & Image translation with OCR
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
# TEXT TRANSLATION TAB
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
            key="cloud_text_src_lang",
            index=default_src,
        )

    with col_tgt:
        _section_header("Target Text", "Output translation", "🌐")
        tgt_lang_name = st.selectbox(
            "Target language",
            languages,
            key="cloud_text_tgt_lang",
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
        key="cloud_text_input_area",
    )

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        translate_clicked = st.button("🔁 Translate Text", key="cloud_translate_text")
    with col_btn2:
        tts_toggle = st.checkbox(
            "🔊 Generate audio for translated text", value=True, key="cloud_tts_toggle"
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
                st.warning("TTS could not generate audio for the translated text.")
    except Exception as e:
        st.error(f"Error while translating text: {e}")


# =========================================================
# IMAGE (PRESCRIPTION) TAB – OCR + TRANSLATE
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
            key="cloud_img_src_lang",
            index=default_src,
        )

    with col_tgt:
        _section_header("Target language", "Language for translated text/audio", "🌐")
        tgt_lang_name = st.selectbox(
            "Target language",
            languages,
            key="cloud_img_tgt_lang",
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
        key="cloud_img_uploader",
    )

    if not uploaded_img:
        return

    image = Image.open(uploaded_img).convert("RGB")
    st.image(image, caption="Uploaded image", use_column_width=True)

    if st.button("📖 Extract Text from Image", key="cloud_extract_btn"):
        try:
            with st.spinner("Running OCR on image..."):
                extracted_text, processed = ocr_image(image, src_lang_name)

            if processed is not None:
                st.markdown("**Image after preprocessing (for OCR):**")
                st.image(processed, use_column_width=True)

            extracted_text = (extracted_text or "").strip()

            editable_text = st.text_area(
                "Extracted text (you can edit / correct before translation)",
                value=extracted_text,
                height=180,
                key="cloud_img_extracted_text",
            )

            if st.button("🔁 Translate Above Text", key="cloud_translate_img_text"):
                final_text = (editable_text or "").strip()
                if not final_text:
                    st.error("Please enter or correct the text before translation.")
                    return

                with st.spinner("Translating text..."):
                    translated_text = translate_text(
                        final_text, src_lang_name, tgt_lang_name
                    )

                _write_result_block("Final text to translate", final_text)
                _write_result_block("Translated text", translated_text)

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
            st.error(f"Error while processing image: {e}")


# =========================================================
# MAIN
# =========================================================

def main():
    languages = get_language_list()

    with st.sidebar:
        st.markdown("### 🎨 Theme")
        theme_choice = st.radio(
            "Choose theme", ["Light", "Dark"], index=0, key="cloud_theme_choice"
        )

        st.markdown("---")
        st.markdown("### 📍 Navigation")
        nav_choice = st.radio(
            "Go to",
            ["Home", "Translator – Text", "Translator – Image"],
            index=0,
            key="cloud_nav_choice",
        )

    apply_theme(theme_choice)

    if nav_choice == "Home":
        show_homepage(theme_choice)
    elif nav_choice == "Translator – Text":
        show_text_tab(languages)
    else:
        show_image_tab(languages)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.title("App failed to start")
        st.error("An error happened while starting the app:")
        st.exception(e)
