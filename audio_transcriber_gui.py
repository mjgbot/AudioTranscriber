#!/usr/bin/env python3
"""
AudioTranscriber GUI - A user-friendly graphical interface for audio transcription
Powered by OpenAI Whisper
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
import whisper
from speaker_diarization import SpeakerDiarizer

class AudioTranscriberGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AudioTranscriber - Powered by OpenAI Whisper")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Variables
        self.audio_file_path = tk.StringVar()
        self.selected_model = tk.StringVar(value="base")
        self.selected_language = tk.StringVar()
        self.selected_task = tk.StringVar(value="transcribe")
        self.selected_output = tk.StringVar(value="txt")
        self.detect_speakers = tk.BooleanVar(value=False)
        self.is_transcribing = False
        
        # Available models
        self.models = [
            ("Tiny (Fastest, ~1GB VRAM)", "tiny"),
            ("Base (Balanced, ~1GB VRAM)", "base"),
            ("Small (Good accuracy, ~2GB VRAM)", "small"),
            ("Medium (High accuracy, ~5GB VRAM)", "medium"),
            ("Large (Best accuracy, ~10GB VRAM)", "large"),
            ("Turbo (Fast English-only, ~6GB VRAM)", "turbo")
        ]
        
        # Common languages
        self.languages = [
            ("Auto-detect", ""),
            ("English", "en"),
            ("Spanish", "es"),
            ("French", "fr"),
            ("German", "de"),
            ("Italian", "it"),
            ("Portuguese", "pt"),
            ("Russian", "ru"),
            ("Chinese", "zh"),
            ("Japanese", "ja"),
            ("Korean", "ko"),
            ("Arabic", "ar"),
            ("Dutch", "nl"),
            ("Polish", "pl"),
            ("Turkish", "tr"),
            ("Hindi", "hi")
        ]
        
        # Tasks
        self.tasks = [
            ("Transcribe", "transcribe"),
            ("Translate to English", "translate")
        ]
        
        # Output formats
        self.output_formats = [
            ("Plain Text (.txt)", "txt"),
            ("SRT Subtitles (.srt)", "srt"),
            ("WebVTT Subtitles (.vtt)", "vtt")
        ]
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="AudioTranscriber", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Powered by OpenAI Whisper", 
                                 font=("Arial", 10, "italic"))
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # File selection
        ttk.Label(main_frame, text="Audio File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(0, weight=1)
        
        self.file_entry = ttk.Entry(file_frame, textvariable=self.audio_file_path, state="readonly")
        self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=1)
        
        # Model selection
        ttk.Label(main_frame, text="Model:").grid(row=3, column=0, sticky=tk.W, pady=5)
        model_frame = ttk.Frame(main_frame)
        model_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.selected_model, 
                                       values=[model[0] for model in self.models], 
                                       state="readonly", width=40)
        self.model_combo.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Language selection
        ttk.Label(main_frame, text="Language:").grid(row=4, column=0, sticky=tk.W, pady=5)
        lang_frame = ttk.Frame(main_frame)
        lang_frame.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.language_combo = ttk.Combobox(lang_frame, textvariable=self.selected_language,
                                         values=[lang[0] for lang in self.languages],
                                         state="readonly", width=40)
        self.language_combo.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.language_combo.set("Auto-detect")
        
        # Task selection
        ttk.Label(main_frame, text="Task:").grid(row=5, column=0, sticky=tk.W, pady=5)
        task_frame = ttk.Frame(main_frame)
        task_frame.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.task_combo = ttk.Combobox(task_frame, textvariable=self.selected_task,
                                      values=[task[0] for task in self.tasks],
                                      state="readonly", width=40)
        self.task_combo.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Output format
        ttk.Label(main_frame, text="Output Format:").grid(row=6, column=0, sticky=tk.W, pady=5)
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=6, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.output_combo = ttk.Combobox(output_frame, textvariable=self.selected_output,
                                        values=[fmt[0] for fmt in self.output_formats],
                                        state="readonly", width=40)
        self.output_combo.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Speaker detection checkbox
        speaker_frame = ttk.Frame(main_frame)
        speaker_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.speaker_checkbox = ttk.Checkbutton(speaker_frame, text="Detect different speakers", 
                                              variable=self.detect_speakers)
        self.speaker_checkbox.grid(row=0, column=0, sticky=tk.W)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=3, pady=20)
        
        self.transcribe_button = ttk.Button(button_frame, text="Start Transcription", 
                                           command=self.start_transcription)
        self.transcribe_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear", 
                                      command=self.clear_all)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to transcribe", 
                                    font=("Arial", 10))
        self.status_label.grid(row=10, column=0, columnspan=3, pady=5)
        
        # Results area
        ttk.Label(main_frame, text="Transcription Results:", 
                font=("Arial", 12, "bold")).grid(row=11, column=0, columnspan=3, 
                                                sticky=tk.W, pady=(20, 5))
        
        self.results_text = scrolledtext.ScrolledText(main_frame, height=15, width=80)
        self.results_text.grid(row=12, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure grid weights for resizing
        main_frame.rowconfigure(12, weight=1)
        
    def browse_file(self):
        """Open file dialog to select audio file"""
        filetypes = [
            ("Audio files", "*.mp3 *.wav *.flac *.m4a *.mp4 *.avi *.mov *.mkv"),
            ("MP3 files", "*.mp3"),
            ("WAV files", "*.wav"),
            ("FLAC files", "*.flac"),
            ("M4A files", "*.m4a"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=filetypes
        )
        
        if filename:
            self.audio_file_path.set(filename)
            self.update_status(f"Selected: {os.path.basename(filename)}")
    
    def get_selected_values(self):
        """Get the actual values from the combo boxes"""
        model_index = self.model_combo.current()
        model_value = self.models[model_index][1] if model_index >= 0 else "base"
        
        lang_index = self.language_combo.current()
        lang_value = self.languages[lang_index][1] if lang_index >= 0 else ""
        
        task_index = self.task_combo.current()
        task_value = self.tasks[task_index][1] if task_index >= 0 else "transcribe"
        
        output_index = self.output_combo.current()
        output_value = self.output_formats[output_index][1] if output_index >= 0 else "txt"
        
        return model_value, lang_value, task_value, output_value
    
    def start_transcription(self):
        """Start the transcription process in a separate thread"""
        if self.is_transcribing:
            messagebox.showwarning("Warning", "Transcription is already in progress!")
            return
        
        if not self.audio_file_path.get():
            messagebox.showerror("Error", "Please select an audio file first!")
            return
        
        if not os.path.exists(self.audio_file_path.get()):
            messagebox.showerror("Error", "Selected file does not exist!")
            return
        
        # Disable controls during transcription
        self.is_transcribing = True
        self.transcribe_button.config(text="Transcribing...", state="disabled")
        self.progress_var.set(0)
        
        # Start transcription in separate thread
        thread = threading.Thread(target=self.transcribe_audio)
        thread.daemon = True
        thread.start()
    
    def transcribe_audio(self):
        """Perform the actual transcription"""
        try:
            audio_file = self.audio_file_path.get()
            model_value, lang_value, task_value, output_value = self.get_selected_values()
            detect_speakers = self.detect_speakers.get()
            
            self.update_status("Loading Whisper model...")
            self.progress_var.set(10)
            
            if detect_speakers:
                # Use speaker diarization
                self.update_status("Loading speaker diarization model...")
                diarizer = SpeakerDiarizer(model_value)
                result = diarizer.perform_diarization(audio_file)
            else:
                # Standard transcription
                import whisper
                model = whisper.load_model(model_value)
                
                self.update_status("Transcribing audio...")
                self.progress_var.set(30)
                
                # Perform transcription
                result = model.transcribe(
                    audio_file,
                    language=lang_value if lang_value else None,
                    task=task_value,
                    verbose=False
                )
            
            self.progress_var.set(80)
            self.update_status("Saving results...")
            
            # Save results
            output_file = self.save_transcription(result, audio_file, output_value)
            
            self.progress_var.set(100)
            self.update_status("Transcription completed!")
            
            # Display results in GUI
            self.root.after(0, self.display_results, result, output_file)
            
        except Exception as e:
            error_msg = f"Error during transcription: {str(e)}"
            self.root.after(0, self.show_error, error_msg)
        finally:
            # Re-enable controls
            self.root.after(0, self.transcription_finished)
    
    def save_transcription(self, result, audio_file_path, output_format):
        """Save transcription result to file"""
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
                    start_time = self.format_time(segment["start"])
                    end_time = self.format_time(segment["end"])
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{segment['text'].strip()}\n\n")
        
        elif output_format == "vtt":
            output_file = f"{base_name}_transcription.vtt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("WEBVTT\n\n")
                for segment in result["segments"]:
                    start_time = self.format_time_vtt(segment["start"])
                    end_time = self.format_time_vtt(segment["end"])
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{segment['text'].strip()}\n\n")
        
        return output_file
    
    def format_time(self, seconds):
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
    
    def display_results(self, result, output_file):
        """Display transcription results in the GUI"""
        self.results_text.delete(1.0, tk.END)
        
        # Check if speaker information is available
        has_speakers = any('speaker' in segment for segment in result.get('segments', []))
        
        # Display basic info
        info_text = f"Detected Language: {result.get('language', 'Unknown')}\n"
        info_text += f"Number of Segments: {len(result.get('segments', []))}\n"
        if result.get('segments'):
            info_text += f"Total Duration: {result['segments'][-1]['end']:.2f} seconds\n"
        
        if has_speakers:
            # Count unique speakers
            speakers = set(segment.get('speaker', 'Speaker 1') for segment in result['segments'])
            info_text += f"Detected Speakers: {len(speakers)} ({', '.join(sorted(speakers))})\n"
        
        info_text += f"Output File: {output_file}\n"
        info_text += "=" * 50 + "\n\n"
        
        # Display transcription text
        if has_speakers:
            # Display with speaker labels
            transcription_text = ""
            for segment in result["segments"]:
                speaker = segment.get('speaker', 'Speaker 1')
                start_time = self.format_time(segment["start"])
                end_time = self.format_time(segment["end"])
                text = segment['text'].strip()
                transcription_text += f"[{start_time} - {end_time}] {speaker}: {text}\n"
        else:
            # Standard display
            transcription_text = result["text"]
        
        self.results_text.insert(tk.END, info_text + transcription_text)
        
        messagebox.showinfo("Success", f"Transcription completed!\n\nOutput saved to: {output_file}")
    
    def show_error(self, error_msg):
        """Show error message"""
        messagebox.showerror("Error", error_msg)
        self.update_status("Error occurred")
    
    def transcription_finished(self):
        """Re-enable controls after transcription"""
        self.is_transcribing = False
        self.transcribe_button.config(text="Start Transcription", state="normal")
        self.progress_var.set(0)
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def clear_all(self):
        """Clear all fields and results"""
        self.audio_file_path.set("")
        self.results_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.update_status("Ready to transcribe")
        
        # Reset combo boxes to defaults
        self.model_combo.set("Base (Balanced, ~1GB VRAM)")
        self.language_combo.set("Auto-detect")
        self.task_combo.set("Transcribe")
        self.output_combo.set("Plain Text (.txt)")

def main():
    # Check if whisper is available
    try:
        import whisper
    except ImportError:
        messagebox.showerror("Error", 
                           "Whisper is not installed!\n\n"
                           "Please install it using:\n"
                           "pip install openai-whisper")
        return
    
    # Check if FFmpeg is available
    import subprocess
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        messagebox.showwarning("Warning", 
                             "FFmpeg is not found in PATH!\n\n"
                             "Audio processing may not work properly.\n"
                             "Please install FFmpeg and try again.")
    
    root = tk.Tk()
    app = AudioTranscriberGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
