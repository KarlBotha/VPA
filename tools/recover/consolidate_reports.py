#!/usr/bin/env python3
# Merge local + archive maps; detect what's missing from src; produce consolidated_map.json + CONSOLIDATED_RECOVERY_REPORT.md
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load_recovery_maps():
    """Load archive and local recovery maps"""
    archive_map = {}
    local_map = {}
    
    # Load archive recovery map
    archive_path = ROOT / "tools" / "recover" / "recover_map.json"
    if archive_path.exists():
        with open(archive_path, 'r', encoding='utf-8') as f:
            archive_map = json.load(f)
        print(f"Loaded archive map: {len(archive_map)} component types")
    else:
        print("Archive recovery map not found")
    
    # Load local candidates map  
    local_path = ROOT / "tools" / "recover" / "local_candidates.json"
    if local_path.exists():
        with open(local_path, 'r', encoding='utf-8') as f:
            local_map = json.load(f)
        print(f"Loaded local map: {len(local_map)} pattern types")
    else:
        print("Local candidates map not found")
    
    return archive_map, local_map

def scan_src_directory():
    """Scan src/ to see what's already implemented"""
    src_components = {}
    src_path = ROOT / "src"
    
    if not src_path.exists():
        print("src/ directory not found")
        return src_components
    
    # Define what we're looking for in src/
    src_patterns = {
        "gui": ["gui", "interface", "window", "dialog"],
        "auth": ["auth", "login", "register", "credential"],  
        "llm": ["llm", "chat", "openai", "anthropic", "google"],
        "audio": ["audio", "voice", "speech", "tts", "stt"],
        "email": ["email", "mail", "smtp", "imap"],
        "config": ["config", "settings", "preferences"],
        "database": ["db", "database", "store", "persistence"],
        "plugin": ["plugin", "extension", "module"],
        "event": ["event", "message", "bus", "signal"],
        "security": ["security", "encrypt", "secure", "crypto"]
    }
    
    # Scan src/ directory structure
    for category, keywords in src_patterns.items():
        matching_files = []
        
        for py_file in src_path.rglob("*.py"):
            file_str = str(py_file).lower()
            if any(keyword in file_str for keyword in keywords):
                matching_files.append(str(py_file.relative_to(ROOT)))
        
        if matching_files:
            src_components[category] = matching_files
    
    print(f"Found {len(src_components)} component categories in src/")
    return src_components

def create_consolidated_map(archive_map, local_map, src_components):
    """Create consolidated recovery map"""
    
    # All possible component types we're looking for
    all_components = {
        "gui_manager", "login_form", "registration", "settings_panel", "oauth_callback",
        "email_handler", "llm_client", "stt_engine", "tts_engine", "plugin_loader",
        "event_handler", "auth_manager", "db_manager", "config_manager", "app_launcher",
        "ui_builder", "voice_commands", "security_layer", "notification_system",
        "file_manager", "scheduler"
    }
    
    consolidated = {}
    
    for component in all_components:
        consolidated[component] = {
            "archive_candidates": archive_map.get(component, []),
            "local_evidence": [],
            "src_implemented": False,
            "recovery_feasible": False,
            "priority": "low"
        }
        
        # Map local evidence to components
        local_evidence = []
        component_lower = component.lower()
        
        if "gui" in component_lower or "login" in component_lower or "registration" in component_lower or "settings" in component_lower:
            if "gui_state" in local_map:
                local_evidence.extend(local_map["gui_state"])
            if "vpa_config" in local_map:
                local_evidence.extend(local_map["vpa_config"])
        
        if "auth" in component_lower or "login" in component_lower:
            if "auth_tokens" in local_map:
                local_evidence.extend(local_map["auth_tokens"])
            if "login_cache" in local_map:
                local_evidence.extend(local_map["login_cache"])
        
        if "llm" in component_lower:
            if "llm_config" in local_map:
                local_evidence.extend(local_map["llm_config"])
            if "chat_history" in local_map:
                local_evidence.extend(local_map["chat_history"])
        
        if "stt" in component_lower or "tts" in component_lower or "voice" in component_lower:
            if "voice_settings" in local_map:
                local_evidence.extend(local_map["voice_settings"])
        
        if "email" in component_lower:
            if "email_config" in local_map:
                local_evidence.extend(local_map["email_config"])
        
        if "config" in component_lower:
            if "vpa_config" in local_map:
                local_evidence.extend(local_map["vpa_config"])
            if "plugin_config" in local_map:
                local_evidence.extend(local_map["plugin_config"])
        
        consolidated[component]["local_evidence"] = local_evidence
        
        # Check if implemented in src/
        component_keywords = component.lower().split('_')
        for category, files in src_components.items():
            if any(keyword in category or any(keyword in f.lower() for f in files) for keyword in component_keywords):
                consolidated[component]["src_implemented"] = True
                break
        
        # Determine if recovery is feasible
        has_archive = len(consolidated[component]["archive_candidates"]) > 0
        has_local = len(consolidated[component]["local_evidence"]) > 0
        already_implemented = consolidated[component]["src_implemented"]
        
        consolidated[component]["recovery_feasible"] = has_archive or has_local or already_implemented
        
        # Set priority
        if component in ["gui_manager", "login_form", "llm_client", "stt_engine"]:
            consolidated[component]["priority"] = "high"
        elif component in ["auth_manager", "config_manager", "email_handler", "tts_engine"]:
            consolidated[component]["priority"] = "medium"
        else:
            consolidated[component]["priority"] = "low"
    
    return consolidated

