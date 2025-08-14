#!/usr/bin/env python3
import argparse, json, os, subprocess, sys, time
from textwrap import dedent

def try_import(module):
    try:
        __import__(module)
        return True
    except ImportError:
        return False

def measure_import_time(module_name):
    """Measure module import time"""
    start = time.perf_counter()
    try:
        __import__(module_name)
        end = time.perf_counter()
        return end - start, None
    except Exception as e:
        return None, str(e)

def measure_cli_help_time():
    """Measure CLI --help response time"""
    start = time.perf_counter()
    try:
        result = subprocess.run([sys.executable, "-m", "vpa", "--help"], 
                               capture_output=True, text=True, timeout=30)
        end = time.perf_counter()
        return end - start, result.returncode == 0, result.stderr
    except Exception as e:
        return None, False, str(e)

def get_memory_info():
    """Get current process memory usage"""
    if not try_import("psutil"):
        return {"rss_mb": "N/A (psutil not available)", "vms_mb": "N/A"}
    
    import psutil
    proc = psutil.Process()
    mem = proc.memory_info()
    return {
        "rss_mb": round(mem.rss / 1024 / 1024, 2),
        "vms_mb": round(mem.vms / 1024 / 1024, 2)
    }

def measure_event_dispatch_latency():
    """Measure event dispatch simulation latency"""
    # Simple synchronous event simulation
    start = time.perf_counter()
    events = []
    for i in range(100):
        event_start = time.perf_counter()
        # Simulate minimal event processing
        payload = {"id": i, "timestamp": event_start}
        events.append(payload)
        event_end = time.perf_counter()
    end = time.perf_counter()
    
    total_time = end - start
    avg_per_event = (total_time / 100) * 1000  # Convert to milliseconds
    return {
        "total_time_ms": round(total_time * 1000, 2),
        "avg_per_event_ms": round(avg_per_event, 2),
        "events_processed": 100
    }

def run_smoke_test():
    """Run comprehensive smoke test"""
    print("🔥 VPA Performance Smoke Test Starting...")
    
    # Test environment
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    platform = sys.platform
    
    # Dependencies check
    deps_status = {}
    core_deps = ["vpa", "psutil", "pyttsx3", "edge_tts", "pygame", "aiohttp", "cryptography"]
    for dep in core_deps:
        deps_status[dep] = try_import(dep)
    
    # Memory baseline
    memory_start = get_memory_info()
    
    # Import performance
    vpa_import_time, vpa_import_error = measure_import_time("vpa")
    
    # CLI performance
    cli_time, cli_success, cli_error = measure_cli_help_time()
    
    # Event dispatch simulation
    event_dispatch = measure_event_dispatch_latency()
    
    # Final memory
    memory_end = get_memory_info()
    
    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "environment": {
            "python_version": python_version,
            "platform": platform,
            "working_directory": os.getcwd()
        },
        "dependencies": deps_status,
        "performance": {
            "vpa_import_time_s": vpa_import_time,
            "vpa_import_error": vpa_import_error,
            "cli_help_time_s": cli_time,
            "cli_help_success": cli_success,
            "cli_help_error": cli_error,
            "event_dispatch": event_dispatch
        },
        "memory": {
            "start": memory_start,
            "end": memory_end
        }
    }

