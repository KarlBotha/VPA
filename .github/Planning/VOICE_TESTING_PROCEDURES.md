# [DEPRECATED] Voice Testing Procedures

## ⚠️ DEPRECATION NOTICE

This document has been moved to its proper location according to VPA architecture standards.

**Please use the updated version at: [docs/voice/testing/VOICE_TESTING_PROCEDURES.md](docs/voice/testing/VOICE_TESTING_PROCEDURES.md)**

This file is maintained temporarily for reference but will be removed in a future update.

---

## Overview

This document outlines comprehensive testing procedures for the VPA Audio/Voice System. It provides structured methodologies for testing all 13 voices, evaluating voice quality, verifying performance metrics, and validating integration with other system components.

## 1. Voice Catalog Testing

### 1.1 Basic Catalog Validation

| Test ID | Test Description | Expected Outcome | Verification Method |
|---------|-----------------|------------------|-------------------|
| VC-001 | Initialize voice system and verify catalog size | Exactly 13 voices available | Count voices from `get_available_voices()` |
| VC-002 | Verify all required voice names are present | All 13 specified voices exist | Check each voice by name |
| VC-003 | Verify voice metadata completeness | Each voice has complete metadata | Validate all voice info fields |
| VC-004 | Verify default voice selection | "Aria" selected as default | Check `current_voice` |

```python
def test_voice_catalog_basic():
    """Basic voice catalog validation tests"""
    from audio.voice_system import audio_system
    
    # Test VC-001: Catalog size
    voices = audio_system.get_available_voices()
    assert len(voices) == 13, f"Expected 13 voices, found {len(voices)}"
    
    # Test VC-002: Required voices
    required_voices = [
        "Aria", "Guy", "Jenny", "Christopher", "Emma", "Steffan", 
        "Michelle", "Roger", "Ava", "Eric", "Libby", "Andrew", "System"
    ]
    
    voice_names = [v["name"] for v in voices]
    for required in required_voices:
        assert required in voice_names, f"Required voice missing: {required}"
    
    # Test VC-003: Metadata completeness
    for voice in voices:
        assert "name" in voice, "Voice missing name"
        assert "gender" in voice, "Voice missing gender"
        assert "description" in voice, "Voice missing description"
        assert "voice_id" in voice, "Voice missing voice_id"
    
    # Test VC-004: Default voice
    voice_info = audio_system.get_voice_info()
    assert voice_info["name"] == "Aria", f"Expected default voice 'Aria', found {voice_info['name']}"
```

### 1.2 Voice Selection Testing

| Test ID | Test Description | Expected Outcome | Verification Method |
|---------|-----------------|------------------|-------------------|
| VS-001 | Set voice by name for all voices | All voices selectable by name | Check return value and current voice |
| VS-002 | Set voice by ID for all voices | All voices selectable by ID | Check return value and current voice |
| VS-003 | Try invalid voice name | Return False, keep current voice | Verify return and unchanged state |
| VS-004 | Voice persistence across sessions | Voice selection persisted | Restart and verify selection |

```python
def test_voice_selection():
    """Voice selection testing"""
    from audio.voice_system import audio_system
    
    # Get all voices
    voices = audio_system.get_available_voices()
    original_voice = audio_system.get_voice_info()["name"]
    
    # Test VS-001: Set by name
    for voice in voices:
        voice_name = voice["name"]
        success = audio_system.set_voice(voice_name)
        assert success, f"Failed to set voice to {voice_name}"
        
        # Verify voice change
        current = audio_system.get_voice_info()
        assert current["name"] == voice_name, f"Voice not set correctly: expected {voice_name}, got {current['name']}"
    
    # Test VS-003: Invalid voice name
    invalid_voice = "NonExistentVoice"
    success = audio_system.set_voice(invalid_voice)
    assert not success, "Setting invalid voice should return False"
    
    current = audio_system.get_voice_info()
    assert current["name"] != invalid_voice, "Voice should not change to invalid name"
    
    # Restore original voice
    audio_system.set_voice(original_voice)
```

