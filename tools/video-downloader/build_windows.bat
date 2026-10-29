@echo off
REM Builds dist\FreeVideoDownloader.exe (single file, ffmpeg bundled).
cd /d "%~dp0"
set PY=
py -3 --version >nul 2>&1 && set PY=py -3
if not defined PY python --version >nul 2>&1 && set PY=python
if not defined PY (
  echo Python 3.10+ not found. Install it from https://www.python.org/downloads/
  pause
  exit /b 1
)
%PY% -m pip install --upgrade -r requirements.txt pyinstaller
%PY% -m PyInstaller --noconfirm --onefile --windowed --name FreeVideoDownloader ^
  --collect-all imageio_ffmpeg app.py
echo.
echo Done: dist\FreeVideoDownloader.exe
pause
