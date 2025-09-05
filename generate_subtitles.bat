@echo off
REM Batch file for generating subtitles with AudioTranscriber

if "%~1"=="" (
    echo ========================================
    echo    AudioTranscriber - Subtitle Generator
    echo    Powered by OpenAI Whisper
    echo ========================================
    echo.
    echo Usage: Drag an audio file onto this batch file
    echo.
    echo This will generate SRT subtitle files with timestamps
    echo.
    pause
    exit /b 1
)

echo ========================================
echo    AudioTranscriber - Subtitle Generator
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

echo Choose subtitle quality:
echo 1. Fast (base model)
echo 2. High quality (large model)
echo.
set /p choice="Enter your choice (1-2): "

if "%choice%"=="1" (
    echo Generating subtitles with base model...
    python audio_transcriber.py "%1" --model base --output srt --verbose
) else if "%choice%"=="2" (
    echo Generating subtitles with large model (this will take longer)...
    python audio_transcriber.py "%1" --model large --output srt --verbose
) else (
    echo Invalid choice. Using base model...
    python audio_transcriber.py "%1" --model base --output srt --verbose
)

echo.
echo ========================================
echo Subtitle generation completed!
echo Check the current directory for .srt files.
echo ========================================
echo.
pause
