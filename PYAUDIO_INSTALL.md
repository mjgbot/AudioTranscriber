# PyAudio Installation Guide

PyAudio is required for microphone recording functionality in AudioTranscriber. Here's how to install it on different operating systems:

## Windows

### Method 1: Using pip (Recommended)
```bash
pip install pyaudio
```

### Method 2: If pip fails, use conda
```bash
conda install pyaudio
```

### Method 3: Pre-compiled wheel
If the above methods fail, download a pre-compiled wheel from:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

Then install with:
```bash
pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl
```
(Replace with the correct version for your Python version)

## macOS

### Method 1: Using Homebrew (Recommended)
```bash
brew install portaudio
pip install pyaudio
```

### Method 2: Using conda
```bash
conda install pyaudio
```

## Linux (Ubuntu/Debian)

### Method 1: Using apt
```bash
sudo apt update
sudo apt install python3-pyaudio
```

### Method 2: Using pip with system dependencies
```bash
sudo apt install portaudio19-dev python3-pyaudio
pip install pyaudio
```

## Linux (CentOS/RHEL/Fedora)

```bash
sudo yum install portaudio-devel
pip install pyaudio
```

## Verification

After installation, you can verify PyAudio is working by running:
```python
import pyaudio
print("PyAudio installed successfully!")
```

## Troubleshooting

### Windows: "Microsoft Visual C++ 14.0 is required"
- Install Microsoft Visual C++ Build Tools
- Or use conda instead: `conda install pyaudio`

### macOS: "PortAudio not found"
- Install portaudio first: `brew install portaudio`
- Then install pyaudio: `pip install pyaudio`

### Linux: "fatal error: portaudio.h: No such file or directory"
- Install portaudio development headers:
  - Ubuntu/Debian: `sudo apt install portaudio19-dev`
  - CentOS/RHEL: `sudo yum install portaudio-devel`

## Alternative: Use AudioTranscriber Without Recording

If you can't install PyAudio, you can still use AudioTranscriber to transcribe existing audio files. The recording functionality will be disabled, but all other features work normally.
