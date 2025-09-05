#!/usr/bin/env python3
"""
AudioTranscriber GUI - Modern, Clean Interface
A modern GUI for audio transcription using OpenAI Whisper with speaker diarization.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import platform
import subprocess
from pathlib import Path

# Try to import audio recording functionality
try:
    from audio_recorder import AudioRecorder
    AUDIO_RECORDING_AVAILABLE = True
except ImportError:
    AUDIO_RECORDING_AVAILABLE = False

# Try to import speaker diarization
try:
    from speaker_diarization import transcribe_with_speaker_diarization
    SPEAKER_DIARIZATION_AVAILABLE = True
except ImportError:
    SPEAKER_DIARIZATION_AVAILABLE = False


class AudioTranscriberGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AudioTranscriber - AI-Powered Transcription")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Variables
        self.audio_file_path = tk.StringVar()
        self.recording_format = tk.StringVar(value="wav")
        self.hf_token = tk.StringVar()
        self.detect_speakers = tk.BooleanVar()
        self.is_recording = False
        self.is_transcribing = False
        
        # Model options
        self.model_options = [
            ("Tiny (Fastest, ~1GB VRAM)", "tiny"),
            ("Base (Balanced, ~1GB VRAM)", "base"),
            ("Small (Better, ~2GB VRAM)", "small"),
            ("Medium (Good, ~5GB VRAM)", "medium"),
            ("Large (Best, ~10GB VRAM)", "large")
        ]
        
        # Language options
        self.language_options = [
            ("Auto-detect", None),
            ("English", "en"),
            ("Spanish", "es"),
            ("French", "fr"),
            ("German", "de"),
            ("Italian", "it"),
            ("Portuguese", "pt"),
            ("Chinese", "zh"),
            ("Japanese", "ja")
        ]
        
        # Task options
        self.task_options = [
            ("Transcribe", "transcribe"),
            ("Translate to English", "translate")
        ]
        
        # Output format options
        self.output_format_options = [
            ("Plain Text (.txt)", "txt"),
            ("SRT Subtitles (.srt)", "srt"),
            ("WebVTT Subtitles (.vtt)", "vtt")
        ]
        
        self.setup_ui()
        
    def setup_ui(self):
        # Configure modern styling with colors
        style = ttk.Style()
        style.theme_use('clam')
        
        # Modern color scheme
        colors = {
            'primary': '#2563eb',      # Modern Blue
            'secondary': '#10b981',    # Modern Green
            'accent': '#ef4444',       # Modern Red
            'warning': '#f59e0b',      # Modern Orange
            'success': '#059669',      # Modern Dark Green
            'background': '#f8fafc',   # Light Gray Background
            'surface': '#ffffff',      # White Cards
            'text': '#1e293b',         # Dark Text
            'text_light': '#64748b',   # Light Text
            'border': '#e2e8f0',       # Light Border
            'hover': '#f1f5f9'         # Hover Background
        }
        
        # Configure modern button styles
        style.configure('Primary.TButton', 
                       font=('Segoe UI', 11, 'bold'),
                       foreground='white',
                       background=colors['primary'],
                       padding=(20, 12),
                       borderwidth=0,
                       focuscolor='none')
        
        style.configure('Success.TButton', 
                       font=('Segoe UI', 10, 'bold'),
                       foreground='white',
                       background=colors['success'],
                       padding=(16, 10),
                       borderwidth=0,
                       focuscolor='none')
        
        style.configure('Warning.TButton', 
                       font=('Segoe UI', 10, 'bold'),
                       foreground='white',
                       background=colors['warning'],
                       padding=(16, 10),
                       borderwidth=0,
                       focuscolor='none')
        
        style.configure('Accent.TButton', 
                       font=('Segoe UI', 10, 'bold'),
                       foreground='white',
                       background=colors['accent'],
                       padding=(16, 10),
                       borderwidth=0,
                       focuscolor='none')
        
        # Configure button hover effects
        style.map('Primary.TButton',
                 background=[('active', '#1d4ed8')])
        
        style.map('Success.TButton',
                 background=[('active', '#047857')])
        
        style.map('Warning.TButton',
                 background=[('active', '#d97706')])
        
        style.map('Accent.TButton',
                 background=[('active', '#dc2626')])
        
        # Set main window background
        self.root.configure(bg=colors['background'])
        
        # Create menu bar
        menubar = tk.Menu(self.root, tearoff=0)
        self.root.config(menu=menubar)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Hugging Face Authentication", command=self.open_hf_settings)
        
        # Main container with padding
        main_container = tk.Frame(self.root, bg=colors['background'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header section
        header_frame = tk.Frame(main_container, bg=colors['background'])
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Title
        title_label = tk.Label(header_frame, text="AudioTranscriber", 
                             font=('Segoe UI', 28, 'bold'), 
                             fg=colors['primary'], bg=colors['background'])
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(header_frame, text="Transform audio into text with AI-powered transcription", 
                                 font=('Segoe UI', 14), 
                                 fg=colors['text_light'], bg=colors['background'])
        subtitle_label.pack(pady=(5, 0))
        
        # Create main workflow cards
        self.create_workflow_cards(main_container, colors)
    
    def create_workflow_cards(self, parent, colors):
        """Create modern workflow cards for the UI"""
        
        # Step 1: Audio Input Card
        self.create_audio_input_card(parent, colors)
        
        # Step 2: Transcription Settings Card  
        self.create_settings_card(parent, colors)
        
        # Step 3: Results Card
        self.create_results_card(parent, colors)
    
    def create_audio_input_card(self, parent, colors):
        """Create the audio input card"""
        # Card container
        card_frame = tk.Frame(parent, bg=colors['surface'], relief='flat', bd=0)
        card_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Add subtle shadow effect with border
        shadow_frame = tk.Frame(parent, bg=colors['border'], height=2)
        shadow_frame.pack(fill=tk.X, pady=(0, 18))
        
        # Card content
        content_frame = tk.Frame(card_frame, bg=colors['surface'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Card title
        title_frame = tk.Frame(content_frame, bg=colors['surface'])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(title_frame, text="🎤 Audio Input", 
                font=('Segoe UI', 16, 'bold'), 
                fg=colors['text'], bg=colors['surface']).pack(side=tk.LEFT)
        
        # Input options
        input_frame = tk.Frame(content_frame, bg=colors['surface'])
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Option 1: Record Audio
        record_frame = tk.Frame(input_frame, bg=colors['surface'])
        record_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(record_frame, text="Record new audio:", 
                font=('Segoe UI', 12, 'bold'), 
                fg=colors['text'], bg=colors['surface']).pack(anchor=tk.W)
        
        record_controls = tk.Frame(record_frame, bg=colors['surface'])
        record_controls.pack(fill=tk.X, pady=(10, 0))
        
        if AUDIO_RECORDING_AVAILABLE:
            # Format selection
            format_frame = tk.Frame(record_controls, bg=colors['surface'])
            format_frame.pack(side=tk.LEFT, padx=(0, 20))
            
            tk.Label(format_frame, text="Format:", 
                    font=('Segoe UI', 10), 
                    fg=colors['text'], bg=colors['surface']).pack(side=tk.LEFT, padx=(0, 8))
            
            format_options = ["WAV", "MP3"]
            format_var = tk.StringVar(value=self.recording_format.get().upper())
            format_dropdown = tk.OptionMenu(format_frame, format_var, *format_options, 
                                          command=lambda x: self.recording_format.set(x.lower()))
            format_dropdown.config(bg=colors['surface'], fg=colors['text'], 
                                 activebackground=colors['primary'], activeforeground='white',
                                 relief='solid', bd=1, width=8)
            format_dropdown.pack(side=tk.LEFT)
            
            # Recording buttons
            button_frame = tk.Frame(record_controls, bg=colors['surface'])
            button_frame.pack(side=tk.LEFT, padx=(0, 20))
            
            self.record_button = ttk.Button(button_frame, text="🎤 Start Recording", 
                                           command=self.start_recording, style='Success.TButton')
            self.record_button.pack(side=tk.LEFT, padx=(0, 10))
            
            self.stop_record_button = ttk.Button(button_frame, text="⏹️ Stop", 
                                                 command=self.stop_recording, state="disabled", style='Accent.TButton')
            self.stop_record_button.pack(side=tk.LEFT)
            
            # Status
            self.record_status_label = tk.Label(record_controls, text="Ready to record", 
                                               font=('Segoe UI', 10), 
                                               fg=colors['text_light'], bg=colors['surface'])
            self.record_status_label.pack(side=tk.LEFT, padx=(20, 0))
            
            # Audio level meter
            level_frame = tk.Frame(record_controls, bg=colors['surface'])
            level_frame.pack(side=tk.RIGHT)
            
            tk.Label(level_frame, text="Level:", 
                    font=('Segoe UI', 9), 
                    fg=colors['text_light'], bg=colors['surface']).pack(side=tk.LEFT, padx=(0, 5))
            
            self.audio_level_canvas = tk.Canvas(level_frame, width=80, height=16, 
                                               bg=colors['surface'], highlightthickness=0)
            self.audio_level_canvas.pack(side=tk.LEFT, padx=(0, 5))
            
            # Draw the progress bar background
            self.audio_level_canvas.create_rectangle(0, 0, 80, 16, fill=colors['surface'], outline=colors['border'])
            self.audio_level_progress = self.audio_level_canvas.create_rectangle(0, 0, 0, 16, fill=colors['primary'], outline="")
            
            self.audio_level_label = tk.Label(level_frame, text="0%", 
                                             font=('Segoe UI', 9), 
                                             fg=colors['text_light'], bg=colors['surface'])
            self.audio_level_label.pack(side=tk.LEFT)
        else:
            tk.Label(record_frame, text="Audio recording not available. Install PyAudio to enable recording.", 
                    font=('Segoe UI', 10), 
                    fg=colors['accent'], bg=colors['surface']).pack(anchor=tk.W, pady=(10, 0))
        
        # Option 2: Upload File
        upload_frame = tk.Frame(input_frame, bg=colors['surface'])
        upload_frame.pack(fill=tk.X)
        
        tk.Label(upload_frame, text="Or upload audio file:", 
                font=('Segoe UI', 12, 'bold'), 
                fg=colors['text'], bg=colors['surface']).pack(anchor=tk.W)
        
        file_frame = tk.Frame(upload_frame, bg=colors['surface'])
        file_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.audio_file_entry = tk.Entry(file_frame, textvariable=self.audio_file_path, state="readonly", 
                                       bg=colors['surface'], fg=colors['text'], 
                                       font=('Segoe UI', 10), relief='solid', bd=1)
        self.audio_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(file_frame, text="📁 Browse", command=self.browse_file, style='Warning.TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(file_frame, text="🗑️ Clear", command=self.clear_audio_file, style='Accent.TButton').pack(side=tk.LEFT)
    
    def create_settings_card(self, parent, colors):
        """Create the transcription settings card"""
        # Card container
        card_frame = tk.Frame(parent, bg=colors['surface'], relief='flat', bd=0)
        card_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Add subtle shadow effect with border
        shadow_frame = tk.Frame(parent, bg=colors['border'], height=2)
        shadow_frame.pack(fill=tk.X, pady=(0, 18))
        
        # Card content
        content_frame = tk.Frame(card_frame, bg=colors['surface'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Card title
        title_frame = tk.Frame(content_frame, bg=colors['surface'])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(title_frame, text="⚙️ Transcription Settings", 
                font=('Segoe UI', 16, 'bold'), 
                fg=colors['text'], bg=colors['surface']).pack(side=tk.LEFT)
        
        # Settings grid
        settings_frame = tk.Frame(content_frame, bg=colors['surface'])
        settings_frame.pack(fill=tk.X)
        
        # Row 1: Model and Language
        row1 = tk.Frame(settings_frame, bg=colors['surface'])
        row1.pack(fill=tk.X, pady=(0, 15))
        
        # Model selection
        model_frame = tk.Frame(row1, bg=colors['surface'])
        model_frame.pack(side=tk.LEFT, padx=(0, 30))
        
        tk.Label(model_frame, text="Model:", 
                font=('Segoe UI', 11, 'bold'), 
                fg=colors['text'], bg=colors['surface']).pack(anchor=tk.W)
        
        model_options = ["Tiny (Fastest)", "Base (Balanced)", "Small (Better)", "Medium (Good)", "Large (Best)"]
        model_var = tk.StringVar(value="Base (Balanced)")
        model_dropdown = tk.OptionMenu(model_frame, model_var, *model_options)
        model_dropdown.config(bg=colors['surface'], fg=colors['text'], 
                             activebackground=colors['primary'], activeforeground='white',
                             relief='solid', bd=1, width=15)
        model_dropdown.pack(anchor=tk.W, pady=(5, 0))
        
        # Language selection
        lang_frame = tk.Frame(row1, bg=colors['surface'])
        lang_frame.pack(side=tk.LEFT, padx=(0, 30))
        
        tk.Label(lang_frame, text="Language:", 
                font=('Segoe UI', 11, 'bold'), 
                fg=colors['text'], bg=colors['surface']).pack(anchor=tk.W)
        
        lang_options = ["Auto-detect", "English", "Spanish", "French", "German", "Italian", "Portuguese", "Chinese", "Japanese"]
        lang_var = tk.StringVar(value="Auto-detect")
        lang_dropdown = tk.OptionMenu(lang_frame, lang_var, *lang_options)
        lang_dropdown.config(bg=colors['surface'], fg=colors['text'], 
                            activebackground=colors['primary'], activeforeground='white',
                            relief='solid', bd=1, width=12)
        lang_dropdown.pack(anchor=tk.W, pady=(5, 0))
        
        # Output format
        output_frame = tk.Frame(row1, bg=colors['surface'])
        output_frame.pack(side=tk.LEFT)
        
        tk.Label(output_frame, text="Output:", 
                font=('Segoe UI', 11, 'bold'), 
                fg=colors['text'], bg=colors['surface']).pack(anchor=tk.W)
        
        output_options = ["Plain Text", "SRT Subtitles", "WebVTT Subtitles"]
        output_var = tk.StringVar(value="Plain Text")
        output_dropdown = tk.OptionMenu(output_frame, output_var, *output_options)
        output_dropdown.config(bg=colors['surface'], fg=colors['text'], 
                              activebackground=colors['primary'], activeforeground='white',
                              relief='solid', bd=1, width=12)
        output_dropdown.pack(anchor=tk.W, pady=(5, 0))
        
        # Row 2: Advanced options
        row2 = tk.Frame(settings_frame, bg=colors['surface'])
        row2.pack(fill=tk.X, pady=(15, 0))
        
        # Speaker detection
        speaker_frame = tk.Frame(row2, bg=colors['surface'])
        speaker_frame.pack(side=tk.LEFT, padx=(0, 30))
        
        self.speaker_checkbox = tk.Checkbutton(speaker_frame, text="Detect different speakers", 
                                              variable=self.detect_speakers,
                                              font=('Segoe UI', 10),
                                              fg=colors['text'], bg=colors['surface'],
                                              activebackground=colors['surface'],
                                              selectcolor=colors['primary'])
        self.speaker_checkbox.pack(anchor=tk.W)
        
        # View transcriptions button
        ttk.Button(row2, text="📄 View Transcriptions", 
                  command=self.view_transcriptions, style='Warning.TButton').pack(side=tk.LEFT, padx=(20, 0))
        
        # Main action button
        action_frame = tk.Frame(content_frame, bg=colors['surface'])
        action_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.transcribe_button = ttk.Button(action_frame, text="🚀 Start Transcription", 
                                           command=self.start_transcription, style='Primary.TButton')
        self.transcribe_button.pack(side=tk.LEFT)
        
        self.clear_button = ttk.Button(action_frame, text="🧹 Clear All", 
                                      command=self.clear_all, style='Accent.TButton')
        self.clear_button.pack(side=tk.LEFT, padx=(15, 0))
    
    def create_results_card(self, parent, colors):
        """Create the results card"""
        # Card container
        card_frame = tk.Frame(parent, bg=colors['surface'], relief='flat', bd=0)
        card_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Add subtle shadow effect with border
        shadow_frame = tk.Frame(parent, bg=colors['border'], height=2)
        shadow_frame.pack(fill=tk.X, pady=(0, 18))
        
        # Card content
        content_frame = tk.Frame(card_frame, bg=colors['surface'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Card title
        title_frame = tk.Frame(content_frame, bg=colors['surface'])
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(title_frame, text="📝 Transcription Results", 
                font=('Segoe UI', 16, 'bold'), 
                fg=colors['text'], bg=colors['surface']).pack(side=tk.LEFT)
        
        # Progress bar
        progress_frame = tk.Frame(content_frame, bg=colors['surface'])
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_var = tk.DoubleVar()
        
        # Create modern progress bar using Canvas
        self.progress_canvas = tk.Canvas(progress_frame, width=400, height=8, 
                                        bg=colors['surface'], highlightthickness=0)
        self.progress_canvas.pack(fill=tk.X)
        
        # Draw the progress bar background
        self.progress_canvas.create_rectangle(0, 0, 400, 8, fill=colors['border'], outline="")
        self.progress_fill = self.progress_canvas.create_rectangle(0, 0, 0, 8, fill=colors['primary'], outline="")
        
        # Status label
        self.status_label = tk.Label(content_frame, text="Ready to transcribe", 
                                    font=('Segoe UI', 11), 
                                    fg=colors['text_light'], bg=colors['surface'])
        self.status_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(content_frame, height=12, width=80,
                                                     font=('Segoe UI', 10),
                                                     bg=colors['surface'], fg=colors['text'],
                                                     relief='solid', bd=1,
                                                     wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for resizing
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Initialize audio recorder if available
        if AUDIO_RECORDING_AVAILABLE:
            self.audio_recorder = AudioRecorder()
            self.audio_recorder.set_audio_level_callback(self.update_audio_level)
        else:
            self.audio_recorder = None
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_var.set(value)
        if hasattr(self, 'progress_canvas') and hasattr(self, 'progress_fill'):
            width = int((value / 100.0) * 400)
            self.progress_canvas.coords(self.progress_fill, 0, 0, width, 8)
    
    def update_audio_level(self, level):
        """Update the audio level display"""
        if hasattr(self, 'audio_level_canvas') and hasattr(self, 'audio_level_progress'):
            self.root.after(0, self._update_audio_level_ui, level)
    
    def _update_audio_level_ui(self, level):
        """Update audio level UI elements (called from main thread)"""
        try:
            if hasattr(self, 'audio_level_canvas') and hasattr(self, 'audio_level_progress'):
                # Update canvas-based progress bar
                width = int((level / 100.0) * 80)
                self.audio_level_canvas.coords(self.audio_level_progress, 0, 0, width, 16)
            self.audio_level_label.config(text=f"{level:.1f}%")
        except:
            pass  # Ignore errors if widgets don't exist yet
    
    def start_recording(self):
        """Start recording audio from microphone"""
        if not AUDIO_RECORDING_AVAILABLE:
            messagebox.showerror("Error", "Audio recording not available. Please install PyAudio:\n\npip install pyaudio")
            return
        
        if self.is_recording:
            messagebox.showwarning("Warning", "Recording is already in progress!")
            return
        
        try:
            # Start recording
            self.is_recording = True
            self.record_button.config(state="disabled")
            self.stop_record_button.config(state="normal")
            self.record_status_label.config(text="Recording...")
            self.update_status("Recording started")
            
            # Start recording in a separate thread
            recording_thread = threading.Thread(target=self._record_audio_thread)
            recording_thread.daemon = True
            recording_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start recording: {str(e)}")
            self.is_recording = False
            self.record_button.config(state="normal")
            self.stop_record_button.config(state="disabled")
    
    def _record_audio_thread(self):
        """Record audio in a separate thread"""
        try:
            # Start recording
            saved_file = self.audio_recorder.start_recording(
                output_dir="recordings", 
                format=self.recording_format.get()
            )
            
            # Update UI in main thread
            self.root.after(0, self._recording_complete, saved_file)
            
        except Exception as e:
            # Update UI in main thread
            self.root.after(0, self._recording_error, str(e))
    
    def _recording_complete(self, saved_file):
        """Handle recording completion in main thread"""
        if saved_file:
            self.is_recording = False
            self.record_button.config(state="normal")
            self.stop_record_button.config(state="disabled")
            self.record_status_label.config(text="Recording saved")
            self.update_status("Recording completed")
            
            # Reset audio level display
            if hasattr(self, 'audio_level_canvas') and hasattr(self, 'audio_level_progress'):
                self.audio_level_canvas.coords(self.audio_level_progress, 0, 0, 0, 16)
            if hasattr(self, 'audio_level_label'):
                self.audio_level_label.config(text="0%")
            
            # Update the file path to the saved recording
            self.audio_file_path.set(saved_file)
            
            messagebox.showinfo("Recording Complete", 
                              f"Recording saved successfully!\n\nFile: {saved_file}")
        else:
            self._recording_error("Failed to save recording")
    
    def _recording_error(self, error_message):
        """Handle recording error in main thread"""
        self.is_recording = False
        self.record_button.config(state="normal")
        self.stop_record_button.config(state="disabled")
        self.record_status_label.config(text="Recording failed")
        self.update_status("Recording failed")
        messagebox.showerror("Recording Error", f"Recording failed: {error_message}")
    
    def stop_recording(self):
        """Stop recording audio"""
        if not self.is_recording:
            return
        
        try:
            # Stop recording
            saved_file = self.audio_recorder.stop_recording()
            
            if saved_file:
                self.is_recording = False
                self.record_button.config(state="normal")
                self.stop_record_button.config(state="disabled")
                self.record_status_label.config(text="Recording saved")
                self.update_status("Recording completed")
                
                # Reset audio level display
                if hasattr(self, 'audio_level_canvas') and hasattr(self, 'audio_level_progress'):
                    self.audio_level_canvas.coords(self.audio_level_progress, 0, 0, 0, 16)
                if hasattr(self, 'audio_level_label'):
                    self.audio_level_label.config(text="0%")
                
                # Update the file path to the saved recording
                self.audio_file_path.set(saved_file)
                
                messagebox.showinfo("Recording Complete", 
                                  f"Recording saved successfully!\n\nFile: {saved_file}")
            else:
                messagebox.showerror("Error", "Failed to save recording")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop recording: {str(e)}")
            self.is_recording = False
            self.record_button.config(state="normal")
            self.stop_record_button.config(state="disabled")
    
    def browse_file(self):
        """Browse for audio file"""
        filetypes = [
            ("Audio files", "*.wav *.mp3 *.m4a *.flac *.ogg"),
            ("WAV files", "*.wav"),
            ("MP3 files", "*.mp3"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=filetypes
        )
        
        if filename:
            self.audio_file_path.set(filename)
    
    def clear_audio_file(self):
        """Clear the selected audio file"""
        self.audio_file_path.set("")
    
    def view_transcriptions(self):
        """Open the Transcriptions folder"""
        transcriptions_dir = Path("Transcriptions")
        if transcriptions_dir.exists():
            if platform.system() == "Windows":
                os.startfile(str(transcriptions_dir))
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(transcriptions_dir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(transcriptions_dir)])
        else:
            messagebox.showinfo("No Transcriptions", "No transcriptions folder found. Create some transcriptions first!")
    
    def open_hf_settings(self):
        """Open Hugging Face settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Hugging Face Authentication Settings")
        settings_window.geometry("500x300")
        settings_window.resizable(False, False)
        
        # Center the window
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Main frame
        main_frame = tk.Frame(settings_window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Hugging Face Authentication", 
                              font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_text = """To use speaker diarization features, you need a Hugging Face token.
        
1. Go to https://huggingface.co/settings/tokens
2. Create a new token with 'Read' access
3. Paste the token below"""
        
        desc_label = tk.Label(main_frame, text=desc_text, 
                             font=('Segoe UI', 10), justify=tk.LEFT)
        desc_label.pack(pady=(0, 20))
        
        # Token input
        token_frame = tk.Frame(main_frame)
        token_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(token_frame, text="Token:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
        
        token_entry = tk.Entry(token_frame, textvariable=self.hf_token, 
                             font=('Segoe UI', 10), show="*", width=50)
        token_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(button_frame, text="Save", command=lambda: self.save_hf_token(settings_window),
                 font=('Segoe UI', 10), bg='#4CAF50', fg='white', padx=20).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(button_frame, text="Clear", command=lambda: self.clear_hf_token(settings_window),
                 font=('Segoe UI', 10), bg='#f44336', fg='white', padx=20).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(button_frame, text="Close", command=settings_window.destroy,
                 font=('Segoe UI', 10), bg='#9E9E9E', fg='white', padx=20).pack(side=tk.RIGHT)
        
        # Focus on token entry
        token_entry.focus()
    
    def save_hf_token(self, window):
        """Save Hugging Face token"""
        token = self.hf_token.get().strip()
        if token:
            messagebox.showinfo("Success", "Hugging Face token saved successfully!")
            window.destroy()
        else:
            messagebox.showwarning("Warning", "Please enter a valid token.")
    
    def clear_hf_token(self, window):
        """Clear Hugging Face token"""
        self.hf_token.set("")
        messagebox.showinfo("Cleared", "Hugging Face token cleared.")
        window.destroy()
    
    def start_transcription(self):
        """Start transcription process"""
        if self.is_transcribing:
            messagebox.showwarning("Warning", "Transcription is already in progress!")
            return
        
        # Check if audio file is selected
        audio_file = self.audio_file_path.get()
        if not audio_file:
            messagebox.showerror("Error", "Please select an audio file or record audio first!")
            return
        
        # Check if file exists
        if not os.path.exists(audio_file):
            messagebox.showerror("Error", f"Audio file not found: {audio_file}")
            return
        
        # Start transcription in a separate thread
        self.is_transcribing = True
        self.transcribe_button.config(text="Transcribing...", state="disabled")
        self.update_progress(0)
        
        transcription_thread = threading.Thread(target=self._transcribe_audio_thread)
        transcription_thread.daemon = True
        transcription_thread.start()
    
    def _transcribe_audio_thread(self):
        """Transcribe audio in a separate thread"""
        try:
            audio_file = self.audio_file_path.get()
            detect_speakers = self.detect_speakers.get()
            
            self.update_status("Loading Whisper model...")
            self.update_progress(10)
            
            if detect_speakers and SPEAKER_DIARIZATION_AVAILABLE:
                # Use speaker diarization
                self.update_status("Loading speaker diarization model...")
                hf_token = self.hf_token.get().strip() if self.hf_token.get().strip() else None
                
                result = transcribe_with_speaker_diarization(
                    audio_file, 
                    "base", 
                    None, 
                    "transcribe", 
                    hf_token
                )
            else:
                # Standard transcription
                import whisper
                model = whisper.load_model("base")
                
                self.update_status("Transcribing audio...")
                self.update_progress(30)
                
                # Perform transcription
                result = model.transcribe(
                    audio_file,
                    language=None,
                    task="transcribe",
                    verbose=False
                )
            
            self.update_progress(80)
            self.update_status("Saving results...")
            
            # Save results
            output_file = self.save_transcription(result, audio_file, "txt")
            
            self.update_progress(100)
            self.update_status("Transcription completed!")
            
            # Display results in GUI
            self.root.after(0, self.display_results, result, output_file)
            
        except Exception as e:
            error_msg = f"Transcription failed: {str(e)}"
            self.root.after(0, self._transcription_error, error_msg)
    
    def _transcription_error(self, error_message):
        """Handle transcription error in main thread"""
        self.is_transcribing = False
        self.transcribe_button.config(text="Start Transcription", state="normal")
        self.update_progress(0)
        self.update_status("Transcription failed")
        messagebox.showerror("Transcription Error", error_message)
    
    def display_results(self, result, output_file):
        """Display transcription results in GUI"""
        self.is_transcribing = False
        self.transcribe_button.config(text="Start Transcription", state="normal")
        self.update_progress(0)
        
        # Display results
        if isinstance(result, dict) and 'segments' in result:
            # Speaker diarization results
            text = ""
            for segment in result['segments']:
                speaker = segment.get('speaker', 'Unknown')
                text += f"[{speaker}]: {segment['text']}\n"
        else:
            # Standard transcription results
            text = result.get('text', 'No transcription available')
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, text)
        
        # Show success message
        messagebox.showinfo("Transcription Complete", 
                          f"Transcription completed successfully!\n\nOutput saved to: {output_file}")
    
    def save_transcription(self, result, audio_file_path, output_format):
        """Save transcription results to file"""
        # Create Transcriptions directory
        transcriptions_dir = Path("Transcriptions")
        transcriptions_dir.mkdir(exist_ok=True)
        
        # Get base filename
        base_name = Path(audio_file_path).stem
        
        if output_format == "txt":
            output_file = transcriptions_dir / f"{base_name}_transcription.txt"
            
            if isinstance(result, dict) and 'segments' in result:
                # Speaker diarization results
                with open(output_file, 'w', encoding='utf-8') as f:
                    for segment in result['segments']:
                        speaker = segment.get('speaker', 'Unknown')
                        start_time = segment.get('start', 0)
                        end_time = segment.get('end', 0)
                        text = segment.get('text', '')
                        
                        f.write(f"[{start_time:.2f}s - {end_time:.2f}s] {speaker}: {text}\n")
            else:
                # Standard transcription results
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result.get('text', 'No transcription available'))
        
        return output_file
    
    def clear_all(self):
        """Clear all fields and results"""
        self.audio_file_path.set("")
        self.results_text.delete(1.0, tk.END)
        self.update_progress(0)
        self.update_status("Ready to transcribe")


def main():
    root = tk.Tk()
    app = AudioTranscriberGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
