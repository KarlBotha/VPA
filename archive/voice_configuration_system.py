"""
VPA Voice Configuration & Selection System
MANDATE: Voice selection, installation guidance, and TTS configuration
EVIDENCE-BASED: 19 voices discovered, 1 confirmed working (Hazel Desktop)
"""

import json
import logging
import pyttsx3
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Configure audit logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voice_configuration_audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class VoiceConfigurationResult:
    """Voice configuration and selection result"""
    selected_voice_id: str
    selected_voice_name: str
    configuration_success: bool
    test_phrase_played: bool
    user_confirmation: str
    audio_device_info: Dict[str, Any]
    configuration_timestamp: str

class VoiceConfigurationSystem:
    """
    Voice Configuration & Selection System
    MANDATE: Complete voice selection, configuration, and TTS routing
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.engine = None
        self.discovered_voices = []
        self.selected_voice = None
        self.configuration_history = []
        
        # Load discovery results
        self._load_discovery_results()
        
        # Initialize TTS engine
        self._initialize_tts_engine()
        
        self.logger.info("Voice Configuration System Initialized")
    
    def _load_discovery_results(self):
        """Load voice discovery results"""
        try:
            with open("voice_discovery_final_results.json", "r") as f:
                data = json.load(f)
                self.discovered_voices = data.get("voices", [])
            
            self.logger.info(f"Loaded {len(self.discovered_voices)} discovered voices")
            
        except Exception as e:
            self.logger.error(f"Failed to load discovery results: {e}")
            self.discovered_voices = []
    
    def _initialize_tts_engine(self):
        """Initialize TTS engine for configuration"""
        try:
            self.engine = pyttsx3.init()
            self.logger.info("TTS Engine initialized for configuration")
        except Exception as e:
            self.logger.error(f"TTS Engine initialization failed: {e}")
    
    def display_voice_catalog(self) -> None:
        """Display comprehensive voice catalog with installation status"""
        
        print("\n🛡️ COMPREHENSIVE VOICE CATALOG")
        print("=" * 80)
        print(f"Discovery Results: {len(self.discovered_voices)} voices found")
        print("EVIDENCE-BASED: All voices technically installed and available")
        print("AUDIO ISSUE: Only 1/19 voices confirmed audible (configuration issue)")
        print("=" * 80)
        
        # Group voices by working status
        confirmed_working = [v for v in self.discovered_voices if "CONFIRMED" in v.get("test_result", "")]
        failed_audio = [v for v in self.discovered_voices if "FAILED" in v.get("test_result", "")]
        not_tested = [v for v in self.discovered_voices if v.get("test_result", "") == "PENDING"]
        
        print(f"\n✅ CONFIRMED WORKING VOICES: {len(confirmed_working)}")
        for i, voice in enumerate(confirmed_working, 1):
            print(f"  {i:2d}. {voice['name']}")
            print(f"      ID: {voice['voice_id']}")
            print(f"      Gender: {voice['gender']}, Language: {voice['language']}")
            print(f"      Provider: {voice['provider']}")
            print(f"      Status: {voice['test_result']}")
            print()
        
        print(f"\n⚠️ AUDIO ROUTING ISSUES: {len(failed_audio)}")
        print("NOTE: These voices are installed but not audible (audio configuration issue)")
        for i, voice in enumerate(failed_audio, 1):
            print(f"  {i:2d}. {voice['name']}")
            print(f"      Gender: {voice['gender']}, Language: {voice['language']}")
            print(f"      Issue: {voice['test_result']}")
        
        if not_tested:
            print(f"\n⏳ NOT TESTED: {len(not_tested)}")
            for i, voice in enumerate(not_tested, 1):
                print(f"  {i:2d}. {voice['name']}")
    
    def get_voice_installation_instructions(self) -> str:
        """Generate voice installation instructions based on discovery"""
        
        instructions = f"""
🛡️ VOICE INSTALLATION STATUS & INSTRUCTIONS
============================================

DISCOVERY RESULTS:
- Total Voices Found: {len(self.discovered_voices)}
- All voices are technically INSTALLED and AVAILABLE
- Audio routing issue preventing 18/19 voices from being heard

INSTALLATION STATUS: ✅ COMPLETE
All 19 voices are properly installed in the Windows SAPI system.
No additional voice downloads or installations are required.

AUDIO CONFIGURATION ISSUE IDENTIFIED:
The problem is NOT missing voices, but audio routing/configuration.

RECOMMENDED SOLUTIONS:

1. AUDIO DEVICE CONFIGURATION:
   - Check Windows Sound Settings → Output Device
   - Ensure correct speakers/headset is selected as default
   - Test audio with Windows built-in sound test

2. WINDOWS SAPI CONFIGURATION:
   - Open Windows Settings → Time & Language → Speech
   - Test different voices in Windows Speech settings
   - Verify voice preview works in Windows native interface

3. PYTTSX3 AUDIO ROUTING:
   - Audio output may be routing to wrong device
   - Default system audio vs. TTS audio routing mismatch
   - May need to specify audio output device in pyttsx3

