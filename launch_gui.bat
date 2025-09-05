@echo off
REM Launch AudioTranscriber GUI

echo ========================================
echo    AudioTranscriber GUI Launcher
echo    Powered by OpenAI Whisper
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if audio_transcriber_gui.py exists
if not exist "audio_transcriber_gui.py" (
    echo ERROR: audio_transcriber_gui.py not found
    echo Please make sure you're running this from the AudioTranscriber directory
    pause
    exit /b 1
)

echo Starting AudioTranscriber GUI...
echo.

python audio_transcriber_gui.py

if errorlevel 1 (
    echo.
    echo GUI exited with an error.
    pause
)
