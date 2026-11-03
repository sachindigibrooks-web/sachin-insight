@echo off
REM Builds the app into dist\FreeVideoDownloader\ and, if Inno Setup 6 is installed,
REM the installer dist\FreeVideoDownloader-Setup.exe (Start Menu + Desktop shortcut + uninstall).
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
%PY% build.py --installer
if errorlevel 1 (
  echo.
  echo The app folder is ready, but the installer was not made.
  echo Install Inno Setup 6 from https://jrsoftware.org/isdl.php and run this again.
)
rmdir /s /q build 2>nul
del /q *.spec 2>nul
echo.
echo ============================================================
echo  Done! Look in: %~dp0dist
echo    FreeVideoDownloader-Setup.exe  - installer to share
echo    FreeVideoDownloader\           - the app folder (portable)
echo ============================================================
explorer dist
pause
exit /b 0

:fail
echo.
echo Build FAILED - please send a screenshot of this window.
pause
exit /b 1