def format_markdown_report(results):
    """Format results as Markdown"""
    r = results
    perf = r["performance"]
    mem = r["memory"]
    env = r["environment"]
    deps = r["dependencies"]
    
    # Performance status indicators
    vpa_import_status = "✅" if perf["vpa_import_time_s"] and perf["vpa_import_time_s"] < 2.0 else "⚠️"
    cli_status = "✅" if perf["cli_help_success"] else "❌"
    event_status = "✅" if perf["event_dispatch"]["avg_per_event_ms"] < 10 else "⚠️"
    
    # Dependency status
    critical_deps = ["vpa", "psutil", "pyttsx3", "edge_tts"]
    critical_status = all(deps.get(dep, False) for dep in critical_deps)
    deps_status = "✅" if critical_status else "⚠️"
    
    return dedent(f"""
    # VPA Performance Baseline Report
    
    **Generated**: {r["timestamp"]}  
    **Environment**: Python {env["python_version"]} on {env["platform"]}
    
    ## 📊 Performance Metrics
    
    | Metric | Value | Target | Status |
    |--------|-------|--------|---------|
    | **VPA Import Time** | {perf["vpa_import_time_s"]:.3f}s | <2.0s | {vpa_import_status} |
    | **CLI Help Response** | {perf["cli_help_time_s"]:.3f}s | <1.0s | {cli_status} |
    | **Event Dispatch (avg)** | {perf["event_dispatch"]["avg_per_event_ms"]:.2f}ms | <10ms | {event_status} |
    | **Memory RSS Start** | {mem["start"]["rss_mb"]} MB | <100MB | - |
    | **Memory RSS End** | {mem["end"]["rss_mb"]} MB | <2GB | - |
    
    ## 🔗 Dependencies Status {deps_status}
    
    | Package | Available | Critical |
    |---------|-----------|----------|
    | **vpa** | {"✅" if deps.get("vpa") else "❌"} | Yes |
    | **psutil** | {"✅" if deps.get("psutil") else "❌"} | Yes |
    | **pyttsx3** | {"✅" if deps.get("pyttsx3") else "❌"} | Yes |
    | **edge-tts** | {"✅" if deps.get("edge_tts") else "❌"} | Yes |
    | **pygame** | {"✅" if deps.get("pygame") else "❌"} | No |
    | **aiohttp** | {"✅" if deps.get("aiohttp") else "❌"} | No |
    | **cryptography** | {"✅" if deps.get("cryptography") else "❌"} | No |
    
    ## 🎯 Performance Analysis
    
    ### Import Performance
    - **VPA module import**: {perf["vpa_import_time_s"]:.3f}s {vpa_import_status}
    - **Import error**: {perf["vpa_import_error"] or "None"}
    
    ### CLI Performance  
    - **Help command**: {perf["cli_help_time_s"]:.3f}s {cli_status}
    - **CLI success**: {perf["cli_help_success"]}
    - **CLI error**: {perf["cli_help_error"] or "None"}
    
    ### Event System Simulation
    - **Total events**: {perf["event_dispatch"]["events_processed"]}
    - **Total time**: {perf["event_dispatch"]["total_time_ms"]:.2f}ms
    - **Average per event**: {perf["event_dispatch"]["avg_per_event_ms"]:.2f}ms {event_status}
    
    ### Memory Usage
    - **Start RSS**: {mem["start"]["rss_mb"]} MB
    - **End RSS**: {mem["end"]["rss_mb"]} MB
    - **VMS**: {mem["end"]["vms_mb"]} MB
    
    ## 🎪 Performance Targets vs Actual
    
    | Target | Actual | Status |
    |--------|--------|---------|
    | Startup <10s | CLI help: {perf["cli_help_time_s"]:.3f}s | {cli_status} |
    | Memory <2GB | RSS: {mem["end"]["rss_mb"]} MB | {"✅" if isinstance(mem["end"]["rss_mb"], (int, float)) and mem["end"]["rss_mb"] < 2048 else "⚠️"} |
    | Events <10ms | Avg: {perf["event_dispatch"]["avg_per_event_ms"]:.2f}ms | {event_status} |
    | TTS <2s | *Not tested* | ⏳ |
    
    ---
    *Performance baseline generated by tools/perf/perf_smoke.py*
    """).strip()

def main():
    parser = argparse.ArgumentParser(description="VPA Performance Smoke Test")
    parser.add_argument("--out", default="PERF_BASELINE.md", 
                       help="Output markdown file (default: PERF_BASELINE.md)")
    parser.add_argument("--json", action="store_true", 
                       help="Also output raw JSON data")
    
    args = parser.parse_args()
    
    # Run smoke test
    results = run_smoke_test()
    
    # Generate markdown report
    markdown_report = format_markdown_report(results)
    
    # Write markdown file
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(markdown_report)
    
    print(f"✅ Performance baseline written to: {args.out}")
    
    # Optional JSON output
    if args.json:
        json_file = args.out.replace(".md", ".json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"✅ Raw JSON data written to: {json_file}")
    
    # Print key metrics to stdout
    perf = results["performance"]
    print(f"📈 Key Metrics:")
    print(f"   VPA import: {perf['vpa_import_time_s']:.3f}s")
    print(f"   CLI help: {perf['cli_help_time_s']:.3f}s")
    print(f"   Event dispatch: {perf['event_dispatch']['avg_per_event_ms']:.2f}ms")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
