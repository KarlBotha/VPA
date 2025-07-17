"""
Voice Switching Fix Test
Tests potential solutions for the voice switching issue identified in diagnostic
"""

import pyttsx3
import time
import logging
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceSwitchingFixTest:
    """Test different approaches to fix voice switching"""
    
    def __init__(self):
        self.engine = None
        self.voices = []
        self._initialize()
    
    def _initialize(self):
        """Initialize engine and get voices"""
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            if voices:
                self.voices = voices
                logger.info(f"Found {len(self.voices)} voices")
                for i, voice in enumerate(self.voices):
                    logger.info(f"Voice {i}: {voice.name}")
            else:
                logger.error("No voices found")
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
    
    def test_all_solutions(self):
        """Test all potential solutions"""
        print("="*80)
        print("🔧 VOICE SWITCHING FIX TESTS")
        print("="*80)
        
        if not self.engine or len(self.voices) < 2:
            print("❌ Cannot test - need engine and at least 2 voices")
            return
        
        solutions = [
            ("Solution 1: Engine Restart", self._test_engine_restart),
            ("Solution 2: Property Reset", self._test_property_reset),
            ("Solution 3: Forced runAndWait", self._test_forced_run_and_wait),
            ("Solution 4: New Engine Per Voice", self._test_new_engine_per_voice),
            ("Solution 5: Voice Index Instead of ID", self._test_voice_index),
        ]
        
        results = {}
        
        for solution_name, test_func in solutions:
            print(f"\n{'='*60}")
            print(f"🧪 {solution_name}")
            print(f"{'='*60}")
            
            try:
                result = test_func()
                results[solution_name] = result
                print(f"Result: {'✅ SUCCESS' if result else '❌ FAILED'}")
            except Exception as e:
                print(f"Result: ❌ ERROR - {e}")
                results[solution_name] = False
        
        self._summarize_results(results)
    
    def _test_engine_restart(self) -> bool:
        """Test if restarting engine helps with voice switching"""
        print("Testing engine restart approach...")
        
        try:
            # Test with first voice
            voice1 = self.voices[0]
            voice2 = self.voices[1]
            
            print(f"🎵 Testing: {voice1.name}")
            self.engine.setProperty('voice', voice1.id)
            test_text1 = f"Hello, I am {voice1.name.split()[-1]}, voice number 1."
            print(f"Speaking: {test_text1}")
            self.engine.say(test_text1)
            self.engine.runAndWait()
            
            # Restart engine
            print("🔄 Restarting engine...")
            self.engine.stop()
            self.engine = pyttsx3.init()
            
            # Test with second voice
            print(f"🎵 Testing: {voice2.name}")
            self.engine.setProperty('voice', voice2.id)
            test_text2 = f"Hello, I am {voice2.name.split()[-1]}, voice number 2."
            print(f"Speaking: {test_text2}")
            self.engine.say(test_text2)
            self.engine.runAndWait()
            
            print("🎯 Did you hear two different voices? (manual verification needed)")
            return True  # Cannot auto-verify audio
            
        except Exception as e:
            print(f"❌ Engine restart test failed: {e}")
            return False
    
    def _test_property_reset(self) -> bool:
        """Test if resetting properties helps"""
        print("Testing property reset approach...")
        
        try:
            voice1 = self.voices[0]
            voice2 = self.voices[1]
            
            # Voice 1 with property reset
            print(f"🎵 Testing: {voice1.name}")
            self.engine.setProperty('voice', voice1.id)
            self.engine.setProperty('rate', 180)  # Reset rate
            self.engine.setProperty('volume', 0.9)  # Reset volume
            test_text1 = f"Voice one: {voice1.name.split()[-1]}"
            print(f"Speaking: {test_text1}")
            self.engine.say(test_text1)
            self.engine.runAndWait()
            
            # Small pause
            time.sleep(1)
            
            # Voice 2 with property reset
            print(f"🎵 Testing: {voice2.name}")
            self.engine.setProperty('voice', voice2.id)
            self.engine.setProperty('rate', 180)  # Reset rate again
            self.engine.setProperty('volume', 0.9)  # Reset volume again
            test_text2 = f"Voice two: {voice2.name.split()[-1]}"
            print(f"Speaking: {test_text2}")
            self.engine.say(test_text2)
            self.engine.runAndWait()
            
            print("🎯 Did you hear two different voices? (manual verification needed)")
            return True
            
        except Exception as e:
            print(f"❌ Property reset test failed: {e}")
            return False
    
    def _test_forced_run_and_wait(self) -> bool:
        """Test if forcing runAndWait between voice changes helps"""
        print("Testing forced runAndWait approach...")
        
        try:
            voice1 = self.voices[0]
            voice2 = self.voices[1]
            
            # Voice 1
            print(f"🎵 Testing: {voice1.name}")
            self.engine.setProperty('voice', voice1.id)
            self.engine.runAndWait()  # Force wait after voice change
            test_text1 = f"First voice: {voice1.name.split()[-1]}"
            print(f"Speaking: {test_text1}")
            self.engine.say(test_text1)
            self.engine.runAndWait()
            
            # Clear and wait
            time.sleep(1)
            
            # Voice 2
            print(f"🎵 Testing: {voice2.name}")
            self.engine.setProperty('voice', voice2.id)
            self.engine.runAndWait()  # Force wait after voice change
            test_text2 = f"Second voice: {voice2.name.split()[-1]}"
            print(f"Speaking: {test_text2}")
            self.engine.say(test_text2)
            self.engine.runAndWait()
            
            print("🎯 Did you hear two different voices? (manual verification needed)")
            return True
            
        except Exception as e:
            print(f"❌ Forced runAndWait test failed: {e}")
            return False
    
    def _test_new_engine_per_voice(self) -> bool:
        """Test creating new engine instance for each voice"""
        print("Testing new engine per voice approach...")
        
        try:
            voice1 = self.voices[0]
            voice2 = self.voices[1]
            
            # Engine 1 for voice 1
            print(f"🎵 Testing: {voice1.name} (new engine)")
            engine1 = pyttsx3.init()
            engine1.setProperty('voice', voice1.id)
            test_text1 = f"Engine one: {voice1.name.split()[-1]}"
            print(f"Speaking: {test_text1}")
            engine1.say(test_text1)
            engine1.runAndWait()
            engine1.stop()
            
            # Small pause
            time.sleep(1)
            
            # Engine 2 for voice 2
            print(f"🎵 Testing: {voice2.name} (new engine)")
            engine2 = pyttsx3.init()
            engine2.setProperty('voice', voice2.id)
            test_text2 = f"Engine two: {voice2.name.split()[-1]}"
            print(f"Speaking: {test_text2}")
            engine2.say(test_text2)
            engine2.runAndWait()
            engine2.stop()
            
            print("🎯 Did you hear two different voices? (manual verification needed)")
            return True
            
        except Exception as e:
            print(f"❌ New engine per voice test failed: {e}")
            return False
    
    def _test_voice_index(self) -> bool:
        """Test using voice index instead of ID"""
        print("Testing voice index approach...")
        
        try:
            # Method: Use voice objects directly
            voice1 = self.voices[0]
            voice2 = self.voices[1]
            
            # Voice 1 by index
            print(f"🎵 Testing: {voice1.name} (by index)")
            voices_list = self.engine.getProperty('voices')
            self.engine.setProperty('voice', voices_list[0].id)
            test_text1 = f"Index zero: {voice1.name.split()[-1]}"
            print(f"Speaking: {test_text1}")
            self.engine.say(test_text1)
            self.engine.runAndWait()
            
            # Small pause
            time.sleep(1)
            
            # Voice 2 by index
            print(f"🎵 Testing: {voice2.name} (by index)")
            self.engine.setProperty('voice', voices_list[1].id)
            test_text2 = f"Index one: {voice2.name.split()[-1]}"
            print(f"Speaking: {test_text2}")
            self.engine.say(test_text2)
            self.engine.runAndWait()
            
            print("🎯 Did you hear two different voices? (manual verification needed)")
            return True
            
        except Exception as e:
            print(f"❌ Voice index test failed: {e}")
            return False
    
    def _summarize_results(self, results: Dict[str, bool]):
        """Summarize test results"""
        print(f"\n{'='*80}")
        print("📊 SOLUTION TEST SUMMARY")
        print(f"{'='*80}")
        
        successful_solutions = []
        failed_solutions = []
        
        for solution, success in results.items():
            if success:
                successful_solutions.append(solution)
                print(f"✅ {solution}")
            else:
                failed_solutions.append(solution)
                print(f"❌ {solution}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        
        if successful_solutions:
            print(f"✅ {len(successful_solutions)} solution(s) completed without errors")
            print("🎯 Next step: Run user validation test to confirm audio differences")
            print("🔧 Implement the most practical working solution")
        else:
            print("❌ All solutions encountered errors")
            print("🔍 Consider alternative TTS libraries:")
            print("   → Azure Cognitive Services Speech SDK")
            print("   → Google Text-to-Speech")
            print("   → Windows SAPI direct integration")
        
        print(f"\n⚠️ IMPORTANT: These tests require manual audio verification")
        print("🎧 You need to listen and confirm if voices sound different")

def main():
    """Main test function"""
    print("🔧 VPA Voice Switching Fix Tests")
    print("This will test potential solutions for voice switching issue")
    
    try:
        tester = VoiceSwitchingFixTest()
        tester.test_all_solutions()
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n📝 Press Enter to exit...")

if __name__ == "__main__":
    main()