## 2. Voice Quality Testing

### 2.1 Objective Quality Metrics

| Test ID | Test Description | Expected Outcome | Verification Method |
|---------|-----------------|------------------|-------------------|
| QM-001 | Verify audio sampling rate | 24kHz or higher | Check audio file properties |
| QM-002 | Verify audio bit depth | 16-bit or higher | Check audio file properties |
| QM-003 | Verify stereo output | Stereo audio channels | Check audio file properties |
| QM-004 | Measure signal-to-noise ratio | SNR > 40dB | Audio analysis tool |

### 2.2 Subjective Quality Assessment

| Test ID | Test Description | Expected Outcome | Verification Method |
|---------|-----------------|------------------|-------------------|
| SQ-001 | Voice naturalness assessment | Score ≥ 4/5 for all voices | Human evaluator rating |
| SQ-002 | Pronunciation clarity | Score ≥ 4/5 for all voices | Human evaluator rating |
| SQ-003 | Emotional appropriateness | Score ≥ 3.5/5 for all voices | Human evaluator rating |
| SQ-004 | Overall voice pleasantness | Score ≥ 4/5 for all voices | Human evaluator rating |

#### Voice Quality Assessment Form

For each voice, rate the following qualities on a scale of 1-5 (1=Poor, 5=Excellent):

| Voice Name | Naturalness | Clarity | Emotional Tone | Pleasantness | Overall Rating |
|------------|------------|---------|----------------|--------------|----------------|
| Aria       |            |         |                |              |                |
| Guy        |            |         |                |              |                |
| Jenny      |            |         |                |              |                |
| Christopher|            |         |                |              |                |
| Emma       |            |         |                |              |                |
| Steffan    |            |         |                |              |                |
| Michelle   |            |         |                |              |                |
| Roger      |            |         |                |              |                |
| Ava        |            |         |                |              |                |
| Eric       |            |         |                |              |                |
| Libby      |            |         |                |              |                |
| Andrew     |            |         |                |              |                |

### 2.3 Voice-Specific Test Phrases

These phrases are designed to test specific aspects of each voice:

| Voice | Test Phrase | Testing Aspect |
|-------|------------|----------------|
| Aria | "Welcome to your personal assistant. I'm here to help you with scheduling, information, and productivity." | Professional tone, complex words |
| Guy | "I've analyzed your calendar and found three potential conflicts in next week's schedule." | Authoritative delivery, clarity |
| Jenny | "Hi there! I'm happy to help you with anything you need today. Just let me know how I can assist." | Warmth, friendliness |
| Christopher | "The technical specifications include a quad-core processor with hyperthreading and virtualization support." | Technical terms, articulation |
| Emma | "Your presentation is scheduled for tomorrow at 2:30 PM in the main conference room." | Clarity, professional tone |
| Steffan | "Good morning! I've prepared a summary of yesterday's meeting highlights and action items." | Accent consistency, clarity |
| Michelle | "Would you like me to continue reading the article, or would you prefer a summary of the key points?" | Conversational flow, questions |
| Roger | "Important security alert: your system has detected unusual activity on your network." | Authority, emphasis |
| Ava | "Hey! Just a quick reminder about your dinner reservation tonight at 7:30." | Casual tone, naturalness |
| Eric | "Great job! You've completed all your tasks for today. Would you like to see tomorrow's schedule?" | Enthusiasm, encouragement |
| Libby | "I've found several interesting articles on that topic. Shall I read the headlines for you?" | British pronunciation, intonation |
| Andrew | "The quarterly report indicates a fifteen percent increase in revenue compared to last year." | Business terms, measured pace |

## 3. Performance Testing

### 3.1 Response Time Testing

| Test ID | Test Description | Expected Outcome | Verification Method |
|---------|-----------------|------------------|-------------------|
| RT-001 | Measure synthesis time for short phrases (< 50 chars) | < 1 second | Time measurement |
| RT-002 | Measure synthesis time for medium phrases (50-150 chars) | < 1.5 seconds | Time measurement |
| RT-003 | Measure synthesis time for long phrases (> 150 chars) | < 2 seconds | Time measurement |
| RT-004 | Measure playback initialization time | < 200ms | Time measurement |

