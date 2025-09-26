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
        self.is_paused = False
        self.recording_thread = None
        self.frames = []
        self.recording_file = None
        self.audio_level_callback = None
        
        # Audio settings
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1  # Mono
        self.rate = 16000   # 16kHz sample rate (optimal for Whisper)
        
        # For mixed recording
        self.mic_stream = None
        self.system_stream = None
        self.mic_frames = []
        self.system_frames = []
        
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
                    device_type = self._classify_device(device_info['name'])
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxInputChannels'],
                        'sample_rate': int(device_info['defaultSampleRate']),
                        'type': device_type
                    })
        except Exception as e:
            print(f"Error getting audio devices: {e}")
        return devices
    
    def _classify_device(self, device_name):
        """Classify device type based on name"""
        device_name_lower = device_name.lower()
        
        # System audio devices (stereo mix, what u hear, etc.)
        system_keywords = ['stereo mix', 'what u hear', 'speakers', 'headphones', 'output', 'loopback']
        if any(keyword in device_name_lower for keyword in system_keywords):
            return 'system'
        
        # Microphone devices
        mic_keywords = ['microphone', 'mic', 'input', 'capture']
        if any(keyword in device_name_lower for keyword in mic_keywords):
            return 'microphone'
        
        # Default to microphone if unclear
        return 'microphone'
    
    def get_system_audio_devices(self):
        """Get list of system audio devices (Stereo Mix, etc.)"""
        devices = self.get_available_devices()
        return [device for device in devices if device['type'] == 'system']
    
    def get_microphone_devices(self):
        """Get list of microphone devices"""
        devices = self.get_available_devices()
        return [device for device in devices if device['type'] == 'microphone']
    
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
    
    def start_recording(self, output_dir="recordings", device_index=None, format="wav", recording_mode="microphone"):
        """
        Start recording audio
        
        Args:
            output_dir (str): Directory to save recordings
            device_index (int): Audio device index (None for default)
            format (str): Output format ('wav' or 'mp3')
            recording_mode (str): Recording mode ('microphone', 'system', or 'both')
            
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
            mode_suffix = f"_{recording_mode}" if recording_mode != "microphone" else ""
            filename = f"recording{mode_suffix}_{timestamp}.{format}"
            self.recording_file = os.path.join(output_dir, filename)
            self.recording_format = format
            self.recording_mode = recording_mode
            
            # Auto-select device if not specified
            if device_index is None:
                device_index = self._get_auto_device(recording_mode)
                if device_index is None and device_index != "mixed":
                    print(f"No suitable device found for {recording_mode} recording")
                    return None
            
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
    
    def _get_auto_device(self, recording_mode):
        """Auto-select device based on recording mode"""
        print(f"Auto-selecting device for mode: {recording_mode}")
        
        if recording_mode == "system":
            # Look for system audio devices
            system_devices = self.get_system_audio_devices()
            print(f"Found {len(system_devices)} system devices")
            if system_devices:
                selected_device = system_devices[0]['index']
                print(f"Selected system device: {system_devices[0]['name']} (index {selected_device})")
                return selected_device
        elif recording_mode == "microphone":
            # Look for microphone devices
            mic_devices = self.get_microphone_devices()
            print(f"Found {len(mic_devices)} microphone devices")
            if mic_devices:
                selected_device = mic_devices[0]['index']
                print(f"Selected microphone device: {mic_devices[0]['name']} (index {selected_device})")
                return selected_device
        elif recording_mode == "both":
            # For mixed recording, we'll handle this specially
            print("Mixed recording mode - will use both microphone and system audio")
            return "mixed"
        
        # Fallback to default device
        default_device = self.get_default_device()
        if default_device:
            print(f"Using default device: {default_device['name']} (index {default_device['index']})")
            return default_device['index']
        
        print("No suitable device found!")
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
                print(f"Saving recording to: {self.recording_file}")
                print(f"Number of frames: {len(self.frames)}")
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(self.recording_file), exist_ok=True)
                
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
                print(f"Recording file: {self.recording_file}")
                print(f"Frames available: {len(self.frames) if self.frames else 0}")
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
            if device_index == "mixed":
                # Mixed recording mode - record from both microphone and system audio
                self._record_mixed_audio()
            else:
                # Single source recording
                self._record_single_source(device_index)
            
        except Exception as e:
            error_msg = str(e)
            if "Unanticipated host error" in error_msg:
                print(f"System audio device error: {error_msg}")
                print("This usually means Stereo Mix is not enabled or configured properly.")
                print("Please check SYSTEM_AUDIO_SETUP.md for instructions.")
            else:
                print(f"Error in recording thread: {e}")
            self.is_recording = False
    
    def _record_mixed_audio(self):
        """Record from both microphone and system audio simultaneously"""
        try:
            # Get microphone device
            mic_devices = self.get_microphone_devices()
            system_devices = self.get_system_audio_devices()
            
            if not mic_devices:
                raise Exception("No microphone devices found")
            if not system_devices:
                raise Exception("No system audio devices found")
            
            mic_device = mic_devices[0]['index']
            system_device = system_devices[0]['index']
            
            print(f"Opening microphone stream (device {mic_device})")
            self.mic_stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=mic_device,
                frames_per_buffer=self.chunk
            )
            
            print(f"Opening system audio stream (device {system_device})")
            self.system_stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=system_device,
                frames_per_buffer=self.chunk
            )
            
            # Initialize frame lists
            self.mic_frames = []
            self.system_frames = []
            
            print("Recording from both microphone and system audio...")
            
            # Record audio from both sources
            while self.is_recording:
                try:
                    # Check if recording is paused
                    if self.is_paused:
                        time.sleep(0.1)  # Sleep briefly when paused
                        continue
                    
                    # Read from both streams
                    mic_data = self.mic_stream.read(self.chunk, exception_on_overflow=False)
                    system_data = self.system_stream.read(self.chunk, exception_on_overflow=False)
                    
                    # Store frames separately
                    self.mic_frames.append(mic_data)
                    self.system_frames.append(system_data)
                    
                    # Mix the audio
                    mixed_data = self._mix_audio_data(mic_data, system_data)
                    self.frames.append(mixed_data)
                    
                    # Calculate audio level from mixed data
                    if self.audio_level_callback:
                        import numpy as np
                        audio_data = np.frombuffer(mixed_data, dtype=np.int16)
                        rms = np.sqrt(np.mean(audio_data**2))
                        level = min(100, (rms / 32767.0) * 100)
                        self.audio_level_callback(level)
                        
                except Exception as e:
                    print(f"Error reading mixed audio data: {e}")
                    break
            
            # Clean up streams
            if self.mic_stream:
                self.mic_stream.stop_stream()
                self.mic_stream.close()
            if self.system_stream:
                self.system_stream.stop_stream()
                self.system_stream.close()
                
        except Exception as e:
            print(f"Error in mixed recording: {e}")
            print("Falling back to microphone-only recording...")
            
            # Try to fallback to microphone only
            try:
                mic_devices = self.get_microphone_devices()
                if mic_devices:
                    mic_device = mic_devices[0]['index']
                    print(f"Starting fallback recording with microphone (device {mic_device})")
                    # Reset recording state for fallback
                    self.is_recording = True
                    self._record_single_source(mic_device)
                else:
                    print("No microphone devices available for fallback")
                    self.is_recording = False
            except Exception as fallback_error:
                print(f"Fallback recording also failed: {fallback_error}")
                self.is_recording = False
    
    def _record_single_source(self, device_index):
        """Record from a single audio source"""
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
                    # Check if recording is paused
                    if self.is_paused:
                        time.sleep(0.1)  # Sleep briefly when paused
                        continue
                    
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
            error_msg = str(e)
            if "Unanticipated host error" in error_msg and self.recording_mode == "system":
                print(f"System audio recording failed: {error_msg}")
                print("Falling back to microphone-only recording...")
                
                # Try to fallback to microphone only
                try:
                    mic_devices = self.get_microphone_devices()
                    if mic_devices:
                        mic_device = mic_devices[0]['index']
                        print(f"Starting fallback recording with microphone (device {mic_device})")
                        # Reset recording state for fallback
                        self.is_recording = True
                        self._record_single_source(mic_device)
                    else:
                        print("No microphone devices available for fallback")
                        self.is_recording = False
                except Exception as fallback_error:
                    print(f"Fallback recording also failed: {fallback_error}")
                    self.is_recording = False
            else:
                print(f"Error in single source recording: {e}")
                self.is_recording = False
    
    def _mix_audio_data(self, mic_data, system_data):
        """Mix microphone and system audio data"""
        try:
            import numpy as np
            
            # Convert bytes to numpy arrays
            mic_array = np.frombuffer(mic_data, dtype=np.int16)
            system_array = np.frombuffer(system_data, dtype=np.int16)
            
            # Mix the audio (simple addition with scaling to prevent clipping)
            mixed_array = (mic_array * 0.7 + system_array * 0.7).astype(np.int16)
            
            # Convert back to bytes
            return mixed_array.tobytes()
            
        except Exception as e:
            print(f"Error mixing audio: {e}")
            # Fallback to microphone only
            return mic_data
    
    def pause_recording(self):
        """Pause the current recording"""
        if self.is_recording and not self.is_paused:
            self.is_paused = True
            print("Recording paused")
            return True
        return False
    
    def resume_recording(self):
        """Resume the paused recording"""
        if self.is_recording and self.is_paused:
            self.is_paused = False
            print("Recording resumed")
            return True
        return False
    
    def get_recording_status(self):
        """Get current recording status"""
        return {
            'is_recording': self.is_recording,
            'is_paused': self.is_paused,
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
