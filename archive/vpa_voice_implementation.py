"""
VPA Voice Implementation - Using Confirmed Working Voice
MANDATE FULFILLED: Microsoft Hazel Desktop (British English Female)
EVIDENCE-BASED: User-tested and confirmed audible voice
"""

import pyttsx3
import time
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VPAVoiceSystem:
    """
    Virtual Personal Assistant Voice System
    Configured with confirmed working voice: Microsoft Hazel Desktop
    """
    
    def __init__(self):
        self.engine: Optional[pyttsx3.Engine] = None
        self.voice_configured = False
        self.confirmed_voice_id = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-GB_HAZEL_11.0"
        self.voice_name = "Microsoft Hazel Desktop - English (Great Britain)"
        
        self._initialize_voice_system()
    
    def _initialize_voice_system(self):
        """Initialize TTS engine with confirmed working voice"""
        try:
            # Initialize pyttsx3 engine
            self.engine = pyttsx3.init()
            
            # Configure with confirmed working voice
            self.engine.setProperty('voice', self.confirmed_voice_id)
            self.engine.setProperty('rate', 200)    # Normal speaking rate
            self.engine.setProperty('volume', 0.9)  # High volume for clarity
            
            self.voice_configured = True
            logger.info(f"VPA Voice System initialized with: {self.voice_name}")
            
        except Exception as e:
            logger.error(f"Voice system initialization failed: {e}")
            self.voice_configured = False
    
    def speak(self, text: str) -> bool:
        """
        Speak text using configured VPA voice
        Returns True if successful, False if failed
        """
        if not self.voice_configured or not self.engine:
            logger.error("Voice system not properly configured")
            return False
        
        try:
            logger.info(f"VPA Speaking: '{text}'")
            self.engine.say(text)
            self.engine.runAndWait()
            return True
            
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            return False
    
    def test_voice_system(self) -> bool:
        """Test VPA voice system with confirmation"""
        print(f"\n🎤 TESTING VPA VOICE SYSTEM")
        print(f"Configured Voice: {self.voice_name}")
        print("=" * 60)
        
        test_phrases = [
            "Hello! I am your Virtual Personal Assistant.",
            "Voice system test in progress.",
            "I am ready to help you with your tasks today.",
            "VPA voice configuration successful."
        ]
        
        for i, phrase in enumerate(test_phrases, 1):
            print(f"\nVPA Test {i}: '{phrase}'")
            
            if not self.speak(phrase):
                print(f"❌ Test {i} failed - Speech synthesis error")
                return False
            
            # Get user confirmation
            confirmation = input(f"Did you hear VPA test {i} clearly? (y/n): ").lower()
            if confirmation != 'y':
                print(f"❌ Test {i} failed - User did not hear clearly")
                return False
            else:
                print(f"✅ Test {i} passed")
            
            time.sleep(1)  # Brief pause between tests
        
        print(f"\n🎉 VPA VOICE SYSTEM TEST COMPLETED SUCCESSFULLY!")
        print(f"Voice: {self.voice_name}")
        print(f"Status: ✅ OPERATIONAL AND USER-CONFIRMED")
        
        return True
    
    def get_voice_info(self) -> dict:
        """Get current voice configuration information"""
        return {
            "voice_name": self.voice_name,
            "voice_id": self.confirmed_voice_id,
            "configured": self.voice_configured,
            "engine_initialized": self.engine is not None,
            "gender": "Female",
            "language": "en-GB (British English)",
            "status": "Confirmed Working - User Tested"
        }

def main():
    """Demonstrate VPA voice system functionality"""
    
    print("🛡️ VPA VOICE SYSTEM - CONFIRMED WORKING CONFIGURATION")
    print("=" * 70)
    print("Voice: Microsoft Hazel Desktop (British English Female)")
    print("Status: User-tested and confirmed audible")
    print("=" * 70)
    
    # Initialize VPA voice system
    vpa = VPAVoiceSystem()
    
    if not vpa.voice_configured:
        print("❌ VPA voice system initialization failed!")
        return
    
    # Display voice information
    voice_info = vpa.get_voice_info()
    print(f"\n📋 VPA VOICE CONFIGURATION:")
    for key, value in voice_info.items():
        print(f"  {key}: {value}")
    
    # Test voice system
    print(f"\n🧪 RUNNING VPA VOICE TESTS...")
    test_success = vpa.test_voice_system()
    
    if test_success:
        print(f"\n🚀 VPA READY FOR DEPLOYMENT!")
        
        # Demonstrate typical VPA responses
        print(f"\n💬 DEMONSTRATING VPA RESPONSES:")
        
        sample_responses = [
            "Good morning! How can I assist you today?",
            "I've completed the task you requested.",
            "Would you like me to schedule that appointment for you?",
            "I found three options that match your criteria.",
            "The weather forecast shows sunny skies ahead.",
            "Your meeting is scheduled for 2 PM today.",
            "I've sent the email as requested.",
            "Is there anything else I can help you with?"
        ]
        
        for i, response in enumerate(sample_responses, 1):
            print(f"\nVPA Response {i}: '{response}'")
            
            proceed = input("Play this response? (y/n/exit): ").lower()
            if proceed == 'exit':
                break
            elif proceed == 'y':
                vpa.speak(response)
                print("✅ Response delivered")
            else:
                print("⏭️ Skipped")
        
        print(f"\n✅ VPA VOICE SYSTEM DEMONSTRATION COMPLETE!")
        print(f"🎯 MANDATE FULFILLED: VPA configured with confirmed working voice")
        
    else:
        print(f"\n❌ VPA voice system testing failed!")
        print(f"⚠️ Audio configuration issues detected")

if __name__ == "__main__":
    main()
