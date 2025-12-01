# src/ocr.py  –  Tesseract-based OCR for printed + neat handwriting

from __future__ import annotations

from typing import Tuple

import numpy as np
import cv2
from PIL import Image
import pytesseract


# Map UI language names to Tesseract language codes
LANG_MAP = {
    "English": "eng",
    "Hindi": "hin",
    "Kannada": "kan",
    "Tamil": "tam",
    "Telugu": "tel",
    "Malayalam": "mal",
    "Marathi": "mar",
    "Gujarati": "guj",
    "Bengali": "ben",
    "Punjabi": "pan",
    "Urdu": "urd",
    # add more here if needed
}


def _preprocess_for_tesseract(pil_img: Image.Image) -> np.ndarray:
    """
    Basic preprocessing for Tesseract:
    - convert to grayscale
    - resize up
    - denoise
    - adaptive threshold
    Returns a NumPy array that can be shown with st.image().
    """
    img = np.array(pil_img.convert("RGB"))

    # grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # upscale slightly to help OCR
    gray = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)

    # denoise
    gray = cv2.fastNlMeansDenoising(gray, None, 25, 7, 21)

    # adaptive thresholding
    thr = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        10,
    )

    return thr


def ocr_image(pil_img: Image.Image, lang_name: str) -> Tuple[str, np.ndarray]:
    """
    Main OCR function used by main_app.show_image_tab.

    Args:
        pil_img: PIL Image uploaded by user
        lang_name: language name selected in dropdown (e.g. "English")

    Returns:
        text: extracted text (string)
        processed: processed image (NumPy array) for display
    """
    processed = _preprocess_for_tesseract(pil_img)

    tess_lang = LANG_MAP.get(lang_name, "eng")

    # psm 6 = assume a block of text
    config = "--oem 3 --psm 6"

    try:
        text = pytesseract.image_to_string(
            processed, lang=tess_lang, config=config
        )
    except Exception as e:
        print("Tesseract OCR error:", e)
        text = ""

    return text.strip(), processed
