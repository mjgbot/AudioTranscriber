@echo off
REM AudioTranscriber Launcher with Virtual Environment Setup
REM This script automatically creates a virtual environment and installs dependencies

echo ============================================================
echo AudioTranscriber - Automated Setup and Launch
echo ============================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python found. Starting setup...

REM Run the setup script
python setup_and_run.py

REM Check if setup was successful
if errorlevel 1 (
    echo.
    echo Setup failed. Press any key to exit.
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
echo.
echo You can now run AudioTranscriber using:
echo   - This launcher: %~nx0
echo   - Direct Python: python setup_and_run.py
echo   - Manual activation: venv\Scripts\activate
echo.
pause
