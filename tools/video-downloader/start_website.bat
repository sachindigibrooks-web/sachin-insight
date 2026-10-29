@echo off
REM Starts the website on http://localhost:8000
cd /d "%~dp0"
call :findpy || goto :eof
%PY% -m pip install --upgrade -r requirements.txt
start "" http://localhost:8000
%PY% web.py
pause
goto :eof

:findpy
set PY=
py -3 --version >nul 2>&1 && set PY=py -3
if not defined PY python --version >nul 2>&1 && set PY=python
if defined PY exit /b 0
echo Python 3.10+ not found. Install it from https://www.python.org/downloads/
echo and tick "Add python.exe to PATH" on the first installer screen.
pause
exit /b 1
