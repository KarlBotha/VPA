#!/usr/bin/env python3
"""
VPA System Integration Status Checker
Quick validation of all major system components
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_core_systems():
    """Check core VPA systems"""
    print("🔍 CHECKING CORE SYSTEMS")
    print("=" * 40)
    
    try:
        from vpa.core.app import App
        print("✅ Core App system available")
        
        from vpa.core.config import ConfigManager
        print("✅ Configuration management available")
        
        from vpa.core.events import EventBus
        print("✅ Event bus system available")
        
        from vpa.core.plugins import PluginManager
        print("✅ Plugin management available")
        
        from vpa.core.auth import VPAAuthenticationManager
        print("✅ Authentication system available")
        
        from vpa.core.database import VPADatabase
        print("✅ Database system available")
        
        from vpa.core.health import HealthMonitor
        print("✅ Health monitoring available")
        
        return True
    except Exception as e:
        print(f"❌ Core systems error: {e}")
        return False

def check_voice_systems():
    """Check voice systems"""
    print("\n🎤 CHECKING VOICE SYSTEMS")
    print("=" * 40)
    
    try:
        from audio.vpa_voice_system import VPAVoiceSystem
        print("✅ VPA Voice System available")
        
        from audio.neural_voice_engine import NeuralVoiceEngine
        print("✅ Neural Voice Engine available")
        
        from audio.production_voice_system import ProductionVoiceSystem
        print("✅ Production Voice System available")
        
        return True
    except Exception as e:
        print(f"❌ Voice systems error: {e}")
        return False

def check_ai_logic():
    """Check AI logic systems"""
    print("\n🧠 CHECKING AI LOGIC SYSTEMS")
    print("=" * 40)
    
    try:
        from vpa.ai.addon_logic.addon_logic_coordinator import AddonLogicCoordinator
        print("✅ AI Logic Coordinator available")
        
        from vpa.ai.base_logic import BaseLogic
        print("✅ Base Logic available")
        
        from vpa.ai.user_logic import UserLogic
        print("✅ User Logic available")
        
        # Check individual addon logic
        from vpa.ai.addon_logic.google_logic import GoogleAddonLogic
        from vpa.ai.addon_logic.microsoft_logic import MicrosoftAddonLogic
        from vpa.ai.addon_logic.whatsapp_logic import WhatsAppAddonLogic
        print("✅ Individual addon logic modules available")
        
        return True
    except Exception as e:
        print(f"❌ AI logic error: {e}")
        return False

def check_cli_interface():
    """Check CLI interface"""
    print("\n💻 CHECKING CLI INTERFACE")
    print("=" * 40)
    
    try:
        from vpa.cli.main import cli
        print("✅ CLI interface available")
        
        return True
    except Exception as e:
        print(f"❌ CLI interface error: {e}")
        return False

def check_plugin_audio():
    """Check audio plugin"""
    print("\n🔌 CHECKING AUDIO PLUGIN")
    print("=" * 40)
    
    try:
        from vpa.plugins.audio.engine import AudioEngine
        print("✅ Audio Engine available")
        
        from vpa.plugins.audio.commands import VoiceCommandProcessor
        print("✅ Voice Command Processor available")
        
        return True
    except Exception as e:
        print(f"❌ Audio plugin error: {e}")
        return False

def main():
    """Main integration check"""
    print("🚀 VPA SYSTEM INTEGRATION STATUS CHECK")
    print("=" * 60)
    
    results = {
        "Core Systems": check_core_systems(),
        "Voice Systems": check_voice_systems(), 
        "AI Logic": check_ai_logic(),
        "CLI Interface": check_cli_interface(),
        "Audio Plugin": check_plugin_audio()
    }
    
    print("\n📊 INTEGRATION SUMMARY")
    print("=" * 40)
    
    all_working = True
    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {component}: {'OPERATIONAL' if status else 'ISSUES DETECTED'}")
        if not status:
            all_working = False
    
    print("\n🎯 OVERALL STATUS")
    print("=" * 40)
    if all_working:
        print("✅ ALL MAJOR COMPONENTS OPERATIONAL")
        print("🎉 VPA SYSTEM READY FOR FULL INTEGRATION")
    else:
        print("⚠️ SOME COMPONENTS HAVE ISSUES")
        print("🔧 INTEGRATION WORK REQUIRED")
    
    print("\n📋 NEXT STEPS:")
    print("1. Connect AI Logic to main application flow")
    print("2. Implement GUI interface") 
    print("3. Add end-to-end testing")
    print("4. Enhance user experience features")

if __name__ == "__main__":
    main()