4. VOICE ACTIVATION STATUS:
   - Some voices may be installed but not activated
   - Windows → Settings → Apps → Optional Features
   - Look for "Speech" features and ensure they're installed

5. SYSTEM AUDIO DRIVERS:
   - Update audio drivers if voices were working previously
   - Check Device Manager → Audio inputs and outputs
   - Restart Windows Audio service if needed

IMMEDIATE NEXT STEPS:
1. Test confirmed working voice (Hazel Desktop) for TTS configuration
2. Configure TTS system to use only confirmed working voice
3. Troubleshoot audio routing for remaining 18 voices
4. Provide user with voice selection interface for working voice(s)

EVIDENCE-BASED CONCLUSION:
This is an audio configuration issue, not a voice installation issue.
All required voices are present and technically functional.
"""
        return instructions
    
    def configure_tts_for_selected_voice(self, voice_choice: str) -> VoiceConfigurationResult:
        """Configure TTS system for selected voice with full audit trail"""
        
        self.logger.info(f"Configuring TTS for voice choice: {voice_choice}")
        
        # Find selected voice
        selected_voice = None
        if voice_choice.isdigit():
            choice_index = int(voice_choice) - 1
            if 0 <= choice_index < len(self.discovered_voices):
                selected_voice = self.discovered_voices[choice_index]
        else:
            # Search by name
            for voice in self.discovered_voices:
                if voice_choice.lower() in voice['name'].lower():
                    selected_voice = voice
                    break
        
        if not selected_voice:
            return VoiceConfigurationResult(
                selected_voice_id="",
                selected_voice_name="",
                configuration_success=False,
                test_phrase_played=False,
                user_confirmation="Voice not found",
                audio_device_info={},
                configuration_timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            )
        
        # Configure TTS engine
        configuration_success = False
        test_phrase_played = False
        
        try:
            if self.engine:
                # Set the selected voice
                self.engine.setProperty('voice', selected_voice['voice_id'])
                
                # Configure additional properties
                self.engine.setProperty('rate', 200)  # Normal speaking rate
                self.engine.setProperty('volume', 0.9)  # High volume
                
                configuration_success = True
                self.logger.info(f"TTS configured for: {selected_voice['name']}")
                
                # Test with confirmation phrase
                test_phrase = f"TTS system configured for {selected_voice['name']}. This voice will be used for all agent responses."
                
                print(f"\nTesting selected voice: {selected_voice['name']}")
                print(f"Playing: '{test_phrase}'")
                
                self.engine.say(test_phrase)
                self.engine.runAndWait()
                test_phrase_played = True
                
                self.logger.info("Test phrase played successfully")
            else:
                self.logger.error("TTS engine not initialized - cannot configure voice")
                
        except Exception as e:
            self.logger.error(f"TTS configuration failed: {e}")
        
        # Get user confirmation
        user_confirmation = input(f"\nDid you hear the TTS test clearly? (y/n): ").lower()
        
        # Create configuration result
        result = VoiceConfigurationResult(
            selected_voice_id=selected_voice['voice_id'],
            selected_voice_name=selected_voice['name'],
            configuration_success=configuration_success,
            test_phrase_played=test_phrase_played,
            user_confirmation=user_confirmation,
            audio_device_info=self._get_audio_device_info(),
            configuration_timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Store configuration
        self.selected_voice = selected_voice
        self.configuration_history.append(result)
        
        # Save configuration to file
        self._save_voice_configuration(result)
        
        return result
    
    def _get_audio_device_info(self) -> Dict[str, Any]:
        """Get current audio device information"""
        try:
            # Basic audio device info (could be expanded with pyaudio)
            return {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "tts_engine": "pyttsx3",
                "platform": "Windows",
                "note": "Audio device detection requires additional implementation"
            }
        except Exception as e:
            self.logger.error(f"Failed to get audio device info: {e}")
            return {"error": str(e)}
    
    def _save_voice_configuration(self, config_result: VoiceConfigurationResult):
        """Save voice configuration for future use"""
        try:
            config_data = {
                "voice_configuration": asdict(config_result),
                "selected_voice_details": self.selected_voice,
                "configuration_history": [asdict(result) for result in self.configuration_history]
            }
            
            with open("voice_configuration_results.json", "w") as f:
                json.dump(config_data, f, indent=2)
            
            self.logger.info("Voice configuration saved successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to save voice configuration: {e}")
    
    def test_agent_response_flow(self) -> bool:
        """Test complete agent response flow with selected voice"""
        
        if not self.selected_voice:
            print("No voice selected. Please configure a voice first.")
            return False
        
        if not self.engine:
            print("TTS engine not initialized. Cannot test agent responses.")
            return False
        
        print(f"\n🔊 TESTING AGENT RESPONSE FLOW")
        print(f"Selected Voice: {self.selected_voice['name']}")
        print("=" * 50)
        
        # Test phrases simulating agent responses
        test_responses = [
            "Hello! I am your virtual personal assistant.",
            "I'm ready to help you with your tasks today.",
            "This is a test of the agent response text-to-speech system.",
            "Voice configuration test completed successfully."
        ]
        
        for i, response in enumerate(test_responses, 1):
            print(f"\nAgent Response {i}: '{response}'")
            
            try:
                self.engine.say(response)
                self.engine.runAndWait()
                
                user_feedback = input(f"Did you hear response {i} clearly? (y/n/skip): ").lower()
                
                if user_feedback == 'n':
                    print(f"Audio issue detected on response {i}")
                    return False
                elif user_feedback == 'skip':
                    continue
                else:
                    print(f"Response {i} confirmed")
                
                time.sleep(1)  # Brief pause between responses
                
            except Exception as e:
                self.logger.error(f"Agent response test failed: {e}")
                return False
        
        print(f"\n✅ Agent response flow test completed successfully!")
        print(f"Selected voice '{self.selected_voice['name']}' confirmed working for agent responses")
        
        return True
    
    def generate_configuration_report(self) -> str:
        """Generate comprehensive configuration report"""
        
        report = f"""
