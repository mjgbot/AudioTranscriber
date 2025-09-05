# AudioTranscriber

A powerful tool for transcribing audio files to text using [OpenAI's Whisper](https://github.com/openai/whisper) - a state-of-the-art speech recognition model trained on diverse audio data.

## Features

- **High Accuracy**: Uses OpenAI's Whisper model for superior transcription quality
- **Multiple Languages**: Supports 99+ languages with automatic language detection
- **Translation**: Translate non-English speech to English
- **Speaker Detection**: Identify different speakers and label them as Speaker 1, Speaker 2, etc.
- **Advanced Speaker Diarization**: Uses Hugging Face's pyannote.audio for superior speaker detection
- **Audio Recording**: Record audio directly from your microphone (WAV/MP3)
- **File Management**: Easy access to recordings and transcriptions
- **Organized Output**: Transcriptions saved in dedicated "Transcriptions" folder
- **Audio File Selection**: Browse and select any audio file for transcription
- **Real-time Audio Monitoring**: Visual audio level meter during recording
- **Multiple Formats**: Support for WAV, MP3, FLAC, M4A, and more audio formats
- **Multiple Output Formats**: Plain text (.txt), SRT subtitles (.srt), and WebVTT (.vtt)
- **Model Options**: Choose from different model sizes (tiny, base, small, medium, large, turbo)
- **Timestamps**: Generate subtitle files with precise timing information
- **Meeting/Interview Mode**: Perfect for transcribing multi-speaker conversations

## Installation

### 🚀 Quick Start (Recommended)

**Windows Users**: Simply double-click `launch_gui.bat` - the setup is fully automated!

The launcher will:
- ✅ Create a virtual environment automatically
- ✅ Install all dependencies
- ✅ Launch the GUI application

### Manual Installation

### Prerequisites

1. **Python 3.8+** (recommended: Python 3.9+)
2. **FFmpeg** - Required for audio processing

#### Install FFmpeg

**Windows:**
```bash
# Using Chocolatey
choco install ffmpeg

# Using Scoop
scoop install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Linux (Arch):**
```bash
sudo pacman -S ffmpeg
```

### Install AudioTranscriber

#### Option 1: Automated Setup (Recommended)
1. Clone the repository:
```bash
git clone https://github.com/mjgbot/AudioTranscriber.git
cd AudioTranscriber
```

2. **Windows**: Double-click `launch_gui.bat`
   **macOS/Linux**: Run `python setup_and_run.py`

#### Option 2: Manual Setup
1. Clone the repository:
```bash
git clone https://github.com/mjgbot/AudioTranscriber.git
cd AudioTranscriber
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
```bash
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### GUI Application (Recommended)

The easiest way to use AudioTranscriber is through the graphical interface:

**Windows:**
```bash
# Double-click the batch file
launch_gui.bat

# Or run directly
python audio_transcriber_gui.py
```

**Features of the GUI:**
- **File Browser**: Easy audio file selection with drag-and-drop support
- **Model Selection**: Choose from all available Whisper models with descriptions
- **Language Selection**: Pick from 16+ common languages or use auto-detection
- **Task Options**: Transcribe or translate to English
- **Output Formats**: Plain text, SRT subtitles, or WebVTT subtitles
- **Progress Bar**: Real-time transcription progress
- **Results Display**: View transcription results directly in the interface
- **Status Updates**: Clear feedback on what's happening
- **Audio Recording**: Record audio directly from your microphone (WAV/MP3)
- **File Management**: Easy access to recordings and transcriptions
- **Organized Output**: Transcriptions saved in dedicated "Transcriptions" folder
- **Audio File Selection**: Browse and select any audio file for transcription
- **Real-time Audio Monitoring**: Visual audio level meter during recording
- **Recording Controls**: Start/stop recording with visual feedback

### Batch Files (Windows)

For quick access, several batch files are provided:

- **`launch_gui.bat`** - Launch the GUI application
- **`run_transcriber.bat`** - Interactive command-line menu with options
- **`transcribe.bat`** - Drag-and-drop audio files for quick transcription
- **`generate_subtitles.bat`** - Drag-and-drop audio files to generate SRT subtitles
- **`detect_speakers.bat`** - Drag-and-drop audio files for speaker detection

### Command Line Usage

For advanced users or automation, you can use the command-line interface:

#### Basic Usage

```bash
python audio_transcriber.py audio_file.mp3
```

### Advanced Usage

```bash
# Use a specific model (faster/slower, more/less accurate)
python audio_transcriber.py audio_file.mp3 --model large

# Specify language for better accuracy
python audio_transcriber.py spanish_audio.mp3 --language es

# Translate to English
python audio_transcriber.py french_audio.mp3 --task translate --model medium

# Generate SRT subtitle file
python audio_transcriber.py audio_file.mp3 --output srt

# Generate WebVTT subtitle file
python audio_transcriber.py audio_file.mp3 --output vtt

# Detect different speakers (perfect for meetings/interviews)
python audio_transcriber.py meeting_audio.mp3 --speakers --model large

# Use advanced speaker diarization with Hugging Face token
python audio_transcriber.py meeting_audio.mp3 --speakers --hf-token YOUR_HF_TOKEN --model large

# Verbose output with detailed information
python audio_transcriber.py audio_file.mp3 --verbose
```

### Command Line Options

- `audio_file`: Path to the audio file to transcribe
- `--model, -m`: Whisper model size (tiny, base, small, medium, large, turbo)
- `--language, -l`: Language code (e.g., 'en', 'es', 'fr'). Auto-detect if not specified
- `--task, -t`: Task type - 'transcribe' or 'translate' (default: transcribe)
- `--output, -o`: Output format - 'txt', 'srt', or 'vtt' (default: txt)
- `--speakers, -s`: Detect and label different speakers
- `--hf-token`: Hugging Face token for advanced speaker detection
- `--verbose, -v`: Show detailed progress and metadata

## Model Comparison

| Model  | Parameters | VRAM Required | Speed | Accuracy | Best For |
|--------|------------|---------------|-------|----------|----------|
| tiny   | 39M        | ~1 GB         | ~10x  | Good     | Quick testing |
| base   | 74M        | ~1 GB         | ~7x   | Better   | Balanced performance |
| small  | 244M       | ~2 GB         | ~4x   | Good     | Good accuracy/speed |
| medium | 769M       | ~5 GB         | ~2x   | Better   | High accuracy |
| large  | 1550M      | ~10 GB        | 1x    | Best     | Maximum accuracy |
| turbo  | 809M       | ~6 GB         | ~8x   | Good     | Fast English only |

**Note**: The `turbo` model is optimized for speed and English-only applications. For translation tasks, use `medium` or `large` models.

## Supported Audio Formats

- WAV
- MP3
- FLAC
- M4A
- MP4 (audio)
- And many more (via FFmpeg)

## Supported Languages

Whisper supports 99+ languages including:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- Arabic (ar)
- And many more...

## Examples

### Transcribe English Audio
```bash
python audio_transcriber.py meeting_recording.mp3 --model base
```

### Transcribe Spanish Audio
```bash
python audio_transcriber.py spanish_speech.wav --language es --model medium
```

### Translate French to English
```bash
python audio_transcriber.py french_interview.mp3 --task translate --model large
```

### Generate Subtitles
```bash
python audio_transcriber.py podcast.mp3 --output srt --model base
```

### Detect Speakers (Meeting/Interview Mode)
```bash
python audio_transcriber.py meeting_recording.mp3 --speakers --model large
```

### Translate with Speaker Detection
```bash
python audio_transcriber.py multilingual_meeting.mp3 --task translate --speakers --model medium
```

## Hugging Face Authentication for Advanced Speaker Detection

For the most accurate speaker detection, AudioTranscriber can use Hugging Face's pyannote.audio pipeline. This requires a Hugging Face account and token.

### Getting a Hugging Face Token

1. **Create a Hugging Face account**: Go to [huggingface.co](https://huggingface.co) and sign up
2. **Get your token**: Visit [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
3. **Create a new token**: Click "New token" and give it a name (e.g., "AudioTranscriber")
4. **Copy the token**: Save the token securely - you'll need it for authentication

### Using Hugging Face Authentication

#### In the GUI
1. **Enter your token**: In the "Hugging Face Authentication" section, paste your token
2. **Save the token**: Click "Save Token" to authenticate and store it securely
3. **Enable speaker detection**: Check "Detect different speakers" for advanced diarization
4. **Start transcription**: The system will automatically use the advanced pyannote.audio pipeline

#### Command Line
```bash
# Use your Hugging Face token for advanced speaker detection
python audio_transcriber.py meeting.mp3 --speakers --hf-token YOUR_HF_TOKEN --model large
```

#### Token Storage
- **Secure storage**: Tokens are stored in `~/.audiotranscriber/hf_config.json`
- **Persistent**: Once saved, the token persists across sessions
- **Clear token**: Use the "Clear Token" button in GUI or delete the config file

### Speaker Detection Methods

AudioTranscriber offers two speaker detection methods:

1. **Fallback Method** (No token required):
   - Uses MFCC features and clustering
   - Good for basic speaker separation
   - Works without internet connection

2. **Advanced Method** (Requires HF token):
   - Uses pyannote.audio pipeline
   - Superior accuracy and speaker separation
   - Requires internet connection for model download
   - Better handling of overlapping speech

### Authentication Status

The system will show you which method is being used:
- ✅ "Using Hugging Face authentication for pyannote pipeline..." (Advanced method)
- ⚠️ "Using fallback speaker detection method..." (Basic method)

### Real-time Audio Monitoring

During recording, you can monitor audio levels:

- **Visual Meter**: Progress bar showing current audio level (0-100%)
- **Level Display**: Percentage indicator of microphone input
- **Real-time Updates**: Live feedback during recording
- **Noise Detection**: Helps ensure good audio quality

## Audio Recording

AudioTranscriber includes built-in audio recording functionality that allows you to record audio directly from your microphone and transcribe it immediately.

### Recording Features

- **Direct microphone recording**: Record audio using your computer's microphone
- **Automatic file management**: Recordings are saved with timestamps
- **Seamless workflow**: Record and transcribe in one application
- **High-quality audio**: Optimized settings for Whisper transcription (16kHz, mono)
- **Multiple device support**: Choose from available audio input devices

### Using Audio Recording

#### In the GUI
1. **Start Recording**: Click "Start Recording" to begin capturing audio
2. **Record Audio**: Speak into your microphone
3. **Stop Recording**: Click "Stop Recording" when finished
4. **Transcribe**: The recorded file is automatically loaded for transcription

#### Recording Settings
- **Sample Rate**: 16kHz (optimized for Whisper)
- **Channels**: Mono (single channel)
- **Format**: WAV or MP3 (user selectable)
- **Location**: Saved in `recordings/` folder with timestamp
- **MP3 Conversion**: Automatic conversion using FFmpeg

### Prerequisites for Recording

- **PyAudio**: Required for microphone access (optional - see installation guide below)
- **Microphone**: Working microphone connected to your computer
- **Audio Drivers**: Proper audio drivers installed

#### Install PyAudio

**Note**: PyAudio is optional. If not installed, you can still transcribe existing audio files.

**Windows:**
```bash
pip install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install python3-pyaudio
# or
sudo apt install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**Troubleshooting**: See `PYAUDIO_INSTALL.md` for detailed installation instructions and troubleshooting.

### Recording Workflow

1. **Record**: Use the recording controls to capture audio
2. **Review**: Check the recorded file path in the file selection
3. **Configure**: Set your transcription preferences (model, language, speakers)
4. **Transcribe**: Click "Start Transcription" to process the recording

### File Organization

AudioTranscriber automatically organizes your files:

- **Recordings**: Saved in `recordings/` folder
- **Transcriptions**: Saved in `Transcriptions/` folder
- **Easy Access**: Use "View Recordings" and "View Transcriptions" buttons to open folders

### Settings Menu

Access advanced features through the Settings menu:

- **Hugging Face Authentication**: Click Settings → Hugging Face Authentication
- **Token Management**: Save, clear, and manage your HF token
- **Advanced Speaker Detection**: Enable with valid HF token
- **Clean Interface**: Settings moved out of main workflow

### Audio File Selection

You can transcribe any audio file by:

1. **Browse**: Click "Browse" to select an audio file
2. **Clear**: Click "Clear" to remove the selected file
3. **Supported Formats**: MP3, WAV, FLAC, M4A, MP4, AVI, MOV, MKV

### GUI Layout

The interface features a modern, streamlined design:

- **Recording First**: Audio recording controls at the top for immediate access
- **Transcription Last**: Transcription controls at the bottom for processing
- **Settings Menu**: Hugging Face authentication moved to Settings menu
- **Modern Styling**: Clean typography, improved spacing, and professional appearance
- **Compact Design**: Results area sized for immediate viewing
- **No Expansion Needed**: All features visible in default window size
- **Responsive Layout**: Adapts to different screen sizes

## Output Files

The tool generates output files in the `Transcriptions/` folder based on the specified format:

- **TXT**: Plain text transcription (with speaker labels if --speakers is used)
- **SRT**: SubRip subtitle format with timestamps (includes speaker names)
- **VTT**: WebVTT subtitle format for web players (includes speaker names)

### Speaker Detection Output

When using the `--speakers` flag, the output will include speaker identification:

**TXT Format (with speaker detection):**
```
[00:00:05 - 00:00:12] Speaker 1: Hello everyone, welcome to today's meeting.
[00:00:13 - 00:00:18] Speaker 2: Thank you for having me here.
[00:00:19 - 00:00:25] Speaker 1: Let's start with the quarterly review.
```

**TXT Format (without speaker detection):**
```
[00:00:05 - 00:00:12] Hello everyone, welcome to today's meeting.
[00:00:13 - 00:00:18] Thank you for having me here.
[00:00:19 - 00:00:25] Let's start with the quarterly review.
```

**SRT Format:**
```
1
00:00:05,000 --> 00:00:12,000
Speaker 1: Hello everyone, welcome to today's meeting.

2
00:00:13,000 --> 00:00:18,000
Speaker 2: Thank you for having me here.
```

## Performance Tips

1. **For English-only content**: Use `base.en` or `small.en` models for better performance
2. **For translation**: Use `medium` or `large` models for best results
3. **For speed**: Use `tiny` or `turbo` models
4. **For accuracy**: Use `large` model (requires more VRAM)

## Troubleshooting

### Common Issues

1. **FFmpeg not found**: Install FFmpeg using the instructions above
2. **CUDA out of memory**: Use a smaller model or CPU-only mode
3. **Slow transcription**: Consider using a smaller model or better hardware

### Getting Help

- Check the [Whisper repository](https://github.com/openai/whisper) for detailed documentation
- Review the [Whisper paper](https://arxiv.org/abs/2212.04356) for technical details

## License

This project is licensed under the MIT License. See the [Whisper repository](https://github.com/openai/whisper) for the original Whisper license.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - The core speech recognition model
- Based on the paper: "Robust Speech Recognition via Large-Scale Weak Supervision"