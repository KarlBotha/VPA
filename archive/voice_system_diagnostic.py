"""
Voice System Diagnostic - Step-by-Step Analysis
Systematic investigation of voice availability and configuration
"""

import pyttsx3
import logging
import sys
import platform
from typing import List, Dict, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VoiceSystemDiagnostic:
    """Comprehensive voice system diagnostic tool"""
    
    def __init__(self):
        self.engine = None
        self.system_info = {}
        self.voice_analysis = {}
        
    def run_complete_diagnostic(self):
        """Run complete step-by-step diagnostic"""
        print("="*80)
        print("🔍 VPA VOICE SYSTEM DIAGNOSTIC")
        print("="*80)
        
        # Step 1: System Environment Check
        print("\n📋 STEP 1: SYSTEM ENVIRONMENT")
        self._check_system_environment()
        
        # Step 2: pyttsx3 Engine Initialization
        print("\n🔧 STEP 2: ENGINE INITIALIZATION")
        engine_success = self._initialize_pyttsx3_engine()
        
        if not engine_success:
            print("❌ Cannot proceed - engine initialization failed")
            return False
        
        # Step 3: Voice Discovery and Analysis
        print("\n🎵 STEP 3: VOICE DISCOVERY")
        self._discover_and_analyze_voices()
        
        # Step 4: Engine Property Analysis
        print("\n⚙️ STEP 4: ENGINE PROPERTIES")
        self._analyze_engine_properties()
        
        # Step 5: Voice Switching Test
        print("\n🔄 STEP 5: VOICE SWITCHING TEST")
        self._test_voice_switching_capability()
        
        # Step 6: Diagnostic Summary
        print("\n📊 STEP 6: DIAGNOSTIC SUMMARY")
        self._provide_diagnostic_summary()
        
        return True
    
    def _check_system_environment(self):
        """Check system environment and dependencies"""
        try:
            # Python version
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            print(f"🐍 Python Version: {python_version}")
            
            # Operating System
            os_info = f"{platform.system()} {platform.release()}"
            print(f"🖥️ Operating System: {os_info}")
            
            # pyttsx3 version and availability
            try:
                import pyttsx3
                print(f"✅ pyttsx3: Available")
                # Try to get version if available
                try:
                    version = getattr(pyttsx3, '__version__', 'Unknown')
                    print(f"   Version: {version}")
                except:
                    print(f"   Version: Unknown")
            except ImportError as e:
                print(f"❌ pyttsx3: Not available - {e}")
                return False
            
            # Windows-specific checks
            if platform.system() == "Windows":
                try:
                    import win32com.client
                    print(f"✅ win32com: Available")
                    
                    # Try to access SAPI directly
                    try:
                        sapi = win32com.client.Dispatch("SAPI.SpVoice")
                        voices = sapi.GetVoices()
                        print(f"✅ Windows SAPI: {voices.Count} voices found")
                        sapi = None  # Clean up
                    except Exception as sapi_error:
                        print(f"⚠️ Windows SAPI: Error - {sapi_error}")
                        
                except ImportError:
                    print(f"⚠️ win32com: Not available (optional)")
            
            self.system_info = {
                'python_version': python_version,
                'os_info': os_info,
                'pyttsx3_available': True
            }
            
            return True
            
        except Exception as e:
            print(f"❌ System environment check failed: {e}")
            return False
    
    def _initialize_pyttsx3_engine(self):
        """Initialize pyttsx3 engine with detailed logging"""
        try:
            print("🔄 Initializing pyttsx3 engine...")
            
            # Try different initialization methods
            methods = [
                ("Default", lambda: pyttsx3.init()),
                ("SAPI5", lambda: pyttsx3.init('sapi5')),
                ("nsss (if available)", lambda: pyttsx3.init('nsss')),
                ("espeak (if available)", lambda: pyttsx3.init('espeak'))
            ]
            
            for method_name, init_func in methods:
                try:
                    print(f"   Trying {method_name} initialization...")
                    self.engine = init_func()
                    if self.engine:
                        print(f"✅ {method_name} initialization successful")
                        
                        # Test basic engine properties
                        try:
                            rate = self.engine.getProperty('rate')
                            volume = self.engine.getProperty('volume')
                            print(f"   Default rate: {rate}")
                            print(f"   Default volume: {volume}")
                        except Exception as prop_error:
                            print(f"   ⚠️ Property access error: {prop_error}")
                        
                        return True
                    else:
                        print(f"   ❌ {method_name} returned None")
                        
                except Exception as e:
                    print(f"   ❌ {method_name} failed: {e}")
                    continue
            
            print("❌ All initialization methods failed")
            return False
            
        except Exception as e:
            print(f"❌ Engine initialization error: {e}")
            return False
    
    def _discover_and_analyze_voices(self):
        """Discover and analyze available voices"""
        if not self.engine:
            print("❌ No engine available for voice discovery")
            return
        
        try:
            print("🔍 Discovering voices...")
            
            # Get voices using different methods
            voices_data = {}
            
            # Method 1: Direct getProperty
            try:
                voices = self.engine.getProperty('voices')
                print(f"📋 getProperty('voices') result type: {type(voices)}")
                
                if voices is None:
                    print("   Result: None")
                    voices_data['direct'] = None
                elif hasattr(voices, '__len__'):
                    try:
                        voice_count = len(voices)  # type: ignore
                        print(f"   Result: Collection with {voice_count} items")
                    except:
                        print("   Result: Collection (length unknown)")
                    voices_data['direct'] = voices
                else:
                    print(f"   Result: {voices}")
                    voices_data['direct'] = voices
                    
            except Exception as e:
                print(f"   ❌ getProperty('voices') failed: {e}")
                voices_data['direct'] = None
            
            # Method 2: Try to iterate if possible
            voices = voices_data.get('direct')
            if voices:
                print("\n🔍 Analyzing voice collection...")
                voice_list = []
                
                try:
                    # Check if iterable
                    if hasattr(voices, '__iter__'):
                        print("   Collection is iterable")
                        
                        try:
                            for i, voice in enumerate(voices):
                                if voice:
                                    voice_info = self._analyze_single_voice(voice, i)
                                    if voice_info:
                                        voice_list.append(voice_info)
                                        print(f"   ✅ Voice {i}: {voice_info.get('name', 'Unknown')}")
                                else:
                                    print(f"   ⚠️ Voice {i}: None/Empty")
                                    
                        except Exception as iter_error:
                            print(f"   ❌ Iteration failed: {iter_error}")
                            
                            # Try index-based access
                            print("   🔄 Trying index-based access...")
                            try:
                                for i in range(20):  # reasonable limit
                                    try:
                                        voice = voices[i]
                                        if voice:
                                            voice_info = self._analyze_single_voice(voice, i)
                                            if voice_info:
                                                voice_list.append(voice_info)
                                                print(f"   ✅ Voice {i}: {voice_info.get('name', 'Unknown')}")
                                        else:
                                            break
                                    except (IndexError, KeyError):
                                        break
                                    except Exception as voice_error:
                                        print(f"   ⚠️ Voice {i} error: {voice_error}")
                                        
                            except Exception as index_error:
                                print(f"   ❌ Index access failed: {index_error}")
                    
                    else:
                        print("   Collection is not iterable")
                        
                except Exception as analysis_error:
                    print(f"   ❌ Voice analysis failed: {analysis_error}")
                
                self.voice_analysis = {
                    'total_found': len(voice_list),
                    'voices': voice_list
                }
                
                print(f"\n📊 Voice Discovery Summary:")
                print(f"   Total voices found: {len(voice_list)}")
                for voice in voice_list:
                    print(f"   - {voice.get('name', 'Unknown')} ({voice.get('id', 'No ID')[:50]}...)")
            
            else:
                print("❌ No voices collection available")
                self.voice_analysis = {'total_found': 0, 'voices': []}
                
        except Exception as e:
            print(f"❌ Voice discovery failed: {e}")
            self.voice_analysis = {'total_found': 0, 'voices': [], 'error': str(e)}
    
    def _analyze_single_voice(self, voice, index: int) -> Optional[Dict[str, Any]]:
        """Analyze a single voice object"""
        try:
            voice_info = {'index': index}
            
            # Get basic properties
            if hasattr(voice, 'name'):
                voice_info['name'] = str(voice.name)
            elif hasattr(voice, 'Name'):
                voice_info['name'] = str(voice.Name)
            else:
                voice_info['name'] = f"Voice_{index}"
            
            if hasattr(voice, 'id'):
                voice_info['id'] = str(voice.id)
            elif hasattr(voice, 'Id'):
                voice_info['id'] = str(voice.Id)
            elif hasattr(voice, 'ID'):
                voice_info['id'] = str(voice.ID)
            else:
                voice_info['id'] = f"voice_{index}"
            
            # Try to get additional properties
            for attr in ['age', 'gender', 'language', 'languages']:
                if hasattr(voice, attr):
                    try:
                        value = getattr(voice, attr)
                        voice_info[attr] = str(value) if value else None
                    except:
                        pass
            
            return voice_info
            
        except Exception as e:
            print(f"   ⚠️ Error analyzing voice {index}: {e}")
            return None
    
    def _analyze_engine_properties(self):
        """Analyze engine properties and capabilities"""
        if not self.engine:
            print("❌ No engine available")
            return
        
        try:
            print("🔍 Analyzing engine properties...")
            
            # Standard properties
            properties = ['rate', 'volume', 'voices']
            
            for prop in properties:
                try:
                    value = self.engine.getProperty(prop)
                    print(f"   {prop}: {value} (type: {type(value)})")
                except Exception as e:
                    print(f"   {prop}: Error - {e}")
            
            # Try to set properties
            print("\n🔧 Testing property setting...")
            
            try:
                original_rate = self.engine.getProperty('rate')
                self.engine.setProperty('rate', 200)
                new_rate = self.engine.getProperty('rate')
                print(f"   Rate setting: {original_rate} → {new_rate} ({'✅' if new_rate == 200 else '❌'})")
            except Exception as e:
                print(f"   Rate setting: ❌ {e}")
            
            try:
                original_volume = self.engine.getProperty('volume')
                self.engine.setProperty('volume', 0.8)
                new_volume = self.engine.getProperty('volume')
                print(f"   Volume setting: {original_volume} → {new_volume} ({'✅' if abs(new_volume - 0.8) < 0.1 else '❌'})")
            except Exception as e:
                print(f"   Volume setting: ❌ {e}")
                
        except Exception as e:
            print(f"❌ Property analysis failed: {e}")
    
    def _test_voice_switching_capability(self):
        """Test if voice switching actually works"""
        if not self.engine:
            print("❌ No engine available")
            return
        
        voices = self.voice_analysis.get('voices', [])
        if len(voices) < 2:
            print("⚠️ Need at least 2 voices to test switching")
            return
        
        print(f"🔄 Testing voice switching with {len(voices)} voices...")
        
        try:
            # Test switching between first two voices
            voice1 = voices[0]
            voice2 = voices[1]
            
            print(f"\n🎵 Testing switch: {voice1['name']} → {voice2['name']}")
            
            # Set first voice
            try:
                self.engine.setProperty('voice', voice1['id'])
                current_voice = self.engine.getProperty('voice')
                print(f"   Set to voice 1: {current_voice == voice1['id']} (requested: {voice1['id'][:50]}...)")
            except Exception as e:
                print(f"   ❌ Failed to set voice 1: {e}")
                return
            
            # Set second voice
            try:
                self.engine.setProperty('voice', voice2['id'])
                current_voice = self.engine.getProperty('voice')
                print(f"   Set to voice 2: {current_voice == voice2['id']} (requested: {voice2['id'][:50]}...)")
            except Exception as e:
                print(f"   ❌ Failed to set voice 2: {e}")
                return
            
            # Test if voice property actually changes
            voice_switching_works = True
            
            for i, voice in enumerate(voices[:3]):  # Test first 3 voices
                try:
                    self.engine.setProperty('voice', voice['id'])
                    current_voice = self.engine.getProperty('voice')
                    
                    if current_voice == voice['id']:
                        print(f"   ✅ Voice {i+1} ({voice['name']}): Switch successful")
                    else:
                        print(f"   ❌ Voice {i+1} ({voice['name']}): Switch failed")
                        print(f"      Expected: {voice['id'][:50]}...")
                        print(f"      Got: {str(current_voice)[:50]}...")
                        voice_switching_works = False
                        
                except Exception as e:
                    print(f"   ❌ Voice {i+1} ({voice['name']}): Exception - {e}")
                    voice_switching_works = False
            
            self.voice_analysis['switching_works'] = voice_switching_works
            
        except Exception as e:
            print(f"❌ Voice switching test failed: {e}")
            self.voice_analysis['switching_works'] = False
    
    def _provide_diagnostic_summary(self):
        """Provide comprehensive diagnostic summary"""
        print("📋 DIAGNOSTIC SUMMARY")
        print("-" * 60)
        
        # System status
        print("🖥️ System Status:")
        if self.system_info:
            print(f"   Python: {self.system_info.get('python_version', 'Unknown')}")
            print(f"   OS: {self.system_info.get('os_info', 'Unknown')}")
            print(f"   pyttsx3: {'✅ Available' if self.system_info.get('pyttsx3_available') else '❌ Not Available'}")
        
        # Engine status
        print(f"\n🔧 Engine Status:")
        print(f"   Initialization: {'✅ Success' if self.engine else '❌ Failed'}")
        
        # Voice status
        print(f"\n🎵 Voice Status:")
        voice_count = self.voice_analysis.get('total_found', 0)
        print(f"   Voices found: {voice_count}")
        
        if voice_count > 0:
            switching_works = self.voice_analysis.get('switching_works', False)
            print(f"   Voice switching: {'✅ Working' if switching_works else '❌ Not working'}")
            
            print(f"\n📝 Available Voices:")
            for voice in self.voice_analysis.get('voices', []):
                name = voice.get('name', 'Unknown')
                print(f"   - {name}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        
        if not self.engine:
            print("   ❌ CRITICAL: Fix pyttsx3 engine initialization")
            print("   → Check pyttsx3 installation")
            print("   → Try reinstalling: pip uninstall pyttsx3 && pip install pyttsx3")
            
        elif voice_count == 0:
            print("   ❌ CRITICAL: No voices detected")
            print("   → Check Windows SAPI installation")
            print("   → Install additional voice packs")
            
        elif voice_count == 1:
            print("   ⚠️ WARNING: Only one voice available")
            print("   → Install additional Windows voice packs")
            print("   → Voice switching will not work with single voice")
            
        elif not self.voice_analysis.get('switching_works', False):
            print("   ⚠️ WARNING: Voice switching not working")
            print("   → pyttsx3 voice switching may be broken")
            print("   → Consider alternative TTS solutions")
            
        else:
            print("   ✅ EXCELLENT: Voice system fully functional")
            print("   → Ready for VPA implementation")
            print("   → Voice switching working properly")

def main():
    """Main diagnostic function"""
    print("🚀 VPA Voice System Diagnostic Tool")
    print("This will systematically test your voice system")
    
    try:
        diagnostic = VoiceSystemDiagnostic()
        success = diagnostic.run_complete_diagnostic()
        
        if success:
            print(f"\n✅ Diagnostic completed successfully")
        else:
            print(f"\n❌ Diagnostic completed with issues")
            
    except KeyboardInterrupt:
        print("\n⚠️ Diagnostic interrupted by user")
    except Exception as e:
        print(f"\n💥 Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n📝 Press Enter to exit...")

if __name__ == "__main__":
    main()
