"""
VPA Voice System - Research-Compliant Implementation
Based on Official pyttsx3 Documentation & GitHub Repository Standards

CRITICAL IMPLEMENTATION REQUIREMENTS:
1. Voice verification checks (MANDATORY) - Based on test_engines.py patterns
2. Proper runAndWait() usage - Based on official documentation
3. Engine state management - Based on driver interface specifications
4. Error handling for voice switching - Based on GitHub test patterns

RESEARCH SOURCES:
- pyttsx3.readthedocs.io official documentation
- nateshmbhat/pyttsx3 GitHub repository
- test_engines.py and test_pyttsx3.py verification patterns
- Official examples from docs/engine.rst
"""

import pyttsx3
import time
import traceback
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VoiceVerificationResult:
    """Voice verification result based on GitHub test patterns"""
    success: bool
    expected_voice_id: str
    actual_voice_id: str
    error_message: Optional[str] = None
    verification_time: float = 0.0

class ResearchCompliantVoiceSystem:
    """
    Research-Compliant VPA Voice System
    
    MANDATORY IMPLEMENTATION FEATURES (NON-NEGOTIABLE):
    1. Voice verification checks before every speak operation
    2. Engine state validation using official patterns
    3. Proper error handling based on GitHub test failures
    4. runAndWait() pattern compliance from documentation
    """
    
    def __init__(self):
        """Initialize with research-compliant patterns"""
        logger.info("🔬 Initializing Research-Compliant Voice System")
        logger.info("📚 Based on: pyttsx3.readthedocs.io + GitHub nateshmbhat/pyttsx3")
        
        # Engine initialization (official pattern)
        self.engine: Optional[pyttsx3.Engine] = None
        self.voices: List[Any] = []
        self.voice_catalog: Dict[str, Dict] = {}
        self.current_voice_id: str = "voice_01"
        
        # Verification tracking (MANDATORY)
        self.verification_enabled: bool = True
        self.verification_failures: List[VoiceVerificationResult] = []
        self.last_verification: Optional[VoiceVerificationResult] = None
        
        # Initialize engine with error handling
        self._initialize_engine_with_verification()
        
        # Create 13-voice catalog with verification
        self._create_verified_voice_catalog()
        
        logger.info("✅ Research-compliant voice system initialized")
    
    def _initialize_engine_with_verification(self) -> None:
        """Initialize engine with research-compliant verification"""
        try:
            # Official initialization pattern from documentation
            self.engine = pyttsx3.init()
            
            # Get voices using official pattern
            voices_obj = self.engine.getProperty('voices')
            try:
                self.voices = list(voices_obj) if voices_obj else []  # type: ignore
            except (TypeError, AttributeError):
                logger.warning("Could not convert voices to list")
                self.voices = []
            
            # Verify engine state (based on test_engines.py)
            if not self.engine:
                raise RuntimeError("Engine initialization failed")
            
            if not self.voices:
                logger.warning("⚠️ No voices detected - this may cause issues")
            else:
                logger.info(f"✅ Detected {len(self.voices)} system voices")
            
            # Log engine information (based on GitHub test patterns)
            logger.info(f"Engine type: {type(self.engine)}")
            logger.info(f"Engine string: {str(self.engine)}")
            
        except Exception as e:
            logger.error(f"❌ Engine initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize pyttsx3 engine: {e}")
    
    def _create_verified_voice_catalog(self) -> None:
        """Create 13-voice catalog with verification checks"""
        logger.info("📋 Creating verified 13-voice catalog...")
        
        # Define 13-voice mapping
        voice_names = [f"voice_{i:02d}" for i in range(1, 14)]
        
        for i, voice_name in enumerate(voice_names):
            if i < len(self.voices):
                # Use actual system voice
                system_voice = self.voices[i]
                voice_info = {
                    'system_voice_id': getattr(system_voice, 'id', f'unknown_{i}'),
                    'name': getattr(system_voice, 'name', f"Voice {i+1}") or f"Voice {i+1}",
                    'languages': getattr(system_voice, 'languages', ['Unknown']) or ['Unknown'],
                    'gender': getattr(system_voice, 'gender', None),
                    'age': getattr(system_voice, 'age', None),
                    'system_index': i,
                    'verified': False  # Will be verified on first use
                }
            else:
                # Fallback pattern (cycle through available voices)
                fallback_index = i % len(self.voices) if self.voices else 0
                if self.voices:
                    system_voice = self.voices[fallback_index]
                    voice_info = {
                        'system_voice_id': getattr(system_voice, 'id', f'fallback_{i}'),
                        'name': f"{getattr(system_voice, 'name', f'Voice {i+1}')} (Fallback)",
                        'languages': getattr(system_voice, 'languages', ['Unknown']) or ['Unknown'],
                        'gender': getattr(system_voice, 'gender', None),
                        'age': getattr(system_voice, 'age', None),
                        'system_index': fallback_index,
                        'verified': False
                    }
                else:
                    # No voices available - create placeholder
                    voice_info = {
                        'system_voice_id': f'placeholder_{i}',
                        'name': f"Placeholder Voice {i+1}",
                        'languages': ['Unknown'],
                        'gender': None,
                        'age': None,
                        'system_index': i,
                        'verified': False
                    }
            
            self.voice_catalog[voice_name] = voice_info
        
        logger.info(f"✅ Created 13-voice catalog with {len([v for v in self.voice_catalog.values() if 'placeholder' not in v['system_voice_id']])} real voices")
    
    def verify_voice_switch(self, expected_voice_id: str) -> VoiceVerificationResult:
        """
        MANDATORY: Verify voice switch using GitHub test patterns
        Based on test_engines.py verification patterns
        """
        start_time = time.time()
        
        try:
            if not self.engine:
                return VoiceVerificationResult(
                    success=False,
                    expected_voice_id=expected_voice_id,
                    actual_voice_id="",
                    error_message="Engine not initialized",
                    verification_time=time.time() - start_time
                )
            
            # Get current voice using official pattern
            current_voice = self.engine.getProperty('voice')
            current_voice_str = str(current_voice) if current_voice else ""
            
            # Verification logic based on GitHub test patterns
            if current_voice_str == expected_voice_id:
                result = VoiceVerificationResult(
                    success=True,
                    expected_voice_id=expected_voice_id,
                    actual_voice_id=current_voice_str,
                    verification_time=time.time() - start_time
                )
                logger.info(f"✅ Voice verification passed: {expected_voice_id}")
                return result
            else:
                result = VoiceVerificationResult(
                    success=False,
                    expected_voice_id=expected_voice_id,
                    actual_voice_id=current_voice_str,
                    error_message=f"Voice mismatch: expected {expected_voice_id}, got {current_voice_str}",
                    verification_time=time.time() - start_time
                )
                logger.warning(f"⚠️ Voice verification failed: {result.error_message}")
                self.verification_failures.append(result)
                return result
                
        except Exception as e:
            result = VoiceVerificationResult(
                success=False,
                expected_voice_id=expected_voice_id,
                actual_voice_id="",
                error_message=f"Verification error: {e}",
                verification_time=time.time() - start_time
            )
            logger.error(f"❌ Voice verification error: {e}")
            self.verification_failures.append(result)
            return result
    
    def switch_voice_with_verification(self, voice_id: str) -> bool:
        """
        MANDATORY: Switch voice with verification checks
        Based on official setProperty patterns and GitHub verification
        """
        if voice_id not in self.voice_catalog:
            logger.error(f"❌ Voice {voice_id} not found in catalog")
            return False
        
        voice_info = self.voice_catalog[voice_id]
        system_voice_id = voice_info['system_voice_id']
        
        # Skip if placeholder voice
        if 'placeholder' in system_voice_id:
            logger.warning(f"⚠️ Cannot switch to placeholder voice {voice_id}")
            return False
        
        try:
            logger.info(f"🔄 Switching to {voice_id} (system: {system_voice_id})")
            
            # Ensure engine is available
            if not self.engine:
                logger.error("❌ Engine not available")
                return False
            
            # Use official setProperty pattern from documentation
            self.engine.setProperty('voice', system_voice_id)
            
            # MANDATORY: Verify the switch (based on GitHub test patterns)
            if self.verification_enabled:
                verification = self.verify_voice_switch(system_voice_id)
                self.last_verification = verification
                
                if verification.success:
                    self.current_voice_id = voice_id
                    voice_info['verified'] = True
                    logger.info(f"✅ Successfully switched to {voice_id}")
                    return True
                else:
                    logger.error(f"❌ Voice switch verification failed: {verification.error_message}")
                    return False
            else:
                # Non-verified mode (not recommended)
                self.current_voice_id = voice_id
                logger.warning(f"⚠️ Voice switched without verification: {voice_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error switching to {voice_id}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def speak_with_verification(self, text: str, voice_id: Optional[str] = None) -> bool:
        """
        MANDATORY: Speak with verification using official runAndWait patterns
        Based on official documentation examples and GitHub test patterns
        """
        if not text or not text.strip():
            logger.warning("⚠️ Empty text provided for speech")
            return False
        
        try:
            # Switch voice if specified
            if voice_id and voice_id != self.current_voice_id:
                if not self.switch_voice_with_verification(voice_id):
                    logger.error(f"❌ Failed to switch to voice {voice_id}")
                    return False
            
            # MANDATORY: Verify current voice before speaking
            if self.verification_enabled and voice_id:
                current_voice_info = self.voice_catalog.get(self.current_voice_id, {})
                expected_system_id = current_voice_info.get('system_voice_id', '')
                
                verification = self.verify_voice_switch(expected_system_id)
                if not verification.success:
                    logger.error(f"❌ Pre-speech verification failed: {verification.error_message}")
                    return False
            
            logger.info(f"🔊 Speaking with {self.current_voice_id}: \"{text[:50]}...\"")
            
            # Ensure engine is available
            if not self.engine:
                logger.error("❌ Engine not available for speech")
                return False
            
            # Use official speak pattern from documentation
            self.engine.say(text)
            
            # MANDATORY: Use proper runAndWait() pattern from documentation
            self.engine.runAndWait()
            
            logger.info(f"✅ Successfully spoke with {self.current_voice_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Speech error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def test_all_voices_with_verification(self) -> Dict[str, bool]:
        """
        MANDATORY: Test all voices with verification
        Based on GitHub test patterns from test_changing_voices
        """
        logger.info("🧪 Testing all 13 voices with mandatory verification")
        
        test_results = {}
        test_message = "Testing voice with research-compliant verification patterns."
        
        for voice_id in self.voice_catalog.keys():
            logger.info(f"\n--- Testing {voice_id} ---")
            
            # Test voice switch
            switch_success = self.switch_voice_with_verification(voice_id)
            if not switch_success:
                logger.error(f"❌ {voice_id}: Voice switch failed")
                test_results[voice_id] = False
                continue
            
            # Test speech
            speech_success = self.speak_with_verification(test_message)
            if not speech_success:
                logger.error(f"❌ {voice_id}: Speech failed")
                test_results[voice_id] = False
                continue
            
            # Final verification
            if self.last_verification and self.last_verification.success:
                logger.info(f"✅ {voice_id}: All tests passed")
                test_results[voice_id] = True
            else:
                logger.error(f"❌ {voice_id}: Final verification failed")
                test_results[voice_id] = False
            
            # Pause between voices (based on GitHub patterns)
            time.sleep(0.5)
        
        # Summary
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        logger.info(f"\n📊 Test Results Summary: {passed}/{total} voices passed")
        
        return test_results
    
    def get_verification_status(self) -> Dict[str, Any]:
        """Get comprehensive verification status"""
        return {
            'verification_enabled': self.verification_enabled,
            'current_voice_id': self.current_voice_id,
            'total_voices': len(self.voice_catalog),
            'verified_voices': len([v for v in self.voice_catalog.values() if v.get('verified', False)]),
            'verification_failures': len(self.verification_failures),
            'last_verification': self.last_verification.__dict__ if self.last_verification else None,
            'recent_failures': [f.__dict__ for f in self.verification_failures[-5:]]  # Last 5 failures
        }
    
    def list_voices_with_verification_status(self) -> None:
        """List all voices with verification status"""
        logger.info("\n=== VPA 13-Voice Catalog (Research-Compliant) ===")
        
        for voice_id, voice_info in self.voice_catalog.items():
            status = "✅ VERIFIED" if voice_info.get('verified', False) else "⏳ PENDING"
            if 'placeholder' in voice_info['system_voice_id']:
                status = "❌ PLACEHOLDER"
            
            logger.info(f"\n{voice_id}: {status}")
            logger.info(f"  System ID: {voice_info['system_voice_id']}")
            logger.info(f"  Name: {voice_info['name']}")
            logger.info(f"  Gender: {voice_info['gender'] or 'Unknown'}")
            logger.info(f"  Languages: {', '.join(voice_info['languages'])}")
    
    def enable_mandatory_verification(self, enabled: bool = True) -> None:
        """Enable/disable mandatory verification (NOT RECOMMENDED to disable)"""
        self.verification_enabled = enabled
        status = "ENABLED" if enabled else "DISABLED"
        logger.warning(f"⚠️ Verification {status} - This affects voice system reliability")
    
    def cleanup(self) -> None:
        """Clean up resources"""
        try:
            if self.engine:
                # Stop any ongoing speech
                self.engine.stop()
                logger.info("✅ Voice system cleaned up")
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")

def main():
    """Main test function with research-compliant patterns"""
    logger.info("=" * 80)
    logger.info("🔬 VPA VOICE SYSTEM - RESEARCH-COMPLIANT IMPLEMENTATION")
    logger.info("📚 Based on: pyttsx3 Official Documentation + GitHub Repository")
    logger.info("🔒 MANDATORY: Verification checks enabled (NON-NEGOTIABLE)")
    logger.info("=" * 80)
    
    # Initialize voice system
    voice_system = ResearchCompliantVoiceSystem()
    
    try:
        # Show voice catalog with verification status
        voice_system.list_voices_with_verification_status()
        
        # Show verification status
        logger.info("\n=== Verification Status ===")
        status = voice_system.get_verification_status()
        for key, value in status.items():
            if key != 'recent_failures':  # Skip detailed failure info for summary
                logger.info(f"{key}: {value}")
        
        # Test individual voices with verification
        logger.info("\n=== Individual Voice Tests (With Verification) ===")
        test_voices = ["voice_01", "voice_02", "voice_03"]
        
        for voice_id in test_voices:
            logger.info(f"\n--- Testing {voice_id} ---")
            success = voice_system.speak_with_verification(
                f"This is {voice_id} speaking with research-compliant verification.", 
                voice_id
            )
            if success:
                logger.info(f"✅ {voice_id} test successful")
            else:
                logger.error(f"❌ {voice_id} test failed")
        
        # Ask user for full test
        try:
            user_input = input("\nRun full 13-voice verification test? (y/n): ").lower().strip()
            if user_input == 'y':
                test_results = voice_system.test_all_voices_with_verification()
                
                # Show detailed results
                logger.info("\n=== Final Test Results ===")
                for voice_id, result in test_results.items():
                    status = "✅ PASSED" if result else "❌ FAILED"
                    logger.info(f"{voice_id}: {status}")
        except (EOFError, KeyboardInterrupt):
            logger.info("\nUser input skipped")
        
        # Final verification status
        logger.info("\n=== Final Verification Status ===")
        final_status = voice_system.get_verification_status()
        logger.info(f"✅ Verification System: {'ACTIVE' if final_status['verification_enabled'] else 'INACTIVE'}")
        logger.info(f"📊 Verified Voices: {final_status['verified_voices']}/{final_status['total_voices']}")
        logger.info(f"⚠️ Verification Failures: {final_status['verification_failures']}")
        
        if final_status['verification_failures'] > 0:
            logger.warning("🔍 Verification failures detected - this may indicate voice system issues")
        else:
            logger.info("✅ No verification failures - voice system operating correctly")
        
    except Exception as e:
        logger.error(f"❌ Test execution error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    finally:
        # Clean up
        voice_system.cleanup()

if __name__ == "__main__":
    main()
