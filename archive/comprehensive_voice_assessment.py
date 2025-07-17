#!/usr/bin/env python3
"""
COMPREHENSIVE VOICE SYSTEM ASSESSMENT
Deep analysis of all available voices on system
"""

import pyttsx3
import win32com.client
import os
import sys
from pathlib import Path

def analyze_system_voices():
    """Comprehensive analysis of all voice systems available"""
    
    print("=" * 80)
    print("🔍 COMPREHENSIVE VOICE SYSTEM ASSESSMENT")
    print("=" * 80)
    
    # 1. PYTTSX3 Voices
    print("\n1️⃣ PYTTSX3 VOICE ANALYSIS")
    print("-" * 40)
    
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        print(f"Total pyttsx3 voices found: {len(voices)}")
        
        for i, voice in enumerate(voices):
            print(f"\n[{i+1}] {voice.name}")
            print(f"    ID: {voice.id}")
            print(f"    Languages: {getattr(voice, 'languages', 'N/A')}")
            print(f"    Age: {getattr(voice, 'age', 'N/A')}")
            print(f"    Gender: {getattr(voice, 'gender', 'N/A')}")
        
        engine.stop()
        
    except Exception as e:
        print(f"❌ pyttsx3 analysis failed: {e}")
    
    # 2. Windows SAPI Voices (Direct)
    print(f"\n\n2️⃣ WINDOWS SAPI DIRECT ANALYSIS")
    print("-" * 40)
    
    try:
        sapi = win32com.client.Dispatch("SAPI.SpVoice")
        voices = sapi.GetVoices()
        
        print(f"Total SAPI voices found: {voices.Count}")
        
        for i in range(voices.Count):
            voice = voices.Item(i)
            print(f"\n[{i+1}] {voice.GetDescription()}")
            print(f"    ID: {voice.Id}")
            
            # Get additional attributes
            try:
                attrs = voice.GetAttribute("Language")
                print(f"    Language: {attrs}")
            except:
                pass
            
            try:
                attrs = voice.GetAttribute("Gender")
                print(f"    Gender: {attrs}")
            except:
                pass
                
            try:
                attrs = voice.GetAttribute("Age")
                print(f"    Age: {attrs}")
            except:
                pass
    
    except Exception as e:
        print(f"❌ SAPI analysis failed: {e}")
    
    # 3. Registry Analysis
    print(f"\n\n3️⃣ WINDOWS REGISTRY VOICE ANALYSIS")
    print("-" * 40)
    
    try:
        import winreg
        
        # Check main TTS voices registry
        key_path = r"SOFTWARE\Microsoft\Speech\Voices\Tokens"
        
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    print(f"\n[Registry {i+1}] {subkey_name}")
                    
                    # Try to get voice details
                    try:
                        subkey = winreg.OpenKey(key, subkey_name)
                        try:
                            name = winreg.QueryValueEx(subkey, "")[0]
                            print(f"    Name: {name}")
                        except:
                            pass
                        winreg.CloseKey(subkey)
                    except:
                        pass
                    
                    i += 1
                except OSError:
                    break
            
            winreg.CloseKey(key)
            
        except Exception as e:
            print(f"Registry access failed: {e}")
    
    except Exception as e:
        print(f"❌ Registry analysis failed: {e}")
    
    # 4. Check for additional voice packs
    print(f"\n\n4️⃣ ADDITIONAL VOICE PACK ANALYSIS")
    print("-" * 40)
    
    # Common voice pack locations
    voice_locations = [
        r"C:\Windows\Speech\Engines",
        r"C:\Windows\SysWOW64\Speech\Engines",
        r"C:\Program Files\Common Files\Microsoft Shared\Speech",
        r"C:\Program Files (x86)\Common Files\Microsoft Shared\Speech"
    ]
    
    for location in voice_locations:
        if os.path.exists(location):
            print(f"✅ Found voice directory: {location}")
            try:
                files = list(Path(location).rglob("*"))
                print(f"    Files found: {len(files)}")
                for file in files[:5]:  # Show first 5
                    print(f"    - {file.name}")
                if len(files) > 5:
                    print(f"    ... and {len(files) - 5} more")
            except:
                pass
        else:
            print(f"❌ Not found: {location}")
    
    print(f"\n\n5️⃣ VOICE QUALITY & CAPABILITY ASSESSMENT")
    print("-" * 40)
    
    # Test each voice briefly
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        print("Testing voice capabilities...")
        
        for i, voice in enumerate(voices):
            print(f"\n[Test {i+1}] {voice.name}")
            
            try:
                engine.setProperty('voice', voice.id)
                
                # Test rate range
                rates = [100, 200, 300]
                for rate in rates:
                    try:
                        engine.setProperty('rate', rate)
                        print(f"    Rate {rate}: ✅")
                        break
                    except:
                        print(f"    Rate {rate}: ❌")
                
                # Test volume range
                volumes = [0.5, 0.9, 1.0]
                for volume in volumes:
                    try:
                        engine.setProperty('volume', volume)
                        print(f"    Volume {volume}: ✅")
                        break
                    except:
                        print(f"    Volume {volume}: ❌")
                
            except Exception as e:
                print(f"    Test failed: {e}")
        
        engine.stop()
        
    except Exception as e:
        print(f"❌ Voice testing failed: {e}")
    
    print(f"\n\n6️⃣ DOWNLOADABLE VOICE RECOMMENDATIONS")
    print("-" * 40)
    
    print("Microsoft Voice Downloads Available:")
    print("1. Windows 10/11 Language Packs (Settings > Time & Language > Language)")
    print("2. Microsoft Speech Platform Runtime Languages")
    print("3. Azure Cognitive Services Speech (Premium)")
    print("4. Windows Speech Recognition Language Packs")
    
    print("\nFree Voice Options:")
    print("1. eSpeak-ng (Open source)")
    print("2. Festival Speech Synthesis (Open source)")
    print("3. Mary TTS (Open source)")
    print("4. Mimic (Mycroft AI)")
    
    print("\n=" * 80)
    print("🏁 VOICE SYSTEM ASSESSMENT COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    analyze_system_voices()
