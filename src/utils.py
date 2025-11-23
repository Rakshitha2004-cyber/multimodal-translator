# utils.py
# utils.py

from config import SUPPORTED_LANGUAGES


def get_language_list():
    # Return all languages sorted alphabetically for nice dropdowns
    return sorted(SUPPORTED_LANGUAGES.keys())
