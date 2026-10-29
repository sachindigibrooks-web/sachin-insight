@echo off
REM Builds dist\FreeVideoDownloader.exe (single file, ffmpeg bundled).
python -m pip install --upgrade -r requirements.txt pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name FreeVideoDownloader ^
  --collect-all imageio_ffmpeg app.py
echo.
echo Done: dist\FreeVideoDownloader.exe
pause
