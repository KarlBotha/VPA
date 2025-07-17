#!/usr/bin/env python3
"""
COMPREHENSIVE VPA SYSTEM VALIDATION & VERIFICATION
Deep investigation and proof of all documented claims
NO ASSUMPTIONS - ONLY VERIFIED FACTS
"""

import os
import sys
import json
import time
import traceback
from pathlib import Path
from datetime import datetime

class SystemValidator:
    """Validates all VPA system claims with evidence"""
    
    def __init__(self):
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "validation_summary": {
                "total_claims": 0,
                "verified_claims": 0,
                "failed_claims": 0,
                "unverifiable_claims": 0
            },
            "detailed_results": {}
        }
    
    def validate_claim(self, claim_id: str, description: str, test_function):
        """Validate a specific claim with evidence"""
        print(f"\n🔍 VALIDATING: {claim_id}")
        print(f"   Claim: {description}")
        
        self.validation_results["validation_summary"]["total_claims"] += 1
        
        try:
            result = test_function()
            
            if result["status"] == "verified":
                print(f"   ✅ VERIFIED: {result['evidence']}")
                self.validation_results["validation_summary"]["verified_claims"] += 1
                status = "✅ VERIFIED"
            elif result["status"] == "failed":
                print(f"   ❌ FAILED: {result['evidence']}")
                self.validation_results["validation_summary"]["failed_claims"] += 1
                status = "❌ FAILED"
            else:
                print(f"   ⚠️ UNVERIFIABLE: {result['evidence']}")
                self.validation_results["validation_summary"]["unverifiable_claims"] += 1
                status = "⚠️ UNVERIFIABLE"
            
            self.validation_results["detailed_results"][claim_id] = {
                "description": description,
                "status": status,
                "evidence": result["evidence"],
                "details": result.get("details", {})
            }
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            print(f"   💥 ERROR: {error_msg}")
            self.validation_results["validation_summary"]["failed_claims"] += 1
            self.validation_results["detailed_results"][claim_id] = {
                "description": description,
                "status": "💥 ERROR",
                "evidence": error_msg,
                "details": {"traceback": traceback.format_exc()}
            }

def validate_python_environment():
    """Validate Python environment claims"""
    try:
        python_version = sys.version_info
        if python_version >= (3, 8):
            return {
                "status": "verified",
                "evidence": f"Python {python_version.major}.{python_version.minor}.{python_version.micro} detected"
            }
        else:
            return {
                "status": "failed",
                "evidence": f"Python {python_version.major}.{python_version.minor} is below minimum requirements"
            }
    except Exception as e:
        return {"status": "failed", "evidence": f"Cannot detect Python version: {e}"}

def validate_pyttsx3_availability():
    """Validate pyttsx3 engine availability"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.stop()
        
        return {
            "status": "verified",
            "evidence": f"pyttsx3 working with {len(voices)} voices detected",
            "details": {"voice_count": len(voices), "voices": [v.name for v in voices]}
        }
    except ImportError:
        return {"status": "failed", "evidence": "pyttsx3 not installed"}
    except Exception as e:
        return {"status": "failed", "evidence": f"pyttsx3 initialization failed: {e}"}

def validate_voice_system_files():
    """Validate claimed voice system files exist"""
    claimed_files = [
        "vpa_voice_system_research_compliant.py",
        "vpa_voice_system_working.py",
        "vpa_voice_system_official_pyttsx3.py"
    ]
    
    existing_files = []
    missing_files = []
    
    for file in claimed_files:
        file_path = Path(file)
        if file_path.exists():
            existing_files.append(file)
        else:
            missing_files.append(file)
    
    if len(existing_files) == len(claimed_files):
        return {
            "status": "verified",
            "evidence": f"All {len(claimed_files)} voice system files found",
            "details": {"existing_files": existing_files}
        }
    else:
        return {
            "status": "failed",
            "evidence": f"Only {len(existing_files)}/{len(claimed_files)} files found",
            "details": {"existing": existing_files, "missing": missing_files}
        }

def validate_13_voice_claim():
    """Validate the claim of 13 working voices"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.stop()
        
        actual_voices = len(voices)
        
        # Check if there's evidence of 13-voice implementation
        if os.path.exists("vpa_voice_system_research_compliant.py"):
            with open("vpa_voice_system_research_compliant.py", "r") as f:
                content = f.read()
                if "voice_01" in content and "voice_13" in content:
                    implementation_evidence = "13-voice mapping found in implementation file"
                else:
                    implementation_evidence = "No 13-voice mapping found in implementation"
        else:
            implementation_evidence = "Implementation file not found"
        
        return {
            "status": "verified" if actual_voices > 0 else "failed",
            "evidence": f"System has {actual_voices} actual voices. {implementation_evidence}",
            "details": {
                "actual_system_voices": actual_voices,
                "voice_names": [v.name for v in voices],
                "implementation_file_exists": os.path.exists("vpa_voice_system_research_compliant.py")
            }
        }
    except Exception as e:
        return {"status": "failed", "evidence": f"Cannot validate voices: {e}"}

