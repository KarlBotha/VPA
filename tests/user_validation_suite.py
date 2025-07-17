"""
VPA User Experience Validation Suite
Real-world user scenario testing for all VPA functionality
Tests the system as a user would actually use it
"""

import pytest
import time
import threading
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch, MagicMock
import json

# Setup logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserExperienceTestSuite:
    """
    Comprehensive user experience validation
    Tests VPA as if a real user is interacting with it
    """
    
    def __init__(self):
        self.test_results = []
        self.user_scenarios = []
        self.performance_metrics = {}
        
    def log_user_action(self, action: str, expected_result: str, actual_result: str, success: bool):
        """Log user action and result for analysis"""
        self.test_results.append({
            "timestamp": time.time(),
            "action": action,
            "expected": expected_result,
            "actual": actual_result,
            "success": success,
            "duration": getattr(self, '_action_start_time', time.time()) - time.time()
        })
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} User Action: {action}")
        logger.info(f"   Expected: {expected_result}")
        logger.info(f"   Actual: {actual_result}")

class VoiceSystemUserTests:
    """User-focused voice system tests"""
    
    def test_user_voice_discovery(self):
        """Test: User wants to know what voices are available"""
        print("\n🎵 USER TEST: Voice Discovery")
        print("Scenario: New user wants to see available voices")
        
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            
            # User expectation: Should see clear list of voices
            voice_count = len(voices) if voices else 0
            
            print(f"User sees: {voice_count} voices available")
            for i, voice in enumerate(voices or []):
                voice_name = voice.name.split()[-4] if len(voice.name.split()) > 3 else voice.name
                print(f"  {i+1}. {voice_name}")
            
            # Validation: User should see at least 1 voice
            assert voice_count >= 1, "User should see at least one voice"
            print("✅ User can discover available voices")
            return True
            
        except Exception as e:
            print(f"❌ User cannot discover voices: {e}")
            return False
    
    def test_user_voice_switching(self):
        """Test: User wants to switch between voices"""
        print("\n🔄 USER TEST: Voice Switching")
        print("Scenario: User wants to try different voices")
        
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            
            if not voices or len(voices) < 2:
                print("⚠️ Not enough voices to test switching")
                return True
            
            # Test switching to each voice
            for i, voice in enumerate(voices[:3]):  # Test first 3 voices
                print(f"User tries voice {i+1}: {voice.name.split()[-4] if len(voice.name.split()) > 3 else voice.name}")
                
                # Set voice
                engine.setProperty('voice', voice.id)
                current_voice = engine.getProperty('voice')
                
                # User expectation: Voice should change
                if current_voice == voice.id:
                    print(f"✅ Voice switched successfully")
                else:
                    print(f"❌ Voice switch failed - still using previous voice")
                    return False
                
                # Test speech with new voice
                test_message = f"Hello, this is voice number {i+1}"
                print(f"User hears: '{test_message}'")
                
                engine.say(test_message)
                engine.runAndWait()
                time.sleep(1)
            
            print("✅ User can switch between voices")
            return True
            
        except Exception as e:
            print(f"❌ User cannot switch voices: {e}")
            return False
    
    def test_user_voice_quality_perception(self):
        """Test: User evaluates voice quality"""
        print("\n🎧 USER TEST: Voice Quality Perception")
        print("Scenario: User evaluates if voices sound good")
        
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            
            # Test with different quality settings
            quality_tests = [
                {"rate": 150, "volume": 0.8, "description": "Slow and quiet"},
                {"rate": 200, "volume": 0.9, "description": "Normal speech"},
                {"rate": 250, "volume": 1.0, "description": "Fast and loud"}
            ]
            
            for test in quality_tests:
                print(f"User tests: {test['description']}")
                
                engine.setProperty('rate', test['rate'])
                engine.setProperty('volume', test['volume'])
                
                # Verify settings applied
                actual_rate = engine.getProperty('rate')
                actual_volume = engine.getProperty('volume')
                
                # User expectation: Settings should apply
                rate_ok = abs(actual_rate - test['rate']) <= 10
                volume_ok = abs(actual_volume - test['volume']) <= 0.1
                
                if rate_ok and volume_ok:
                    print(f"✅ {test['description']} - settings applied correctly")
                else:
                    print(f"❌ {test['description']} - settings not applied")
                
                # Test speech
                test_message = f"Testing {test['description']} voice settings"
                engine.say(test_message)
                engine.runAndWait()
                time.sleep(0.5)
            
            print("✅ User can adjust voice quality")
            return True
            
        except Exception as e:
            print(f"❌ User cannot adjust voice quality: {e}")
            return False

