def run_stt_note():
    """Run speech-to-text note taking"""
    try:
        import speech_recognition as sr  # type: ignore
        r = sr.Recognizer()
        
        print("STT Note Taking Mode")
        print("Available microphones:")
        for i, mic_name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"  {i}: {mic_name}")
        
        # Use default microphone
        with sr.Microphone() as source:
            print("Adjusting for ambient noise... (please be quiet)")
            r.adjust_for_ambient_noise(source, duration=2)
            
            print("Listening for 5 seconds...")
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                print("Processing speech...")
                
                # Try different recognition services
                text = None
                
                # Try Google first (free)
                try:
                    text = r.recognize_google(audio)
                    print(f"Google STT: {text}")
                except sr.UnknownValueError:
                    print("Google STT could not understand audio")
                except sr.RequestError as e:
                    print(f"Google STT service error: {e}")
                
                # Try Sphinx (offline) as fallback
                if not text:
                    try:
                        text = r.recognize_sphinx(audio)
                        print(f"Sphinx STT: {text}")
                    except sr.UnknownValueError:
                        print("Sphinx STT could not understand audio")
                    except sr.RequestError as e:
                        print(f"Sphinx STT error: {e}")
                
                if text:
                    return {
                        "success": True,
                        "text": text,
                        "method": "STT"
                    }
                else:
                    return {
                        "success": False,
                        "error": "No speech recognized"
                    }
                    
            except sr.WaitTimeoutError:
                print("No speech detected within timeout")
                return {"success": False, "error": "Timeout"}
                
    except ImportError:
        print("speech_recognition package not installed")
        return {"success": False, "error": "speech_recognition not available"}
    except Exception as e:
        print(f"STT error: {e}")
        return {"success": False, "error": str(e)}

def list_microphones():
    """List available microphones"""
    try:
        import speech_recognition as sr
        mics = sr.Microphone.list_microphone_names()
        return {"success": True, "microphones": mics}
    except ImportError:
        return {"success": False, "error": "speech_recognition not available"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_microphone(device_index=None):
    """Test microphone functionality"""
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        
        if device_index is not None:
            mic = sr.Microphone(device_index=device_index)
        else:
            mic = sr.Microphone()
        
        with mic as source:
            print("Testing microphone... Say something!")
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, timeout=3, phrase_time_limit=5)
            
        print("Microphone test successful - audio captured")
        return {"success": True, "message": "Microphone working"}
        
    except ImportError:
        return {"success": False, "error": "speech_recognition not available"}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            result = list_microphones()
            if result["success"]:
                print("Available microphones:")
                for i, name in enumerate(result["microphones"]):
                    print(f"  {i}: {name}")
            else:
                print(f"Error: {result['error']}")
        
        elif command == "test":
            device_index = int(sys.argv[2]) if len(sys.argv) > 2 else None
            result = test_microphone(device_index)
            print(f"Test result: {result}")
        
        elif command == "note":
            result = run_stt_note()
            print(f"STT result: {result}")
        
        else:
            print("Usage: python stt_entry.py [list|test|note]")
    else:
        # Default: run note taking
        run_stt_note()