```python
import time
import asyncio

async def test_voice_performance():
    """Test voice synthesis performance"""
    from audio.voice_system import audio_system
    
    # Test phrases of varying length
    test_phrases = {
        "short": "Hello, how can I help you today?",
        "medium": "I've analyzed your calendar and found that you have three meetings scheduled for tomorrow, including a team check-in at 10 AM.",
        "long": "According to the weather forecast, tomorrow will be partly cloudy with temperatures reaching a high of 76 degrees Fahrenheit in the afternoon, dropping to around 62 degrees overnight. There's a 30% chance of scattered showers in the evening."
    }
    
    # Test each voice with each phrase length
    voices_to_test = ["Aria", "Guy", "Steffan", "Jenny"]
    results = {}
    
    for voice in voices_to_test:
        audio_system.set_voice(voice)
        voice_results = {}
        
        for length, phrase in test_phrases.items():
            start_time = time.time()
            success = await audio_system.speak_async(phrase)
            end_time = time.time()
            
            synthesis_time = end_time - start_time
            voice_results[length] = synthesis_time
            
            # Check against requirements
            max_time = 1.0 if length == "short" else 1.5 if length == "medium" else 2.0
            assert synthesis_time <= max_time, f"Voice {voice} exceeded time limit for {length} phrase: {synthesis_time:.2f}s > {max_time}s"
        
        results[voice] = voice_results
    
    return results
```

### 3.2 Concurrent Operation Testing

| Test ID | Test Description | Expected Outcome | Verification Method |
|---------|-----------------|------------------|-------------------|
| CO-001 | Queue multiple voice requests | All processed in sequence | Verify completion order |
| CO-002 | Attempt parallel synthesis | Limited to defined concurrency | Verify concurrent operations |
| CO-003 | Measure performance under load | Minimal degradation | Compare with baseline |
| CO-004 | Long-running synthesis (>30s) | Completes without errors | Monitor for errors |

## 4. Integration Testing

### 4.1 Event Bus Integration

| Test ID | Test Description | Expected Outcome | Verification Method |
|---------|-----------------|------------------|-------------------|
| EB-001 | Voice synthesis event emission | Events emitted correctly | Event listener verification |
| EB-002 | Voice change notification | Change events propagated | Event listener verification |
| EB-003 | Response to system events | Proper behavior on events | Trigger system events |
| EB-004 | Error event handling | Error events properly emitted | Force error conditions |

```python
import asyncio

async def test_voice_event_integration():
    """Test voice system integration with event bus"""
    from audio.voice_system import audio_system
    from vpa.core.events import event_bus
    
    # Set up event listener
    received_events = []
    
    def event_handler(event_data):
        received_events.append(event_data)
    
    # Subscribe to voice events
    unsubscribe_fn = event_bus.subscribe("voice.synthesis.complete", event_handler)
    
    try:
        # Trigger voice synthesis
        await audio_system.speak_async("This is a test of event integration.")
        
        # Give events time to propagate
        await asyncio.sleep(0.1)
        
        # Verify event emission
        assert len(received_events) > 0, "No voice events received"
        assert "duration" in received_events[0], "Event missing duration data"
        assert "voice" in received_events[0], "Event missing voice data"
        
    finally:
        # Clean up subscription
        unsubscribe_fn()
```

### 4.2 Plugin Integration

| Test ID | Test Description | Expected Outcome | Verification Method |
|---------|-----------------|------------------|-------------------|
| PI-001 | Plugin voice request handling | Correct voice used | Verify through plugin API |
| PI-002 | Plugin-specific voice settings | Settings applied correctly | Check voice parameters |
| PI-003 | Multiple plugins voice usage | No conflicts | Test with multiple plugins |
| PI-004 | Plugin voice interruption | Graceful handling | Force interruptions |