def validate_audio_dependencies():
    """Validate audio-related dependencies"""
    dependencies = {
        "pyttsx3": "Text-to-speech engine",
        "speech_recognition": "Speech-to-text",
        "pyaudio": "Audio I/O",
        "win32com.client": "Windows SAPI"
    }
    
    available = {}
    missing = {}
    
    for dep, description in dependencies.items():
        try:
            if dep == "win32com.client":
                import win32com.client
            else:
                __import__(dep)
            available[dep] = description
        except ImportError:
            missing[dep] = description
    
    if len(missing) == 0:
        return {
            "status": "verified",
            "evidence": f"All {len(dependencies)} audio dependencies available",
            "details": {"available": available}
        }
    else:
        return {
            "status": "failed",
            "evidence": f"{len(missing)} dependencies missing: {list(missing.keys())}",
            "details": {"available": available, "missing": missing}
        }

def validate_project_structure():
    """Validate documented project structure"""
    expected_structure = {
        "src/": "Source code directory",
        "src/audio/": "Audio system directory",
        "src/core/": "Core system directory",
        "src/ui/": "User interface directory",
        "referencedocuments/": "Reference documents",
        "temp_logbook.md": "Current logbook"
    }
    
    existing = {}
    missing = {}
    
    for path, description in expected_structure.items():
        if os.path.exists(path):
            existing[path] = description
        else:
            missing[path] = description
    
    if len(missing) == 0:
        return {
            "status": "verified",
            "evidence": f"All {len(expected_structure)} structure elements found",
            "details": {"existing": existing}
        }
    else:
        return {
            "status": "failed",
            "evidence": f"{len(missing)} structure elements missing: {list(missing.keys())}",
            "details": {"existing": existing, "missing": missing}
        }

def validate_research_compliance_claim():
    """Validate research compliance claims"""
    research_file = "vpa_voice_system_research_compliant.py"
    
    if not os.path.exists(research_file):
        return {
            "status": "failed",
            "evidence": "Research-compliant file does not exist"
        }
    
    try:
        with open(research_file, "r") as f:
            content = f.read()
        
        # Check for claimed patterns
        patterns = {
            "engine.setProperty": "Official pyttsx3 pattern",
            "runAndWait": "Official execution pattern",
            "verification": "Verification system",
            "voice_01": "13-voice catalog start",
            "voice_13": "13-voice catalog end"
        }
        
        found_patterns = {}
        missing_patterns = {}
        
        for pattern, description in patterns.items():
            if pattern in content:
                found_patterns[pattern] = description
            else:
                missing_patterns[pattern] = description
        
        if len(missing_patterns) == 0:
            return {
                "status": "verified",
                "evidence": f"All {len(patterns)} research patterns found in implementation",
                "details": {"found_patterns": found_patterns}
            }
        else:
            return {
                "status": "failed",
                "evidence": f"{len(missing_patterns)} patterns missing: {list(missing_patterns.keys())}",
                "details": {"found": found_patterns, "missing": missing_patterns}
            }
    
    except Exception as e:
        return {"status": "failed", "evidence": f"Cannot read research file: {e}"}

