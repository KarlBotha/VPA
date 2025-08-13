"""
Voice Validation Test - User Confirmation Required
Tests voice switching with user validation to confirm different voices are audible
"""

import pyttsx3
import time
import logging
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceValidationTest:
    """Voice validation test requiring user confirmation"""
    
    def __init__(self):
        self.engine = None
        self.available_voices = []
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize pyttsx3 engine"""
        try:
            self.engine = pyttsx3.init()
            logger.info("✅ pyttsx3 engine initialized")
            
            # Get available system voices - pragmatic approach
            try:
                voices = self.engine.getProperty('voices')
                self.available_voices = []
                
                if voices:
                    try:
                        # Try direct iteration (ignore type checker)
                        for voice in voices:  # type: ignore
                            if voice and hasattr(voice, 'name') and hasattr(voice, 'id'):
                                self.available_voices.append(voice)
                                logger.info(f"   Found voice: {voice.name}")
                    except Exception as iteration_error:
                        try:
                            # Try index-based access
                            for i in range(10):  # reasonable limit
                                voice = voices[i]  # type: ignore
                                if voice and hasattr(voice, 'name') and hasattr(voice, 'id'):
                                    self.available_voices.append(voice)
                                    logger.info(f"   Found voice: {voice.name}")
                        except Exception as index_error:
                            logger.error(f"Could not access voices: iteration={iteration_error}, index={index_error}")
                
                logger.info(f"✅ Total voices loaded: {len(self.available_voices)}")
                    
            except Exception as e:
                logger.error(f"Critical error getting voices: {e}")
                self.available_voices = []
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize pyttsx3: {e}")
    
    def test_voice_switching_with_validation(self):
        """Test voice switching with user validation"""
        print("\n" + "="*80)
        print("🎵 VOICE SWITCHING VALIDATION TEST")
        print("="*80)
        print("This test will play each available voice and ask you to confirm")
        print("if you can hear the difference between voices.")
        print(f"Available voices: {len(self.available_voices)}")
        
        if not self.engine or not self.available_voices:
            print("❌ Cannot proceed - no voices available")
            return False
        
        print(f"\n🔊 Testing {len(self.available_voices)} system voices...")
        print("⚠️  Please ensure your speakers/headphones are on!")
        
        # Wait for user ready
        input("\n📢 Press Enter when ready to test voice switching...")
        
        voice_test_results = []
        
        for i, voice in enumerate(self.available_voices):
            print(f"\n{'='*60}")
            print(f"🎵 TESTING SYSTEM VOICE {i+1}/{len(self.available_voices)}")
            print(f"Voice Name: {voice.name}")
            print(f"Voice ID: {voice.id}")
            print(f"{'='*60}")
            
            try:
                # Set the voice
                self.engine.setProperty('voice', voice.id)
                self.engine.setProperty('rate', 180)  # Clear speaking rate
                self.engine.setProperty('volume', 0.9)  # High volume
                
                # Create unique test message for this voice
                test_message = (f"Hello, this is voice number {i+1}, "
                              f"my name is {voice.name.split('-')[1] if '-' in voice.name else 'System Voice'}. "
                              f"Can you hear me clearly? I am voice {i+1} of {len(self.available_voices)}.")
                
                print(f"🔊 Speaking: {test_message}")
                print("⏳ Please listen carefully...")
                
                # Speak the message
                self.engine.say(test_message)
                self.engine.runAndWait()
                
                # Wait a moment for audio to finish
                time.sleep(1)
                
                # Ask user for confirmation
                print(f"\n❓ VOICE VALIDATION QUESTION:")
                print(f"Did you hear voice {i+1} ({voice.name}) speak the message?")
                print("Options:")
                print("  y = Yes, I heard this voice clearly")
                print("  n = No, I didn't hear anything")
                print("  s = Same as previous voice (no difference)")
                print("  d = Different from previous voice")
                
                while True:
                    user_response = input(f"Your response for voice {i+1} [y/n/s/d]: ").lower().strip()
                    if user_response in ['y', 'n', 's', 'd']:
                        break
                    print("Please enter y, n, s, or d")
                
                # Record result
                voice_test_results.append({
                    'voice_index': i+1,
                    'voice_name': voice.name,
                    'voice_id': voice.id,
                    'user_heard': user_response in ['y', 'd'],
                    'user_response': user_response,
                    'same_as_previous': user_response == 's'
                })
                
                print(f"✅ Voice {i+1} test recorded: {user_response}")
                
                # Small pause before next voice
                if i < len(self.available_voices) - 1:
                    print("\n⏳ Preparing next voice test...")
                    time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error testing voice {i+1}: {e}")
                voice_test_results.append({
                    'voice_index': i+1,
                    'voice_name': voice.name,
                    'voice_id': voice.id,
                    'user_heard': False,
                    'user_response': 'error',
                    'error': str(e)
                })
        
        # Analyze results
        self._analyze_voice_test_results(voice_test_results)
        return voice_test_results
    
    def _analyze_voice_test_results(self, results: List[Dict[str, Any]]):
        """Analyze user validation results"""
        print(f"\n{'='*80}")
        print("🎯 VOICE VALIDATION ANALYSIS")
        print(f"{'='*80}")
        
        total_voices = len(results)
        voices_heard = sum(1 for r in results if r['user_heard'])
        voices_same = sum(1 for r in results if r['same_as_previous'])
        voices_different = sum(1 for r in results if r['user_response'] == 'd')
        voices_not_heard = sum(1 for r in results if r['user_response'] == 'n')
        
        print(f"📊 Test Results Summary:")
        print(f"   Total voices tested: {total_voices}")
        print(f"   Voices user heard: {voices_heard}")
        print(f"   Voices sounding same: {voices_same}")
        print(f"   Voices sounding different: {voices_different}")
        print(f"   Voices not heard: {voices_not_heard}")
        
        print(f"\n📋 Detailed Results:")
        for result in results:
            status = "✅" if result['user_heard'] else "❌"
            response_desc = {
                'y': 'Heard clearly',
                'n': 'Not heard',
                's': 'Same as previous',
                'd': 'Different from previous',
                'error': 'Test error'
            }.get(result['user_response'], 'Unknown')
            
            print(f"   {status} Voice {result['voice_index']}: {result['voice_name']} - {response_desc}")
        
        # Provide recommendations
        print(f"\n💡 Analysis & Recommendations:")
        
        if voices_heard == 0:
            print("❌ CRITICAL: No voices heard - audio system problem")
            print("   → Check speaker/headphone connection")
            print("   → Check system volume")
            print("   → Check Windows audio settings")
            
        elif voices_heard == 1:
            print("⚠️  WARNING: Only 1 voice heard - voice switching not working")
            print("   → pyttsx3 may not be switching voices properly")
            print("   → Windows SAPI voice switching issue")
            print("   → Need to investigate voice engine property setting")
            
        elif voices_same > 0:
            print(f"⚠️  WARNING: {voices_same} voices sound the same")
            print("   → Some system voices may be identical")
            print("   → Voice mapping needs refinement")
            
        elif voices_different == total_voices - 1:  # -1 because first voice has no previous
            print("🎯 EXCELLENT: All voices sound different!")
            print("   → Voice switching working perfectly")
            print("   → Ready for 13-voice catalog implementation")
            
        else:
            print("🔄 MIXED RESULTS: Some voice switching working")
            print(f"   → {voices_different} voices detected as different")
            print("   → May need voice engine optimization")
        
        print(f"\n🚦 FINAL STATUS:")
        if voices_heard >= 2 and voices_different >= 1:
            print("✅ VOICE SYSTEM: FUNCTIONAL - Proceed with implementation")
        elif voices_heard == 1:
            print("⚠️  VOICE SYSTEM: LIMITED - Only David voice working")
        else:
            print("❌ VOICE SYSTEM: FAILED - Needs troubleshooting")
            
        return {
            'total_voices': total_voices,
            'voices_heard': voices_heard,
            'voices_different': voices_different,
            'functional': voices_heard >= 2 and voices_different >= 1
        }

def main():
    """Main function to run voice validation test"""
    print("🚀 VPA Voice Validation Test")
    print("This test requires your feedback to validate voice switching")
    
    try:
        validator = VoiceValidationTest()
        results = validator.test_voice_switching_with_validation()
        
        if results:
            print(f"\n✅ Voice validation test completed")
            print("Please review the analysis above before proceeding with implementation")
        else:
            print(f"\n❌ Voice validation test failed")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.error(f"Voice validation error: {e}")
    
    input("\n📝 Press Enter to exit...")

if __name__ == "__main__":
    main()
