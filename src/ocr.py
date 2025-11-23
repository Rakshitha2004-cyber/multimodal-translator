# ocr.py

# ocr.py

import easyocr
import numpy as np
from PIL import Image, ImageOps, ImageFilter
from typing import Tuple, List
from languages import code_for_easyocr  # you already had this
from functools import lru_cache


@lru_cache(maxsize=32)
def get_reader(lang_name: str) -> easyocr.Reader:
    """
    Cache EasyOCR reader per language to avoid reloading models.
    """
    lang_code = code_for_easyocr(lang_name)  # e.g. "en", "hi", "ta"
    # cpu=True avoids GPU requirement
    return easyocr.Reader([lang_code], gpu=False)


def _preprocess_image(image: Image.Image) -> Image.Image:
    """
    Light preprocessing to help both printed and handwritten text:
    - convert to grayscale
    - increase contrast
    - slight sharpen
    """
    img = image.convert("L")  # grayscale
    img = ImageOps.autocontrast(img)
    img = img.filter(ImageFilter.SHARPEN)
    return img


def ocr_image(image: Image.Image, language_name: str) -> Tuple[str, List]:
    """
    Run OCR on a PIL image and return (joined_text, raw_results).
    """
    pre = _preprocess_image(image)
    np_img = np.array(pre)

    reader = get_reader(language_name)
    # detail=1 returns bounding boxes + text; good for debugging if needed
    results = reader.readtext(np_img, detail=1)

    lines = [text for (_, text, conf) in results if text.strip()]
    joined = "\n".join(lines).strip()

    return joined, results
