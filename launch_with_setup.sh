#!/bin/bash
# AudioTranscriber Launcher with Virtual Environment Setup
# This script automatically creates a virtual environment and installs dependencies

echo "============================================================"
echo "AudioTranscriber - Automated Setup and Launch"
echo "============================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed or not in PATH"
        echo "Please install Python from https://python.org"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Python found. Starting setup..."

# Run the setup script
$PYTHON_CMD setup_and_run.py

# Check if setup was successful
if [ $? -ne 0 ]; then
    echo ""
    echo "Setup failed. Press Enter to exit."
    read
    exit 1
fi

echo ""
echo "Setup completed successfully!"
echo ""
echo "You can now run AudioTranscriber using:"
echo "  - This launcher: ./launch_with_setup.sh"
echo "  - Direct Python: python3 setup_and_run.py"
echo "  - Manual activation: source venv/bin/activate"
echo ""
read -p "Press Enter to continue..."
