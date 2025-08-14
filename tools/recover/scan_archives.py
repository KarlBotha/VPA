#!/usr/bin/env python3
import os, re, json, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

PATTERNS = {
    "gui_manager": r"class\s+VPAGUIManager\b",
    "auth_coord": r"class\s+VPAAuthenticationCoordinator\b",
    "secure_config": r"class\s+SecureConfigManager\b",
    "conversation_db": r"class\s+ConversationDatabaseManager\b",
    "login_window": r"class\s+.*LoginWindow\b",
    "register_window": r"class\s+.*Register.*Window\b",
    "settings_window": r"class\s+.*SettingsWindow\b",
    "graph_api": r"class\s+GraphAPIClient\b",
    "gmail_client": r"class\s+Gmail\b",
    "imap_client": r"class\s+.*IMAP\b",
    "smtp_client": r"class\s+.*SMTP\b",
    "openai_client": r"import openai|from openai",
    "anthropic_client": r"import anthropic|from anthropic",
    "google_ai": r"import google.generativeai|from google.generativeai",
    "speech_recognition": r"import speech_recognition|from speech_recognition",
    "whisper_client": r"import whisper|from whisper",
    "microphone": r"class\s+.*Microphone\b|Microphone\(",
    "tts_system": r"class\s+.*TTS\b|pyttsx3|edge_tts",
    "audio_manager": r"class\s+.*AudioManager\b",
    "chat_interface": r"class\s+.*ChatInterface\b|class\s+.*ChatWindow\b",
    "main_window": r"class\s+MainWindow\b|class\s+.*MainApplication\b"
}

def scan_file(filepath):
    """Scan a file for pattern matches"""
    matches = {}
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        for pattern_name, pattern in PATTERNS.items():
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                matches[pattern_name] = True
                
    except Exception as e:
        pass
    
    return matches

def scan_directory(directory):
    """Scan directory for Python files"""
    results = {}
    
    if not os.path.exists(directory):
        return results
    
    for root, dirs, files in os.walk(directory):
        # Skip __pycache__ and .git directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, ROOT)
                
                matches = scan_file(filepath)
                if matches:
                    results[rel_path] = matches
    
    return results

def generate_recovery_map(scan_results):
    """Generate recovery map with best candidates for each symbol"""
    recovery_map = {}
    
    for pattern_name in PATTERNS.keys():
        candidates = []
        for filepath, matches in scan_results.items():
            if matches.get(pattern_name):
                # Score files based on path preferences
                score = 0
                path_lower = filepath.lower()
                
                # Prefer certain directories
                if 'src/' in path_lower:
                    score += 10
                elif 'vpa/' in path_lower:
                    score += 8
                elif 'archive/' in path_lower:
                    score += 5
                elif 'legacy/' in path_lower:
                    score += 3
                
                # Prefer specific modules
                if pattern_name in ['gui_manager', 'main_window', 'chat_interface'] and 'gui' in path_lower:
                    score += 5
                elif pattern_name in ['auth_coord', 'login_window', 'register_window'] and 'auth' in path_lower:
                    score += 5
                elif pattern_name in ['openai_client', 'anthropic_client', 'google_ai'] and ('llm' in path_lower or 'ai' in path_lower):
                    score += 5
                elif pattern_name in ['speech_recognition', 'whisper_client', 'microphone'] and 'audio' in path_lower:
                    score += 5
                
                # Prefer non-test files
                if 'test' not in path_lower:
                    score += 2
                
                candidates.append((filepath, score))
        
        # Sort by score (highest first) and take top candidates
        candidates.sort(key=lambda x: x[1], reverse=True)
        recovery_map[pattern_name] = [c[0] for c in candidates[:5]]  # Top 5 candidates
    
    return recovery_map

