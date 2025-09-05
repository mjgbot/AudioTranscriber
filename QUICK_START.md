# AudioTranscriber - Quick Start Guide

## 🚀 One-Click Setup and Launch

AudioTranscriber now includes **automated setup** that creates a virtual environment and installs all dependencies automatically!

### Windows Users

**Double-click `launch_gui.bat`** - That's it! 

The script will:
1. ✅ Check if Python is installed
2. ✅ Create a virtual environment (`venv` folder)
3. ✅ Install all required dependencies
4. ✅ Launch the GUI application

### What Happens During Setup

```
============================================================
AudioTranscriber Environment Setup
============================================================
✓ Virtual environment already exists
Using Python: C:\...\venv\Scripts\python.exe

Starting AudioTranscriber GUI...
```

### First Time Setup

On first run, you'll see:
- Virtual environment creation
- Dependency installation (may take a few minutes)
- Optional PyAudio installation for recording

### Subsequent Runs

After the first setup:
- ✅ **Instant launch** - Uses existing virtual environment
- ✅ **No reinstallation** - Dependencies are cached
- ✅ **Fast startup** - Ready to transcribe immediately

## 📁 File Structure After Setup

```
AudioTranscriber/
├── venv/                    # Virtual environment (auto-created)
│   ├── Scripts/
│   │   ├── python.exe       # Isolated Python
│   │   └── pip.exe         # Package manager
│   └── Lib/                # Installed packages
├── launch_gui.bat          # Main launcher (double-click this!)
├── setup_and_run.py        # Setup script
├── audio_transcriber_gui.py # GUI application
└── requirements.txt        # Dependencies list
```

## 🔧 Manual Setup (Advanced Users)

If you prefer manual setup:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python audio_transcriber_gui.py
```

## 🎯 Features Available After Setup

- ✅ **Audio Transcription** - Convert audio to text
- ✅ **Speaker Detection** - Identify different speakers
- ✅ **Multiple Formats** - TXT, SRT, VTT output
- ✅ **Audio Recording** - Record from microphone (if PyAudio installed)
- ✅ **Hugging Face Integration** - Advanced speaker diarization

## 🆘 Troubleshooting

### "Python is not installed"
- Download and install Python from [python.org](https://python.org)
- Make sure to check "Add Python to PATH" during installation

### "Setup failed"
- Check your internet connection
- Try running as administrator
- Ensure you have enough disk space

### "PyAudio installation failed"
- This is optional - you can still transcribe existing files
- See `PYAUDIO_INSTALL.md` for detailed installation help

## 🎉 You're Ready!

Once setup completes, you can:
1. **Browse** for audio files to transcribe
2. **Record** audio directly from your microphone
3. **Configure** transcription settings
4. **Get results** with timestamps and speaker labels

**Enjoy using AudioTranscriber!** 🎵➡️📝
