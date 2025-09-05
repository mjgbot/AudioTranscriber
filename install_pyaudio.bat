@echo off
REM PyAudio Installation Script for AudioTranscriber
REM This script installs PyAudio in the virtual environment to enable microphone recording

echo ============================================================
echo AudioTranscriber - PyAudio Installation
echo ============================================================

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run launch_gui.bat first to set up the environment.
    pause
    exit /b 1
)

echo Installing PyAudio for microphone recording...
echo.

REM Install PyAudio
venv\Scripts\pip.exe install pyaudio

if errorlevel 1 (
    echo.
    echo PyAudio installation failed.
    echo You can still use AudioTranscriber to transcribe existing audio files.
    echo.
    echo Troubleshooting:
    echo - Make sure you have Microsoft Visual C++ Build Tools installed
    echo - Try running as administrator
    echo - See PYAUDIO_INSTALL.md for detailed instructions
    pause
    exit /b 1
)

echo.
echo ✓ PyAudio installed successfully!
echo ✓ Microphone recording is now available in AudioTranscriber
echo.
echo You can now:
echo - Record audio directly from your microphone
echo - Use the "Start Recording" button in the GUI
echo - Transcribe recorded audio immediately
echo.
pause
