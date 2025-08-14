"""
Direct Windows SAPI Voice Switching Fix
Bypasses pyttsx3 voice switching using Windows SAPI directly
Based on user feedback: only heard voice 1 with all previous solutions
"""

import win32com.client
import time
import logging
from typing import List, Dict, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DirectSAPIVoiceFix:
    """Direct Windows SAPI voice management bypassing pyttsx3"""
    
    def __init__(self):
        self.sapi_voice = None  # Will be COM object
        self.available_voices = []
        self._initialize_sapi()
    
    def _initialize_sapi(self):
        """Initialize direct SAPI connection"""
        try:
            self.sapi_voice = win32com.client.Dispatch("SAPI.SpVoice")
            
            # Get all available voices
            voices = self.sapi_voice.GetVoices()
            self.available_voices = []
            
            for i in range(voices.Count):
                voice = voices.Item(i)
                voice_info = {
                    'index': i,
                    'name': voice.GetDescription(),
                    'id': voice.Id,
                    'object': voice
                }
                self.available_voices.append(voice_info)
                logger.info(f"SAPI Voice {i}: {voice_info['name']}")
            
            logger.info(f"Direct SAPI initialized with {len(self.available_voices)} voices")
            
        except Exception as e:
            logger.error(f"Direct SAPI initialization failed: {e}")
    
    def test_direct_sapi_switching(self):
        """Test voice switching using direct SAPI"""
        print("="*80)
        print("🔧 DIRECT WINDOWS SAPI VOICE SWITCHING TEST")
        print("This bypasses pyttsx3 completely")
        print("="*80)
        
        if not self.sapi_voice or len(self.available_voices) < 2:
            print("❌ Cannot test - need SAPI and at least 2 voices")
            return False
        
        try:
            # Test each voice individually
            for i, voice_info in enumerate(self.available_voices[:3]):  # Test first 3 voices
                print(f"\n{'='*60}")
                print(f"🎵 Testing Voice {i+1}: {voice_info['name']}")
                print(f"{'='*60}")
                
                # Set voice directly using SAPI
                self.sapi_voice.Voice = voice_info['object']
                
                # Configure speech properties
                self.sapi_voice.Rate = 2  # Normal speed
                self.sapi_voice.Volume = 90  # 90% volume
                
                # Test speech
                test_text = f"Hello, this is voice number {i+1}, {voice_info['name'].split()[-1]}. Can you hear the difference?"
                print(f"Speaking: {test_text}")
                
                self.sapi_voice.Speak(test_text)
                
                # Small pause between voices
                time.sleep(1.5)
            
            print(f"\n{'='*80}")
            print("🎯 DIRECT SAPI TEST COMPLETE")
            print("Did you hear clearly different voices this time?")
            print("This method bypasses all pyttsx3 limitations")
            print("="*80)
            
            return True
            
        except Exception as e:
            print(f"❌ Direct SAPI test failed: {e}")
            return False
    
    def test_voice_with_different_rates(self):
        """Test same voice with different rates to ensure system works"""
        print("\n" + "="*60)
        print("🔧 VOICE RATE TEST (Same voice, different speeds)")
        print("="*60)
        
        if not self.available_voices:
            print("❌ No voices available")
            return False
        
        try:
            # Use first voice with different rates
            voice_info = self.available_voices[0]
            self.sapi_voice.Voice = voice_info['object']
            
            rates = [
                (-5, "Very Slow"),
                (0, "Normal"),
                (5, "Fast"),
                (8, "Very Fast")
            ]
            
            for rate_value, rate_name in rates:
                print(f"🎵 Testing {rate_name} (Rate: {rate_value})")
                self.sapi_voice.Rate = rate_value
                self.sapi_voice.Volume = 90
                
                text = f"This is {rate_name} speech at rate {rate_value}"
                print(f"Speaking: {text}")
                self.sapi_voice.Speak(text)
                time.sleep(1)
            
            print("✅ Rate test complete - you should have heard different speeds")
            return True
            
        except Exception as e:
            print(f"❌ Rate test failed: {e}")
            return False
    
    def test_comprehensive_voice_differences(self):
        """Comprehensive test with maximum voice differentiation"""
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE VOICE DIFFERENTIATION TEST")
        print("Testing with enhanced voice properties for maximum difference")
        print("="*80)
        
        if len(self.available_voices) < 2:
            print("❌ Need at least 2 voices for comparison")
            return False
        
        try:
            # Test configurations for maximum difference
            test_configs = [
                {
                    'voice_index': 0,
                    'rate': -3,
                    'volume': 85,
                    'text': "Voice one: I am the first voice speaking slowly and clearly."
                },
                {
                    'voice_index': 1,
                    'rate': 3,
                    'volume': 95,
                    'text': "Voice two: I am the second voice speaking faster and louder."
                }
            ]
            
            # Add third voice if available
            if len(self.available_voices) >= 3:
                test_configs.append({
                    'voice_index': 2,
                    'rate': 0,
                    'volume': 90,
                    'text': "Voice three: I am the third voice with normal settings."
                })
            
            for i, config in enumerate(test_configs):
                if config['voice_index'] < len(self.available_voices):
                    voice_info = self.available_voices[config['voice_index']]
                    
                    print(f"\n🎵 Voice {i+1}: {voice_info['name']}")
                    print(f"   Rate: {config['rate']}, Volume: {config['volume']}")
                    
                    # Set voice and properties
                    self.sapi_voice.Voice = voice_info['object']
                    self.sapi_voice.Rate = config['rate']
                    self.sapi_voice.Volume = config['volume']
                    
                    print(f"Speaking: {config['text']}")
                    self.sapi_voice.Speak(config['text'])
                    
                    # Pause between voices
                    time.sleep(2)
            
            print(f"\n{'='*80}")
            print("🎯 COMPREHENSIVE TEST COMPLETE")
            print("This test used maximum voice differentiation")
            print("If you still only heard one voice, the issue may be:")
            print("  1. Limited Windows voice installation")
            print("  2. Audio driver/system configuration")
            print("  3. Need to install additional Windows voices")
            print("="*80)
            
            return True
            
        except Exception as e:
            print(f"❌ Comprehensive test failed: {e}")
            return False
    
    def get_voice_report(self):
        """Generate detailed voice system report"""
        print(f"\n{'='*80}")
        print("📊 DETAILED VOICE SYSTEM REPORT")
        print("="*80)
        
        print(f"🔍 Total Voices Detected: {len(self.available_voices)}")
        
        for i, voice_info in enumerate(self.available_voices):
            print(f"\nVoice {i+1}:")
            print(f"  Name: {voice_info['name']}")
            print(f"  Index: {voice_info['index']}")
            print(f"  ID: {voice_info['id']}")
            
            # Try to get more voice details
            try:
                voice_obj = voice_info['object']
                # Get voice attributes if available
                attrs = voice_obj.GetAttribute("Name")
                if attrs:
                    print(f"  Attributes: {attrs}")
            except:
                pass
        
        print(f"\n💡 RECOMMENDATIONS:")
        
        if len(self.available_voices) >= 3:
            print("✅ Good voice selection available")
            print("🔧 Voice switching should work with direct SAPI")
        elif len(self.available_voices) == 2:
            print("⚠️ Limited voice selection (2 voices)")
            print("🔧 Should still work but limited variety")
        else:
            print("❌ Insufficient voices for proper testing")
            print("💿 Consider installing additional Windows voices:")
            print("   → Windows Settings > Time & Language > Speech")
            print("   → Add more voices from Microsoft")
        
        print(f"\n🎯 NEXT STEPS:")
        print("1. Try the comprehensive test above")
        print("2. If still only one voice, check Windows voice installation")
        print("3. Consider implementing Azure Cognitive Services as fallback")

def main():
    """Main test function"""
    print("🔧 Direct Windows SAPI Voice Switching Fix")
    print("This bypasses pyttsx3 to test Windows SAPI directly")
    print("Based on feedback: Only heard voice 1 with previous tests")
    
    try:
        sapi_tester = DirectSAPIVoiceFix()
        
        # Generate voice report first
        sapi_tester.get_voice_report()
        
        # Test voice rate differences (should work)
        print("\n" + "🔧 Testing rate differences first...")
        sapi_tester.test_voice_with_different_rates()
        
        # Test direct SAPI voice switching
        print("\n" + "🔧 Testing direct SAPI voice switching...")
        sapi_tester.test_direct_sapi_switching()
        
        # Comprehensive test with maximum differentiation
        print("\n" + "🔧 Running comprehensive differentiation test...")
        sapi_tester.test_comprehensive_voice_differences()
        
        print(f"\n{'='*80}")
        print("🎯 ALL TESTS COMPLETE")
        print("Please provide feedback:")
        print("1. Did you hear different speeds in the rate test?")
        print("2. Did you hear different voices in the SAPI test?")
        print("3. Did you hear clear differences in the comprehensive test?")
        print("="*80)
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n📝 Press Enter to exit...")

if __name__ == "__main__":
    main()
