"""
Complete 13-Voice Test Script for VPA System
Tests all available voices with clear identification
"""

import pyttsx3
import time
import logging
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceTestSystem:
    """Complete voice testing system for all 13 voices"""
    
    def __init__(self):
        self.engine = None
        self.available_voices = []
        self.voice_catalog = self._create_voice_catalog()
        self._initialize_engine()
    
    def _create_voice_catalog(self) -> List[Dict[str, Any]]:
        """Create the 13-voice catalog as specified in the VPA system"""
        return [
            {"id": "voice_01", "name": "David", "gender": "Male", "purpose": "Professional male"},
            {"id": "voice_02", "name": "Zira", "gender": "Female", "purpose": "Professional female"},
            {"id": "voice_03", "name": "Mark", "gender": "Male", "purpose": "Casual male"},
            {"id": "voice_04", "name": "Hazel", "gender": "Female", "purpose": "Friendly female"},
            {"id": "voice_05", "name": "Helena", "gender": "Female", "purpose": "Assistant female"},
            {"id": "voice_06", "name": "James", "gender": "Male", "purpose": "Executive male"},
            {"id": "voice_07", "name": "Catherine", "gender": "Female", "purpose": "Narrator female"},
            {"id": "voice_08", "name": "Richard", "gender": "Male", "purpose": "Technical male"},
            {"id": "voice_09", "name": "Eva", "gender": "Female", "purpose": "Assistant female"},
            {"id": "voice_10", "name": "Sean", "gender": "Male", "purpose": "Backup male"},
            {"id": "voice_11", "name": "Sabina", "gender": "Female", "purpose": "Backup female"},
            {"id": "voice_12", "name": "Alex", "gender": "Male", "purpose": "Fallback male"},
            {"id": "voice_13", "name": "System", "gender": "Neutral", "purpose": "Default fallback"}
        ]
    
    def _initialize_engine(self):
        """Initialize the pyttsx3 engine"""
        try:
            self.engine = pyttsx3.init()
            logger.info("✅ pyttsx3 engine initialized successfully")
            
            # Get available system voices
            voices = self.engine.getProperty('voices')
            if voices:
                self.available_voices = voices
                logger.info(f"✅ Found {len(voices)} system voices")
                for i, voice in enumerate(voices):
                    logger.info(f"   Voice {i}: {voice.name} (ID: {voice.id})")
            else:
                logger.error("❌ No system voices detected")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize pyttsx3: {e}")
    
    def _find_best_voice_match(self, target_name: str, target_gender: str) -> str:
        """Find the best matching system voice for a catalog voice"""
        if not self.available_voices:
            return None
        
        # First, try exact name match
        for voice in self.available_voices:
            if target_name.lower() in voice.name.lower():
                return voice.id
        
        # Then try gender-based matching
        gender_keywords = {
            "Male": ["david", "mark", "james", "richard", "sean", "alex", "male"],
            "Female": ["zira", "hazel", "helena", "catherine", "eva", "sabina", "female"],
            "Neutral": ["system", "default"]
        }
        
        for voice in self.available_voices:
            voice_name_lower = voice.name.lower()
            for keyword in gender_keywords.get(target_gender, []):
                if keyword in voice_name_lower:
                    return voice.id
        
        # Fallback to first available voice
        return self.available_voices[0].id
    
    def test_individual_voice(self, voice_info: Dict[str, Any], voice_number: int):
        """Test a single voice with detailed information"""
        print(f"\n{'='*60}")
        print(f"🎵 TESTING VOICE {voice_number}/13")
        print(f"Voice ID: {voice_info['id']}")
        print(f"Name: {voice_info['name']}")
        print(f"Gender: {voice_info['gender']}")
        print(f"Purpose: {voice_info['purpose']}")
        print(f"{'='*60}")
        
        if not self.engine:
            print("❌ Engine not available")
            return False
        
        # Find best matching system voice
        system_voice_id = self._find_best_voice_match(voice_info['name'], voice_info['gender'])
        
        if not system_voice_id:
            print(f"❌ No system voice found for {voice_info['name']}")
            return False
        
        try:
            # Set voice properties
            self.engine.setProperty('voice', system_voice_id)
            self.engine.setProperty('rate', 180)  # Slightly slower for clarity
            self.engine.setProperty('volume', 0.9)  # High volume
            
            # Create test message
            test_message = (f"Hello, I am {voice_info['name']}, "
                          f"a {voice_info['gender'].lower()} voice "
                          f"designed for {voice_info['purpose']}. "
                          f"This is voice number {voice_number} of 13 voices in your VPA system.")
            
            print(f"🔊 Speaking: {test_message}")
            print("⏳ Please listen...")
            
            # Speak the message
            self.engine.say(test_message)
            self.engine.runAndWait()
            
            # Short pause between voices
            time.sleep(1)
            
            print(f"✅ Voice {voice_number} ({voice_info['name']}) test completed")
            return True
            
        except Exception as e:
            print(f"❌ Error testing voice {voice_info['name']}: {e}")
            return False
    
    def test_all_voices(self):
        """Test all 13 voices in the catalog"""
        print("\n" + "="*80)
        print("🎵 VPA VOICE SYSTEM - COMPLETE 13-VOICE TEST")
        print("="*80)
        print(f"📊 System Information:")
        print(f"   Available System Voices: {len(self.available_voices)}")
        print(f"   VPA Voice Catalog: {len(self.voice_catalog)} voices")
        print(f"   pyttsx3 Engine: {'✅ Ready' if self.engine else '❌ Not Available'}")
        
        if not self.engine:
            print("\n❌ Cannot proceed - pyttsx3 engine not available")
            return
        
        print(f"\n🔊 Starting voice tests...")
        print("⚠️  Please ensure your speakers/headphones are on and volume is up!")
        
        # Wait for user to adjust audio
        input("\n📢 Press Enter when ready to hear all 13 voices...")
        
        successful_tests = 0
        failed_tests = 0
        
        # Test each voice in the catalog
        for i, voice_info in enumerate(self.voice_catalog, 1):
            success = self.test_individual_voice(voice_info, i)
            if success:
                successful_tests += 1
            else:
                failed_tests += 1
            
            # Pause between voices for clarity
            if i < len(self.voice_catalog):
                time.sleep(2)
        
        # Final summary
        print(f"\n{'='*80}")
        print("🎉 VOICE TEST SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Successful voice tests: {successful_tests}/13")
        print(f"❌ Failed voice tests: {failed_tests}/13")
        print(f"📊 Success rate: {(successful_tests/13)*100:.1f}%")
        
        if successful_tests == 13:
            print("🎯 PERFECT! All 13 voices are working!")
        elif successful_tests > 0:
            print(f"🔄 {successful_tests} voices are working, {failed_tests} need attention")
        else:
            print("❌ No voices working - system needs troubleshooting")
        
        print(f"\n💡 Note: Some voices may use the same system voice if fewer than 13 unique voices are available")
        print("="*80)

def main():
    """Main function to run the complete voice test"""
    print("🚀 VPA Voice System - Complete Voice Test")
    print("Testing all 13 voices in your Virtual Personal Assistant")
    
    try:
        # Create and run voice test system
        voice_tester = VoiceTestSystem()
        voice_tester.test_all_voices()
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.error(f"Voice test error: {e}")
    
    input("\n📝 Press Enter to exit...")

if __name__ == "__main__":
    main()