def generate_report(scan_results, recovery_map):
    """Generate markdown recovery report"""
    report = ["# VPA Integration Recovery Report\n"]
    report.append(f"**Date**: {os.popen('date').read().strip()}")
    report.append("**Phase**: Integration Recovery - Archive Mining")
    report.append("**Scope**: GUI + Auth + LLM + Audio module discovery")
    report.append("")
    
    # Summary statistics
    total_files = len(scan_results)
    total_patterns = len([p for matches in scan_results.values() for p in matches if matches[p]])
    
    report.append("## 📊 **DISCOVERY SUMMARY**")
    report.append("")
    report.append(f"- **Files Scanned**: {total_files}")
    report.append(f"- **Pattern Matches**: {total_patterns}")
    report.append(f"- **Recovery Targets**: {len(PATTERNS)}")
    report.append("")
    
    # Recovery map summary
    report.append("## 🗺️ **RECOVERY MAP**")
    report.append("")
    report.append("| Component | Candidates Found | Best Match |")
    report.append("|-----------|------------------|------------|")
    
    for pattern_name, candidates in recovery_map.items():
        candidate_count = len(candidates)
        best_match = candidates[0] if candidates else "❌ NOT FOUND"
        component_name = pattern_name.replace('_', ' ').title()
        
        status = "✅" if candidates else "❌"
        report.append(f"| {component_name} | {candidate_count} | {status} `{best_match}` |")
    
    report.append("")
    
    # Detailed findings
    report.append("## 🔍 **DETAILED FINDINGS**")
    report.append("")
    
    # Group by category
    categories = {
        "GUI Components": ["gui_manager", "main_window", "chat_interface", "login_window", "register_window", "settings_window"],
        "Authentication": ["auth_coord", "secure_config"],
        "Database": ["conversation_db"],
        "LLM Integration": ["openai_client", "anthropic_client", "google_ai"],
        "Audio System": ["tts_system", "audio_manager", "speech_recognition", "whisper_client", "microphone"],
        "External APIs": ["graph_api", "gmail_client", "imap_client", "smtp_client"]
    }
    
    for category, patterns in categories.items():
        report.append(f"### {category}")
        report.append("")
        
        found_any = False
        for pattern in patterns:
            candidates = recovery_map.get(pattern, [])
            if candidates:
                found_any = True
                report.append(f"- ✅ **{pattern.replace('_', ' ').title()}**: {len(candidates)} candidate(s)")
                for i, candidate in enumerate(candidates[:3]):  # Show top 3
                    report.append(f"  - `{candidate}`")
                if len(candidates) > 3:
                    report.append(f"  - *(+{len(candidates) - 3} more)*")
            else:
                report.append(f"- ❌ **{pattern.replace('_', ' ').title()}**: Not found")
        
        if not found_any:
            report.append("- *No components found in this category*")
        
        report.append("")
    
    # Implementation recommendations
    report.append("## 🚀 **IMPLEMENTATION RECOMMENDATIONS**")
    report.append("")
    
    # Check what's available for implementation
    gui_available = len(recovery_map.get("gui_manager", [])) > 0 or len(recovery_map.get("main_window", [])) > 0
    auth_available = len(recovery_map.get("auth_coord", [])) > 0
    llm_available = any(len(recovery_map.get(p, [])) > 0 for p in ["openai_client", "anthropic_client", "google_ai"])
    audio_available = len(recovery_map.get("speech_recognition", [])) > 0 or len(recovery_map.get("whisper_client", [])) > 0
    
    if gui_available:
        report.append("✅ **GUI Recovery**: Feasible - GUI components found")
        report.append("   - Implement `src/vpa/gui/chat_entry.py` with dynamic loading")
        report.append("   - Add `--gui` CLI flag")
    else:
        report.append("❌ **GUI Recovery**: Limited - Create minimal tkinter fallback")
    
    if auth_available:
        report.append("✅ **Auth Recovery**: Feasible - Authentication coordinator found")
        report.append("   - Implement `src/vpa/auth/auth_bridge.py`")
        report.append("   - Restore login/register flows")
    else:
        report.append("⚠️ **Auth Recovery**: Basic - Simple config-based auth only")
    
    if llm_available:
        report.append("✅ **LLM Recovery**: Feasible - LLM integrations found")
        report.append("   - Implement `src/vpa/llm/llm_router.py`")
        report.append("   - Add `--chat` CLI flag")
    else:
        report.append("⚠️ **LLM Recovery**: Fallback - Echo/mock responses only")
    
    if audio_available:
        report.append("✅ **Audio Recovery**: Feasible - STT components found")
        report.append("   - Implement `src/vpa/audio/stt_entry.py`")
        report.append("   - Add microphone input capabilities")
    else:
        report.append("⚠️ **Audio Recovery**: TTS-only - No STT integration")
    
    report.append("")
    report.append("## 🎯 **NEXT ACTIONS**")
    report.append("")
    report.append("1. **Create dynamic loaders** for top-priority components")
    report.append("2. **Implement CLI flags** (`--gui`, `--chat`, `--listen`)")
    report.append("3. **Add feature flags** (`VPA_ENABLE_GUI`, `VPA_ENABLE_LLM`, `VPA_ENABLE_STT`)")
    report.append("4. **Test recovered functionality** with validation scripts")
    report.append("")
    report.append("---")
    report.append("*Recovery scan completed. Ready for dynamic integration implementation.*")
    
    return "\n".join(report)

def main():
    print("Scanning archive and legacy directories for recoverable modules...")
    
    # Directories to scan
    scan_dirs = [
        os.path.join(ROOT, "archive"),
        os.path.join(ROOT, "legacy"),
        os.path.join(ROOT, "src"),
        os.path.join(ROOT, "vpa"),  # In case there's a top-level vpa dir
        os.path.join(ROOT, "backup"),
        os.path.join(ROOT, "old"),
    ]
    
    all_results = {}
    
    for scan_dir in scan_dirs:
        print(f"Scanning {scan_dir}...")
        results = scan_directory(scan_dir)
        all_results.update(results)
    
    print(f"Scan completed. Found {len(all_results)} files with pattern matches.")
    
    # Generate recovery map
    recovery_map = generate_recovery_map(all_results)
    
    # Write recovery map JSON
    map_path = os.path.join(ROOT, "tools", "recover", "recover_map.json")
    with open(map_path, 'w', encoding='utf-8') as f:
        json.dump(recovery_map, f, indent=2)
    
    # Generate report
    report = generate_report(all_results, recovery_map)
    
    # Write report
    report_path = os.path.join(ROOT, "RECOVERY_REPORT.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Recovery map written to: {map_path}")
    print(f"Recovery report written to: {report_path}")
    
    # Summary
    found_components = sum(1 for candidates in recovery_map.values() if candidates)
    total_components = len(recovery_map)
    
    print(f"Recovery feasibility: {found_components}/{total_components} components found")

if __name__ == '__main__':
    main()
