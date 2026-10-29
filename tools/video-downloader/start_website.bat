@echo off
REM Starts the website on http://localhost:8000
python -m pip install --upgrade -r requirements.txt
start "" http://localhost:8000
python web.py
pause
