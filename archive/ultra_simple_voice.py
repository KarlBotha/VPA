#!/usr/bin/env python3
"""
ULTRA SIMPLE - Just play ONE voice with pyttsx3
"""

import pyttsx3

def one_voice_test():
    print("🔊 ULTRA SIMPLE VOICE TEST")
    
    # Initialize engine
    engine = pyttsx3.init()
    
    # Just speak something
    engine.say("Hello, this is a simple voice test")
    engine.runAndWait()
    
    print("✅ Done!")

if __name__ == "__main__":
    one_voice_test()
