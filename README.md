# AudioTranscriber

A powerful tool for transcribing audio files to text using [OpenAI's Whisper](https://github.com/openai/whisper) - a state-of-the-art speech recognition model trained on diverse audio data.

## Features

- **High Accuracy**: Uses OpenAI's Whisper model for superior transcription quality
- **Multiple Languages**: Supports 99+ languages with automatic language detection
- **Translation**: Translate non-English speech to English
- **Multiple Formats**: Support for WAV, MP3, FLAC, M4A, and more audio formats
- **Multiple Output Formats**: Plain text (.txt), SRT subtitles (.srt), and WebVTT (.vtt)
- **Model Options**: Choose from different model sizes (tiny, base, small, medium, large, turbo)
- **Timestamps**: Generate subtitle files with precise timing information

## Installation

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

1. Clone the repository:
```bash
git clone https://github.com/mjgbot/AudioTranscriber.git
cd AudioTranscriber
```

2. Install Python dependencies:
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

### Batch Files (Windows)

For quick access, several batch files are provided:

- **`launch_gui.bat`** - Launch the GUI application
- **`run_transcriber.bat`** - Interactive command-line menu with options
- **`transcribe.bat`** - Drag-and-drop audio files for quick transcription
- **`generate_subtitles.bat`** - Drag-and-drop audio files to generate SRT subtitles

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

# Verbose output with detailed information
python audio_transcriber.py audio_file.mp3 --verbose
```

### Command Line Options

- `audio_file`: Path to the audio file to transcribe
- `--model, -m`: Whisper model size (tiny, base, small, medium, large, turbo)
- `--language, -l`: Language code (e.g., 'en', 'es', 'fr'). Auto-detect if not specified
- `--task, -t`: Task type - 'transcribe' or 'translate' (default: transcribe)
- `--output, -o`: Output format - 'txt', 'srt', or 'vtt' (default: txt)
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

## Output Files

The tool generates output files based on the specified format:

- **TXT**: Plain text transcription
- **SRT**: SubRip subtitle format with timestamps
- **VTT**: WebVTT subtitle format for web players

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