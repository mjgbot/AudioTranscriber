#!/usr/bin/env python3
"""
AudioTranscriber - A powerful tool for transcribing audio files to text using OpenAI's Whisper
Based on: https://github.com/openai/whisper
"""

import whisper
import sys
import os
import argparse
from pathlib import Path

def transcribe_audio(audio_file_path, model_size="base", language=None, task="transcribe"):
    """
    Transcribe an audio file to text using OpenAI's Whisper model
    
    Args:
        audio_file_path (str): Path to the audio file
        model_size (str): Whisper model size (tiny, base, small, medium, large, turbo)
        language (str): Language code (e.g., 'en', 'es', 'fr') or None for auto-detection
        task (str): 'transcribe' or 'translate' (translate to English)
    
    Returns:
        dict: Transcription result with text and metadata
    """
    try:
        print(f"Loading Whisper model: {model_size}")
        model = whisper.load_model(model_size)
        
        print(f"Transcribing: {audio_file_path}")
        print("This may take a while depending on the audio length and model size...")
        
        # Transcribe the audio
        result = model.transcribe(
            audio_file_path,
            language=language,
            task=task,
            verbose=True
        )
        
        return result
        
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return None

def save_transcription(result, audio_file_path, output_format="txt"):
    """
    Save transcription result to file
    
    Args:
        result (dict): Whisper transcription result
        audio_file_path (str): Original audio file path
        output_format (str): Output format ('txt', 'srt', 'vtt')
    """
    if not result:
        return None
    
    base_name = Path(audio_file_path).stem
    
    if output_format == "txt":
        output_file = f"{base_name}_transcription.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result["text"])
    
    elif output_format == "srt":
        output_file = f"{base_name}_transcription.srt"
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result["segments"], 1):
                start_time = format_time(segment["start"])
                end_time = format_time(segment["end"])
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment['text'].strip()}\n\n")
    
    elif output_format == "vtt":
        output_file = f"{base_name}_transcription.vtt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for segment in result["segments"]:
                start_time = format_time_vtt(segment["start"])
                end_time = format_time_vtt(segment["end"])
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment['text'].strip()}\n\n")
    
    return output_file

def format_time(seconds):
    """Format time in seconds to SRT format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def format_time_vtt(seconds):
    """Format time in seconds to VTT format (HH:MM:SS.mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millisecs:03d}"

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio files using OpenAI's Whisper")
    parser.add_argument("audio_file", help="Path to the audio file to transcribe")
    parser.add_argument("--model", "-m", default="base", 
                       choices=["tiny", "base", "small", "medium", "large", "turbo"],
                       help="Whisper model size (default: base)")
    parser.add_argument("--language", "-l", help="Language code (e.g., 'en', 'es', 'fr'). Auto-detect if not specified")
    parser.add_argument("--task", "-t", default="transcribe", choices=["transcribe", "translate"],
                       help="Task: transcribe or translate to English (default: transcribe)")
    parser.add_argument("--output", "-o", default="txt", choices=["txt", "srt", "vtt"],
                       help="Output format (default: txt)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed progress")
    
    args = parser.parse_args()
    
    # Check if audio file exists
    if not os.path.exists(args.audio_file):
        print(f"Error: File '{args.audio_file}' not found")
        sys.exit(1)
    
    # Validate model choice for translation task
    if args.task == "translate" and args.model == "turbo":
        print("Warning: The 'turbo' model is not trained for translation tasks.")
        print("Consider using 'medium' or 'large' for better translation results.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("=" * 60)
    print("AudioTranscriber - Powered by OpenAI Whisper")
    print("=" * 60)
    print(f"Audio file: {args.audio_file}")
    print(f"Model: {args.model}")
    print(f"Language: {args.language or 'Auto-detect'}")
    print(f"Task: {args.task}")
    print(f"Output format: {args.output}")
    print("=" * 60)
    
    # Perform transcription
    result = transcribe_audio(
        args.audio_file, 
        model_size=args.model,
        language=args.language,
        task=args.task
    )
    
    if result:
        print("\n" + "=" * 60)
        print("TRANSCRIPTION RESULT")
        print("=" * 60)
        print(result["text"])
        print("=" * 60)
        
        # Save to file
        output_file = save_transcription(result, args.audio_file, args.output)
        if output_file:
            print(f"\nTranscription saved to: {output_file}")
        
        # Show additional info if verbose
        if args.verbose and "segments" in result:
            print(f"\nDetected language: {result.get('language', 'Unknown')}")
            print(f"Number of segments: {len(result['segments'])}")
            print(f"Total duration: {result['segments'][-1]['end']:.2f} seconds")
    else:
        print("Transcription failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()