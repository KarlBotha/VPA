#!/usr/bin/env python3
"""
Local Evidence Harvest: scan user-local directories for prior working UI/auth/LLM/STT/email code,
logs, and reference docs that are NOT solely in Git.

- Reads tools/recover/LOCAL_SCAN_PATHS.txt (env vars expanded).
- Scans for Python modules, config files, logs with VPA-related content.
- Produces RECOVERY_REPORT_LOCAL.md and local_candidates.json.
"""

import os
import re  
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCAN_PATHS_FILE = ROOT / "tools" / "recover" / "LOCAL_SCAN_PATHS.txt"

# Patterns for local discovery
PATTERNS = {
    "vpa_config": r"vpa.*config|VPA.*Config",
    "auth_tokens": r"access_token|refresh_token|oauth.*token",
    "chat_history": r"conversation|chat.*history|message.*log",
    "voice_settings": r"microphone|speaker|voice.*config|audio.*setting",
    "llm_config": r"openai.*key|anthropic.*key|gpt.*model|claude.*model",
    "gui_state": r"window.*state|ui.*config|interface.*setting",
    "email_config": r"smtp.*config|imap.*config|gmail.*credential",
    "login_cache": r"login.*cache|user.*session|credential.*store",
    "plugin_config": r"plugin.*config|extension.*setting|module.*config",
    "system_log": r"vpa.*log|error.*log|debug.*log|system.*log"
}

FILE_EXTENSIONS = ['.py', '.json', '.yaml', '.yml', '.ini', '.cfg', '.txt', '.log', '.md']

def expand_env_vars(path_str):
    """Expand environment variables in path string"""
    return os.path.expandvars(path_str)

def load_scan_paths():
    """Load scan paths from LOCAL_SCAN_PATHS.txt"""
    paths = []
    if SCAN_PATHS_FILE.exists():
        with open(SCAN_PATHS_FILE, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    expanded_path = expand_env_vars(line)
                    if os.path.exists(expanded_path):
                        paths.append(Path(expanded_path))
                    else:
                        print(f"Warning: Path not found: {expanded_path}")
    return paths

def scan_file_content(filepath):
    """Scan file for VPA-related patterns"""
    matches = {}
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as content_file:
            content = content_file.read()
        
        # Check for VPA references first
        if not re.search(r'vpa|VPA|Virtual.*Personal.*Assistant', content, re.IGNORECASE):
            return matches
        
        for pattern_name, pattern in PATTERNS.items():
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                matches[pattern_name] = {
                    "file": str(filepath),
                    "size": len(content),
                    "modified": filepath.stat().st_mtime if filepath.exists() else 0
                }
    except Exception:
        pass
    
    return matches

def scan_local_directories(scan_paths):
    """Scan local directories for VPA-related files"""
    all_matches = {}
    total_files_scanned = 0
    
    for base_path in scan_paths:
        print(f"Scanning local directory: {base_path}")
        
        try:
            for root, dirs, files in os.walk(base_path):
                # Skip system directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d.lower() not in 
                          ['node_modules', '__pycache__', 'venv', '.git', 'cache']]
                
                for file in files:
                    if any(file.lower().endswith(ext) for ext in FILE_EXTENSIONS):
                        filepath = Path(root) / file
                        total_files_scanned += 1
                        
                        matches = scan_file_content(filepath)
                        if matches:
                            rel_path = str(filepath.relative_to(base_path))
                            all_matches[rel_path] = matches
                            
        except Exception as e:
            print(f"Error scanning {base_path}: {e}")
    
    print(f"Local scan completed. {total_files_scanned} files scanned, {len(all_matches)} with VPA content.")
    return all_matches

