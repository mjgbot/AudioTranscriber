#!/usr/bin/env python3
"""
Virtual Environment Setup Script for AudioTranscriber
Automatically creates and manages virtual environment with dependencies
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class VenvManager:
    """Manage virtual environment for AudioTranscriber"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.venv_path = self.project_root / "venv"
        self.python_exe = None
        self.pip_exe = None
        self.is_windows = platform.system() == "Windows"
        
    def get_venv_python(self):
        """Get the Python executable path in the virtual environment"""
        if self.is_windows:
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"
    
    def get_venv_pip(self):
        """Get the pip executable path in the virtual environment"""
        if self.is_windows:
            return self.venv_path / "Scripts" / "pip.exe"
        else:
            return self.venv_path / "bin" / "pip"
    
    def venv_exists(self):
        """Check if virtual environment already exists"""
        python_exe = self.get_venv_python()
        return python_exe.exists()
    
    def create_venv(self):
        """Create virtual environment"""
        print("Creating virtual environment...")
        try:
            subprocess.run([
                sys.executable, "-m", "venv", str(self.venv_path)
            ], check=True, capture_output=True)
            print("✓ Virtual environment created successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to create virtual environment: {e}")
            return False
    
    def install_dependencies(self):
        """Install dependencies in virtual environment"""
        pip_exe = self.get_venv_pip()
        requirements_file = self.project_root / "requirements.txt"
        
        if not requirements_file.exists():
            print("✗ requirements.txt not found")
            return False
        
        print("Installing dependencies...")
        try:
            # Try to upgrade pip first (optional)
            try:
                subprocess.run([
                    str(pip_exe), "install", "--upgrade", "pip"
                ], check=True, capture_output=True)
                print("✓ Pip upgraded successfully")
            except subprocess.CalledProcessError:
                print("⚠ Pip upgrade failed, continuing with existing version")
            
            # Install requirements
            result = subprocess.run([
                str(pip_exe), "install", "-r", str(requirements_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ Dependencies installed successfully")
                return True
            else:
                print(f"✗ Failed to install dependencies:")
                print(f"  Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Failed to install dependencies: {e}")
            return False
    
    def install_optional_dependencies(self):
        """Install optional dependencies like PyAudio"""
        pip_exe = self.get_venv_pip()
        
        print("Installing optional dependencies...")
        optional_packages = ["pyaudio"]
        
        for package in optional_packages:
            try:
                print(f"Installing {package}...")
                result = subprocess.run([
                    str(pip_exe), "install", package
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✓ {package} installed successfully")
                else:
                    print(f"⚠ {package} installation failed (optional): {result.stderr}")
                    print(f"  You can still use AudioTranscriber without {package}")
                    
            except Exception as e:
                print(f"⚠ {package} installation failed (optional): {e}")
                print(f"  You can still use AudioTranscriber without {package}")
    
    def setup_environment(self):
        """Set up the complete environment"""
        print("=" * 60)
        print("AudioTranscriber Environment Setup")
        print("=" * 60)
        
        # Check if venv already exists
        if self.venv_exists():
            print("✓ Virtual environment already exists")
            self.python_exe = self.get_venv_python()
            self.pip_exe = self.get_venv_pip()
            print(f"Using Python: {self.python_exe}")
            return True
        
        # Create virtual environment
        if not self.create_venv():
            return False
        
        # Set paths
        self.python_exe = self.get_venv_python()
        self.pip_exe = self.get_venv_pip()
        
        # Install dependencies
        if not self.install_dependencies():
            return False
        
        # Install optional dependencies (including PyAudio)
        self.install_optional_dependencies()
        
        print("=" * 60)
        print("✓ Environment setup completed successfully!")
        print("=" * 60)
        return True
    
    def run_script(self, script_path, *args):
        """Run a script using the virtual environment Python"""
        if not self.python_exe:
            print("✗ Virtual environment not set up")
            return False
        
        cmd = [str(self.python_exe), str(script_path)] + list(args)
        print(f"Running: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Script execution failed: {e}")
            return False
    
    def get_activation_command(self):
        """Get the command to activate the virtual environment"""
        if self.is_windows:
            return f"{self.venv_path}\\Scripts\\activate"
        else:
            return f"source {self.venv_path}/bin/activate"

def main():
    """Main setup function"""
    venv_manager = VenvManager()
    
    if not venv_manager.setup_environment():
        print("✗ Environment setup failed")
        sys.exit(1)
    
    # Run the GUI
    gui_script = venv_manager.project_root / "audio_transcriber_gui.py"
    if gui_script.exists():
        print("\nStarting AudioTranscriber GUI...")
        venv_manager.run_script(gui_script)
    else:
        print("✗ GUI script not found")
        sys.exit(1)

if __name__ == "__main__":
    main()
