@echo off
REM Runs the crawler dashboard from source (opens in your browser).
cd /d "%~dp0"
set PY=
py -3 --version >nul 2>&1 && set PY=py -3
if not defined PY python --version >nul 2>&1 && set PY=python
if not defined PY (
  echo Python 3.10+ not found. Install it from https://www.python.org/downloads/
  pause
  exit /b 1
)
%PY% -m pip install --upgrade -r requirements.txt
%PY% app.py
