#!/usr/bin/env python3
"""
Speaker Diarization Module for AudioTranscriber
Combines Whisper transcription with speaker detection
"""

import whisper
import torch
import numpy as np
from pyannote.audio import Pipeline
from pyannote.core import Segment
import librosa
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
import warnings
import os
import json
from pathlib import Path
from huggingface_hub import login, HfApi
warnings.filterwarnings("ignore")

class HuggingFaceAuth:
    """Handle Hugging Face authentication and token management"""
    
    def __init__(self):
        self.config_file = Path.home() / ".audiotranscriber" / "hf_config.json"
        self.config_file.parent.mkdir(exist_ok=True)
        self.token = None
        self.is_authenticated = False
    
    def save_token(self, token):
        """Save Hugging Face token to secure config file"""
        try:
            config = {"hf_token": token}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            self.token = token
            self.is_authenticated = True
            return True
        except Exception as e:
            print(f"Error saving token: {e}")
            return False
    
    def load_token(self):
        """Load Hugging Face token from config file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.token = config.get("hf_token")
                    if self.token:
                        self.is_authenticated = True
                        return True
        except Exception as e:
            print(f"Error loading token: {e}")
        return False
    
    def authenticate(self, token=None):
        """Authenticate with Hugging Face"""
        if token:
            self.token = token
        
        if not self.token:
            if not self.load_token():
                return False
        
        try:
            # Test authentication by trying to access HF API
            api = HfApi()
            user_info = api.whoami(token=self.token)
            print(f"Successfully authenticated as: {user_info['name']}")
            self.is_authenticated = True
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            self.is_authenticated = False
            return False
    
    def login_to_hf(self, token=None):
        """Login to Hugging Face Hub"""
        if token:
            self.token = token
        
        if not self.token:
            if not self.load_token():
                return False
        
        try:
            login(token=self.token)
            self.is_authenticated = True
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            self.is_authenticated = False
            return False
    
    def clear_token(self):
        """Clear stored token"""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
            self.token = None
            self.is_authenticated = False
            return True
        except Exception as e:
            print(f"Error clearing token: {e}")
            return False

class SpeakerDiarizer:
    def __init__(self, model_size="base", hf_token=None):
        """
        Initialize the speaker diarization system
        
        Args:
            model_size (str): Whisper model size
            hf_token (str): Hugging Face token for authentication
        """
        self.model_size = model_size
        self.whisper_model = None
        self.diarization_pipeline = None
        self.hf_auth = HuggingFaceAuth()
        
        # Handle Hugging Face authentication
        if hf_token:
            self.hf_auth.save_token(hf_token)
            self.hf_auth.login_to_hf(hf_token)
        else:
            # Try to load existing token
            self.hf_auth.load_token()
            if self.hf_auth.is_authenticated:
                self.hf_auth.login_to_hf()
        
    def load_models(self):
        """Load Whisper and speaker diarization models"""
        print("Loading Whisper model...")
        self.whisper_model = whisper.load_model(self.model_size)
        
        print("Loading speaker diarization pipeline...")
        try:
            # Check if we have Hugging Face authentication
            if self.hf_auth.is_authenticated:
                print("Using Hugging Face authentication for pyannote pipeline...")
                self.diarization_pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=self.hf_auth.token
                )
                print("Successfully loaded pyannote speaker diarization pipeline!")
            else:
                print("Note: pyannote pipeline requires Hugging Face authentication.")
                print("Using fallback speaker detection method...")
                self.diarization_pipeline = None
        except Exception as e:
            print(f"Warning: Could not load pyannote pipeline: {e}")
            print("Falling back to simple speaker detection...")
            self.diarization_pipeline = None
    
    def set_hf_token(self, token):
        """Set Hugging Face token and reinitialize authentication"""
        if self.hf_auth.save_token(token):
            if self.hf_auth.login_to_hf(token):
                print("Hugging Face authentication successful!")
                return True
            else:
                print("Failed to authenticate with Hugging Face")
                return False
        else:
            print("Failed to save Hugging Face token")
            return False
    
    def get_auth_status(self):
        """Get current authentication status"""
        return {
            "is_authenticated": self.hf_auth.is_authenticated,
            "has_token": self.hf_auth.token is not None,
            "can_use_pyannote": self.diarization_pipeline is not None
        }
    
    def extract_speaker_embeddings(self, audio_path, segments):
        """
        Extract speaker embeddings for each segment using a simple approach
        
        Args:
            audio_path (str): Path to audio file
            segments (list): List of segments with timestamps
            
        Returns:
            list: Speaker labels for each segment
        """
        try:
            # Load audio
            audio, sr = librosa.load(audio_path, sr=16000)
            
            # Extract features for each segment
            embeddings = []
            for segment in segments:
                start_time = segment['start']
                end_time = segment['end']
                
                # Convert to sample indices
                start_sample = int(start_time * sr)
                end_sample = int(end_time * sr)
                
                # Extract audio segment
                segment_audio = audio[start_sample:end_sample]
                
                # Extract MFCC features as simple speaker embedding
                mfcc = librosa.feature.mfcc(y=segment_audio, sr=sr, n_mfcc=13)
                mfcc_mean = np.mean(mfcc, axis=1)
                embeddings.append(mfcc_mean)
            
            # Cluster embeddings to identify speakers
            if len(embeddings) > 1:
                embeddings_array = np.array(embeddings)
                
                # Use cosine similarity for clustering
                similarity_matrix = cosine_similarity(embeddings_array)
                distance_matrix = 1 - similarity_matrix
                
                # Perform clustering
                n_speakers = min(5, len(segments))  # Assume max 5 speakers
                clustering = AgglomerativeClustering(
                    n_clusters=n_speakers,
                    metric='precomputed',
                    linkage='average'
                )
                
                speaker_labels = clustering.fit_predict(distance_matrix)
                
                # Rename speakers to Speaker 1, Speaker 2, etc.
                unique_labels = np.unique(speaker_labels)
                speaker_mapping = {label: f"Speaker {i+1}" for i, label in enumerate(unique_labels)}
                speaker_names = [speaker_mapping[label] for label in speaker_labels]
                
                return speaker_names
            else:
                return ["Speaker 1"]
                
        except Exception as e:
            print(f"Error in speaker embedding extraction: {e}")
            return ["Speaker 1"] * len(segments)
    
    def perform_diarization(self, audio_path):
        """
        Perform speaker diarization on audio file
        
        Args:
            audio_path (str): Path to audio file
            
        Returns:
            dict: Transcription result with speaker information
        """
        if not self.whisper_model:
            self.load_models()
        
        print("Transcribing audio with Whisper...")
        # Transcribe with Whisper
        result = self.whisper_model.transcribe(audio_path, verbose=False)
        
        print("Detecting speakers...")
        # Extract speaker information
        if self.diarization_pipeline:
            # Use pyannote for advanced diarization
            diarization = self.diarization_pipeline(audio_path)
            
            # Align Whisper segments with speaker segments
            speaker_segments = []
            for segment in result['segments']:
                segment_start = segment['start']
                segment_end = segment['end']
                
                # Find overlapping speaker segments
                speakers_in_segment = []
                for turn, _, speaker in diarization.itertracks(yield_label=True):
                    if turn.start <= segment_end and turn.end >= segment_start:
                        speakers_in_segment.append(speaker)
                
                # Assign speaker (use most common speaker in segment)
                if speakers_in_segment:
                    speaker = max(set(speakers_in_segment), key=speakers_in_segment.count)
                    speaker_segments.append(speaker)
                else:
                    speaker_segments.append("Speaker 1")
        else:
            # Use simple speaker detection
            speaker_segments = self.extract_speaker_embeddings(audio_path, result['segments'])
        
        # Add speaker information to result
        for i, segment in enumerate(result['segments']):
            if i < len(speaker_segments):
                segment['speaker'] = speaker_segments[i]
            else:
                segment['speaker'] = "Speaker 1"
        
        return result
    
    def format_transcription_with_speakers(self, result, output_format="txt"):
        """
        Format transcription with speaker labels
        
        Args:
            result (dict): Whisper result with speaker information
            output_format (str): Output format (txt, srt, vtt)
            
        Returns:
            str: Formatted transcription
        """
        if output_format == "txt":
            formatted_text = ""
            for segment in result['segments']:
                speaker = segment.get('speaker', 'Speaker 1')
                start_time = self.format_time(segment['start'])
                end_time = self.format_time(segment['end'])
                text = segment['text'].strip()
                
                formatted_text += f"[{start_time} - {end_time}] {speaker}: {text}\n"
            
            return formatted_text
        
        elif output_format == "srt":
            srt_text = ""
            for i, segment in enumerate(result['segments'], 1):
                speaker = segment.get('speaker', 'Speaker 1')
                start_time = self.format_time_srt(segment['start'])
                end_time = self.format_time_srt(segment['end'])
                text = segment['text'].strip()
                
                srt_text += f"{i}\n"
                srt_text += f"{start_time} --> {end_time}\n"
                srt_text += f"{speaker}: {text}\n\n"
            
            return srt_text
        
        elif output_format == "vtt":
            vtt_text = "WEBVTT\n\n"
            for segment in result['segments']:
                speaker = segment.get('speaker', 'Speaker 1')
                start_time = self.format_time_vtt(segment['start'])
                end_time = self.format_time_vtt(segment['end'])
                text = segment['text'].strip()
                
                vtt_text += f"{start_time} --> {end_time}\n"
                vtt_text += f"{speaker}: {text}\n\n"
            
            return vtt_text
    
    def format_time(self, seconds):
        """Format time in seconds to HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def format_time_srt(self, seconds):
        """Format time in seconds to SRT format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def format_time_vtt(self, seconds):
        """Format time in seconds to VTT format (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millisecs:03d}"

def test_speaker_diarization():
    """Test function for speaker diarization"""
    diarizer = SpeakerDiarizer("base")
    
    # Test with a sample audio file (replace with actual file)
    audio_path = "test_audio.wav"
    
    if os.path.exists(audio_path):
        result = diarizer.perform_diarization(audio_path)
        
        # Print results
        print("Speaker Diarization Results:")
        print("=" * 50)
        for segment in result['segments']:
            speaker = segment.get('speaker', 'Speaker 1')
            start_time = diarizer.format_time(segment['start'])
            end_time = diarizer.format_time(segment['end'])
            text = segment['text'].strip()
            print(f"[{start_time} - {end_time}] {speaker}: {text}")
    else:
        print("Test audio file not found. Please provide a valid audio file.")

if __name__ == "__main__":
    import os
    test_speaker_diarization()
