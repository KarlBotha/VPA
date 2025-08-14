"""
VPA Audio System Installer
Installs all required dependencies for the production audio system
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package_name, import_name=None):
    """Install a package using pip"""
    try:
        # Test if package is already installed
        if import_name:
            __import__(import_name)
            print(f"✅ {package_name} already installed")
            return True
        else:
            __import__(package_name.replace('-', '_'))
            print(f"✅ {package_name} already installed")
            return True
    except ImportError:
        pass
    
    try:
        print(f"📦 Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        return False

def main():
    """Install all audio dependencies"""
    print("🎵 VPA Audio System - Dependency Installer")
    print("=" * 50)
    
    # Required packages for production audio system
    audio_packages = [
        ("pyaudio", "pyaudio"),
        ("speechrecognition", "speech_recognition"),
        ("openai-whisper", "whisper"),
        ("webrtcvad", "webrtcvad"),
        ("edge-tts", "edge_tts"),
        ("pyttsx3", "pyttsx3"),
        ("pygame", "pygame"),
        ("numpy", "numpy"),
        ("scipy", "scipy"),
        ("sounddevice", "sounddevice"),
        ("librosa", "librosa"),
        ("noisereduce", "noisereduce")
    ]
    
    # Install each package
    installed = []
    failed = []
    
    for package, import_name in audio_packages:
        if install_package(package, import_name):
            installed.append(package)
        else:
            failed.append(package)
    
    print("\n" + "=" * 50)
    print(f"✅ Successfully installed: {len(installed)} packages")
    for pkg in installed:
        print(f"  - {pkg}")
    
    if failed:
        print(f"\n❌ Failed to install: {len(failed)} packages")
        for pkg in failed:
            print(f"  - {pkg}")
        print("\nPlease install these manually or check your environment.")
    
    print("\n🎵 Audio system setup complete!")
    
    # Test audio system
    print("\n🧪 Testing audio system...")
    try:
        # Test basic imports
        import pyaudio
        import speech_recognition as sr
        import pyttsx3
        print("✅ Core audio libraries loaded successfully")
        
        # Test microphone access
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("✅ Microphone access successful")
        
        # Test TTS
        engine = pyttsx3.init()
        print("✅ Text-to-speech engine initialized")
        
        print("🎉 Audio system is ready!")
        
    except Exception as e:
        print(f"⚠️ Audio system test failed: {e}")
        print("Please check your audio device settings.")

if __name__ == "__main__":
    main()
