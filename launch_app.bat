@echo off
REM Change to the folder where this script is located
cd /d "%~dp0"

REM Activate venv
call venv\Scripts\activate

REM Run the Streamlit app
streamlit run src\main_app.py

pause

