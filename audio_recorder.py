#!/usr/bin/env python3
"""
Audio Recording Module for AudioTranscriber
Handles microphone recording functionality
"""

import pyaudio
import wave
import threading
import time
import os
from datetime import datetime
from pathlib import Path
import subprocess

class AudioRecorder:
    """Handle audio recording from microphone"""
    
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        self.recording_thread = None
        self.frames = []
        self.recording_file = None
        self.audio_level_callback = None
        
        # Audio settings
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1  # Mono
        self.rate = 16000   # 16kHz sample rate (optimal for Whisper)
        
    def set_audio_level_callback(self, callback):
        """Set callback function for audio level updates"""
        self.audio_level_callback = callback
        
    def get_available_devices(self):
        """Get list of available audio input devices"""
        devices = []
        try:
            device_count = self.audio.get_device_count()
            for i in range(device_count):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:  # Input device
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxInputChannels'],
                        'sample_rate': int(device_info['defaultSampleRate'])
                    })
        except Exception as e:
            print(f"Error getting audio devices: {e}")
        return devices
    
    def get_default_device(self):
        """Get the default input device"""
        try:
            default_device = self.audio.get_default_input_device_info()
            return {
                'index': default_device['index'],
                'name': default_device['name'],
                'channels': default_device['maxInputChannels'],
                'sample_rate': int(default_device['defaultSampleRate'])
            }
        except Exception as e:
            print(f"Error getting default device: {e}")
            return None
    
    def start_recording(self, output_dir="recordings", device_index=None, format="wav"):
        """
        Start recording audio from microphone
        
        Args:
            output_dir (str): Directory to save recordings
            device_index (int): Audio device index (None for default)
            format (str): Output format ('wav' or 'mp3')
            
        Returns:
            str: Path to the recording file
        """
        if self.is_recording:
            return None
        
        try:
            # Create output directory
            Path(output_dir).mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.{format}"
            self.recording_file = os.path.join(output_dir, filename)
            self.recording_format = format
            
            # Initialize recording
            self.frames = []
            self.is_recording = True
            
            # Start recording thread
            self.recording_thread = threading.Thread(
                target=self._record_audio,
                args=(device_index,)
            )
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            return self.recording_file
            
        except Exception as e:
            print(f"Error starting recording: {e}")
            self.is_recording = False
            return None
    
    def stop_recording(self):
        """Stop recording and save the audio file"""
        if not self.is_recording:
            return None
        
        self.is_recording = False
        
        # Wait for recording thread to finish
        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)
        
        # Save the recording
        if self.frames and self.recording_file:
            try:
                if self.recording_format == "wav":
                    # Save as WAV
                    with wave.open(self.recording_file, 'wb') as wf:
                        wf.setnchannels(self.channels)
                        wf.setsampwidth(self.audio.get_sample_size(self.format))
                        wf.setframerate(self.rate)
                        wf.writeframes(b''.join(self.frames))
                elif self.recording_format == "mp3":
                    # Save as WAV first, then convert to MP3
                    temp_wav = self.recording_file.replace('.mp3', '_temp.wav')
                    with wave.open(temp_wav, 'wb') as wf:
                        wf.setnchannels(self.channels)
                        wf.setsampwidth(self.audio.get_sample_size(self.format))
                        wf.setframerate(self.rate)
                        wf.writeframes(b''.join(self.frames))
                    
                    # Convert to MP3 using FFmpeg
                    if self.convert_to_mp3(temp_wav, self.recording_file):
                        # Remove temporary WAV file
                        os.remove(temp_wav)
                    else:
                        print("MP3 conversion failed, keeping WAV file")
                        os.rename(temp_wav, self.recording_file.replace('.mp3', '.wav'))
                        self.recording_file = self.recording_file.replace('.mp3', '.wav')
                
                print(f"Recording saved to: {self.recording_file}")
                return self.recording_file
                
            except Exception as e:
                print(f"Error saving recording: {e}")
                return None
        
        return None
    
    def convert_to_mp3(self, wav_file, mp3_file):
        """Convert WAV file to MP3 using FFmpeg"""
        try:
            # Check if FFmpeg is available
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            
            # Convert WAV to MP3
            cmd = [
                "ffmpeg", "-i", wav_file, "-acodec", "mp3", 
                "-ab", "128k", "-ar", "44100", "-y", mp3_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Successfully converted to MP3: {mp3_file}")
                return True
            else:
                print(f"FFmpeg conversion failed: {result.stderr}")
                return False
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("FFmpeg not found. Cannot convert to MP3.")
            return False
        except Exception as e:
            print(f"Error converting to MP3: {e}")
            return False
    
    def _record_audio(self, device_index=None):
        """Internal method to record audio"""
        try:
            # Open audio stream
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk
            )
            
            print("Recording started... (Press Ctrl+C to stop)")
            
            # Record audio
            while self.is_recording:
                try:
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    self.frames.append(data)
                    
                    # Calculate audio level
                    if self.audio_level_callback:
                        import numpy as np
                        audio_data = np.frombuffer(data, dtype=np.int16)
                        rms = np.sqrt(np.mean(audio_data**2))
                        # Convert to percentage (0-100)
                        level = min(100, (rms / 32767.0) * 100)
                        self.audio_level_callback(level)
                        
                except Exception as e:
                    print(f"Error reading audio data: {e}")
                    break
            
            # Clean up
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"Error in recording thread: {e}")
            self.is_recording = False
    
    def get_recording_status(self):
        """Get current recording status"""
        return {
            'is_recording': self.is_recording,
            'recording_file': self.recording_file,
            'frames_recorded': len(self.frames)
        }
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.is_recording:
            self.stop_recording()
        
        if hasattr(self, 'audio'):
            self.audio.terminate()

def test_audio_recording():
    """Test function for audio recording"""
    recorder = AudioRecorder()
    
    try:
        # Show available devices
        devices = recorder.get_available_devices()
        print("Available audio input devices:")
        for device in devices:
            print(f"  {device['index']}: {device['name']} ({device['channels']} channels)")
        
        # Get default device
        default_device = recorder.get_default_device()
        if default_device:
            print(f"\nDefault device: {default_device['name']}")
        
        # Start recording
        print("\nStarting recording...")
        recording_file = recorder.start_recording()
        
        if recording_file:
            print(f"Recording to: {recording_file}")
            print("Recording for 5 seconds...")
            time.sleep(5)
            
            # Stop recording
            saved_file = recorder.stop_recording()
            if saved_file:
                print(f"Recording saved to: {saved_file}")
            else:
                print("Failed to save recording")
        else:
            print("Failed to start recording")
    
    except KeyboardInterrupt:
        print("\nStopping recording...")
        recorder.stop_recording()
    
    finally:
        recorder.cleanup()

if __name__ == "__main__":
    test_audio_recording()