def generate_local_report(scan_results):
    """Generate local recovery report"""
    report = ["# VPA Local Evidence Harvest Report\n"]
    report.append(f"**Date**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("**Scope**: User-local directories for VPA-related evidence")
    report.append("")
    
    if not scan_results:
        report.append("## ❌ **NO LOCAL EVIDENCE FOUND**")
        report.append("")
        report.append("No VPA-related files found in local directories.")
        report.append("This may indicate:")
        report.append("- Clean system with no previous VPA installations")
        report.append("- Files may be in different locations")
        report.append("- Previous installations were completely removed")
        report.append("")
        return "\n".join(report)
    
    # Summary
    total_files = len(scan_results)
    pattern_counts = {}
    for file_matches in scan_results.values():
        for pattern_name in file_matches.keys():
            pattern_counts[pattern_name] = pattern_counts.get(pattern_name, 0) + 1
    
    report.append("## 📊 **LOCAL DISCOVERY SUMMARY**")
    report.append("")
    report.append(f"- **Files with VPA Content**: {total_files}")
    report.append(f"- **Pattern Types Found**: {len(pattern_counts)}")
    report.append("")
    
    # Pattern frequency
    report.append("## 📈 **PATTERN FREQUENCY**")
    report.append("")
    report.append("| Pattern | Files | Description |")
    report.append("|---------|-------|-------------|")
    
    for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
        description = {
            "vpa_config": "Configuration files",
            "auth_tokens": "Authentication tokens",
            "chat_history": "Conversation logs",
            "voice_settings": "Audio/Voice config",
            "llm_config": "LLM API settings",
            "gui_state": "UI state/settings",
            "email_config": "Email credentials",
            "login_cache": "Cached login data",
            "plugin_config": "Plugin settings",
            "system_log": "System/error logs"
        }.get(pattern, "Unknown pattern")
        
        report.append(f"| {pattern.replace('_', ' ').title()} | {count} | {description} |")
    
    report.append("")
    
    # Detailed findings
    report.append("## 🔍 **DETAILED FINDINGS**")
    report.append("")
    
    for filepath, matches in scan_results.items():
        report.append(f"### `{filepath}`")
        report.append("")
        
        for pattern_name, details in matches.items():
            report.append(f"- **{pattern_name.replace('_', ' ').title()}**")
            report.append(f"  - Size: {details['size']:,} bytes")
            
            # Convert timestamp to readable format
            try:
                import datetime
                modified_date = datetime.datetime.fromtimestamp(details['modified']).strftime('%Y-%m-%d %H:%M:%S')
                report.append(f"  - Modified: {modified_date}")
            except:
                report.append(f"  - Modified: {details['modified']}")
        
        report.append("")
    
    # Recommendations
    report.append("## 🎯 **RECOVERY RECOMMENDATIONS**")
    report.append("")
    
    if "vpa_config" in pattern_counts:
        report.append("✅ **Config Recovery**: Local VPA config files found - examine for working settings")
    if "auth_tokens" in pattern_counts:
        report.append("⚠️ **Auth Recovery**: Token files found - check for valid credentials")
    if "chat_history" in pattern_counts:
        report.append("📚 **History Recovery**: Conversation logs available - restore user context")
    if "voice_settings" in pattern_counts:
        report.append("🎤 **Voice Recovery**: Audio settings found - restore preferred voice config")
    if "llm_config" in pattern_counts:
        report.append("🤖 **LLM Recovery**: API configs found - restore LLM connections")
    if "system_log" in pattern_counts:
        report.append("🔍 **Debug Recovery**: System logs available - analyze for error patterns")
    
    report.append("")
    report.append("---")
    report.append("*Local evidence harvest completed. Cross-reference with archive recovery for full picture.*")
    
    return "\n".join(report)

def main():
    """Main execution function"""
    print("Starting local evidence harvest...")
    
    # Load scan paths
    scan_paths = load_scan_paths()
    if not scan_paths:
        print("No valid scan paths found. Check LOCAL_SCAN_PATHS.txt")
        return
    
    print(f"Scanning {len(scan_paths)} local directories...")
    
    # Scan directories
    scan_results = scan_local_directories(scan_paths)
    
    # Create recovery candidates map
    local_candidates = {}
    for filepath, matches in scan_results.items():
        for pattern_name, details in matches.items():
            if pattern_name not in local_candidates:
                local_candidates[pattern_name] = []
            local_candidates[pattern_name].append({
                "file": details["file"],
                "size": details["size"],
                "modified": details["modified"]
            })
    
    # Write results
    output_dir = ROOT / "tools" / "recover"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write JSON candidates
    with open(output_dir / "local_candidates.json", 'w', encoding='utf-8') as json_file:
        json.dump(local_candidates, json_file, indent=2)
    
    # Write report
    report = generate_local_report(scan_results)
    with open(ROOT / "RECOVERY_REPORT_LOCAL.md", 'w', encoding='utf-8') as report_file:
        report_file.write(report)
    
    print(f"Local evidence harvest completed.")
    print(f"Results: local_candidates.json, RECOVERY_REPORT_LOCAL.md")
    
    return len(scan_results), len(local_candidates)

if __name__ == "__main__":
    main()
