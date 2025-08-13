"""
VPA Voice System - Comprehensive Voice Discovery & Validation
Full system voice enumeration, installation verification, and playback validation
MANDATE: Evidence-based voice discovery with installation support
"""

import pyttsx3
import winreg
import subprocess
import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import platform

# Configure logging for audit trail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voice_discovery_audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SystemVoice:
    """Complete system voice information"""
    voice_id: str
    name: str
    gender: str
    language: str
    provider: str
    installed: bool
    available: bool
    tested: bool = False
    test_result: str = "PENDING"
    installation_path: Optional[str] = None
    registry_key: Optional[str] = None

@dataclass
class VoiceDiscoveryResults:
    """Complete voice discovery results"""
    total_voices_found: int
    installed_voices: int
    available_voices: int
    tested_voices: int
    discovery_time: float
    system_info: Dict[str, str]
    voices: List[SystemVoice]
    errors: List[str]

class ComprehensiveVoiceDiscovery:
    """
    Comprehensive Voice Discovery System
    MANDATE: Full voice enumeration, verification, and validation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.discovery_results = VoiceDiscoveryResults(
            total_voices_found=0,
            installed_voices=0,
            available_voices=0,
            tested_voices=0,
            discovery_time=0.0,
            system_info={},
            voices=[],
            errors=[]
        )
        
        # Initialize TTS engine for testing
        self.engine = None
        self._initialize_tts_engine()
        
        self.logger.info("🔍 Comprehensive Voice Discovery System Initialized")
    
    def _initialize_tts_engine(self):
        """Initialize TTS engine for voice testing"""
        try:
            self.engine = pyttsx3.init()
            self.logger.info("✅ TTS Engine initialized for voice testing")
        except Exception as e:
            self.logger.error(f"❌ TTS Engine initialization failed: {e}")
            self.discovery_results.errors.append(f"TTS initialization failed: {e}")
    
    def discover_all_system_voices(self) -> VoiceDiscoveryResults:
        """
        Comprehensive system voice discovery
        MANDATE: Enumerate ALL physically available voices
        """
        start_time = time.time()
        self.logger.info("🚀 Starting comprehensive voice discovery...")
        
        # Collect system information
        self._collect_system_info()
        
        # Multiple discovery methods for comprehensive coverage
        discovered_voices = []
        
        # Method 1: pyttsx3 engine discovery
        pyttsx3_voices = self._discover_pyttsx3_voices()
        discovered_voices.extend(pyttsx3_voices)
        
        # Method 2: Windows SAPI registry discovery
        if platform.system() == "Windows":
            sapi_voices = self._discover_windows_sapi_voices()
            discovered_voices.extend(sapi_voices)
        
        # Method 3: System command discovery
        system_voices = self._discover_system_command_voices()
        discovered_voices.extend(system_voices)
        
        # Deduplicate and merge voice information
        merged_voices = self._merge_voice_discoveries(discovered_voices)
        
        # Update discovery results
        self.discovery_results.voices = merged_voices
        self.discovery_results.total_voices_found = len(merged_voices)
        self.discovery_results.installed_voices = sum(1 for v in merged_voices if v.installed)
        self.discovery_results.available_voices = sum(1 for v in merged_voices if v.available)
        self.discovery_results.discovery_time = time.time() - start_time
        
        self.logger.info(f"✅ Voice discovery complete in {self.discovery_results.discovery_time:.2f}s")
        self.logger.info(f"📊 Found {self.discovery_results.total_voices_found} voices total")
        self.logger.info(f"📊 {self.discovery_results.installed_voices} installed voices")
        self.logger.info(f"📊 {self.discovery_results.available_voices} available voices")
        
        return self.discovery_results
    
    def _collect_system_info(self):
        """Collect system information for audit"""
        self.discovery_results.system_info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "discovery_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.logger.info(f"📋 System: {platform.system()} {platform.release()}")
        self.logger.info(f"📋 Python: {platform.python_version()}")
    
    def _discover_pyttsx3_voices(self) -> List[SystemVoice]:
        """Discover voices through pyttsx3 engine"""
        voices = []
        try:
            if not self.engine:
                self.logger.warning("⚠️ TTS engine not available for pyttsx3 discovery")
                return voices
            
            pyttsx3_voices = self.engine.getProperty('voices')
            if not pyttsx3_voices:
                self.logger.warning("⚠️ No voices found through pyttsx3")
                return voices
            
            # Handle the voices safely
            try:
                voice_list = list(pyttsx3_voices)
                self.logger.info(f"🔍 Found {len(voice_list)} voices through pyttsx3")
            except (TypeError, AttributeError):
                self.logger.warning("⚠️ Unable to iterate pyttsx3 voices")
                return voices
            
            for i, voice in enumerate(voice_list):
                try:
                    # Extract voice information
                    voice_id = getattr(voice, 'id', f"pyttsx3_voice_{i}")
                    name = getattr(voice, 'name', f"Unknown Voice {i}")
                    languages = getattr(voice, 'languages', [])
                    
                    # Determine gender from name (basic heuristic)
                    gender = self._determine_gender_from_name(name)
                    
                    # Determine language
                    language = languages[0] if languages else "unknown"
                    
                    system_voice = SystemVoice(
                        voice_id=voice_id,
                        name=name,
                        gender=gender,
                        language=language,
                        provider="pyttsx3/SAPI",
                        installed=True,
                        available=True,
                        registry_key=voice_id
                    )
                    
                    voices.append(system_voice)
                    self.logger.info(f"✅ pyttsx3 Voice: {name} ({gender}, {language})")
                    
                except Exception as e:
                    self.logger.error(f"❌ Error processing pyttsx3 voice {i}: {e}")
                    self.discovery_results.errors.append(f"pyttsx3 voice {i} error: {e}")
            
        except Exception as e:
            self.logger.error(f"❌ pyttsx3 voice discovery failed: {e}")
            self.discovery_results.errors.append(f"pyttsx3 discovery failed: {e}")
        
        return voices
    
    def _discover_windows_sapi_voices(self) -> List[SystemVoice]:
        """Discover voices through Windows SAPI registry"""
        voices = []
        if platform.system() != "Windows":
            return voices
        
        try:
            self.logger.info("🔍 Searching Windows SAPI registry for voices...")
            
            # Common SAPI registry paths
            registry_paths = [
                r"SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens",
                r"SOFTWARE\\Microsoft\\Speech_OneCore\\Voices\\Tokens",
                r"SOFTWARE\\WOW6432Node\\Microsoft\\Speech\\Voices\\Tokens"
            ]
            
            for registry_path in registry_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
                        voice_count = winreg.QueryInfoKey(key)[0]
                        
                        for i in range(voice_count):
                            try:
                                voice_key_name = winreg.EnumKey(key, i)
                                voice_key_path = f"{registry_path}\\{voice_key_name}"
                                
                                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, voice_key_path) as voice_key:
                                    # Get voice name
                                    try:
                                        name = winreg.QueryValueEx(voice_key, "")[0]
                                    except:
                                        name = voice_key_name
                                    
                                    # Get voice attributes
                                    try:
                                        with winreg.OpenKey(voice_key, "Attributes") as attr_key:
                                            gender = "Unknown"
                                            language = "unknown"
                                            
                                            try:
                                                gender = winreg.QueryValueEx(attr_key, "Gender")[0]
                                            except:
                                                gender = self._determine_gender_from_name(name)
                                            
                                            try:
                                                language = winreg.QueryValueEx(attr_key, "Language")[0]
                                            except:
                                                pass
                                    except:
                                        gender = self._determine_gender_from_name(name)
                                        language = "unknown"
                                    
                                    system_voice = SystemVoice(
                                        voice_id=f"HKEY_LOCAL_MACHINE\\{voice_key_path}",
                                        name=name,
                                        gender=gender,
                                        language=language,
                                        provider="Windows SAPI",
                                        installed=True,
                                        available=True,
                                        registry_key=voice_key_path
                                    )
                                    
                                    voices.append(system_voice)
                                    self.logger.info(f"✅ SAPI Voice: {name} ({gender}, {language})")
                                    
                            except Exception as e:
                                self.logger.warning(f"⚠️ Error reading voice {i} from {registry_path}: {e}")
                                
                except Exception as e:
                    self.logger.warning(f"⚠️ Cannot access registry path {registry_path}: {e}")
            
            self.logger.info(f"✅ Found {len(voices)} voices through SAPI registry")
            
        except Exception as e:
            self.logger.error(f"❌ Windows SAPI discovery failed: {e}")
            self.discovery_results.errors.append(f"SAPI discovery failed: {e}")
        
        return voices
    
    def _discover_system_command_voices(self) -> List[SystemVoice]:
        """Discover voices through system commands"""
        voices = []
        
        if platform.system() == "Windows":
            voices.extend(self._discover_windows_powershell_voices())
        
        return voices
    
    def _discover_windows_powershell_voices(self) -> List[SystemVoice]:
        """Discover voices through PowerShell commands"""
        voices = []
        try:
            self.logger.info("🔍 Discovering voices through PowerShell...")
            
            # PowerShell command to list SAPI voices
            ps_command = """
            Add-Type -AssemblyName System.Speech
            $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
            $synth.GetInstalledVoices() | ForEach-Object {
                $voice = $_.VoiceInfo
                [PSCustomObject]@{
                    Name = $voice.Name
                    Gender = $voice.Gender
                    Age = $voice.Age
                    Culture = $voice.Culture.Name
                    Id = $voice.Id
                    Enabled = $_.Enabled
                }
            } | ConvertTo-Json
            """
            
            result = subprocess.run([
                "powershell", "-Command", ps_command
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout:
                try:
                    ps_voices = json.loads(result.stdout)
                    if not isinstance(ps_voices, list):
                        ps_voices = [ps_voices]
                    
                    for voice_data in ps_voices:
                        system_voice = SystemVoice(
                            voice_id=voice_data.get("Id", "unknown"),
                            name=voice_data.get("Name", "Unknown"),
                            gender=voice_data.get("Gender", "Unknown"),
                            language=voice_data.get("Culture", "unknown"),
                            provider="PowerShell/SAPI",
                            installed=True,
                            available=voice_data.get("Enabled", False)
                        )
                        
                        voices.append(system_voice)
                        self.logger.info(f"✅ PowerShell Voice: {system_voice.name} ({system_voice.gender}, {system_voice.language})")
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"❌ Failed to parse PowerShell voice data: {e}")
                    self.discovery_results.errors.append(f"PowerShell JSON parse error: {e}")
            else:
                self.logger.warning(f"⚠️ PowerShell command failed: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f"❌ PowerShell voice discovery failed: {e}")
            self.discovery_results.errors.append(f"PowerShell discovery failed: {e}")
        
        return voices
    
    def _determine_gender_from_name(self, name: str) -> str:
        """Determine gender from voice name using heuristics"""
        name_lower = name.lower()
        
        # Common male voice names
        male_indicators = ['david', 'mark', 'richard', 'james', 'sean', 'alex', 'male']
        
        # Common female voice names  
        female_indicators = ['zira', 'hazel', 'helena', 'catherine', 'eva', 'sabina', 'female']
        
        for indicator in male_indicators:
            if indicator in name_lower:
                return "Male"
        
        for indicator in female_indicators:
            if indicator in name_lower:
                return "Female"
        
        return "Unknown"
    
    def _merge_voice_discoveries(self, discovered_voices: List[List[SystemVoice]]) -> List[SystemVoice]:
        """Merge and deduplicate voice discoveries from multiple sources"""
        merged_voices = {}
        
        for voice_list in discovered_voices:
            # Handle both lists and individual voice objects
            if isinstance(voice_list, list):
                voices_to_process = voice_list
            else:
                voices_to_process = [voice_list]
            
            for voice in voices_to_process:
                # Use name as primary key for deduplication
                key = voice.name.lower().strip()
                
                if key in merged_voices:
                    # Merge information from multiple sources
                    existing = merged_voices[key]
                    
                    # Prefer more detailed information
                    if voice.registry_key and not existing.registry_key:
                        existing.registry_key = voice.registry_key
                    
                    if voice.language != "unknown" and existing.language == "unknown":
                        existing.language = voice.language
                    
                    if voice.gender != "Unknown" and existing.gender == "Unknown":
                        existing.gender = voice.gender
                    
                    # Update availability
                    existing.available = existing.available or voice.available
                    existing.installed = existing.installed or voice.installed
                    
                else:
                    merged_voices[key] = voice
        
        return list(merged_voices.values())

    def validate_voice_playback(self, voice: SystemVoice, test_phrase: Optional[str] = None) -> bool:
        """
        Validate voice playback with user confirmation
        MANDATE: Play test phrase and log results
        """
        if not test_phrase:
            test_phrase = f"This is {voice.name}. Please confirm you hear this voice clearly."
        
        self.logger.info(f"🔊 Testing voice playback: {voice.name}")
        
        try:
            if not self.engine:
                self.logger.error("❌ TTS engine not available for testing")
                voice.test_result = "FAILED - No TTS engine"
                return False
            
            # Set the voice
            self.engine.setProperty('voice', voice.voice_id)
            
            # Test playback
            self.logger.info(f"🎵 Playing test phrase: '{test_phrase}'")
            self.engine.say(test_phrase)
            self.engine.runAndWait()
            
            # Log the test
            voice.tested = True
            voice.test_result = "PLAYED - Awaiting user confirmation"
            
            self.logger.info(f"✅ Voice test completed for {voice.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Voice test failed for {voice.name}: {e}")
            voice.tested = True
            voice.test_result = f"FAILED - {str(e)}"
            self.discovery_results.errors.append(f"Voice test failed for {voice.name}: {e}")
            return False

    def get_discovery_report(self) -> str:
        """Generate comprehensive discovery report"""
        report = f"""