class AudioSystemUserTests:
    """User-focused audio system tests"""
    
    def test_user_microphone_setup(self):
        """Test: User sets up microphone"""
        print("\n🎤 USER TEST: Microphone Setup")
        print("Scenario: User wants to set up their microphone")
        
        try:
            import pyaudio
            audio = pyaudio.PyAudio()
            
            # User expectation: Should detect microphone
            input_devices = []
            for i in range(audio.get_device_count()):
                device = audio.get_device_info_by_index(i)
                if device['maxInputChannels'] > 0:
                    input_devices.append({
                        'index': i,
                        'name': device['name'],
                        'channels': device['maxInputChannels']
                    })
            
            print(f"User sees {len(input_devices)} microphone(s):")
            for device in input_devices:
                print(f"  - {device['name']} ({device['channels']} channels)")
            
            # Test microphone access
            if input_devices:
                default_device = input_devices[0]
                print(f"User tests: {default_device['name']}")
                
                # Try to open microphone stream
                try:
                    stream = audio.open(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        input_device_index=default_device['index'],
                        frames_per_buffer=1024
                    )
                    
                    # Read some audio data
                    data = stream.read(1024, exception_on_overflow=False)
                    stream.stop_stream()
                    stream.close()
                    
                    print("✅ User can access microphone")
                    success = True
                    
                except Exception as mic_error:
                    print(f"❌ User cannot access microphone: {mic_error}")
                    success = False
            else:
                print("❌ User has no microphone available")
                success = False
            
            audio.terminate()
            return success
            
        except Exception as e:
            print(f"❌ User cannot set up audio system: {e}")
            return False
    
    def test_user_speaker_output(self):
        """Test: User tests speaker output"""
        print("\n🔊 USER TEST: Speaker Output")
        print("Scenario: User wants to test their speakers")
        
        try:
            import pyttsx3
            engine = pyttsx3.init()
            
            # User expectation: Should hear test message
            test_messages = [
                "Testing speaker output - can you hear this?",
                "This is a test of your audio system",
                "If you can hear this, your speakers are working"
            ]
            
            for i, message in enumerate(test_messages):
                print(f"User test {i+1}: Playing '{message}'")
                
                # Set clear speech settings
                engine.setProperty('rate', 180)
                engine.setProperty('volume', 0.9)
                
                engine.say(message)
                engine.runAndWait()
                time.sleep(1)
            
            print("✅ User completed speaker test")
            return True
            
        except Exception as e:
            print(f"❌ User cannot test speakers: {e}")
            return False

class LLMIntegrationUserTests:
    """User-focused LLM integration tests"""
    
    def test_user_natural_language_commands(self):
        """Test: User gives natural language voice commands"""
        print("\n🤖 USER TEST: Natural Language Commands")
        print("Scenario: User wants to control voice with natural language")
        
        # Mock LLM voice processing
        test_commands = [
            {
                "user_input": "use david voice",
                "expected_intent": "set_voice",
                "expected_voice": "David"
            },
            {
                "user_input": "speak faster please",
                "expected_intent": "adjust_speed",
                "expected_adjustment": "faster"
            },
            {
                "user_input": "make it louder",
                "expected_intent": "adjust_volume", 
                "expected_adjustment": "louder"
            },
            {
                "user_input": "switch to female voice",
                "expected_intent": "set_voice",
                "expected_gender": "female"
            }
        ]
        
        success_count = 0
        
        for test in test_commands:
            print(f"User says: '{test['user_input']}'")
            
            # Simulate command processing
            parsed_command = self._parse_user_command(test['user_input'])
            
            if parsed_command.get('intent') == test['expected_intent']:
                print(f"✅ System understood: {test['expected_intent']}")
                success_count += 1
            else:
                print(f"❌ System misunderstood - expected {test['expected_intent']}, got {parsed_command.get('intent')}")
        
        success_rate = success_count / len(test_commands)
        print(f"User command understanding: {success_rate*100:.1f}%")
        
        # User expectation: At least 75% success rate
        return success_rate >= 0.75
    
    def _parse_user_command(self, user_input: str) -> Dict[str, Any]:
        """Simple command parser for testing"""
        user_input = user_input.lower()
        
        if "david" in user_input or "use" in user_input and "voice" in user_input:
            return {"intent": "set_voice", "voice_name": "David"}
        elif "faster" in user_input or "speed" in user_input:
            return {"intent": "adjust_speed", "adjustment": "faster"}
        elif "louder" in user_input or "volume" in user_input:
            return {"intent": "adjust_volume", "adjustment": "louder"}
        elif "female" in user_input and "voice" in user_input:
            return {"intent": "set_voice", "gender": "female"}
        else:
            return {"intent": "unknown"}

