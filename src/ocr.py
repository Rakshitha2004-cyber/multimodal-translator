# ---------------------------------------------------------
# ocr.py — Hybrid OCR (TrOCR + Tesseract)
# ---------------------------------------------------------

from __future__ import annotations   # MUST be at very top

import numpy as np
import cv2
from PIL import Image
import pytesseract

import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# -------------------------------
# Load TrOCR Model (English only)
# -------------------------------
try:
    processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
    trocr_model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")
    trocr_available = True
except Exception as e:
    print("TrOCR loading failed:", e)
    trocr_available = False


# ---------------------------------------------------------
# Helper: preprocess for Tesseract
# ---------------------------------------------------------
def preprocess_for_tesseract(pil_img: Image.Image):
    """Convert to grayscale + threshold + denoise."""
    img = np.array(pil_img.convert("L"))

    # Light denoising
    img = cv2.fastNlMeansDenoising(img, None, 25)

    # Adaptive threshold
    th = cv2.adaptiveThreshold(
        img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 10
    )
    return th


# ---------------------------------------------------------
# MAIN HYBRID OCR FUNCTION
# ---------------------------------------------------------
def ocr_image(pil_img: Image.Image, lang_name: str):
    """
    Returns: (extracted_text, processed_image_preview)
    processed_image_preview is a numpy array ready for st.image()
    """

    # Convert PIL -> RGB
    img = pil_img.convert("RGB")

    # ---------------------------------------
    # 1. ***TESSERACT supports 100+ languages***
    # ---------------------------------------
    lang_map = {
        "English": "eng",
        "Hindi": "hin",
        "Kannada": "kan",
        "Tamil": "tam",
        "Telugu": "tel",
        "Malayalam": "mal",
        "Marathi": "mar",
        "Gujarati": "guj",
        "Urdu": "urd",
    }

    tess_lang = lang_map.get(lang_name, "eng")

    processed = preprocess_for_tesseract(img)

    try:
        tess_text = pytesseract.image_to_string(processed, lang=tess_lang)
    except Exception as e:
        print("Tesseract OCR failed:", e)
        tess_text = ""

    # ---------------------------------------
    # 2. ***TrOCR for English handwritten***
    # ---------------------------------------
    trocr_text = ""
    if lang_name == "English" and trocr_available:
        try:
            pixel_values = processor(images=img, return_tensors="pt").pixel_values
            generated = trocr_model.generate(pixel_values)
            trocr_text = processor.batch_decode(generated, skip_special_tokens=True)[0]
        except Exception as e:
            print("TrOCR error:", e)
            trocr_text = ""

    # ---------------------------------------
    # 3. Combine both (TrOCR strongest)
    # ---------------------------------------
    combined = (trocr_text + "\n" + tess_text).strip()

    return combined, processed