🛡️ COMPREHENSIVE VOICE DISCOVERY REPORT
===========================================
Discovery Time: {time.strftime("%Y-%m-%d %H:%M:%S")}
Total Discovery Time: {self.discovery_results.discovery_time:.2f} seconds

📊 DISCOVERY SUMMARY:
- Total Voices Found: {self.discovery_results.total_voices_found}
- Installed Voices: {self.discovery_results.installed_voices}
- Available Voices: {self.discovery_results.available_voices}
- Tested Voices: {self.discovery_results.tested_voices}
- Discovery Errors: {len(self.discovery_results.errors)}

🖥️ SYSTEM INFORMATION:
- Platform: {self.discovery_results.system_info.get('platform', 'Unknown')}
- Release: {self.discovery_results.system_info.get('platform_release', 'Unknown')}
- Python Version: {self.discovery_results.system_info.get('python_version', 'Unknown')}

📋 VOICE CATALOG:
"""
        
        for i, voice in enumerate(self.discovery_results.voices, 1):
            report += f"""
Voice {i:02d}: {voice.name}
  - ID: {voice.voice_id}
  - Gender: {voice.gender}
  - Language: {voice.language}
  - Provider: {voice.provider}
  - Installed: {'✅' if voice.installed else '❌'}
  - Available: {'✅' if voice.available else '❌'}
  - Tested: {'✅' if voice.tested else '⏳'}
  - Test Result: {voice.test_result}