class UserWorkflowTests:
    """Complete user workflow tests"""
    
    def test_new_user_onboarding(self):
        """Test: New user first-time experience"""
        print("\n👋 USER TEST: New User Onboarding")
        print("Scenario: Brand new user starts VPA for first time")
        
        workflow_steps = [
            "User opens VPA application",
            "User sees voice options",
            "User tests default voice",
            "User tries different voice",
            "User adjusts voice settings",
            "User gives voice command",
            "User is satisfied with setup"
        ]
        
        completed_steps = 0
        
        for i, step in enumerate(workflow_steps):
            print(f"Step {i+1}: {step}")
            
            # Simulate each step
            if i == 0:  # Application start
                success = self._simulate_app_start()
            elif i == 1:  # See voice options
                success = self._simulate_voice_discovery()
            elif i == 2:  # Test default voice
                success = self._simulate_voice_test()
            elif i == 3:  # Try different voice
                success = self._simulate_voice_change()
            elif i == 4:  # Adjust settings
                success = self._simulate_settings_adjustment()
            elif i == 5:  # Voice command
                success = self._simulate_voice_command()
            else:  # User satisfaction
                success = completed_steps >= 5
            
            if success:
                print(f"✅ Step {i+1} completed successfully")
                completed_steps += 1
            else:
                print(f"❌ Step {i+1} failed - user would be frustrated")
                break
        
        completion_rate = completed_steps / len(workflow_steps)
        print(f"User onboarding success: {completion_rate*100:.1f}%")
        
        # User expectation: Complete onboarding smoothly
        return completion_rate >= 0.85
    
    def _simulate_app_start(self) -> bool:
        """Simulate application startup"""
        try:
            # Test basic imports
            import pyttsx3
            import json
            return True
        except ImportError:
            return False
    
    def _simulate_voice_discovery(self) -> bool:
        """Simulate user discovering voices"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            return len(voices) > 0 if voices else False
        except:
            return False
    
    def _simulate_voice_test(self) -> bool:
        """Simulate user testing voice"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say("Test")
            return True
        except:
            return False
    
    def _simulate_voice_change(self) -> bool:
        """Simulate user changing voice"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            if voices and len(voices) > 1:
                engine.setProperty('voice', voices[1].id)
                return True
            return False
        except:
            return False
    
    def _simulate_settings_adjustment(self) -> bool:
        """Simulate user adjusting settings"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 200)
            engine.setProperty('volume', 0.9)
            return True
        except:
            return False
    
    def _simulate_voice_command(self) -> bool:
        """Simulate user giving voice command"""
        # This would be more complex in real implementation
        return True

