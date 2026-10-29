@echo off
REM Builds two single-file programs in the dist folder (ffmpeg bundled, no Python needed to run them):
REM   FreeVideoDownloader.exe     - desktop app
REM   FreeVideoDownloaderWeb.exe  - website version (opens in the browser)
cd /d "%~dp0"
set PY=
py -3 --version >nul 2>&1 && set PY=py -3
if not defined PY python --version >nul 2>&1 && set PY=python
if not defined PY (
  echo Python 3.10+ not found. Install it from https://www.python.org/downloads/
  pause
  exit /b 1
)
%PY% -m pip install --upgrade -r requirements.txt pyinstaller || goto :fail

echo.
echo [1/2] Building desktop app...
%PY% -m PyInstaller --noconfirm --onefile --windowed --name FreeVideoDownloader ^
  --collect-all imageio_ffmpeg app.py || goto :fail

echo.
echo [2/2] Building website version...
%PY% -m PyInstaller --noconfirm --onefile --name FreeVideoDownloaderWeb ^
  --add-data "web;web" --collect-all imageio_ffmpeg web.py || goto :fail

rmdir /s /q build 2>nul
del /q *.spec 2>nul
echo.
echo ============================================================
echo  Done! Your .exe files are in: %~dp0dist
echo ============================================================
explorer dist
pause
exit /b 0

:fail
echo.
echo Build FAILED - please send a screenshot of this window.
pause
exit /b 1
