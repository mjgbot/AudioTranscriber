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

# Try to import audio recorder, but make it optional
try:
    from audio_recorder import AudioRecorder
    AUDIO_RECORDING_AVAILABLE = True
except ImportError:
    AudioRecorder = None
    AUDIO_RECORDING_AVAILABLE = False

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
        self.hf_token = tk.StringVar()
        self.is_transcribing = False
        
        # Recording variables
        if AUDIO_RECORDING_AVAILABLE:
            self.audio_recorder = AudioRecorder()
            self.audio_recorder.set_audio_level_callback(self.update_audio_level)
        else:
            self.audio_recorder = None
        self.is_recording = False
        self.recording_file = None
        self.recording_format = tk.StringVar(value="wav")
        
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
    
    def update_status(self, message):
            format_options = ["wav", "mp3"]
            format_var = tk.StringVar(value=self.recording_format.get())
            format_dropdown = tk.OptionMenu(recording_frame, format_var, *format_options, 
                                          command=lambda x: self.recording_format.set(x))
            format_dropdown.config(bg=colors['background'], fg=colors['text'], 
                                 activebackground=colors['primary'], activeforeground='white',
                                 relief='solid', bd=1, width=8)
            format_dropdown.grid(row=1, column=1, padx=(0, 10), pady=5)
            
            # Recording controls
            self.record_button = ttk.Button(recording_frame, text="🎤 Start Recording", 
                                           command=self.start_recording, style='Success.TButton')
            self.record_button.grid(row=1, column=2, padx=(10, 15), pady=5)
            
            self.stop_record_button = ttk.Button(recording_frame, text="⏹️ Stop Recording", 
                                                 command=self.stop_recording, state="disabled", style='Accent.TButton')
            self.stop_record_button.grid(row=1, column=3, padx=(0, 15), pady=5)
            
            self.record_status_label = tk.Label(recording_frame, text="Ready to record", 
                                               font=("Arial", 9), fg=colors['text'], bg=colors['background'])
            self.record_status_label.grid(row=1, column=4, sticky=tk.W, padx=(10, 15), pady=5)
            
            # Audio level meter
            self.audio_level_frame = tk.Frame(recording_frame, bg=colors['background'])
            self.audio_level_frame.grid(row=1, column=5, sticky=tk.W, padx=(10, 15), pady=5)
            
            tk.Label(self.audio_level_frame, text="Level:", font=("Arial", 8), fg=colors['text'], bg=colors['background']).pack(side=tk.LEFT)
            
            # Create white progress bar using Canvas
            self.audio_level_canvas = tk.Canvas(self.audio_level_frame, width=100, height=20, 
                                               bg=colors['background'], highlightthickness=0)
            self.audio_level_canvas.pack(side=tk.LEFT, padx=(5, 0))
            
            # Draw the progress bar background
            self.audio_level_canvas.create_rectangle(0, 0, 100, 20, fill=colors['background'], outline=colors['border'])
            self.audio_level_progress = self.audio_level_canvas.create_rectangle(0, 0, 0, 20, fill=colors['primary'], outline="")
            
            self.audio_level_label = tk.Label(self.audio_level_frame, text="0%", font=("Arial", 8), fg=colors['text'], bg=colors['background'])
            self.audio_level_label.pack(side=tk.LEFT, padx=(5, 0))
            
            # View recordings button only
            view_frame = tk.Frame(recording_frame, bg=colors['background'])
            view_frame.grid(row=2, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(5, 10), padx=15)
            
            self.view_recordings_button = ttk.Button(view_frame, text="📁 View Recordings", 
                                                   command=self.view_recordings, style='Warning.TButton')
            self.view_recordings_button.pack(side=tk.LEFT, padx=(0, 8))
            
            # Recording info
            recording_info_text = "Record audio directly from your microphone for transcription"
            tk.Label(recording_frame, text=recording_info_text, font=("Arial", 8), 
                     fg=colors['text_light'], bg=colors['background']).grid(row=3, column=0, columnspan=5, sticky=tk.W, pady=(0, 10), padx=15)
        else:
            # Show message when recording is not available
            self.record_button = None
            self.stop_record_button = None
            self.record_status_label = None
            
            no_recording_text = "Audio recording not available. Install PyAudio to enable recording."
            tk.Label(recording_frame, text=no_recording_text, font=("Arial", 9), 
                     fg="red", bg=colors['background']).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5, padx=15)
            
            install_text = "To install PyAudio: pip install pyaudio"
            tk.Label(recording_frame, text=install_text, font=("Arial", 8), 
                     fg=colors['text_light'], bg=colors['background']).grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(0, 10), padx=15)
        
        # Transcription Settings section
        settings_frame = tk.Frame(main_frame, bg=colors['background'], relief='solid', bd=1)
        settings_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)
        settings_frame.columnconfigure(1, weight=1)
        
        # Add title label for the settings frame
        settings_title = tk.Label(settings_frame, text="⚙️ Transcription Settings", 
                                 font=('Segoe UI', 11, 'bold'), 
                                 fg=colors['text'], bg=colors['background'])
        settings_title.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(10, 15), padx=15)
        
        # File selection
        tk.Label(settings_frame, text="Audio File:", font=("Arial", 10, "bold"), fg=colors['text'], bg=colors['background']).grid(row=1, column=0, sticky=tk.W, pady=(0, 5), padx=15)
        file_frame = tk.Frame(settings_frame, bg=colors['background'])
        file_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5), padx=(0, 15))
        file_frame.columnconfigure(0, weight=1)
        
        self.audio_file_entry = tk.Entry(file_frame, textvariable=self.audio_file_path, state="readonly", 
                                       bg=colors['background'], fg=colors['text'], relief='solid', bd=1)
        self.audio_file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 8))
        
        ttk.Button(file_frame, text="📂 Browse", command=self.browse_file, style='Warning.TButton').grid(row=0, column=1, padx=(0, 8))
        ttk.Button(file_frame, text="🗑️ Clear", command=self.clear_audio_file, style='Accent.TButton').grid(row=0, column=2)
        
        # Model selection
        ttk.Label(settings_frame, text="Model:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        model_frame = ttk.Frame(settings_frame)
        model_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        model_frame.columnconfigure(0, weight=1)
        
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.selected_model, 
                                       values=[model[0] for model in self.models], 
                                       state="readonly", width=45)
        self.model_combo.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.model_combo.set("Base (Balanced, ~1GB VRAM)")
        
        # Language selection
        ttk.Label(settings_frame, text="Language:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        lang_frame = ttk.Frame(settings_frame)
        lang_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        lang_frame.columnconfigure(0, weight=1)
        
        self.language_combo = ttk.Combobox(lang_frame, textvariable=self.selected_language,
                                         values=[lang[0] for lang in self.languages],
                                         state="readonly", width=45)
        self.language_combo.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.language_combo.set("Auto-detect")
        
        # Task selection
        ttk.Label(settings_frame, text="Task:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        task_frame = ttk.Frame(settings_frame)
        task_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        task_frame.columnconfigure(0, weight=1)
        
        self.task_combo = ttk.Combobox(task_frame, textvariable=self.selected_task,
                                      values=[task[0] for task in self.tasks],
                                      state="readonly", width=45)
        self.task_combo.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.task_combo.set("transcribe")
        
        # Output format
        ttk.Label(settings_frame, text="Output Format:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        output_frame = ttk.Frame(settings_frame)
        output_frame.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_combo = ttk.Combobox(output_frame, textvariable=self.selected_output,
                                        values=[fmt[0] for fmt in self.output_formats],
                                        state="readonly", width=45)
        self.output_combo.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.output_combo.set("Plain Text (.txt)")
        
        # Speaker detection checkbox
        speaker_frame = ttk.Frame(settings_frame)
        speaker_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(15, 5))
        
        self.speaker_checkbox = ttk.Checkbutton(speaker_frame, text="Detect different speakers", 
                                              variable=self.detect_speakers)
        self.speaker_checkbox.grid(row=0, column=0, sticky=tk.W)
        
        # View transcriptions button
        self.view_transcriptions_button = ttk.Button(speaker_frame, text="📄 View Transcriptions", 
                                                    command=self.view_transcriptions, style='Warning.TButton')
        self.view_transcriptions_button.grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # Control buttons (moved to bottom)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        self.transcribe_button = ttk.Button(button_frame, text="🚀 Start Transcription", 
                                           command=self.start_transcription, style='Primary.TButton')
        self.transcribe_button.pack(side=tk.LEFT, padx=(0, 20))
        
        self.clear_button = ttk.Button(button_frame, text="🧹 Clear", 
                                      command=self.clear_all, style='Accent.TButton')
        self.clear_button.pack(side=tk.LEFT, padx=(0, 0))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        
        # Create white progress bar using Canvas
        self.progress_canvas = tk.Canvas(main_frame, width=400, height=25, 
                                        bg=colors['background'], highlightthickness=0)
        self.progress_canvas.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Draw the progress bar background
        self.progress_canvas.create_rectangle(0, 0, 400, 25, fill=colors['background'], outline=colors['border'])
        self.progress_fill = self.progress_canvas.create_rectangle(0, 0, 0, 25, fill=colors['primary'], outline="")
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to transcribe", 
                                    font=("Segoe UI", 10, "bold"))
        self.status_label.grid(row=6, column=0, columnspan=3, pady=5)
        
        # Results area
        ttk.Label(main_frame, text="📝 Transcription Results:", 
                font=("Segoe UI", 12, "bold")).grid(row=7, column=0, columnspan=3, 
                                                sticky=tk.W, pady=(20, 5))
        
        self.results_text = scrolledtext.ScrolledText(main_frame, height=8, width=80)
        self.results_text.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure grid weights for resizing
        main_frame.rowconfigure(8, weight=1)
        
    def open_hf_settings(self):
        """Open Hugging Face settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Hugging Face Authentication Settings")
        settings_window.geometry("500x200")
        settings_window.resizable(False, False)
        
        # Center the window
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(settings_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Hugging Face Authentication", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_label = ttk.Label(main_frame, 
                              text="Enter your Hugging Face token for advanced speaker detection",
                              font=("Arial", 10))
        desc_label.pack(pady=(0, 15))
        
        # Token input frame
        token_frame = ttk.Frame(main_frame)
        token_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(token_frame, text="HF Token:").pack(side=tk.LEFT, padx=(0, 10))
        
        token_entry = ttk.Entry(token_frame, textvariable=self.hf_token, show="*", width=40)
        token_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(buttons_frame, text="Save Token", command=self.save_hf_token).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Clear Token", command=self.clear_hf_token).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Close", command=settings_window.destroy).pack(side=tk.RIGHT)
        
        # Info text
        info_text = "Get your token from: https://huggingface.co/settings/tokens"
        info_label = ttk.Label(main_frame, text=info_text, font=("Arial", 8), foreground="gray")
        info_label.pack(pady=(10, 0))
        
        # Focus on token entry
        token_entry.focus()
    
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
    
    def clear_audio_file(self):
        """Clear the selected audio file"""
        self.audio_file_path.set("")
        self.update_status("Audio file cleared")
    
    def save_hf_token(self):
        """Save Hugging Face token"""
        token = self.hf_token.get().strip()
        if not token:
            messagebox.showwarning("Warning", "Please enter a Hugging Face token!")
            return
        
        try:
            from speaker_diarization import HuggingFaceAuth
            hf_auth = HuggingFaceAuth()
            if hf_auth.save_token(token):
                if hf_auth.authenticate(token):
                    messagebox.showinfo("Success", "Hugging Face token saved and authenticated successfully!")
                    self.update_status("HF token authenticated")
                else:
                    messagebox.showerror("Error", "Failed to authenticate with Hugging Face. Please check your token.")
            else:
                messagebox.showerror("Error", "Failed to save token.")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving token: {str(e)}")
    
    def clear_hf_token(self):
        """Clear Hugging Face token"""
        try:
            from speaker_diarization import HuggingFaceAuth
            hf_auth = HuggingFaceAuth()
            if hf_auth.clear_token():
                self.hf_token.set("")
                messagebox.showinfo("Success", "Hugging Face token cleared!")
                self.update_status("HF token cleared")
            else:
                messagebox.showerror("Error", "Failed to clear token.")
        except Exception as e:
            messagebox.showerror("Error", f"Error clearing token: {str(e)}")
    
    def update_audio_level(self, level):
        """Update the audio level display"""
        if hasattr(self, 'audio_level_bar') and hasattr(self, 'audio_level_label'):
            self.root.after(0, self._update_audio_level_ui, level)
    
    def _update_audio_level_ui(self, level):
        """Update audio level UI elements (called from main thread)"""
        try:
            if hasattr(self, 'audio_level_canvas') and hasattr(self, 'audio_level_progress'):
                # Update canvas-based progress bar
                width = int((level / 100.0) * 100)
                self.audio_level_canvas.coords(self.audio_level_progress, 0, 0, width, 20)
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
            # Check if PyAudio is available
            if not hasattr(self, 'audio_recorder') or self.audio_recorder is None:
                messagebox.showerror("Error", "Audio recording not available. Please install PyAudio.")
                return
            
            # Start recording with selected format
            recording_format = self.recording_format.get()
            self.recording_file = self.audio_recorder.start_recording(format=recording_format)
            
            if self.recording_file:
                self.is_recording = True
                self.record_button.config(state="disabled")
                self.stop_record_button.config(state="normal")
                self.record_status_label.config(text="Recording...")
                self.update_status("Recording audio...")
                
                # Update the file path to the recording
                self.audio_file_path.set(self.recording_file)
                
                messagebox.showinfo("Recording Started", 
                                  f"Recording started!\n\nFile: {os.path.basename(self.recording_file)}\n\nClick 'Stop Recording' when finished.")
            else:
                messagebox.showerror("Error", "Failed to start recording. Please check your microphone.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start recording: {str(e)}")
    
    def stop_recording(self):
        """Stop recording and save the audio file"""
        if not AUDIO_RECORDING_AVAILABLE:
            return
        
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
                    self.audio_level_canvas.coords(self.audio_level_progress, 0, 0, 0, 20)
                if hasattr(self, 'audio_level_label'):
                    self.audio_level_label.config(text="0%")
                
                # Update the file path to the saved recording
                self.audio_file_path.set(saved_file)
                
                messagebox.showinfo("Recording Complete", 
                                  f"Recording saved successfully!\n\nFile: {os.path.basename(saved_file)}\n\nYou can now transcribe this recording.")
            else:
                messagebox.showerror("Error", "Failed to save recording.")
                self.record_status_label.config(text="Recording failed")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop recording: {str(e)}")
            self.record_status_label.config(text="Recording error")
    
    def view_recordings(self):
        """Open the recordings folder"""
        recordings_dir = Path("recordings")
        if recordings_dir.exists():
            try:
                import subprocess
                import platform
                
                if platform.system() == "Windows":
                    subprocess.run(["explorer", str(recordings_dir.absolute())])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", str(recordings_dir.absolute())])
                else:  # Linux
                    subprocess.run(["xdg-open", str(recordings_dir.absolute())])
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open recordings folder: {str(e)}")
        else:
            messagebox.showinfo("No Recordings", "No recordings folder found. Record some audio first!")
    
    def view_transcriptions(self):
        """Open the Transcriptions folder"""
        transcriptions_dir = Path("Transcriptions")
        if transcriptions_dir.exists():
            try:
                import subprocess
                import platform
                
                if platform.system() == "Windows":
                    subprocess.run(["explorer", str(transcriptions_dir.absolute())])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", str(transcriptions_dir.absolute())])
                else:  # Linux
                    subprocess.run(["xdg-open", str(transcriptions_dir.absolute())])
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open transcriptions folder: {str(e)}")
        else:
            messagebox.showinfo("No Transcriptions", "No transcriptions folder found. Create some transcriptions first!")
    
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
        self.update_progress(0)
        
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
            self.update_progress(10)
            
            if detect_speakers:
                # Use speaker diarization
                self.update_status("Loading speaker diarization model...")
                hf_token = self.hf_token.get().strip() if self.hf_token.get().strip() else None
                diarizer = SpeakerDiarizer(model_value, hf_token=hf_token)
                result = diarizer.perform_diarization(audio_file)
            else:
                # Standard transcription
                import whisper
                model = whisper.load_model(model_value)
                
                self.update_status("Transcribing audio...")
                self.update_progress(30)
                
                # Perform transcription
                result = model.transcribe(
                    audio_file,
                    language=lang_value if lang_value else None,
                    task=task_value,
                    verbose=False
                )
            
            self.update_progress(80)
            self.update_status("Saving results...")
            
            # Save results
            output_file = self.save_transcription(result, audio_file, output_value)
            
            self.update_progress(100)
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
        
        # Create Transcriptions folder if it doesn't exist
        transcriptions_dir = Path("Transcriptions")
        transcriptions_dir.mkdir(exist_ok=True)
        
        base_name = Path(audio_file_path).stem
        
        if output_format == "txt":
            output_file = transcriptions_dir / f"{base_name}_transcription.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                # Check if speaker information is available
                has_speakers = any('speaker' in segment for segment in result.get('segments', []))
                
                if has_speakers:
                    # Format with speaker labels and timestamps
                    for segment in result["segments"]:
                        speaker = segment.get('speaker', 'Speaker 1')
                        start_time = self.format_time(segment["start"])
                        end_time = self.format_time(segment["end"])
                        text = segment['text'].strip()
                        f.write(f"[{start_time} - {end_time}] {speaker}: {text}\n")
                else:
                    # Standard format without speakers but with timestamps
                    for segment in result["segments"]:
                        start_time = self.format_time(segment["start"])
                        end_time = self.format_time(segment["end"])
                        text = segment['text'].strip()
                        f.write(f"[{start_time} - {end_time}] {text}\n")
        
        elif output_format == "srt":
            output_file = transcriptions_dir / f"{base_name}_transcription.srt"
            with open(output_file, 'w', encoding='utf-8') as f:
                has_speakers = any('speaker' in segment for segment in result.get('segments', []))
                
                for i, segment in enumerate(result["segments"], 1):
                    start_time = self.format_time_srt(segment["start"])
                    end_time = self.format_time_srt(segment["end"])
                    text = segment['text'].strip()
                    
                    if has_speakers:
                        speaker = segment.get('speaker', 'Speaker 1')
                        text = f"{speaker}: {text}"
                    
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{text}\n\n")
        
        elif output_format == "vtt":
            output_file = transcriptions_dir / f"{base_name}_transcription.vtt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("WEBVTT\n\n")
                for segment in result["segments"]:
                    start_time = self.format_time_vtt(segment["start"])
                    end_time = self.format_time_vtt(segment["end"])
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{segment['text'].strip()}\n\n")
        
        return output_file
    
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
        self.update_progress(0)
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_var.set(value)
        if hasattr(self, 'progress_canvas') and hasattr(self, 'progress_fill'):
            width = int((value / 100.0) * 400)
            self.progress_canvas.coords(self.progress_fill, 0, 0, width, 25)
        self.root.update_idletasks()
    
    def clear_all(self):
        """Clear all fields and results"""
        self.audio_file_path.set("")
        self.results_text.delete(1.0, tk.END)
        self.update_progress(0)
        self.update_status("Ready to transcribe")
        
        # Reset combo boxes to defaults
        self.model_combo.set("Base (Balanced, ~1GB VRAM)")
        self.language_combo.set("Auto-detect")
        self.task_combo.set("Transcribe")
        self.output_combo.set("Plain Text (.txt)")
        
        # Note: Don't clear HF token as it's persistent across sessions
    
    def cleanup(self):
        """Clean up resources when closing the application"""
        if hasattr(self, 'audio_recorder') and self.audio_recorder is not None:
            self.audio_recorder.cleanup()

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
    
    # Check if PyAudio is available for recording
    if not AUDIO_RECORDING_AVAILABLE:
        messagebox.showinfo("Audio Recording", 
                           "Audio recording is not available.\n\n"
                           "To enable microphone recording, install PyAudio:\n"
                           "pip install pyaudio\n\n"
                           "You can still transcribe existing audio files.")
    
    root = tk.Tk()
    app = AudioTranscriberGUI(root)
    
    # Handle window close event
    def on_closing():
        app.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