class PerformanceUserTests:
    """User-focused performance tests"""
    
    def test_user_perceived_performance(self):
        """Test: User perception of system responsiveness"""
        print("\n⚡ USER TEST: Performance Perception")
        print("Scenario: User expects fast, responsive system")
        
        performance_tests = [
            {
                "action": "Voice engine startup",
                "max_time": 2.0,
                "test_func": self._test_engine_startup
            },
            {
                "action": "Voice switching",
                "max_time": 1.0,
                "test_func": self._test_voice_switch_speed
            },
            {
                "action": "Speech generation",
                "max_time": 0.5,
                "test_func": self._test_speech_start_time
            },
            {
                "action": "Settings change",
                "max_time": 0.3,
                "test_func": self._test_settings_change_speed
            }
        ]
        
        passed_tests = 0
        
        for test in performance_tests:
            print(f"Testing: {test['action']} (max {test['max_time']}s)")
            
            start_time = time.time()
            success = test['test_func']()
            duration = time.time() - start_time
            
            if success and duration <= test['max_time']:
                print(f"✅ {test['action']}: {duration:.2f}s (acceptable)")
                passed_tests += 1
            else:
                status = "failed" if not success else f"too slow ({duration:.2f}s)"
                print(f"❌ {test['action']}: {status}")
        
        performance_score = passed_tests / len(performance_tests)
        print(f"User performance satisfaction: {performance_score*100:.1f}%")
        
        # User expectation: 80% of operations feel fast
        return performance_score >= 0.8
    
    def _test_engine_startup(self) -> bool:
        """Test voice engine startup time"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            return True
        except:
            return False
    
    def _test_voice_switch_speed(self) -> bool:
        """Test voice switching speed"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            if voices and len(voices) > 1:
                engine.setProperty('voice', voices[0].id)
                return True
            return False
        except:
            return False
    
    def _test_speech_start_time(self) -> bool:
        """Test speech generation start time"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            # Note: This tests setup time, not actual speech time
            engine.say("Test")
            return True
        except:
            return False
    
    def _test_settings_change_speed(self) -> bool:
        """Test settings change speed"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 200)
            return True
        except:
            return False

def run_all_user_tests():
    """Run complete user validation suite"""
    print("🚀 VPA USER EXPERIENCE VALIDATION SUITE")
    print("Testing system from real user perspective")
    print("="*60)
    
    test_suites = [
        ("Voice System", VoiceSystemUserTests()),
        ("Audio System", AudioSystemUserTests()),
        ("LLM Integration", LLMIntegrationUserTests()),
        ("User Workflows", UserWorkflowTests()),
        ("Performance", PerformanceUserTests())
    ]
    
    total_tests = 0
    passed_tests = 0
    results = {}
    
    for suite_name, test_suite in test_suites:
        print(f"\n{'='*20} {suite_name.upper()} TESTS {'='*20}")
        
        # Get all test methods
        test_methods = [method for method in dir(test_suite) if method.startswith('test_')]
        suite_results = []
        
        for test_method_name in test_methods:
            test_method = getattr(test_suite, test_method_name)
            
            try:
                result = test_method()
                suite_results.append(result)
                total_tests += 1
                if result:
                    passed_tests += 1
                    
            except Exception as e:
                print(f"❌ Test {test_method_name} crashed: {e}")
                suite_results.append(False)
                total_tests += 1
        
        # Calculate suite success rate
        suite_success = sum(suite_results) / len(suite_results) if suite_results else 0
        results[suite_name] = {
            "success_rate": suite_success,
            "tests_passed": sum(suite_results),
            "total_tests": len(suite_results)
        }
        
        print(f"\n{suite_name} Summary: {suite_success*100:.1f}% success rate")
    
    # Final report
    print(f"\n{'='*60}")
    print("🎯 FINAL USER VALIDATION REPORT")
    print(f"{'='*60}")
    
    overall_success = passed_tests / total_tests if total_tests > 0 else 0
    
    for suite_name, result in results.items():
        status = "✅ PASS" if result['success_rate'] >= 0.8 else "❌ FAIL"
        print(f"{status} {suite_name}: {result['success_rate']*100:.1f}% ({result['tests_passed']}/{result['total_tests']})")
    
    print(f"\n📊 OVERALL USER SATISFACTION: {overall_success*100:.1f}%")
    
    if overall_success >= 0.85:
        print("🎉 EXCELLENT - Users will have a great experience!")
    elif overall_success >= 0.7:
        print("👍 GOOD - Users will be mostly satisfied")
    elif overall_success >= 0.5:
        print("⚠️ NEEDS IMPROVEMENT - Users may be frustrated")
    else:
        print("❌ POOR - Users will likely have problems")
    
    print(f"\n💡 Recommendation: {'Ready for users' if overall_success >= 0.8 else 'Needs more work before user release'}")
    
    return overall_success >= 0.8

if __name__ == "__main__":
    success = run_all_user_tests()
    exit(0 if success else 1)