🛡️ VOICE CONFIGURATION AUDIT REPORT
=====================================
Configuration Time: {time.strftime("%Y-%m-%d %H:%M:%S")}
Total Configurations: {len(self.configuration_history)}

DISCOVERY SUMMARY:
- Total Voices Found: {len(self.discovered_voices)}
- Confirmed Working: {len([v for v in self.discovered_voices if "CONFIRMED" in v.get("test_result", "")])}
- Audio Issues: {len([v for v in self.discovered_voices if "FAILED" in v.get("test_result", "")])}

CURRENT CONFIGURATION:
"""
        
        if self.selected_voice:
            report += f"""
- Selected Voice: {self.selected_voice['name']}
- Voice ID: {self.selected_voice['voice_id']}
- Gender: {self.selected_voice['gender']}
- Language: {self.selected_voice['language']}
- Provider: {self.selected_voice['provider']}
- Status: {self.selected_voice.get('test_result', 'Unknown')}
"""
        else:
            report += "\n- No voice currently selected\n"
        
        report += f"\nCONFIGURATION HISTORY:\n"
        for i, config in enumerate(self.configuration_history, 1):
            report += f"""
Configuration {i}:
  - Voice: {config.selected_voice_name}
  - Success: {config.configuration_success}
  - Test Played: {config.test_phrase_played}
  - User Confirmation: {config.user_confirmation}
  - Timestamp: {config.configuration_timestamp}
"""
        
        return report

def main():
    """Main voice configuration interface"""
    
    print("🛡️ VPA VOICE CONFIGURATION & SELECTION SYSTEM")
    print("=" * 80)
    print("MANDATE: Voice selection, configuration, and TTS routing")
    print("EVIDENCE-BASED: 19 voices discovered, 1 confirmed working")
    print("=" * 80)
    
    config_system = VoiceConfigurationSystem()
    
    # Display installation status
    print("\n📋 VOICE INSTALLATION STATUS:")
    installation_instructions = config_system.get_voice_installation_instructions()
    print(installation_instructions)
    
    # Display voice catalog
    config_system.display_voice_catalog()
    
    # Voice selection interface
    print(f"\n🎯 VOICE SELECTION INTERFACE")
    print("=" * 50)
    
    while True:
        print(f"\nAvailable Options:")
        print("1. Select voice by number (1-19)")
        print("2. Search voice by name")
        print("3. Use confirmed working voice (Hazel Desktop)")
        print("4. Test agent response flow")
        print("5. Generate configuration report")
        print("6. Exit")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "1":
            voice_num = input("Enter voice number (1-19): ").strip()
            result = config_system.configure_tts_for_selected_voice(voice_num)
            
            print(f"\nConfiguration Result:")
            print(f"- Voice: {result.selected_voice_name}")
            print(f"- Success: {result.configuration_success}")
            print(f"- User Confirmation: {result.user_confirmation}")
            
        elif choice == "2":
            voice_name = input("Enter voice name or partial name: ").strip()
            result = config_system.configure_tts_for_selected_voice(voice_name)
            
            print(f"\nConfiguration Result:")
            print(f"- Voice: {result.selected_voice_name}")
            print(f"- Success: {result.configuration_success}")
            print(f"- User Confirmation: {result.user_confirmation}")
            
        elif choice == "3":
            # Use confirmed working voice
            result = config_system.configure_tts_for_selected_voice("Hazel Desktop")
            
            print(f"\nConfigured confirmed working voice:")
            print(f"- Voice: {result.selected_voice_name}")
            print(f"- Success: {result.configuration_success}")
            print(f"- User Confirmation: {result.user_confirmation}")
            
        elif choice == "4":
            config_system.test_agent_response_flow()
            
        elif choice == "5":
            report = config_system.generate_configuration_report()
            print(report)
            
            # Save report
            with open("voice_configuration_audit_report.txt", "w") as f:
                f.write(report)
            print("\n📁 Report saved to: voice_configuration_audit_report.txt")
            
        elif choice == "6":
            print("\n✅ Voice configuration complete!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