def generate_consolidated_report(consolidated_map):
    """Generate consolidated recovery report"""
    report = ["# VPA Consolidated Recovery Report\n"]
    report.append(f"**Generated**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("**Phase**: Evidence Harvest + Runtime Proof")
    report.append("**Scope**: Archive + Local + src/ analysis")
    report.append("")
    
    # Executive Summary
    total_components = len(consolidated_map)
    feasible_count = sum(1 for comp in consolidated_map.values() if comp["recovery_feasible"])
    implemented_count = sum(1 for comp in consolidated_map.values() if comp["src_implemented"])
    archive_count = sum(1 for comp in consolidated_map.values() if comp["archive_candidates"])
    local_count = sum(1 for comp in consolidated_map.values() if comp["local_evidence"])
    
    report.append("## 🎯 **EXECUTIVE SUMMARY**")
    report.append("")
    report.append(f"- **Total Components Assessed**: {total_components}")
    report.append(f"- **Recovery Feasible**: {feasible_count}/{total_components} ({feasible_count/total_components*100:.1f}%)")
    report.append(f"- **Already in src/**: {implemented_count} components")  
    report.append(f"- **Archive Candidates**: {archive_count} component types")
    report.append(f"- **Local Evidence**: {local_count} component types")
    report.append("")
    
    # Priority Matrix
    report.append("## 📊 **RECOVERY PRIORITY MATRIX**")
    report.append("")
    
    priority_groups = {"high": [], "medium": [], "low": []}
    for component, details in consolidated_map.items():
        priority_groups[details["priority"]].append((component, details))
    
    for priority in ["high", "medium", "low"]:
        components = priority_groups[priority]
        if not components:
            continue
            
        report.append(f"### {priority.upper()} PRIORITY ({len(components)} components)")
        report.append("")
        report.append("| Component | Status | Archive | Local | src/ |")
        report.append("|-----------|--------|---------|-------|------|")
        
        for component, details in components:
            status = "✅ Feasible" if details["recovery_feasible"] else "❌ Blocked"
            archive_status = f"{len(details['archive_candidates'])} files" if details['archive_candidates'] else "None"
            local_status = f"{len(details['local_evidence'])} files" if details['local_evidence'] else "None"
            src_status = "✅ Done" if details["src_implemented"] else "❌ Missing"
            
            display_name = component.replace('_', ' ').title()
            report.append(f"| {display_name} | {status} | {archive_status} | {local_status} | {src_status} |")
        
        report.append("")
    
    # Missing in src/ Analysis
    missing_in_src = [comp for comp, details in consolidated_map.items() if not details["src_implemented"]]
    
    report.append("## ❌ **MISSING IN src/**")
    report.append("")
    
    if missing_in_src:
        report.append(f"**{len(missing_in_src)} components** not yet implemented in src/:")
        report.append("")
        
        for component in missing_in_src:
            details = consolidated_map[component]
            recovery_status = "✅ Recoverable" if details["recovery_feasible"] else "⚠️ Limited options"
            
            report.append(f"- **{component.replace('_', ' ').title()}** ({recovery_status})")
            
            if details["archive_candidates"]:
                report.append(f"  - Archive: {len(details['archive_candidates'])} candidates available")
            if details["local_evidence"]:
                report.append(f"  - Local: {len(details['local_evidence'])} evidence files")
            if not details["archive_candidates"] and not details["local_evidence"]:
                report.append(f"  - ⚠️ No recovery sources found - requires new implementation")
    else:
        report.append("🎉 **All components are implemented in src/**")
    
    report.append("")
    
    # Implementation Recommendations
    report.append("## 🚀 **IMPLEMENTATION ROADMAP**")
    report.append("")
    
    # Phase 1: High priority with good recovery options
    phase1_candidates = [comp for comp, details in consolidated_map.items() 
                        if details["priority"] == "high" and details["recovery_feasible"] and not details["src_implemented"]]
    
    if phase1_candidates:
        report.append("### Phase 1: High Priority Recovery")
        for component in phase1_candidates:
            details = consolidated_map[component]
            report.append(f"- **{component.replace('_', ' ').title()}**")
            if details["archive_candidates"]:
                best_candidate = max(details["archive_candidates"], key=lambda x: x.get("size", 0))
                report.append(f"  - Recover from: `{best_candidate.get('file', 'unknown')}`")
            report.append(f"  - Target: `src/vpa/{component.split('_')[0]}/{component}.py`")
        report.append("")
    
    # Phase 2: Medium priority
    phase2_candidates = [comp for comp, details in consolidated_map.items() 
                        if details["priority"] == "medium" and details["recovery_feasible"] and not details["src_implemented"]]
    
    if phase2_candidates:
        report.append("### Phase 2: Medium Priority Recovery")
        for component in phase2_candidates:
            report.append(f"- **{component.replace('_', ' ').title()}** - Implement with feature flags")
        report.append("")
    
    # Phase 3: New implementations needed
    no_recovery_candidates = [comp for comp, details in consolidated_map.items() 
                             if not details["recovery_feasible"] and not details["src_implemented"]]
    
    if no_recovery_candidates:
        report.append("### Phase 3: New Implementation Required")
        for component in no_recovery_candidates:
            report.append(f"- **{component.replace('_', ' ').title()}** - Create minimal implementation")
        report.append("")
    
    report.append("---")
    report.append("*Consolidated analysis completed. Ready for targeted recovery implementation.*")
    
    return "\n".join(report)

def main():
    """Main consolidation function"""
    print("Starting report consolidation...")
    
    # Load recovery maps
    archive_map, local_map = load_recovery_maps()
    
    # Scan src/ directory
    src_components = scan_src_directory()
    
    # Create consolidated map
    consolidated = create_consolidated_map(archive_map, local_map, src_components)
    
    # Write consolidated map
    output_dir = ROOT / "tools" / "recover"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "consolidated_map.json", 'w', encoding='utf-8') as f:
        json.dump(consolidated, f, indent=2)
    
    # Generate and write report
    report = generate_consolidated_report(consolidated)
    with open(ROOT / "CONSOLIDATED_RECOVERY_REPORT.md", 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("Consolidation completed.")
    print("Results: consolidated_map.json, CONSOLIDATED_RECOVERY_REPORT.md")
    
    return consolidated

if __name__ == "__main__":
    main()
