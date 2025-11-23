# homepage.py
# homepage.py

import streamlit as st
from themes import apply_theme


def show_home(theme: str):
    apply_theme(theme)

    st.title("🌍 Multimodal AI Medical Translator")
    st.subheader("Bridging language gaps between doctors and rural patients")

    st.markdown("""
    ### 🎯 What this system can do
    - 🗣 **Speech → Speech** translation between patient & doctor  
    - 📝 **Text → Text + Audio** translation in 100+ languages  
    - 🖼 **Image / Prescription OCR** with translation  
    - 💬 **Doctor–Patient conversation mode** (back-and-forth dialogue)  
    - 🌐 Supports **100+ world languages** for text & image  
    """)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌎 Languages", "100+")
    with col2:
        st.metric("🎙 Modes", "Speech, Text, Image")
    with col3:
        st.metric("🏥 Target Users", "Doctors & Patients")

    st.markdown("---")

    st.markdown("""
    ### 👩‍⚕️ Use cases
    - Rural patient explaining symptoms to a city doctor  
    - Multilingual hospital OPD  
    - Translating discharge summaries or test reports  
    - Helping non-English speaking family members understand treatment  
    """)

    st.info("Use the **left sidebar** to switch between Home, Translator and Doctor–Patient Chat.")
