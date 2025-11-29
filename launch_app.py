import subprocess
import sys
import os

# Activate virtual environment
venv_path = os.path.join(os.path.dirname(__file__), "venv", "Scripts", "activate")

# Run Streamlit app
app_path = os.path.join(os.path.dirname(__file__), "src", "main_app.py")

subprocess.call(f'start cmd /k "{venv_path} && streamlit run {app_path}"', shell=True)