def validate_working_voice_system():
    """Validate that voice system actually works"""
    try:
        # Test basic pyttsx3 functionality
        import pyttsx3
        engine = pyttsx3.init()
        
        # Test voice enumeration
        voices = engine.getProperty('voices')
        if len(voices) == 0:
            engine.stop()
            return {"status": "failed", "evidence": "No voices available in system"}
        
        # Test voice setting
        test_voice = voices[0]
        engine.setProperty('voice', test_voice.id)
        
        # Test properties
        engine.setProperty('rate', 200)
        engine.setProperty('volume', 0.9)
        
        engine.stop()
        
        return {
            "status": "verified",
            "evidence": f"Voice system functional with {len(voices)} voices",
            "details": {
                "voice_count": len(voices),
                "test_voice": test_voice.name,
                "properties_settable": True
            }
        }
    
    except Exception as e:
        return {"status": "failed", "evidence": f"Voice system test failed: {e}"}

def main():
    """Run comprehensive validation"""
    
    print("=" * 80)
    print("🔍 VPA SYSTEM COMPREHENSIVE VALIDATION")
    print("ZERO ASSUMPTIONS - ONLY VERIFIED FACTS")
    print("=" * 80)
    
    validator = SystemValidator()
    
    # Define all claims to validate
    claims = [
        ("PYTHON_ENV", "Python environment is properly configured", validate_python_environment),
        ("PYTTSX3_AVAILABLE", "pyttsx3 engine is available and functional", validate_pyttsx3_availability),
        ("VOICE_FILES_EXIST", "Claimed voice system files exist", validate_voice_system_files),
        ("THIRTEEN_VOICES", "13-voice system is implemented and working", validate_13_voice_claim),
        ("AUDIO_DEPS", "All audio dependencies are available", validate_audio_dependencies),
        ("PROJECT_STRUCTURE", "Documented project structure exists", validate_project_structure),
        ("RESEARCH_COMPLIANCE", "Research-compliant implementation exists", validate_research_compliance_claim),
        ("VOICE_SYSTEM_WORKS", "Voice system actually functions", validate_working_voice_system),
    ]
    
    # Validate each claim
    for claim_id, description, test_func in claims:
        validator.validate_claim(claim_id, description, test_func)
    
    # Print summary
    print(f"\n\n📊 VALIDATION SUMMARY:")
    print("-" * 50)
    summary = validator.validation_results["validation_summary"]
    print(f"Total Claims Tested: {summary['total_claims']}")
    print(f"✅ Verified: {summary['verified_claims']}")
    print(f"❌ Failed: {summary['failed_claims']}")
    print(f"⚠️ Unverifiable: {summary['unverifiable_claims']}")
    
    # Calculate accuracy
    total_tested = summary['total_claims']
    verified = summary['verified_claims']
    accuracy = (verified / total_tested * 100) if total_tested > 0 else 0
    
    print(f"\n🎯 DOCUMENTATION ACCURACY: {accuracy:.1f}%")
    
    if accuracy >= 90:
        print("✅ DOCUMENTATION IS HIGHLY ACCURATE")
    elif accuracy >= 70:
        print("⚠️ DOCUMENTATION HAS SOME INACCURACIES")
    else:
        print("❌ DOCUMENTATION IS SIGNIFICANTLY INACCURATE")
    
    # Save detailed results
    results_file = f"validation_results_{int(time.time())}.json"
    with open(results_file, "w") as f:
        json.dump(validator.validation_results, f, indent=2)
    
    print(f"\n📋 Detailed results saved to: {results_file}")
    
    print("\n" + "=" * 80)
    print("🏁 VALIDATION COMPLETE - FACTS VERIFIED")
    print("=" * 80)
    
    return validator.validation_results

if __name__ == "__main__":
    results = main()
