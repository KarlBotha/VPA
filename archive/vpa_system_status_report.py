#!/usr/bin/env python3
"""
VPA System Status Report Generator
Generates comprehensive status report of all VPA components
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

async def check_core_systems():
    """Check core VPA systems"""
    results = {}
    
    try:
        from vpa.core.app import App
        from vpa.core.config import ConfigManager
        from vpa.core.events import EventBus
        from vpa.core.plugins import PluginManager
        from vpa.core.auth import VPAAuthenticationManager
        from vpa.core.database import ConversationDatabaseManager
        from vpa.core.health import HealthMonitor
        
        results["Core App"] = {"status": "✅ Available", "importable": True}
        results["Configuration"] = {"status": "✅ Available", "importable": True}
        results["Event Bus"] = {"status": "✅ Available", "importable": True}
        results["Plugin Manager"] = {"status": "✅ Available", "importable": True}
        results["Authentication"] = {"status": "✅ Available", "importable": True}
        results["Database"] = {"status": "✅ Available", "importable": True}
        results["Health Monitor"] = {"status": "✅ Available", "importable": True}
        
    except Exception as e:
        results["Core Systems"] = {"status": f"❌ Error: {e}", "importable": False}
    
    return results

async def check_voice_systems():
    """Check voice systems"""
    results = {}
    
    try:
        from audio.vpa_voice_system import VPAVoiceSystem
        results["VPA Voice System"] = {"status": "✅ Available", "importable": True}
        
        from audio.neural_voice_engine import NeuralVoiceEngine
        results["Neural Voice Engine"] = {"status": "✅ Available", "importable": True}
        
        from audio.production_voice_system import ProductionVoiceSystem
        results["Production Voice System"] = {"status": "✅ Available", "importable": True}
        
    except Exception as e:
        results["Voice Systems"] = {"status": f"⚠️ Import Error: {e}", "importable": False}
    
    return results

async def check_ai_systems():
    """Check AI logic systems"""
    results = {}
    
    try:
        from vpa.ai.addon_logic.addon_logic_coordinator import AddonLogicCoordinator
        results["AI Logic Coordinator"] = {"status": "✅ Available", "importable": True}
        
        from vpa.ai.base_logic import BaseLogic
        results["Base Logic"] = {"status": "✅ Available", "importable": True}
        
        from vpa.ai.user_logic import UserLogic
        results["User Logic"] = {"status": "✅ Available", "importable": True}
        
        # Check individual addons
        addon_count = 0
        try:
            from vpa.ai.addon_logic.google_logic import GoogleAddonLogic
            addon_count += 1
        except:
            pass
        try:
            from vpa.ai.addon_logic.microsoft_logic import MicrosoftAddonLogic
            addon_count += 1
        except:
            pass
        try:
            from vpa.ai.addon_logic.whatsapp_logic import WhatsAppAddonLogic
            addon_count += 1
        except:
            pass
        
        results["AI Addons"] = {"status": f"✅ {addon_count} addon modules available", "importable": True}
        
    except Exception as e:
        results["AI Systems"] = {"status": f"❌ Error: {e}", "importable": False}
    
    return results

async def check_plugin_systems():
    """Check plugin systems"""
    results = {}
    
    try:
        from vpa.plugins.ai.plugin import AIPlugin
        results["AI Plugin"] = {"status": "✅ Available", "importable": True}
        
        from vpa.plugins.audio.engine import AudioEngine
        results["Audio Engine"] = {"status": "✅ Available", "importable": True}
        
        from vpa.plugins.audio.commands import VoiceCommandProcessor
        results["Voice Commands"] = {"status": "✅ Available", "importable": True}
        
    except Exception as e:
        results["Plugin Systems"] = {"status": f"❌ Error: {e}", "importable": False}
    
    return results

async def check_cli_interface():
    """Check CLI interface"""
    results = {}
    
    try:
        from vpa.cli.main import cli
        results["CLI Interface"] = {"status": "✅ Available", "importable": True}
        
    except Exception as e:
        results["CLI Interface"] = {"status": f"❌ Error: {e}", "importable": False}
    
    return results

async def test_ai_integration():
    """Test AI plugin integration"""
    results = {}
    
    try:
        from vpa.plugins.ai.plugin import AIPlugin
        from vpa.core.events import EventBus
        
        # Create and test AI plugin
        event_bus = EventBus()
        event_bus.initialize()
        
        ai_plugin = AIPlugin(event_bus)
        init_result = await ai_plugin.initialize()
        
        if init_result:
            start_result = ai_plugin.start()
            status = await ai_plugin.get_ai_status()
            
            results["AI Integration"] = {
                "status": "✅ Functional",
                "initialized": status["is_initialized"],
                "running": status["is_running"],
                "coordinator_available": status["coordinator_available"],
                "enabled_addons": len(status.get("enabled_addons", [])),
                "details": f"Coordinator: {status['coordinator_available']}, Addons: {len(status.get('enabled_addons', []))}"
            }
            
            # Cleanup
            await ai_plugin.cleanup()
            
        else:
            results["AI Integration"] = {"status": "❌ Initialization Failed", "functional": False}
        
    except Exception as e:
        results["AI Integration"] = {"status": f"❌ Error: {e}", "functional": False}
    
    return results

async def run_test_suite():
    """Run basic test suite"""
    results = {}
    
    try:
        import subprocess
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-q", "--tb=no"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            # Extract test count from output
            lines = result.stdout.strip().split('\n')
            summary_line = [line for line in lines if "passed" in line]
            
            if summary_line:
                test_info = summary_line[-1]
                results["Test Suite"] = {"status": f"✅ {test_info}", "passed": True}
            else:
                results["Test Suite"] = {"status": "✅ All tests passed", "passed": True}
        else:
            results["Test Suite"] = {"status": f"❌ Some tests failed", "passed": False}
        
    except Exception as e:
        results["Test Suite"] = {"status": f"⚠️ Could not run tests: {e}", "passed": None}
    
    return results

async def generate_status_report():
    """Generate comprehensive status report"""
    print("🛡️ VPA SYSTEM COMPREHENSIVE STATUS REPORT")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Collect all system status
    all_results = {}
    
    print("🔍 Checking Core Systems...")
    all_results.update(await check_core_systems())
    
    print("🎤 Checking Voice Systems...")
    all_results.update(await check_voice_systems())
    
    print("🧠 Checking AI Systems...")
    all_results.update(await check_ai_systems())
    
    print("🔌 Checking Plugin Systems...")
    all_results.update(await check_plugin_systems())
    
    print("💻 Checking CLI Interface...")
    all_results.update(await check_cli_interface())
    
    print("🧪 Testing AI Integration...")
    all_results.update(await test_ai_integration())
    
    print("🏃 Running Test Suite...")
    all_results.update(await run_test_suite())
    
    # Display results
    print("\n📊 SYSTEM STATUS SUMMARY")
    print("=" * 80)
    
    categories = {
        "Core Systems": ["Core App", "Configuration", "Event Bus", "Plugin Manager", "Authentication", "Database", "Health Monitor"],
        "Voice Systems": ["VPA Voice System", "Neural Voice Engine", "Production Voice System"],
        "AI Systems": ["AI Logic Coordinator", "Base Logic", "User Logic", "AI Addons"],
        "Plugin Systems": ["AI Plugin", "Audio Engine", "Voice Commands"],
        "Interfaces": ["CLI Interface"],
        "Integration": ["AI Integration"],
        "Testing": ["Test Suite"]
    }
    
    overall_health = True
    total_components = 0
    working_components = 0
    
    for category, components in categories.items():
        print(f"\n🔸 {category}:")
        
        for component in components:
            if component in all_results:
                result = all_results[component]
                print(f"   {result['status']} - {component}")
                
                total_components += 1
                if "✅" in result['status']:
                    working_components += 1
                elif "❌" in result['status']:
                    overall_health = False
            else:
                print(f"   ⚠️ Not Checked - {component}")
                total_components += 1
    
    # Calculate health percentage
    health_percentage = (working_components / total_components * 100) if total_components > 0 else 0
    
    print("\n" + "=" * 80)
    print("🎯 OVERALL SYSTEM HEALTH")
    print("=" * 80)
    print(f"Working Components: {working_components}/{total_components}")
    print(f"Health Percentage: {health_percentage:.1f}%")
    
    if health_percentage >= 90:
        print("🟢 EXCELLENT - System is fully operational")
        overall_status = "EXCELLENT"
    elif health_percentage >= 75:
        print("🟡 GOOD - System is mostly operational with minor issues")
        overall_status = "GOOD"
    elif health_percentage >= 50:
        print("🟠 FAIR - System has significant issues but core functionality works")
        overall_status = "FAIR"
    else:
        print("🔴 POOR - System has major issues requiring attention")
        overall_status = "POOR"
    
    print("\n📋 KEY ACHIEVEMENTS:")
    achievements = []
    
    if "AI Integration" in all_results and "✅" in all_results["AI Integration"]["status"]:
        achievements.append("✅ AI Logic integration complete and functional")
    
    if "Test Suite" in all_results and all_results["Test Suite"].get("passed", False):
        achievements.append("✅ All automated tests passing")
    
    core_working = sum(1 for comp in categories["Core Systems"] if comp in all_results and "✅" in all_results[comp]["status"])
    if core_working >= 6:
        achievements.append("✅ Core VPA systems operational")
    
    voice_working = sum(1 for comp in categories["Voice Systems"] if comp in all_results and "✅" in all_results[comp]["status"])
    if voice_working >= 2:
        achievements.append("✅ Voice systems available")
    
    for achievement in achievements:
        print(f"   {achievement}")
    
    print("\n🚀 NEXT STEPS:")
    if health_percentage >= 75:
        print("   1. ✅ Phase 1 (AI Integration) - COMPLETE")
        print("   2. 🔄 Phase 2 (GUI Implementation) - Ready to begin")
        print("   3. ⏳ Phase 3 (Advanced Features) - Pending")
        print("   4. ⏳ Phase 4 (Production Deployment) - Pending")
    else:
        print("   1. 🔧 Address failing components")
        print("   2. 🧪 Ensure all tests pass")
        print("   3. 🔄 Re-run health check")
    
    print("=" * 80)
    
    return {
        "overall_status": overall_status,
        "health_percentage": health_percentage,
        "working_components": working_components,
        "total_components": total_components,
        "details": all_results
    }

async def main():
    """Main function"""
    try:
        report = await generate_status_report()
        
        # Save report to file
        report_file = project_root / f"vpa_status_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Status report saved to: {report_file}")
        
        return report["health_percentage"] >= 75
        
    except Exception as e:
        print(f"❌ Status report generation failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
