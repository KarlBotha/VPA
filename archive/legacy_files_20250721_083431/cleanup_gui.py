"""
GUI Cleanup Script
Safely terminates any hanging GUI processes and cleans up resources
"""

import os
import sys
import psutil
import signal
from pathlib import Path

def cleanup_gui_processes():
    """Clean up any hanging GUI processes"""
    print("🧹 Cleaning up GUI processes...")
    
    # Find Python processes that might be running GUI
    gui_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                cmdline = proc.info['cmdline']
                if cmdline and any('gui' in str(arg).lower() for arg in cmdline):
                    gui_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Terminate GUI processes
    for proc in gui_processes:
        try:
            print(f"🔄 Terminating process {proc.pid}: {' '.join(proc.cmdline())}")
            proc.terminate()
            proc.wait(timeout=3)
            print(f"✅ Process {proc.pid} terminated")
        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
            try:
                proc.kill()
                print(f"💀 Process {proc.pid} killed (forced)")
            except psutil.NoSuchProcess:
                print(f"⚠️ Process {proc.pid} already gone")
        except Exception as e:
            print(f"❌ Failed to terminate process {proc.pid}: {e}")
    
    return len(gui_processes)

def cleanup_temp_files():
    """Clean up temporary GUI files"""
    print("🗂️ Cleaning up temporary files...")
    
    temp_patterns = [
        "*.tmp",
        "vpa_tts_*.mp3",
        "__pycache__"
    ]
    
    # Clean current directory
    current_dir = Path.cwd()
    cleaned = 0
    
    for pattern in temp_patterns:
        for file in current_dir.glob(pattern):
            try:
                if file.is_file():
                    file.unlink()
                    cleaned += 1
                elif file.is_dir():
                    import shutil
                    shutil.rmtree(file)
                    cleaned += 1
            except Exception as e:
                print(f"⚠️ Could not remove {file}: {e}")
    
    print(f"✅ Cleaned {cleaned} temporary files")
    return cleaned

def reset_gui_state():
    """Reset GUI state variables"""
    print("🔄 Resetting GUI state...")
    
    try:
        # Try to import and reset CustomTkinter
        import customtkinter as ctk
        
        # Reset appearance mode
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        
        print("✅ CustomTkinter state reset")
        return True
        
    except ImportError:
        print("⚠️ CustomTkinter not available")
        return False
    except Exception as e:
        print(f"❌ GUI reset failed: {e}")
        return False

def main():
    """Main cleanup routine"""
    print("🚨 VPA GUI Cleanup Utility")
    print("=" * 40)
    
    # Step 1: Clean up processes
    proc_count = cleanup_gui_processes()
    
    # Step 2: Clean up files
    file_count = cleanup_temp_files()
    
    # Step 3: Reset GUI state
    gui_reset = reset_gui_state()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Cleanup Summary:")
    print(f"  🔄 Processes terminated: {proc_count}")
    print(f"  🗂️ Files cleaned: {file_count}")
    print(f"  🎨 GUI state reset: {'✅' if gui_reset else '❌'}")
    
    if proc_count == 0 and gui_reset:
        print("\n✅ System is clean - GUI errors should be resolved")
    else:
        print("\n⚠️ Manual intervention may be required")
        print("💡 Try restarting VS Code if errors persist")
    
    return True

if __name__ == "__main__":
    main()
