@echo off
REM Simple drag-and-drop batch file for AudioTranscriber
REM Just drag an audio file onto this batch file to transcribe it

if "%~1"=="" (
    echo ========================================
    echo    AudioTranscriber - Drag & Drop
    echo    Powered by OpenAI Whisper
    echo ========================================
    echo.
    echo Usage: Drag an audio file onto this batch file
    echo.
    echo Or run: run_transcriber.bat for more options
    echo.
    pause
    exit /b 1
)

echo ========================================
echo    AudioTranscriber - Quick Transcribe
echo    Powered by OpenAI Whisper
echo ========================================
echo.
echo Processing: %~nx1
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo WARNING: FFmpeg not found in PATH
    echo Audio processing may not work properly
    echo.
)

echo Starting transcription with base model...
echo This may take a while depending on the audio length...
echo.

python audio_transcriber.py "%1" --model base --verbose

echo.
echo ========================================
echo Transcription completed!
echo Check the current directory for output files.
echo ========================================
echo.
pause
