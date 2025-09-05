# System Audio Recording Setup Guide

## Windows System Audio Recording

To record system audio (what's playing on your computer), you need to enable "Stereo Mix" in Windows sound settings.

### Step 1: Enable Stereo Mix

1. **Right-click the speaker icon** in your system tray
2. **Select "Open Sound settings"**
3. **Click "Sound Control Panel"** (on the right side)
4. **Go to the "Recording" tab**
5. **Right-click in empty space** and select **"Show Disabled Devices"**
6. **Right-click on "Stereo Mix"** and select **"Enable"**
7. **Right-click on "Stereo Mix"** again and select **"Set as Default Device"**

### Step 2: Test System Audio Recording

1. **Play some audio** on your computer (music, video, etc.)
2. **Open AudioTranscriber**
3. **Select "System Audio"** from the Source dropdown
4. **Click "Start"** to begin recording
5. **Click "Stop"** when done

### Troubleshooting

**If you don't see "Stereo Mix":**
- Your audio driver may not support it
- Try updating your audio drivers
- Some laptops have limited audio capabilities

**If recording fails:**
- Make sure audio is playing while recording
- Check that Stereo Mix is enabled and set as default
- Try restarting the application

### Alternative Solutions

If Stereo Mix is not available, you can use third-party software like:
- **VB-Audio Virtual Cable** (free)
- **VoiceMeeter** (free)
- **Audio Router** (free)

These create virtual audio devices that can capture system audio.

## macOS System Audio Recording

On macOS, system audio recording requires additional permissions:

1. **System Preferences** → **Security & Privacy** → **Privacy** → **Microphone**
2. **Grant permission** to your terminal/Python application
3. **Use "BlackHole"** or similar virtual audio driver for system audio capture

## Linux System Audio Recording

On Linux, you can use:
- **PulseAudio**: `pactl load-module module-null-sink`
- **ALSA**: Configure loopback devices
- **JACK**: Professional audio routing
