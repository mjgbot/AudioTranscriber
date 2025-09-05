@echo off
REM Batch file for speaker detection with AudioTranscriber

if "%~1"=="" (
    echo ========================================
    echo    AudioTranscriber - Speaker Detection
    echo    Powered by OpenAI Whisper
    echo ========================================
    echo.
    echo Usage: Drag an audio file onto this batch file
    echo.
    echo This will identify different speakers and label them as:
    echo Speaker 1, Speaker 2, Speaker 3, etc.
    echo.
    pause
    exit /b 1
)

echo ========================================
echo    AudioTranscriber - Speaker Detection
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

echo Choose model for speaker detection:
echo 1. Base model (balanced speed/accuracy)
echo 2. Large model (best accuracy, slower)
echo.
set /p choice="Enter your choice (1-2): "

if "%choice%"=="1" (
    echo Detecting speakers with base model...
    python audio_transcriber.py "%1" --model base --speakers --verbose
) else if "%choice%"=="2" (
    echo Detecting speakers with large model (this will take longer)...
    python audio_transcriber.py "%1" --model large --speakers --verbose
) else (
    echo Invalid choice. Using base model...
    python audio_transcriber.py "%1" --model base --speakers --verbose
)

echo.
echo ========================================
echo Speaker detection completed!
echo Check the current directory for output files.
echo ========================================
echo.
pause