### 4.3 GUI Integration

| Test ID | Test Description | Expected Outcome | Verification Method |
|---------|-----------------|------------------|-------------------|
| GI-001 | Voice selection in settings | Selection applied correctly | Verify through UI |
| GI-002 | Voice test functionality | Test voice plays correctly | Trigger through UI |
| GI-003 | Visual feedback during speech | UI indicators update | Observe UI during speech |
| GI-004 | Error handling in UI | Error messages displayed | Force error conditions |

## 5. Comprehensive Voice Testing Suite

### 5.1 Automated Test Suite

```python
import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, List, Any

class VoiceTestSuite:
    """Comprehensive voice testing suite"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.results = {}
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all voice tests"""
        self.logger.info("Starting comprehensive voice test suite")
        start_time = time.time()
        
        # Test categories
        await self._test_voice_catalog()
        await self._test_voice_selection()
        await self._test_voice_synthesis()
        await self._test_voice_performance()
        await self._test_event_integration()
        
        end_time = time.time()
        self.results["total_time"] = end_time - start_time
        self.results["overall_success"] = all(
            category.get("success", False) 
            for category in self.results.values() 
            if isinstance(category, dict)
        )
        
        self.logger.info(f"Voice test suite completed in {end_time - start_time:.2f}s")
        self.logger.info(f"Overall success: {self.results['overall_success']}")
        
        return self.results
    
    async def _test_voice_catalog(self) -> None:
        """Test voice catalog completeness"""
        from audio.voice_system import audio_system
        
        try:
            self.logger.info("Testing voice catalog")
            catalog_results = {"success": True, "tests": {}}
            
            # Test catalog size
            voices = audio_system.get_available_voices()
            catalog_results["tests"]["catalog_size"] = {
                "expected": 13,
                "actual": len(voices),
                "success": len(voices) == 13
            }
            if len(voices) != 13:
                catalog_results["success"] = False
            
            # Test required voices
            required_voices = [
                "Aria", "Guy", "Jenny", "Christopher", "Emma", "Steffan",
                "Michelle", "Roger", "Ava", "Eric", "Libby", "Andrew", "System"
            ]
            
            voice_names = [v.get("name") for v in voices]
            missing_voices = [name for name in required_voices if name not in voice_names]
            
            catalog_results["tests"]["required_voices"] = {
                "missing": missing_voices,
                "success": len(missing_voices) == 0
            }
            if missing_voices:
                catalog_results["success"] = False
            
            # Metadata completeness
            invalid_metadata = []
            for voice in voices:
                if not all(key in voice for key in ["name", "gender", "description", "voice_id"]):
                    invalid_metadata.append(voice.get("name", "Unknown"))
            
            catalog_results["tests"]["metadata"] = {
                "invalid": invalid_metadata,
                "success": len(invalid_metadata) == 0
            }
            if invalid_metadata:
                catalog_results["success"] = False
                
            self.results["voice_catalog"] = catalog_results
            self.logger.info(f"Voice catalog tests completed: {catalog_results['success']}")
            
        except Exception as e:
            self.logger.error(f"Voice catalog test failed: {e}")
            self.results["voice_catalog"] = {
                "success": False,
                "error": str(e)
            }
    
    async def _test_voice_selection(self) -> None:
        """Test voice selection capabilities"""
        # Implementation similar to test_voice_catalog
        pass
    
    async def _test_voice_synthesis(self) -> None:
        """Test voice synthesis for all voices"""
        # Implementation similar to test_voice_catalog
        pass
    
    async def _test_voice_performance(self) -> None:
        """Test voice synthesis performance"""
        # Implementation similar to test_voice_performance shown earlier
        pass
    
    async def _test_event_integration(self) -> None:
        """Test integration with event bus"""
        # Implementation similar to test_voice_event_integration shown earlier
        pass
        
    def generate_report(self, output_path: Path) -> Path:
        """Generate HTML test report"""
        # Create HTML report from results
        report_path = output_path / f"voice_test_report_{time.time()}.html"
        
        # Report generation logic
        # ...
        
        return report_path
```