"""
        
        if self.discovery_results.errors:
            report += f"\n❌ ERRORS ENCOUNTERED:\n"
            for error in self.discovery_results.errors:
                report += f"  - {error}\n"
        
        return report

if __name__ == "__main__":
    print("🛡️ VPA VOICE SYSTEM - COMPREHENSIVE DISCOVERY & VALIDATION")
    print("=" * 80)
    
    discovery = ComprehensiveVoiceDiscovery()
    
    # Run comprehensive discovery
    results = discovery.discover_all_system_voices()
    
    # Generate and display report
    report = discovery.get_discovery_report()
    print(report)
    
    # Save detailed results
    with open("voice_discovery_results.json", "w") as f:
        json.dump({
            "discovery_results": asdict(results),
            "voices": [asdict(voice) for voice in results.voices]
        }, f, indent=2)
    
    print(f"\n📁 Detailed results saved to: voice_discovery_results.json")
    print(f"📁 Audit log saved to: voice_discovery_audit.log")
    
    # Test each available voice
    print(f"\n🔊 VOICE PLAYBACK TESTING:")
    print("=" * 50)
    
    available_voices = [v for v in results.voices if v.available]
    
    if available_voices:
        user_input = input(f"\nRun playback tests for {len(available_voices)} available voices? (y/n): ").lower()
        
        if user_input == 'y':
            for voice in available_voices:
                print(f"\n--- Testing {voice.name} ---")
                success = discovery.validate_voice_playback(voice)
                
                if success:
                    user_feedback = input(f"Did you hear '{voice.name}' clearly? (y/n/skip): ").lower()
                    if user_feedback == 'y':
                        voice.test_result = "CONFIRMED - User heard voice clearly"
                        discovery.discovery_results.tested_voices += 1
                    elif user_feedback == 'n':
                        voice.test_result = "FAILED - User did not hear voice"
                    else:
                        voice.test_result = "SKIPPED - User skipped validation"
                
                time.sleep(1)  # Brief pause between tests
        
        # Final report with test results
        final_report = discovery.get_discovery_report()
        print(f"\n🎯 FINAL DISCOVERY REPORT:")
        print("=" * 50)
        print(final_report)
        
        # Save updated results
        with open("voice_discovery_final_results.json", "w") as f:
            json.dump({
                "discovery_results": asdict(discovery.discovery_results),
                "voices": [asdict(voice) for voice in discovery.discovery_results.voices]
            }, f, indent=2)
        
        print(f"\n✅ Final results saved to: voice_discovery_final_results.json")
    
    else:
        print("❌ No available voices found for testing")
    
    print(f"\n🛡️ Voice discovery and validation complete!")
