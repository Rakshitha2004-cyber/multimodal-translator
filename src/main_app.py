# main_app.py

import streamlit as st
from PIL import Image
import tempfile

from utils import get_language_list
from stt import speech_to_text
from translate import translate_text
from tts import text_to_speech_file, cleanup_temp_file
from ocr import ocr_image
from languages import has_sr_support
from themes import apply_theme
from homepage import show_home
from conversation import show_conversation
from mic_ui import medical_mic   # premium mic UI


# ----------------- PAGE CONFIG -----------------

st.set_page_config(
    page_title="Multimodal AI Medical Translator",
    page_icon="🌐",
    layout="wide"
)

# ---------- THEME SELECTION + NAVIGATION ----------

if "theme" not in st.session_state:
    st.session_state["theme"] = "Light"

st.sidebar.subheader("🌓 Theme")
theme_choice = st.sidebar.radio(
    "Choose Theme",
    ["Light", "Dark"],
    index=0
)
st.session_state.theme = theme_choice

# Apply selected theme
apply_theme(st.session_state.theme)

st.sidebar.markdown("---")
st.sidebar.subheader("📍 Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Translator", "Doctor–Patient Chat"],
    index=0
)

languages = get_language_list()
st.session_state.languages = languages  # for other modules if needed

# store last mic recording path for speech tab
if "last_recorded_path" not in st.session_state:
    st.session_state["last_recorded_path"] = None

# -------------------------------------------------


# ============== HOME PAGE =========================

if page == "Home":
    show_home(st.session_state.theme)


# ============== TRANSLATOR PAGE ===================

