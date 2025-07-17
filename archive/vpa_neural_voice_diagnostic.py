#!/usr/bin/env python3
"""
VPA Neural Voice System Direct Test
Tests the neural voice system independently to verify functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_neural_voice_direct():
    """Test the neural voice system directly"""
    try:
        print("🔍 DIAGNOSTIC: Testing Neural Voice System Direct Access")
        print("=" * 60)
        
        # Test direct neural voice engine
        from audio.neural_voice_engine import NeuralVoiceEngine
        print("✅ Neural Voice Engine imported successfully")
        
        # Initialize neural engine
        neural_engine = NeuralVoiceEngine()
        print("✅ Neural Voice Engine initialized")
        
        # Get available voices
        voices = neural_engine.get_available_voices()
        print(f"✅ Found {len(voices)} neural voices:")
        for voice in voices[:5]:  # Show first 5
            print(f"  - {voice.name} ({voice.voice_id})")
        
        # Test with Aria voice
        aria_voice = None
        for voice in voices:
            if 'aria' in voice.name.lower():
                aria_voice = voice
                break
        
        if aria_voice:
            print(f"✅ Found Aria voice: {aria_voice.name}")
            neural_engine.set_voice(aria_voice.voice_id)
            print("✅ Aria voice set successfully")
            
            # Test speech
            print("🎤 Testing speech synthesis...")
            success = neural_engine.speak("Hello! This is your VPA using the Aria neural voice. Your neural voice system is working correctly!", blocking=True)
            print(f"✅ Speech test result: {success}")
        else:
            print("⚠️ Aria voice not found, using default")
            success = neural_engine.speak("Hello! This is your VPA neural voice system. It is working correctly!", blocking=True)
            print(f"✅ Speech test result: {success}")
        
        print("=" * 60)
        print("🎉 Neural Voice System Test Complete!")
        
    except Exception as e:
        print(f"❌ Error during neural voice test: {e}")
        import traceback
        traceback.print_exc()

def test_production_voice_system():
    """Test the production voice system"""
    try:
        print("\n🔍 DIAGNOSTIC: Testing Production Voice System")
        print("=" * 60)
        
        from audio.production_voice_system import ProductionVoiceSystem
        print("✅ Production Voice System imported successfully")
        
        # Initialize production system
        production_system = ProductionVoiceSystem()
        print("✅ Production Voice System initialized")
        
        # Test speech
        print("🎤 Testing production speech...")
        success = production_system.speak_agent_response("Hello! This is your VPA production voice system. All systems are operational!", blocking=True)
        print(f"✅ Production speech test result: {success}")
        
        # Get catalog
        catalog = production_system.get_production_voice_catalog()
        print(f"✅ Production voice catalog: {len(catalog)} voices available")
        
        print("=" * 60)
        print("🎉 Production Voice System Test Complete!")
        
    except Exception as e:
        print(f"❌ Error during production voice test: {e}")
        import traceback
        traceback.print_exc()

def test_vpa_voice_system():
    """Test the complete VPA voice system"""
    try:
        print("\n🔍 DIAGNOSTIC: Testing Complete VPA Voice System")
        print("=" * 60)
        
        from audio.vpa_voice_system import VPAVoiceSystem
        print("✅ VPA Voice System imported successfully")
        
        # Initialize VPA voice system
        vpa_voice = VPAVoiceSystem()
        print("✅ VPA Voice System initialized")
        
        # Get status
        status = vpa_voice.get_system_status()
        print(f"✅ Primary system: {status['primary_system']}")
        print(f"✅ Initialization complete: {status['initialization_complete']}")
        print(f"✅ Neural engine available: {status['neural_engine']['available']}")
        
        # Test speech
        print("🎤 Testing VPA voice system speech...")
        success = vpa_voice.speak("Hello! This is your complete VPA voice system. All neural voice components are operational and ready for use!", blocking=True)
        print(f"✅ VPA speech test result: {success}")
        
        # Get available voices
        voices = vpa_voice.get_available_voices()
        print(f"✅ Available voices: {len(voices)}")
        
        print("=" * 60)
        print("🎉 Complete VPA Voice System Test Complete!")
        
    except Exception as e:
        print(f"❌ Error during VPA voice system test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 VPA Neural Voice System Comprehensive Diagnostic")
    print("This test verifies all neural voice components are working correctly")
    print("=" * 80)
    
    # Run all tests
    test_neural_voice_direct()
    test_production_voice_system()
    test_vpa_voice_system()
    
    print("\n" + "=" * 80)
    print("🏁 All VPA Voice System Diagnostics Complete!")
    print("If you heard voice output from all tests, your VPA is fully operational!")