### 5.2 Manual Test Protocol

1. **Voice Quality Assessment Procedure**:
   - Listen to each voice with its test phrase
   - Complete assessment form for each voice
   - Rate overall clarity, naturalness, and appropriate tone
   - Note any specific issues or strengths

2. **Voice Use Case Validation**:
   - Test each voice in its recommended context
   - Verify appropriate tone and delivery for the context
   - Rate effectiveness for the intended use case

3. **User Acceptance Testing**:
   - Gather feedback from at least 3 different users
   - Have users rate each voice on a 1-5 scale
   - Document preferred voices for different use cases
   - Note any accessibility concerns or preferences

## 6. Voice Testing Deliverables

### 6.1 Required Test Reports

1. **Voice Catalog Validation Report**:
   - Confirmation of 13-voice catalog completeness
   - Verification of all required voice properties
   - Documentation of any deviations or issues

2. **Voice Quality Assessment Report**:
   - Objective metrics for each voice
   - Subjective quality scores
   - Recommendations for optimal use cases

3. **Performance Metrics Report**:
   - Synthesis time measurements for all voices
   - Comparison against performance targets
   - Identification of optimization opportunities

4. **Integration Test Report**:
   - Event bus integration verification
   - Plugin integration verification
   - GUI integration verification

### 6.2 Test Report Template

```markdown
# Voice System Test Report

## Test Summary
- **Test Date**: [DATE]
- **Test Environment**: [ENVIRONMENT]
- **Test Suite Version**: [VERSION]
- **Overall Result**: [PASS/FAIL]

## Voice Catalog Tests
- **Catalog Size**: [PASS/FAIL] - Found [X]/13 voices
- **Required Voices**: [PASS/FAIL] - [DETAILS]
- **Metadata Completeness**: [PASS/FAIL] - [DETAILS]

## Voice Quality Tests
- **Audio Quality**: [PASS/FAIL] - [DETAILS]
- **Voice Naturalness**: [AVERAGE SCORE]/5
- **Pronunciation Clarity**: [AVERAGE SCORE]/5

## Performance Tests
- **Average Synthesis Time**: [TIME]s (Target: <2.0s)
- **Fastest Voice**: [VOICE] - [TIME]s
- **Slowest Voice**: [VOICE] - [TIME]s
- **Performance Under Load**: [PASS/FAIL]

## Integration Tests
- **Event Bus Integration**: [PASS/FAIL]
- **Plugin Integration**: [PASS/FAIL]
- **GUI Integration**: [PASS/FAIL]

## Issues and Recommendations
- [LIST OF ISSUES]
- [RECOMMENDATIONS]

## Detailed Results
[DETAILED TEST RESULTS]
```

## 7. Continuous Voice Testing

### 7.1 Automated Testing Integration

1. **CI/CD Pipeline Integration**:
   - Include voice tests in continuous integration
   - Run basic tests on each commit
   - Run comprehensive tests before release

2. **Regression Test Suite**:
   - Maintain baseline quality metrics
   - Compare new test results against baseline
   - Alert on significant deviations

3. **Performance Trend Monitoring**:
   - Track synthesis performance over time
   - Monitor for degradation or improvement
   - Document impact of system changes

### 7.2 Voice Quality Monitoring

1. **Regular Quality Assessments**:
   - Schedule monthly quality reviews
   - Rotate human evaluators
   - Document changes in perceived quality

2. **User Feedback Collection**:
   - Implement feedback mechanism in UI
   - Collect voice-specific feedback
   - Analyze feedback trends

3. **Service Level Monitoring**:
   - Monitor Edge-TTS service availability
   - Track fallback frequency to Windows SAPI
   - Document any service disruptions

## Conclusion

This comprehensive voice testing protocol ensures all aspects of the VPA voice system are thoroughly tested and validated. By following these procedures, the system can maintain high-quality voice output, consistent performance, and seamless integration with other components.

---

*Voice Testing Procedures document completed on August 27, 2025*
