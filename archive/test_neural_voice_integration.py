"""
Neural Voice Integration Test Suite
Comprehensive testing and validation for Edge-TTS neural voice system
Provides demo functionality and user validation interface

AUDIT COMPLIANCE:
- Complete test coverage for all neural voice functions
- User validation interface for voice testing
- Integration verification with existing VPA architecture
- Evidence collection for audit reporting
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import sys
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from audio.neural_voice_engine import NeuralVoiceEngine, NeuralVoice
from audio.vpa_voice_system import VPAVoiceSystem

class NeuralVoiceTestSuite:
    """
    Comprehensive test suite for neural voice integration
    Validates all functionality and provides user demo interface
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.output_dir = output_dir or Path("test_results")
        self.output_dir.mkdir(exist_ok=True)
        
        # Test results storage
        self.test_results: Dict[str, Any] = {}
        self.test_log: List[Dict[str, Any]] = []
        
        # Initialize logging for tests
        self._setup_test_logging()
        
        self.logger.info("Neural Voice Test Suite initialized")
    
    def _setup_test_logging(self):
        """Setup detailed logging for test execution"""
        log_file = self.output_dir / f"neural_voice_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.info(f"Test logging initialized: {log_file}")
    
    def run_complete_test_suite(self) -> Dict[str, Any]:
        """
        Run complete test suite for neural voice integration
        
        Returns:
            Dict containing comprehensive test results
        """
        print("🧪 NEURAL VOICE INTEGRATION TEST SUITE")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test 1: System Availability
        print("\n📋 Test 1: System Availability Check")
        availability_results = self._test_system_availability()
        self._log_test("system_availability", availability_results)
        self._print_test_result("System Availability", availability_results["success"])
        
        # Test 2: Neural Engine Initialization
        print("\n📋 Test 2: Neural Engine Initialization")
        init_results = self._test_neural_engine_initialization()
        self._log_test("neural_engine_init", init_results)
        self._print_test_result("Neural Engine Init", init_results["success"])
        
        # Test 3: Voice Catalog Validation
        print("\n📋 Test 3: Voice Catalog Validation")
        catalog_results = self._test_voice_catalog()
        self._log_test("voice_catalog", catalog_results)
        self._print_test_result("Voice Catalog", catalog_results["success"])
        
        # Test 4: Voice Selection
        print("\n📋 Test 4: Voice Selection Testing")
        selection_results = self._test_voice_selection()
        self._log_test("voice_selection", selection_results)
        self._print_test_result("Voice Selection", selection_results["success"])
        
        # Test 5: Speech Synthesis
        print("\n📋 Test 5: Speech Synthesis Testing")
        synthesis_results = self._test_speech_synthesis()
        self._log_test("speech_synthesis", synthesis_results)
        self._print_test_result("Speech Synthesis", synthesis_results["success"])
        
        # Test 6: VPA Integration
        print("\n📋 Test 6: VPA Integration Testing")
        integration_results = self._test_vpa_integration()
        self._log_test("vpa_integration", integration_results)
        self._print_test_result("VPA Integration", integration_results["success"])
        
        # Test 7: Performance Validation
        print("\n📋 Test 7: Performance Validation")
        performance_results = self._test_performance()
        self._log_test("performance", performance_results)
        self._print_test_result("Performance", performance_results["success"])
        
        # Calculate overall results
        total_time = time.time() - start_time
        
        # Compile final results
        final_results = {
            "test_suite": "Neural Voice Integration",
            "timestamp": datetime.now().isoformat(),
            "total_time": round(total_time, 2),
            "tests": {
                "system_availability": availability_results,
                "neural_engine_init": init_results,
                "voice_catalog": catalog_results,
                "voice_selection": selection_results,
                "speech_synthesis": synthesis_results,
                "vpa_integration": integration_results,
                "performance": performance_results
            },
            "summary": self._calculate_test_summary()
        }
        
        # Save results
        self._save_test_results(final_results)
        
        # Print summary
        self._print_test_summary(final_results)
        
        return final_results
    
    def _test_system_availability(self) -> Dict[str, Any]:
        """Test system dependencies and availability"""
        results = {
            "success": True,
            "details": {},
            "errors": []
        }
        
        try:
            # Test Edge-TTS import
            try:
                import edge_tts
                results["details"]["edge_tts"] = True
            except ImportError as e:
                results["details"]["edge_tts"] = False
                results["errors"].append(f"edge-tts not available: {e}")
                results["success"] = False
            
            # Test pygame import
            try:
                import pygame
                results["details"]["pygame"] = True
            except ImportError as e:
                results["details"]["pygame"] = False
                results["errors"].append(f"pygame not available: {e}")
                results["success"] = False
            
            # Test asyncio
            try:
                import asyncio
                results["details"]["asyncio"] = True
            except ImportError as e:
                results["details"]["asyncio"] = False
                results["errors"].append(f"asyncio not available: {e}")
                results["success"] = False
            
            # Test pathlib
            try:
                from pathlib import Path
                results["details"]["pathlib"] = True
            except ImportError as e:
                results["details"]["pathlib"] = False
                results["errors"].append(f"pathlib not available: {e}")
                results["success"] = False
            
        except Exception as e:
            results["success"] = False
            results["errors"].append(f"System availability test failed: {e}")
        
        return results
    
    def _test_neural_engine_initialization(self) -> Dict[str, Any]:
        """Test neural voice engine initialization"""
        results = {
            "success": False,
            "details": {},
            "errors": []
        }
        
        try:
            # Initialize neural engine
            start_time = time.time()
            neural_engine = NeuralVoiceEngine()
            init_time = time.time() - start_time
            
            results["details"]["initialization_time"] = round(init_time, 3)
            results["details"]["pygame_initialized"] = neural_engine.pygame_initialized
            results["details"]["async_loop_running"] = neural_engine.loop is not None
            results["details"]["voice_catalog_size"] = len(neural_engine.voice_catalog)
            results["details"]["current_voice"] = neural_engine.current_voice.name if neural_engine.current_voice else None
            
            # Validate engine state
            if neural_engine.pygame_initialized and neural_engine.voice_catalog:
                results["success"] = True
            else:
                results["errors"].append("Engine initialization incomplete")
            
            # Cleanup
            neural_engine.shutdown()
            
        except Exception as e:
            results["errors"].append(f"Neural engine initialization failed: {e}")
        
        return results
    
    def _test_voice_catalog(self) -> Dict[str, Any]:
        """Test voice catalog completeness and accuracy"""
        results = {
            "success": False,
            "details": {},
            "errors": []
        }
        
        try:
            neural_engine = NeuralVoiceEngine()
            
            # Expected voices from integration specification
            expected_voices = [
                "Andrew", "Christopher", "Guy", "Roger", "Eric", "Steffan",  # Male
                "Emma", "Ava", "Aria", "Jenny", "Libby", "Michelle"  # Female
            ]
            
            available_voices = neural_engine.get_available_voices()
            available_names = [voice.name for voice in available_voices]
            
            results["details"]["total_voices"] = len(available_voices)
            results["details"]["expected_voices"] = len(expected_voices)
            results["details"]["available_names"] = available_names
            
            # Check voice completeness
            missing_voices = [name for name in expected_voices if name not in available_names]
            extra_voices = [name for name in available_names if name not in expected_voices]
            
            results["details"]["missing_voices"] = missing_voices
            results["details"]["extra_voices"] = extra_voices
            
            # Validate voice properties
            valid_voices = 0
            for voice in available_voices:
                if (voice.voice_id and voice.name and voice.gender and 
                    voice.language and voice.sample_phrase):
                    valid_voices += 1
            
            results["details"]["valid_voices"] = valid_voices
            results["details"]["voice_validation_rate"] = round(valid_voices / len(available_voices), 2) if available_voices else 0
            
            # Check gender distribution
            male_voices = len([v for v in available_voices if v.gender == "Male"])
            female_voices = len([v for v in available_voices if v.gender == "Female"])
            
            results["details"]["male_voices"] = male_voices
            results["details"]["female_voices"] = female_voices
            
            # Success criteria: all expected voices present and valid
            if len(missing_voices) == 0 and valid_voices == len(available_voices):
                results["success"] = True
            else:
                if missing_voices:
                    results["errors"].append(f"Missing voices: {missing_voices}")
                if valid_voices != len(available_voices):
                    results["errors"].append(f"Invalid voice configurations: {len(available_voices) - valid_voices}")
            
            neural_engine.shutdown()
            
        except Exception as e:
            results["errors"].append(f"Voice catalog test failed: {e}")
        
        return results
    
    def _test_voice_selection(self) -> Dict[str, Any]:
        """Test voice selection functionality"""
        results = {
            "success": False,
            "details": {},
            "errors": []
        }
        
        try:
            neural_engine = NeuralVoiceEngine()
            
            # Test voice selection by name
            test_voices = ["Aria", "Guy", "Jenny", "Andrew"]
            selection_results = {}
            
            for voice_name in test_voices:
                try:
                    success = neural_engine.set_voice(voice_name)
                    current_voice = neural_engine.current_voice.name if neural_engine.current_voice else None
                    
                    selection_results[voice_name] = {
                        "selection_success": success,
                        "voice_set": current_voice == voice_name
                    }
                    
                except Exception as e:
                    selection_results[voice_name] = {
                        "selection_success": False,
                        "error": str(e)
                    }
            
            results["details"]["voice_selections"] = selection_results
            
            # Test voice selection by ID
            test_voice_id = "en-US-AriaNeural"
            id_selection_success = neural_engine.set_voice(test_voice_id)
            results["details"]["id_selection"] = {
                "voice_id": test_voice_id,
                "success": id_selection_success,
                "current_voice": neural_engine.current_voice.name if neural_engine.current_voice else None
            }
            
            # Success criteria: majority of selections work
            successful_selections = sum(1 for r in selection_results.values() if r.get("selection_success", False))
            selection_rate = successful_selections / len(test_voices) if test_voices else 0
            
            results["details"]["selection_rate"] = round(selection_rate, 2)
            
            if selection_rate >= 0.75 and id_selection_success:  # 75% success rate threshold
                results["success"] = True
            else:
                results["errors"].append(f"Voice selection rate too low: {selection_rate}")
            
            neural_engine.shutdown()
            
        except Exception as e:
            results["errors"].append(f"Voice selection test failed: {e}")
        
        return results
    
    def _test_speech_synthesis(self) -> Dict[str, Any]:
        """Test speech synthesis functionality"""
        results = {
            "success": False,
            "details": {},
            "errors": []
        }
        
        try:
            neural_engine = NeuralVoiceEngine()
            
            # Test speech synthesis with different voices
            test_phrases = [
                "Hello, this is a test of the neural voice system.",
                "The quick brown fox jumps over the lazy dog.",
                "Testing speech synthesis with Edge TTS neural voices."
            ]
            
            test_voices = ["Aria", "Guy", "Jenny"]
            synthesis_results = {}
            
            for voice_name in test_voices:
                voice_results = {}
                
                # Set voice
                if neural_engine.set_voice(voice_name):
                    for i, phrase in enumerate(test_phrases):
                        try:
                            start_time = time.time()
                            success = neural_engine.speak(phrase, blocking=True)
                            synthesis_time = time.time() - start_time
                            
                            voice_results[f"phrase_{i+1}"] = {
                                "text": phrase,
                                "success": success,
                                "synthesis_time": round(synthesis_time, 3)
                            }
                            
                            # Small delay between phrases
                            time.sleep(0.5)
                            
                        except Exception as e:
                            voice_results[f"phrase_{i+1}"] = {
                                "text": phrase,
                                "success": False,
                                "error": str(e)
                            }
                else:
                    voice_results["voice_selection_failed"] = True
                
                synthesis_results[voice_name] = voice_results
            
            results["details"]["synthesis_tests"] = synthesis_results
            
            # Calculate success rate
            total_tests = 0
            successful_tests = 0
            
            for voice_data in synthesis_results.values():
                for test_data in voice_data.values():
                    if isinstance(test_data, dict) and "success" in test_data:
                        total_tests += 1
                        if test_data["success"]:
                            successful_tests += 1
            
            success_rate = successful_tests / total_tests if total_tests > 0 else 0
            results["details"]["success_rate"] = round(success_rate, 2)
            results["details"]["total_tests"] = total_tests
            results["details"]["successful_tests"] = successful_tests
            
            # Success criteria: >75% synthesis success rate
            if success_rate >= 0.75:
                results["success"] = True
            else:
                results["errors"].append(f"Speech synthesis success rate too low: {success_rate}")
            
            neural_engine.shutdown()
            
        except Exception as e:
            results["errors"].append(f"Speech synthesis test failed: {e}")
        
        return results
    
    def _test_vpa_integration(self) -> Dict[str, Any]:
        """Test VPA integration layer"""
        results = {
            "success": False,
            "details": {},
            "errors": []
        }
        
        try:
            # Initialize VPA voice system
            vpa_system = VPAVoiceSystem(enable_legacy_fallback=False)
            
            # Test system status
            status = vpa_system.get_system_status()
            results["details"]["system_status"] = status
            
            # Test voice listing
            available_voices = vpa_system.get_available_voices()
            results["details"]["available_voices_count"] = len(available_voices)
            results["details"]["neural_voices"] = len([v for v in available_voices if v["system"] == "neural"])
            
            # Test voice selection through VPA interface
            test_result = vpa_system.set_voice("Aria")
            results["details"]["vpa_voice_selection"] = test_result
            
            # Test current voice retrieval
            current_voice = vpa_system.get_current_voice()
            results["details"]["current_voice"] = current_voice
            
            # Test speech through VPA interface
            speech_test = vpa_system.speak("Testing VPA integration with neural voices.", blocking=True)
            results["details"]["vpa_speech_test"] = speech_test
            
            # Success criteria
            if (status["initialization_complete"] and 
                len(available_voices) >= 10 and 
                test_result and 
                speech_test):
                results["success"] = True
            else:
                results["errors"].append("VPA integration validation failed")
            
            vpa_system.shutdown()
            
        except Exception as e:
            results["errors"].append(f"VPA integration test failed: {e}")
        
        return results
    
    def _test_performance(self) -> Dict[str, Any]:
        """Test performance characteristics"""
        results = {
            "success": False,
            "details": {},
            "errors": []
        }
        
        try:
            neural_engine = NeuralVoiceEngine()
            
            # Performance test parameters
            test_phrase = "This is a performance test for neural voice synthesis."
            test_iterations = 3
            performance_data = {}
            
            # Test with different voices
            test_voices = ["Aria", "Guy", "Jenny"]
            
            for voice_name in test_voices:
                if neural_engine.set_voice(voice_name):
                    voice_times = []
                    
                    for i in range(test_iterations):
                        start_time = time.time()
                        success = neural_engine.speak(test_phrase, blocking=True)
                        total_time = time.time() - start_time
                        
                        if success:
                            voice_times.append(total_time)
                        
                        time.sleep(0.5)  # Small delay between tests
                    
                    if voice_times:
                        performance_data[voice_name] = {
                            "average_time": round(sum(voice_times) / len(voice_times), 3),
                            "min_time": round(min(voice_times), 3),
                            "max_time": round(max(voice_times), 3),
                            "iterations": len(voice_times)
                        }
            
            results["details"]["performance_data"] = performance_data
            
            # Calculate overall performance metrics
            if performance_data:
                all_times = []
                for data in performance_data.values():
                    all_times.extend([data["average_time"]])
                
                overall_avg = sum(all_times) / len(all_times)
                results["details"]["overall_average_time"] = round(overall_avg, 3)
                
                # Success criteria: average synthesis time < 5 seconds
                if overall_avg < 5.0:
                    results["success"] = True
                else:
                    results["errors"].append(f"Performance too slow: {overall_avg}s average")
            else:
                results["errors"].append("No performance data collected")
            
            neural_engine.shutdown()
            
        except Exception as e:
            results["errors"].append(f"Performance test failed: {e}")
        
        return results
    
    def demo_voice_selection(self) -> Dict[str, bool]:
        """
        Interactive demo for voice selection and testing
        Returns results for user validation
        """
        print("\n🎭 NEURAL VOICE DEMO - Voice Selection Test")
        print("=" * 50)
        
        demo_results = {}
        
        try:
            vpa_system = VPAVoiceSystem(enable_legacy_fallback=False)
            available_voices = vpa_system.get_available_voices()
            
            print(f"\n📢 Available Neural Voices: {len(available_voices)}")
            
            # Demo selected voices with sample phrases
            demo_voices = ["Aria", "Guy", "Jenny", "Andrew", "Emma", "Christopher"]
            
            for voice_name in demo_voices:
                print(f"\n🔊 Testing voice: {voice_name}")
                
                # Set voice
                if vpa_system.set_voice(voice_name):
                    # Get voice info
                    current_voice = vpa_system.get_current_voice()
                    if current_voice:
                        print(f"   Voice: {current_voice['name']} ({current_voice['gender']}, {current_voice['region']})")
                        print(f"   Description: {current_voice['description']}")
                    
                    # Test voice
                    success = vpa_system.test_voice()
                    demo_results[voice_name] = success
                    
                    if success:
                        print("   ✅ Voice test successful")
                    else:
                        print("   ❌ Voice test failed")
                    
                    # Wait between voice tests
                    time.sleep(2)
                else:
                    print(f"   ❌ Failed to set voice: {voice_name}")
                    demo_results[voice_name] = False
            
            vpa_system.shutdown()
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
        
        return demo_results
    
    def _calculate_test_summary(self) -> Dict[str, Any]:
        """Calculate overall test suite summary"""
        total_tests = len(self.test_log)
        passed_tests = sum(1 for test in self.test_log if test.get("result", {}).get("success", False))
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": round(passed_tests / total_tests, 2) if total_tests > 0 else 0,
            "overall_success": passed_tests == total_tests
        }
    
    def _log_test(self, test_name: str, result: Dict[str, Any]):
        """Log test result"""
        self.test_log.append({
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "result": result
        })
    
    def _print_test_result(self, test_name: str, success: bool):
        """Print formatted test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    def _print_test_summary(self, results: Dict[str, Any]):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🏆 NEURAL VOICE INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        summary = results["summary"]
        print(f"\nTotal Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate'] * 100:.1f}%")
        print(f"Overall Result: {'✅ SUCCESS' if summary['overall_success'] else '❌ FAILURE'}")
        
        print(f"\nTotal Test Time: {results['total_time']} seconds")
        
        # Individual test results
        print("\n📋 Individual Test Results:")
        for test_name, test_result in results["tests"].items():
            status = "✅ PASS" if test_result["success"] else "❌ FAIL"
            print(f"   {status} - {test_name.replace('_', ' ').title()}")
            
            if test_result.get("errors"):
                for error in test_result["errors"]:
                    print(f"        Error: {error}")
    
    def _save_test_results(self, results: Dict[str, Any]):
        """Save test results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = self.output_dir / f"neural_voice_test_results_{timestamp}.json"
        
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Test results saved: {results_file}")
            
        except Exception as e:
            print(f"❌ Failed to save test results: {e}")

def main():
    """Main test suite execution"""
    print("🧪 Neural Voice Integration Test Suite")
    print("Starting comprehensive validation...")
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run test suite
    test_suite = NeuralVoiceTestSuite()
    
    # Run complete test suite
    results = test_suite.run_complete_test_suite()
    
    # Run demo
    print("\n" + "=" * 60)
    demo_results = test_suite.demo_voice_selection()
    
    # Final validation
    overall_success = results["summary"]["overall_success"]
    demo_success_rate = sum(demo_results.values()) / len(demo_results) if demo_results else 0
    
    print("\n" + "=" * 60)
    print("🎯 FINAL VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Test Suite Success: {'✅ PASS' if overall_success else '❌ FAIL'}")
    print(f"Demo Success Rate: {demo_success_rate * 100:.1f}%")
    print(f"Integration Ready: {'✅ YES' if overall_success and demo_success_rate >= 0.75 else '❌ NO'}")
    
    if overall_success and demo_success_rate >= 0.75:
        print("\n🎉 Neural Voice Integration VALIDATED - Ready for deployment!")
    else:
        print("\n⚠️ Neural Voice Integration requires attention before deployment")
    
    return overall_success and demo_success_rate >= 0.75

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
