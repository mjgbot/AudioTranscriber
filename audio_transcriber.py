#!/usr/bin/env python3
"""
AudioTranscriber - A simple tool for transcribing audio files to text
"""

import speech_recognition as sr
import sys
import os
from pydub import AudioSegment

def transcribe_audio(audio_file_path):
    """
    Transcribe an audio file to text using Google Speech Recognition
    """
    try:
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Load audio file
        audio = AudioSegment.from_file(audio_file_path)
        
        # Convert to wav format if needed
        if audio_file_path.lower().endswith('.mp3'):
            audio = audio.set_frame_rate(16000).set_channels(1)
            wav_path = audio_file_path.replace('.mp3', '_temp.wav')
            audio.export(wav_path, format="wav")
            audio_file_path = wav_path
        
        # Load audio file for recognition
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)
        
        # Perform speech recognition
        text = recognizer.recognize_google(audio_data)
        
        # Clean up temporary file if created
        if audio_file_path.endswith('_temp.wav'):
            os.remove(audio_file_path)
        
        return text
        
    except sr.UnknownValueError:
        return "Could not understand the audio"
    except sr.RequestError as e:
        return f"Could not request results from speech recognition service; {e}"
    except Exception as e:
        return f"An error occurred: {e}"

def main():
    if len(sys.argv) != 2:
        print("Usage: python audio_transcriber.py <audio_file>")
        print("Supported formats: wav, mp3, flac, m4a")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    if not os.path.exists(audio_file):
        print(f"Error: File '{audio_file}' not found")
        sys.exit(1)
    
    print(f"Transcribing: {audio_file}")
    print("Please wait...")
    
    result = transcribe_audio(audio_file)
    
    print("\nTranscription:")
    print("-" * 50)
    print(result)
    print("-" * 50)
    
    # Save transcription to file
    output_file = audio_file.rsplit('.', 1)[0] + '_transcription.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"\nTranscription saved to: {output_file}")

if __name__ == "__main__":
    main()