if page == "Translator":

    st.title("🌐 Multimodal AI Medical Translator")
    st.caption("For doctors and rural patients – voice, text & image translation across 100+ languages")

    tabs = st.tabs(["🗣 Speech", "📝 Text", "🖼 Image"])

    # ----------------- SPEECH TAB -----------------

    with tabs[0]:
        st.subheader("Speech to Speech Translation")

        col1, col2 = st.columns(2)

        # -------- LEFT: SOURCE / PATIENT --------
        with col1:
            st.markdown("#### Source (Patient)")
            src_lang = st.selectbox(
                "Patient Language",
                languages,
                index=languages.index("English") if "English" in languages else 0,
                key="src_lang_speech"
            )

            st.markdown("**Option 1 – Upload audio file (WAV only)**")
            uploaded_audio = st.file_uploader(
                "Upload patient audio file",
                type=["wav"],
                key="upload_audio"
            )

            st.markdown("---")
            st.markdown("**Option 2 – Record using microphone**")

            # load previously saved recording path (if any)
            recorded_path = st.session_state.get("last_recorded_path", None)

            # PREMIUM MIC UI
            wav_audio_data = medical_mic("Patient Microphone", key="translator")

            # if user recorded new audio, save it
            if wav_audio_data is not None:
                # remove old recording if any
                old_path = st.session_state.get("last_recorded_path")
                if old_path:
                    cleanup_temp_file(old_path)

                tmp_rec = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                tmp_rec.write(wav_audio_data)
                tmp_rec.flush()
                tmp_rec.close()
                recorded_path = tmp_rec.name
                st.session_state["last_recorded_path"] = recorded_path

            # Status for user
            if uploaded_audio is not None:
                st.info("✅ Audio file uploaded – ready to translate.")
            elif st.session_state.get("last_recorded_path"):
                st.info("✅ Microphone recording saved – ready to translate.")
            else:
                st.info("ℹ Upload a WAV file or record using the microphone, then click **Translate Speech**.")

        # -------- RIGHT: TARGET / DOCTOR --------
        with col2:
            st.markdown("#### Target (Doctor)")
            tgt_lang = st.selectbox(
                "Doctor Language",
                languages,
                index=languages.index("Hindi") if "Hindi" in languages else 0,
                key="tgt_lang_speech"
            )

        # -------- TRANSLATE BUTTON (only active when audio exists) --------
        can_translate = (uploaded_audio is not None) or bool(st.session_state.get("last_recorded_path"))

        col_btn, col_msg = st.columns([1, 3])
        with col_btn:
            translate_clicked = st.button(
                "Translate Speech",
                type="primary",
                key="btn_speech",
                disabled=not can_translate,
            )

        with col_msg:
            if not can_translate:
                st.warning("🔒 Waiting for audio input... upload a file or record with the mic.")

        if translate_clicked and can_translate:
            temp_uploaded_path = None
            audio_path = None

            # Priority: uploaded file > last mic recording
            if uploaded_audio is not None:
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                tmp.write(uploaded_audio.read())
                tmp.flush()
                tmp.close()
                temp_uploaded_path = tmp.name
                audio_path = temp_uploaded_path
            elif st.session_state.get("last_recorded_path"):
                audio_path = st.session_state["last_recorded_path"]

            if not has_sr_support(src_lang):
                st.error(
                    f"Speech recognition for '{src_lang}' is not configured. "
                    "Please use the Text tab for this language, or choose a supported language for microphone input."
                )
            else:
                with st.spinner("Processing audio..."):
                    try:
                        # 1) Speech -> Text
                        source_text = speech_to_text(audio_path, source_language_name=src_lang)

                        # ---- handle empty transcription safely ----
                        if not source_text or not source_text.strip():
                            st.error(
                                "❗ I could not recognize any speech from this audio.\n\n"
                                "Please speak a bit louder and closer to the microphone, "
                                "then record again."
                            )
                        else:
                            # 2) Text -> Translated Text
                            translated_text = translate_text(source_text, src_lang, tgt_lang)

                            # 3) Translated Text -> Speech
                            tts_path = text_to_speech_file(translated_text, tgt_lang)

                            st.success("Done!")

                            st.markdown("##### Recognized Patient Speech")
                            st.write(source_text)

                            st.markdown("##### Translated for Doctor")
                            st.write(translated_text)

                            if tts_path:
                                st.markdown("##### Audio (Doctor side)")
                                with open(tts_path, "rb") as f:
                                    audio_bytes = f.read()
                                st.audio(audio_bytes, format="audio/mp3")
                            else:
                                st.warning("Translation text was empty – skipping audio.")
                    except Exception as e:
                        st.error(f"Error while translating speech: {e}")
                    finally:
                        # clean up temporary files
                        if temp_uploaded_path:
                            cleanup_temp_file(temp_uploaded_path)
                        if st.session_state.get("last_recorded_path"):
                            cleanup_temp_file(st.session_state["last_recorded_path"])
                            st.session_state["last_recorded_path"] = None
                        if 'tts_path' in locals() and tts_path:
                            cleanup_temp_file(tts_path)

    # ----------------- TEXT TAB -----------------

        with tabs[1]:
            st.subheader("Text to Text + Speech Translation")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Source Text")
                src_lang_txt = st.selectbox(
                    "Source Language",
                    languages,
                    index=languages.index("English") if "English" in languages else 0,
                    key="src_lang_txt"
                )
                src_text = st.text_area("Enter text", height=150)

            with col2:
                st.markdown("#### Target Text")
                tgt_lang_txt = st.selectbox(
                    "Target Language",
                    languages,
                    index=languages.index("Hindi") if "Hindi" in languages else 0,
                    key="tgt_lang_txt"
                )

            col3, col4 = st.columns([1, 1])

            with col3:
                if st.button("Translate Text", type="primary", key="btn_text"):
                    if not src_text.strip():
                        st.error("Please enter some text.")
                    else:
                        with st.spinner("Translating..."):
                            translated_text = translate_text(src_text, src_lang_txt, tgt_lang_txt)
                            st.markdown("##### Translated Text")
                            st.write(translated_text)
                            st.session_state["last_translated_text"] = translated_text
                            st.session_state["last_tgt_lang_txt"] = tgt_lang_txt

            with col4:
                if st.button("Play as Audio", key="btn_text_tts"):
                    if "last_translated_text" not in st.session_state:
                        st.error("Translate some text first.")
                    else:
                        with st.spinner("Generating speech..."):
                            try:
                                tts_path = text_to_speech_file(
                                    st.session_state["last_translated_text"],
                                    st.session_state["last_tgt_lang_txt"]
                                )
                                if tts_path:
                                    with open(tts_path, "rb") as f:
                                        audio_bytes = f.read()
                                    st.audio(audio_bytes, format="audio/mp3")
                                else:
                                    st.warning("Cannot generate audio for empty text.")
                            except Exception as e:
                                st.error(f"TTS error: {e}")
                            finally:
                                if 'tts_path' in locals() and tts_path:
                                    cleanup_temp_file(tts_path)

    # ----------------- IMAGE TAB -----------------

        with tabs[2]:
            st.subheader("Image (Prescription/Report) to Text Translation")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Source Image")
                src_lang_img = st.selectbox(
                    "Language in Image",
                    languages,
                    index=languages.index("English") if "English" in languages else 0,
                    key="src_lang_img"
                )
                img_file = st.file_uploader("Upload image (jpg, png)", type=["jpg", "jpeg", "png"])

            with col2:
                st.markdown("#### Target Language")
                tgt_lang_img = st.selectbox(
                    "Translate To",
                    languages,
                    index=languages.index("Hindi") if "Hindi" in languages else 0,
                    key="tgt_lang_img"
                )

            if st.button("Extract & Translate Image", type="primary", key="btn_image"):
                if not img_file:
                    st.error("Please upload an image.")
                else:
                    with st.spinner("Running OCR and translation..."):
                        try:
                            image = Image.open(img_file).convert("RGB")
                            extracted_text, raw = ocr_image(image, src_lang_img)

                            st.markdown("##### Extracted Text from Image")
                            if extracted_text.strip():
                                st.write(extracted_text)

                                st.markdown("##### Translated Text")
                                translated_text = translate_text(extracted_text, src_lang_img, tgt_lang_img)
                                st.write(translated_text)

                                st.session_state["img_translated_text"] = translated_text
                                st.session_state["img_tgt_lang"] = tgt_lang_img
                            else:
                                st.warning("No readable text found in the image.")

                        except Exception as e:
                            st.error(f"OCR/translation error: {e}")

            if st.button("Play Translated Image Text", key="btn_image_tts"):
                if "img_translated_text" not in st.session_state:
                    st.error("Run image translation first.")
                else:
                    with st.spinner("Generating audio..."):
                        try:
                            tts_path = text_to_speech_file(
                                st.session_state["img_translated_text"],
                                st.session_state["img_tgt_lang"]
                            )
                            if tts_path:
                                with open(tts_path, "rb") as f:
                                    audio_bytes = f.read()
                                st.audio(audio_bytes, format="audio/mp3")
                            else:
                                st.warning("Cannot generate audio for empty text.")
                        except Exception as e:
                            st.error(f"TTS error: {e}")
                        finally:
                            if 'tts_path' in locals() and tts_path:
                                cleanup_temp_file(tts_path)


# ============== DOCTOR–PATIENT CHAT PAGE =========

if page == "Doctor–Patient Chat":
    show_conversation(st.session_state.theme, languages)
