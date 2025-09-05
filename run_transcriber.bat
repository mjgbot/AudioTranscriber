@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    AudioTranscriber - Batch Launcher
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

REM Check if audio_transcriber.py exists
if not exist "audio_transcriber.py" (
    echo ERROR: audio_transcriber.py not found
    echo Please make sure you're running this from the AudioTranscriber directory
    pause
    exit /b 1
)

REM Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo WARNING: FFmpeg not found in PATH
    echo Audio processing may not work properly
    echo Please install FFmpeg and try again
    echo.
)

echo Available options:
echo 1. Quick transcribe (base model)
echo 2. High accuracy transcribe (large model)
echo 3. Fast transcribe (tiny model)
echo 4. Generate subtitles (SRT format)
echo 5. Translate to English
echo 6. Custom options
echo 7. Show help
echo 8. Exit
echo.

set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" goto quick_transcribe
if "%choice%"=="2" goto high_accuracy
if "%choice%"=="3" goto fast_transcribe
if "%choice%"=="4" goto generate_subtitles
if "%choice%"=="5" goto translate
if "%choice%"=="6" goto custom_options
if "%choice%"=="7" goto show_help
if "%choice%"=="8" goto exit_program
goto invalid_choice

:quick_transcribe
echo.
echo === Quick Transcribe (Base Model) ===
set /p audio_file="Enter path to audio file: "
if "%audio_file%"=="" (
    echo No file specified. Exiting...
    pause
    exit /b 1
)
python audio_transcriber.py "%audio_file%" --model base
goto end

:high_accuracy
echo.
echo === High Accuracy Transcribe (Large Model) ===
echo Note: This will take longer but provide better accuracy
set /p audio_file="Enter path to audio file: "
if "%audio_file%"=="" (
    echo No file specified. Exiting...
    pause
    exit /b 1
)
python audio_transcriber.py "%audio_file%" --model large --verbose
goto end

:fast_transcribe
echo.
echo === Fast Transcribe (Tiny Model) ===
echo Note: This will be faster but less accurate
set /p audio_file="Enter path to audio file: "
if "%audio_file%"=="" (
    echo No file specified. Exiting...
    pause
    exit /b 1
)
python audio_transcriber.py "%audio_file%" --model tiny
goto end

:generate_subtitles
echo.
echo === Generate Subtitles (SRT Format) ===
set /p audio_file="Enter path to audio file: "
if "%audio_file%"=="" (
    echo No file specified. Exiting...
    pause
    exit /b 1
)
set /p model_choice="Choose model (base/large): "
if "%model_choice%"=="large" (
    python audio_transcriber.py "%audio_file%" --model large --output srt --verbose
) else (
    python audio_transcriber.py "%audio_file%" --model base --output srt
)
goto end

:translate
echo.
echo === Translate to English ===
set /p audio_file="Enter path to audio file: "
if "%audio_file%"=="" (
    echo No file specified. Exiting...
    pause
    exit /b 1
)
set /p language="Enter source language code (e.g., es, fr, de) or press Enter for auto-detect: "
if "%language%"=="" (
    python audio_transcriber.py "%audio_file%" --task translate --model medium --verbose
) else (
    python audio_transcriber.py "%audio_file%" --task translate --model medium --language %language% --verbose
)
goto end

:custom_options
echo.
echo === Custom Options ===
set /p audio_file="Enter path to audio file: "
if "%audio_file%"=="" (
    echo No file specified. Exiting...
    pause
    exit /b 1
)
echo.
echo Available models: tiny, base, small, medium, large, turbo
set /p model="Enter model (default: base): "
if "%model%"=="" set model=base

echo.
echo Available tasks: transcribe, translate
set /p task="Enter task (default: transcribe): "
if "%task%"=="" set task=transcribe

echo.
echo Available outputs: txt, srt, vtt
set /p output="Enter output format (default: txt): "
if "%output%"=="" set output=txt

echo.
set /p language="Enter language code (optional, e.g., en, es, fr): "

echo.
echo Running: python audio_transcriber.py "%audio_file%" --model %model% --task %task% --output %output%
if "%language%"=="" (
    python audio_transcriber.py "%audio_file%" --model %model% --task %task% --output %output% --verbose
) else (
    python audio_transcriber.py "%audio_file%" --model %model% --task %task% --output %output% --language %language% --verbose
)
goto end

:show_help
echo.
echo === AudioTranscriber Help ===
python audio_transcriber.py --help
echo.
echo === Additional Information ===
echo.
echo Model Comparison:
echo - tiny:   Fastest, least accurate (~1GB VRAM)
echo - base:  Balanced speed/accuracy (~1GB VRAM)
echo - small: Good accuracy (~2GB VRAM)
echo - medium: High accuracy (~5GB VRAM)
echo - large: Best accuracy (~10GB VRAM)
echo - turbo: Fast English-only (~6GB VRAM)
echo.
echo Supported formats: MP3, WAV, FLAC, M4A, MP4, AVI, MOV, etc.
echo Supported languages: 99+ languages including en, es, fr, de, it, pt, ru, zh, ja, ko, ar
echo.
pause
goto end

:invalid_choice
echo.
echo Invalid choice. Please enter a number between 1-8.
echo.
pause
goto start

:end
echo.
echo ========================================
echo Transcription completed!
echo Check the current directory for output files.
echo ========================================
echo.
pause

:exit_program
echo.
echo Thank you for using AudioTranscriber!
echo.
pause
