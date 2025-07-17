"""
Voice Mapping Diagnostic - Debug Why Only David Voice is Heard
This script will diagnose the exact voice mapping issue
"""

import pyttsx3
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceMappingDiagnostic:
    """Diagnose voice mapping issues"""
    
    def __init__(self):
        self.engine = None
        self.system_voices = []
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize pyttsx3 engine"""
        try:
            self.engine = pyttsx3.init()
            logger.info("✅ pyttsx3 engine initialized")
            
            # Get system voices
            voices = self.engine.getProperty('voices')
            if voices:
                self.system_voices = voices
                logger.info(f"✅ Found {len(voices)} system voices")
            else:
                logger.error("❌ No system voices found")
                
        except Exception as e:
            logger.error(f"❌ Engine initialization failed: {e}")
    
    def analyze_voice_properties(self):
        """Analyze each system voice in detail"""
        print("\n" + "="*80)
        print("🔍 DETAILED VOICE ANALYSIS")
        print("="*80)
        
        if not self.system_voices:
            print("❌ No voices to analyze")
            return
        
        for i, voice in enumerate(self.system_voices):
            print(f"\n📋 VOICE {i+1} DETAILS:")
            print(f"   Name: {voice.name}")
            print(f"   ID: {voice.id}")
            print(f"   Languages: {getattr(voice, 'languages', 'Unknown')}")
            print(f"   Gender: {getattr(voice, 'gender', 'Unknown')}")
            print(f"   Age: {getattr(voice, 'age', 'Unknown')}")
            
            # Try to extract voice characteristics from name
            name_lower = voice.name.lower()
            if 'david' in name_lower:
                print(f"   Type: DAVID (Male, US)")
            elif 'zira' in name_lower:
                print(f"   Type: ZIRA (Female, US)")
            elif 'hazel' in name_lower:
                print(f"   Type: HAZEL (Female, GB)")
            else:
                print(f"   Type: UNKNOWN")
    
    def test_voice_switching(self):
        """Test if voice switching actually works"""
        print(f"\n🔄 VOICE SWITCHING TEST")
        print("="*50)
        
        if not self.engine or not self.system_voices:
            print("❌ Cannot test - engine or voices not available")
            return
        
        for i, voice in enumerate(self.system_voices):
            print(f"\n🎵 Testing Voice {i+1}: {voice.name}")
            
            try:
                # Set the voice
                self.engine.setProperty('voice', voice.id)
                
                # Verify the voice was set
                current_voice = self.engine.getProperty('voice')
                if current_voice == voice.id:
                    print(f"✅ Voice set successfully to: {voice.name}")
                else:
                    print(f"❌ Voice setting failed!")
                    print(f"   Requested: {voice.id}")
                    print(f"   Actual: {current_voice}")
                
                # Test speech
                test_message = f"This is {voice.name.split()[-4] if len(voice.name.split()) > 3 else 'voice'} number {i+1}. Can you hear the difference?"
                print(f"🔊 Speaking: {test_message}")
                
                self.engine.say(test_message)
                self.engine.runAndWait()
                
                # Pause between voices
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error testing voice {voice.name}: {e}")
    
    def test_voice_engine_properties(self):
        """Test engine properties and settings"""
        print(f"\n⚙️ ENGINE PROPERTIES TEST")
        print("="*50)
        
        if not self.engine:
            print("❌ No engine available")
            return
        
        try:
            # Test current voice
            current_voice = self.engine.getProperty('voice')
            print(f"Current Voice ID: {current_voice}")
            
            # Test rate
            current_rate = self.engine.getProperty('rate')
            print(f"Current Rate: {current_rate}")
            
            # Test volume
            current_volume = self.engine.getProperty('volume')
            print(f"Current Volume: {current_volume}")
            
            # Try changing rate and volume
            print(f"\n🔧 Testing property changes...")
            
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 1.0)
            
            new_rate = self.engine.getProperty('rate')
            new_volume = self.engine.getProperty('volume')
            
            print(f"New Rate: {new_rate}")
            print(f"New Volume: {new_volume}")
            
            if new_rate == 150:
                print("✅ Rate change successful")
            else:
                print("❌ Rate change failed")
                
            if abs(new_volume - 1.0) < 0.01:
                print("✅ Volume change successful")
            else:
                print("❌ Volume change failed")
                
        except Exception as e:
            print(f"❌ Engine property test failed: {e}")
    
    def run_complete_diagnosis(self):
        """Run complete voice diagnostic"""
        print("🔍 VOICE MAPPING DIAGNOSTIC TOOL")
        print("Investigating why only David voice is heard")
        print("="*80)
        
        # Step 1: Analyze voices
        self.analyze_voice_properties()
        
        # Step 2: Test engine properties
        self.test_voice_engine_properties()
        
        # Step 3: Test voice switching
        input("\n📢 Press Enter when ready to test voice switching...")
        self.test_voice_switching()
        
        # Step 4: Final analysis
        print(f"\n🎯 DIAGNOSTIC SUMMARY")
        print("="*50)
        print(f"System Voices Found: {len(self.system_voices)}")
        print(f"Engine Available: {'✅ Yes' if self.engine else '❌ No'}")
        
        if len(self.system_voices) == 3:
            print("✅ Expected number of voices found")
        else:
            print("⚠️ Unexpected number of voices")
        
        print(f"\n💡 POSSIBLE CAUSES:")
        print("1. Windows SAPI might be defaulting all voices to David")
        print("2. Voice IDs might not be switching properly")
        print("3. pyttsx3 might have a voice caching issue")
        print("4. System voice drivers might need updating")
        
        print(f"\n🔧 RECOMMENDED SOLUTIONS:")
        print("1. Restart the pyttsx3 engine between voice changes")
        print("2. Use Windows Speech Platform instead of SAPI")
        print("3. Check Windows voice settings in Control Panel")
        print("4. Try creating separate engine instances per voice")

def main():
    """Main diagnostic function"""
    print("🚀 Voice Mapping Diagnostic Tool")
    print("This will help identify why only David voice is heard")
    
    try:
        diagnostic = VoiceMappingDiagnostic()
        diagnostic.run_complete_diagnosis()
        
    except KeyboardInterrupt:
        print("\n⚠️ Diagnostic interrupted by user")
    except Exception as e:
        print(f"\n❌ Diagnostic failed: {e}")
        logger.error(f"Diagnostic error: {e}")
    
    input("\n📝 Press Enter to exit...")

if __name__ == "__main__":
    main()
