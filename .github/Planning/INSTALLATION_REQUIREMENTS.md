# Installation Requirements Specification

## Overview

This document outlines the installation requirements and deployment strategy for the VPA application, ensuring a smooth and user-friendly installation experience.

## Table of Contents

1. [System Requirements](#1-system-requirements)
2. [Installation Process](#2-installation-process)
3. [Dependency Management](#3-dependency-management)
4. [Packaging Strategy](#4-packaging-strategy)
5. [Update Mechanism](#5-update-mechanism)

## 1. System Requirements

### 1.1 Minimum Requirements

| Component | Minimum Requirement | Recommended |
|-----------|---------------------|------------|
| Operating System | Windows 10 (1809+) | Windows 11 |
| Processor | 2 core CPU, 2.0 GHz | 4+ core CPU, 3.0+ GHz |
| Memory | 8 GB RAM | 16+ GB RAM |
| Storage | 2 GB available | 8+ GB available |
| GPU | Not required | NVIDIA GPU with 4+ GB VRAM |
| Display | 1366×768 resolution | 1920×1080 resolution |
| Audio | Microphone for voice input | Microphone + Speakers |
| Internet | Not required (offline mode) | Broadband connection |

### 1.2 Software Prerequisites

The installer will handle these dependencies automatically:

1. **Microsoft Visual C++ Redistributable 2019+**
2. **Microsoft .NET 6.0 Runtime**
3. **Python 3.10 (embedded distribution)**

### 1.3 Optional Components

| Component | Purpose | Size | Auto-Install |
|-----------|---------|------|-------------|
| Ollama | Local LLM support | ~50 MB | Yes, with user consent |
| LLM Models | Local language models | 2-5 GB each | No, on-demand |
| Whisper Models | Offline speech recognition | ~75-500 MB | No, on-demand |
| Speech Recognition Packs | Additional languages | ~50-100 MB each | No, on-demand |

### 1.4 Hardware Detection

During installation, the setup will perform comprehensive hardware detection to optimize the application for each user's system:

1. **CPU Capabilities**: 
   - Core count and thread count
   - CPU architecture and frequency
   - Instruction set support (AVX/AVX2/AVX512)
   - Cache sizes and performance metrics

2. **GPU Capabilities**:
   - CUDA support for NVIDIA GPUs
   - ROCm support for AMD GPUs
   - DirectML support for other GPUs
   - VRAM size and capabilities
   - Compute capability version

3. **Memory Analysis**:
   - Total RAM size
   - Available RAM
   - RAM speed and configuration
   - Virtual memory configuration

4. **Storage Analysis**:
   - Available disk space
   - Storage type detection (SSD vs HDD)
   - Read/write speed assessment
   - Temp directory location and size

5. **Audio Capabilities**:
   - Microphone availability and quality
   - Speaker configuration
   - Audio device capabilities
   - Default audio devices

6. **Display Capabilities**:
   - Screen resolution and scaling
   - Multi-monitor setup
   - Color depth/support
   - Graphics API support

7. **Network Configuration**:
   - Internet connectivity
   - Connection speed and latency
   - Proxy configuration
   - Firewall restrictions

```python
def detect_system_capabilities():
    """Detect comprehensive system capabilities and requirements"""
    capabilities = {
        # System Information
        "os_name": None,
        "os_version": None,
        "os_build": None,
        "system_locale": None,
        "admin_rights": False,
        
        # CPU Information
        "cpu_model": None,
        "cpu_brand": None,
        "cpu_cores_physical": 0,
        "cpu_cores_logical": 0,
        "cpu_frequency_base": 0,
        "cpu_frequency_max": 0,
        "cpu_cache_l1": 0,
        "cpu_cache_l2": 0,
        "cpu_cache_l3": 0,
        "cpu_instructions": {
            "avx": False,
            "avx2": False,
            "avx512": False,
            "sse4": False,
            "fma": False
        },
        
        # GPU Information
        "gpu_count": 0,
        "gpus": [],
        "cuda_available": False,
        "cuda_version": None,
        "cuda_devices": [],
        "rocm_available": False,
        "directml_available": False,
        "opengl_version": None,
        "directx_version": None,
        
        # Memory Information
        "total_ram_gb": 0,
        "available_ram_gb": 0,
        "ram_speed": None,
        "virtual_memory_gb": 0,
        
        # Storage Information
        "system_drive": None,
        "system_drive_type": None,
        "system_drive_total_gb": 0,
        "system_drive_free_gb": 0,
        "installation_drive": None,
        "installation_drive_type": None,
        "installation_drive_free_gb": 0,
        "temp_directory": None,
        "temp_directory_free_gb": 0,
        
        # Audio Information
        "audio_devices_output": [],
        "audio_devices_input": [],
        "microphone_available": False,
        "speakers_available": False,
        "default_audio_input": None,
        "default_audio_output": None,
        "audio_sample_rates_supported": [],
        
        # Display Information
        "display_count": 0,
        "displays": [],
        "primary_display_resolution": None,
        "primary_display_scaling": 1.0,
        "color_depth": 0,
        
        # Network Information
        "internet_available": False,
        "internet_latency_ms": 0,
        "internet_download_speed_mbps": 0,
        "proxy_enabled": False,
        "hostname": None,
        "mac_address": None
    }
    
    # System Information Detection
    try:
        import platform
        import locale
        import ctypes
        import os
        
        capabilities["os_name"] = platform.system()
        win_ver = platform.win32_ver()
        capabilities["os_version"] = win_ver[0] + " " + win_ver[1]
        capabilities["os_build"] = win_ver[2]
        capabilities["system_locale"] = locale.getdefaultlocale()[0]
        capabilities["hostname"] = platform.node()
        
        # Check for admin rights
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            capabilities["admin_rights"] = is_admin
        except:
            pass
    except Exception as e:
        logging.error(f"Error detecting system information: {e}")
    
    # CPU Detection
    try:
        import psutil
        import cpuinfo
        import subprocess
        
        # Basic CPU info from psutil
        capabilities["cpu_cores_physical"] = psutil.cpu_count(logical=False) or 1
        capabilities["cpu_cores_logical"] = psutil.cpu_count(logical=True) or 1
        
        # CPU frequency
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            capabilities["cpu_frequency_base"] = cpu_freq.current
            capabilities["cpu_frequency_max"] = cpu_freq.max
        
        # Detailed CPU info from cpuinfo
        cpu_info = cpuinfo.get_cpu_info()
        capabilities["cpu_brand"] = cpu_info.get('brand_raw', 'Unknown CPU')
        capabilities["cpu_model"] = cpu_info.get('model', 0)
        
        # Check instruction sets
        flags = cpu_info.get('flags', [])
        capabilities["cpu_instructions"]["avx"] = 'avx' in flags
        capabilities["cpu_instructions"]["avx2"] = 'avx2' in flags
        capabilities["cpu_instructions"]["avx512"] = any(flag.startswith('avx512') for flag in flags)
        capabilities["cpu_instructions"]["sse4"] = 'sse4_1' in flags or 'sse4_2' in flags
        capabilities["cpu_instructions"]["fma"] = 'fma' in flags
        
        # Try to get cache sizes using WMI on Windows
        if capabilities["os_name"] == "Windows":
            try:
                import wmi
                w = wmi.WMI()
                for cpu in w.Win32_Processor():
                    capabilities["cpu_cache_l2"] = int(cpu.L2CacheSize) * 1024 if cpu.L2CacheSize else 0
                    capabilities["cpu_cache_l3"] = int(cpu.L3CacheSize) * 1024 if cpu.L3CacheSize else 0
            except:
                pass
    except Exception as e:
        logging.error(f"Error detecting CPU information: {e}")
    
    # GPU Detection
    try:
        # Try CUDA detection
        try:
            import torch
            capabilities["cuda_available"] = torch.cuda.is_available()
            if capabilities["cuda_available"]:
                capabilities["cuda_version"] = torch.version.cuda
                capabilities["gpu_count"] = torch.cuda.device_count()
                
                for i in range(capabilities["gpu_count"]):
                    device_props = torch.cuda.get_device_properties(i)
                    capabilities["cuda_devices"].append({
                        "name": device_props.name,
                        "vram_gb": device_props.total_memory / (1024 ** 3),
                        "compute_capability": f"{device_props.major}.{device_props.minor}",
                        "cores": device_props.multi_processor_count,
                        "max_threads_per_block": device_props.max_threads_per_block
                    })
        except:
            pass
            
        # Try to get more comprehensive GPU info on Windows
        if capabilities["os_name"] == "Windows":
            try:
                import wmi
                w = wmi.WMI()
                for gpu in w.Win32_VideoController():
                    capabilities["gpus"].append({
                        "name": gpu.Name,
                        "driver_version": gpu.DriverVersion,
                        "video_memory_mb": int(gpu.AdapterRAM) / (1024 * 1024) if gpu.AdapterRAM else 0,
                        "resolution": f"{gpu.CurrentHorizontalResolution}x{gpu.CurrentVerticalResolution}" if gpu.CurrentHorizontalResolution else None,
                        "refresh_rate": gpu.CurrentRefreshRate,
                        "bits_per_pixel": gpu.CurrentBitsPerPixel,
                        "driver_date": gpu.DriverDate
                    })
                capabilities["gpu_count"] = len(capabilities["gpus"])
                
                # Check for DirectX version
                try:
                    import subprocess
                    result = subprocess.check_output("dxdiag /t dxdiag_output.txt", shell=True)
                    time.sleep(2)  # Wait for file to be written
                    
                    if os.path.exists("dxdiag_output.txt"):
                        with open("dxdiag_output.txt", "r") as f:
                            content = f.read()
                            
                            # Try to extract DirectX version
                            import re
                            dx_match = re.search(r"DirectX Version: ([\d\.]+)", content)
                            if dx_match:
                                capabilities["directx_version"] = dx_match.group(1)
                                
                        # Clean up
                        try:
                            os.remove("dxdiag_output.txt")
                        except:
                            pass
                except:
                    pass
            except:
                pass
                
        # Check for ROCm (AMD)
        try:
            import subprocess
            result = subprocess.run(["rocm-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                capabilities["rocm_available"] = True
        except:
            pass
            
        # Check for DirectML
        try:
            import onnxruntime
            providers = onnxruntime.get_available_providers()
            capabilities["directml_available"] = 'DmlExecutionProvider' in providers
        except:
            pass
    except Exception as e:
        logging.error(f"Error detecting GPU information: {e}")
    
    # Memory Detection
    try:
        import psutil
        
        vm = psutil.virtual_memory()
        capabilities["total_ram_gb"] = vm.total / (1024 ** 3)
        capabilities["available_ram_gb"] = vm.available / (1024 ** 3)
        
        # Virtual memory (swap)
        swap = psutil.swap_memory()
        capabilities["virtual_memory_gb"] = swap.total / (1024 ** 3)
        
        # RAM speed detection on Windows
        if capabilities["os_name"] == "Windows":
            try:
                import wmi
                w = wmi.WMI()
                for mem in w.Win32_PhysicalMemory():
                    # Speed is in MHz
                    capabilities["ram_speed"] = int(mem.Speed) if mem.Speed else None
                    break  # Just get the first one
            except:
                pass
    except Exception as e:
        logging.error(f"Error detecting memory information: {e}")
    
    # Storage Detection
    try:
        import psutil
        import os
        import shutil
        
        # System drive
        system_drive = os.environ.get("SystemDrive", "C:")
        capabilities["system_drive"] = system_drive
        
        # Get system drive info
        system_usage = psutil.disk_usage(system_drive)
        capabilities["system_drive_total_gb"] = system_usage.total / (1024 ** 3)
        capabilities["system_drive_free_gb"] = system_usage.free / (1024 ** 3)
        
        # Installation drive (current directory)
        install_path = os.path.abspath(os.getcwd())
        install_drive = os.path.splitdrive(install_path)[0]
        capabilities["installation_drive"] = install_drive
        
        if install_drive != system_drive:
            install_usage = psutil.disk_usage(install_drive)
            capabilities["installation_drive_free_gb"] = install_usage.free / (1024 ** 3)
        else:
            capabilities["installation_drive_free_gb"] = capabilities["system_drive_free_gb"]
            
        # Temp directory
        temp_dir = os.environ.get("TEMP", os.path.join(system_drive, "\\Temp"))
        capabilities["temp_directory"] = temp_dir
        
        temp_drive = os.path.splitdrive(temp_dir)[0]
        if temp_drive != system_drive and temp_drive != install_drive:
            temp_usage = psutil.disk_usage(temp_drive)
            capabilities["temp_directory_free_gb"] = temp_usage.free / (1024 ** 3)
        elif temp_drive == install_drive:
            capabilities["temp_directory_free_gb"] = capabilities["installation_drive_free_gb"]
        else:
            capabilities["temp_directory_free_gb"] = capabilities["system_drive_free_gb"]
            
        # Detect if SSD or HDD
        if capabilities["os_name"] == "Windows":
            try:
                import wmi
                w = wmi.WMI()
                
                # Map drive letters to physical disks
                logical_to_physical = {}
                for partition in w.Win32_LogicalDiskToPartition():
                    logical_disk = partition.Dependent.DeviceID
                    physical_disk_id = partition.Antecedent.DeviceID.split("Disk #")[1].split(",")[0]
                    logical_to_physical[logical_disk] = int(physical_disk_id)
                
                # Get disk types
                for disk in w.Win32_DiskDrive():
                    disk_id = disk.Index
                    
                    # 0 = unknown, 3 = HDD, 4 = SSD
                    media_type = 0
                    try:
                        # Try to get media type from MSFT_PhysicalDisk class (Windows 10+)
                        for physical_disk in w.MSFT_PhysicalDisk():
                            if physical_disk.DeviceID == disk_id:
                                media_type = physical_disk.MediaType
                                break
                    except:
                        # Fallback: Check if model name contains SSD
                        if "SSD" in disk.Model.upper():
                            media_type = 4
                        else:
                            media_type = 3
                    
                    # Set disk type for system and installation drives
                    if system_drive[0] + ":" in logical_to_physical and logical_to_physical[system_drive[0] + ":"] == disk_id:
                        capabilities["system_drive_type"] = "SSD" if media_type == 4 else "HDD"
                        
                    if install_drive[0] + ":" in logical_to_physical and logical_to_physical[install_drive[0] + ":"] == disk_id:
                        capabilities["installation_drive_type"] = "SSD" if media_type == 4 else "HDD"
            except Exception as e:
                logging.error(f"Error detecting drive types: {e}")
    except Exception as e:
        logging.error(f"Error detecting storage information: {e}")
    
    # Audio Device Detection
    try:
        import pyaudio
        
        p = pyaudio.PyAudio()
        input_devices = []
        output_devices = []
        sample_rates = set()
        
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            
            # Input devices
            if info['maxInputChannels'] > 0:
                input_devices.append({
                    "name": info['name'],
                    "channels": info['maxInputChannels'],
                    "default": info['index'] == p.get_default_input_device_info()['index'] if p.get_default_input_device_info() else False,
                    "sample_rate": info['defaultSampleRate']
                })
                sample_rates.add(info['defaultSampleRate'])
                
                # Set default audio input
                if info['index'] == p.get_default_input_device_info()['index'] if p.get_default_input_device_info() else False:
                    capabilities["default_audio_input"] = info['name']
            
            # Output devices
            if info['maxOutputChannels'] > 0:
                output_devices.append({
                    "name": info['name'],
                    "channels": info['maxOutputChannels'],
                    "default": info['index'] == p.get_default_output_device_info()['index'] if p.get_default_output_device_info() else False,
                    "sample_rate": info['defaultSampleRate']
                })
                sample_rates.add(info['defaultSampleRate'])
                
                # Set default audio output
                if info['index'] == p.get_default_output_device_info()['index'] if p.get_default_output_device_info() else False:
                    capabilities["default_audio_output"] = info['name']
        
        p.terminate()
        
        capabilities["audio_devices_input"] = input_devices
        capabilities["audio_devices_output"] = output_devices
        capabilities["microphone_available"] = len(input_devices) > 0
        capabilities["speakers_available"] = len(output_devices) > 0
        capabilities["audio_sample_rates_supported"] = list(sample_rates)
    except Exception as e:
        logging.error(f"Error detecting audio devices: {e}")
    
    # Display Detection
    try:
        if capabilities["os_name"] == "Windows":
            import ctypes
            
            user32 = ctypes.windll.user32
            
            # Get system DPI
            LOGPIXELSX = 88
            dc = user32.GetDC(None)
            dpi = ctypes.windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
            user32.ReleaseDC(None, dc)
            scaling = dpi / 96.0
            
            capabilities["primary_display_scaling"] = scaling
            
            # Get monitor count
            monitors = []
            
            try:
                import wmi
                w = wmi.WMI()
                for monitor in w.Win32_DesktopMonitor():
                    if monitor.ScreenWidth and monitor.ScreenHeight:
                        monitors.append({
                            "name": monitor.Name,
                            "resolution": f"{monitor.ScreenWidth}x{monitor.ScreenHeight}",
                            "width": monitor.ScreenWidth,
                            "height": monitor.ScreenHeight
                        })
            except:
                # Fallback method
                width = user32.GetSystemMetrics(0)
                height = user32.GetSystemMetrics(1)
                
                monitors.append({
                    "name": "Primary Display",
                    "resolution": f"{width}x{height}",
                    "width": width,
                    "height": height
                })
                
            capabilities["display_count"] = len(monitors)
            capabilities["displays"] = monitors
            
            if monitors:
                capabilities["primary_display_resolution"] = monitors[0]["resolution"]
                
            # Get color depth
            capabilities["color_depth"] = ctypes.windll.gdi32.GetDeviceCaps(
                user32.GetDC(user32.GetDesktopWindow()), 12)  # BITSPIXEL
    except Exception as e:
        logging.error(f"Error detecting display information: {e}")
    
    # Network Detection
    try:
        import socket
        import urllib.request
        import speedtest
        
        # Check internet
        try:
            urllib.request.urlopen("http://www.google.com", timeout=1)
            capabilities["internet_available"] = True
            
            # Get hostname and MAC address
            capabilities["hostname"] = socket.gethostname()
            
            # Measure latency to Google DNS
            start_time = time.time()
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            latency = (time.time() - start_time) * 1000
            capabilities["internet_latency_ms"] = round(latency, 1)
            
            # Try to measure internet speed (optional, can be skipped if too slow)
            speed_test_enabled = False  # Set to True to enable speed testing
            if speed_test_enabled:
                try:
                    st = speedtest.Speedtest()
                    st.get_best_server()
                    download_speed = st.download() / 1_000_000  # Convert to Mbps
                    capabilities["internet_download_speed_mbps"] = round(download_speed, 1)
                except:
                    pass
        except:
            capabilities["internet_available"] = False
            
        # Check for proxy
        proxy_settings = urllib.request.getproxies()
        capabilities["proxy_enabled"] = bool(proxy_settings)
    except Exception as e:
        logging.error(f"Error detecting network information: {e}")
    
    return capabilities
```

## 2. Installation Process

### 2.1 Installation Wizard

The VPA installation will use a simple wizard interface:

1. **Welcome Screen**: Introduction and license agreement
2. **System Check**: Verify minimum requirements
3. **Installation Location**: Select install directory
4. **Component Selection**: Choose optional components
5. **Start Menu/Desktop**: Create shortcuts
6. **Installation Progress**: Visual progress with details
7. **Completion**: Launch application option

### 2.2 Installation Types

VPA will offer three installation types:

1. **Standard Installation** (~100 MB initial download):
   - Core VPA application
   - Required runtimes
   - Basic configuration
   - On-demand model downloading

2. **Offline-Ready Installation** (~3-5 GB):
   - Standard installation components
   - Ollama pre-installed
   - Small local LLM (Phi-3 Mini)
   - Basic speech recognition model
   - Full documentation

3. **Advanced Installation** (Custom selection):
   - Choose specific components
   - Select preferred LLM models
   - Configure advanced options
   - Set resource usage limits

### 2.3 Executable Package

The primary installer will be a self-extracting executable:

```python
# Specification for PyInstaller configuration

pyinstaller_spec = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Core application files
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('config', 'config'),
        ('docs', 'docs'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtMultimedia',
        'PyQt6.QtNetwork',
        'aiohttp',
        'asyncio',
        'sqlite3',
        'cryptography',
        'platformdirs',
        'pyaudio',
        'numpy',
        'win32security',
        'win32com',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Exclude unnecessary files to reduce size
excluded_binaries = [
    'opengl32sw.dll',
    'libGLESv2.dll',
    'd3dcompiler_47.dll',
    'ucrtbase.dll',
    'MSVCP140_1.dll',
]

a.binaries = TOC([x for x in a.binaries if x[0] not in excluded_binaries])

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VPA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app_icon.ico',
    version='version_info.txt',
    uac_admin=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VPA',
)
"""

# Version info file
version_info = """
# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x40004,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'VPA Project'),
        StringStruct(u'FileDescription', u'Virtual Personal Assistant'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'VPA'),
        StringStruct(u'LegalCopyright', u'© 2025 VPA Project. All rights reserved.'),
        StringStruct(u'OriginalFilename', u'VPA.exe'),
        StringStruct(u'ProductName', u'Virtual Personal Assistant'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
```

### 2.4 Silent Installation

For automated deployment, VPA will support silent installation:

```powershell
# Example silent installation commands

# Standard silent installation
VPA-Installer.exe /S /D=C:\Program Files\VPA

# Advanced silent installation with parameters
VPA-Installer.exe /S /COMPONENTS=core,ollama,whisper /LLM=phi3-mini /OFFLINE=1 /D=C:\Program Files\VPA

# Uninstall silently
C:\Program Files\VPA\uninstall.exe /S
```

## 3. Dependency Management

### 3.1 Core Dependencies

VPA will include these core dependencies within the installer:

| Dependency | Purpose | Included Version |
|------------|---------|------------------|
| PyQt6 | GUI Framework | 6.5.0+ |
| aiohttp | Async HTTP | 3.8.5+ |
| cryptography | Security | 41.0.0+ |
| numpy | Numerical processing | 1.24.0+ |
| pyaudio | Audio processing | 0.2.13+ |
| pywin32 | Windows integration | 306+ |
| sqlite3 | Database | 3.41.2+ (bundled) |
| platformdirs | Config directories | 3.10.0+ |

### 3.2 Runtime Dependencies

For runtime dependencies not included in the installer:

```python
class DependencyManager:
    """Manages external dependencies"""
    
    def __init__(self, settings_manager, event_bus):
        self.settings_manager = settings_manager
        self.event_bus = event_bus
        self.dependencies = {
            "ollama": {
                "name": "Ollama",
                "version": "0.1.20+",
                "download_url": "https://ollama.com/download/windows",
                "installed_path": None,
                "is_installed": False,
                "is_running": False,
                "check_command": "ollama.exe version",
                "start_command": "ollama.exe serve",
                "install_size_mb": 50,
                "required_for": ["local_llm"]
            },
            "whisper": {
                "name": "Whisper Models",
                "version": "latest",
                "download_url": None,  # Downloaded via Python
                "installed_path": None,
                "is_installed": False,
                "is_running": False,
                "check_command": None,
                "start_command": None,
                "install_size_mb": 150,
                "required_for": ["speech_recognition_fallback"]
            }
        }
        
    async def check_dependency(self, dependency_id: str) -> bool:
        """Check if dependency is installed"""
        if dependency_id not in self.dependencies:
            return False
            
        dependency = self.dependencies[dependency_id]
        
        if dependency_id == "ollama":
            return await self._check_ollama()
        elif dependency_id == "whisper":
            return await self._check_whisper()
            
        return False
        
    async def _check_ollama(self) -> bool:
        """Check if Ollama is installed and running"""
        try:
            # Check common installation paths
            paths = [
                os.path.expanduser("~/AppData/Local/Programs/Ollama/ollama.exe"),
                "C:/Program Files/Ollama/ollama.exe",
                os.path.expanduser("~/.ollama/ollama.exe")
            ]
            
            ollama_path = next((path for path in paths if os.path.exists(path)), None)
            if ollama_path:
                self.dependencies["ollama"]["installed_path"] = ollama_path
                self.dependencies["ollama"]["is_installed"] = True
            
            # Check if Ollama server is running
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:11434/api/version", timeout=2) as resp:
                        if resp.status == 200:
                            self.dependencies["ollama"]["is_running"] = True
                            return True
            except:
                self.dependencies["ollama"]["is_running"] = False
                
            return self.dependencies["ollama"]["is_installed"]
        except:
            return False
            
    async def _check_whisper(self) -> bool:
        """Check if Whisper models are installed"""
        try:
            import os
            
            # Check for Whisper models in app data
            app_data = os.path.join(os.getenv('APPDATA'), "VPA", "whisper_models")
            
            if os.path.exists(app_data):
                # Check for at least one model file
                models = [f for f in os.listdir(app_data) if f.endswith(".pt")]
                if models:
                    self.dependencies["whisper"]["installed_path"] = app_data
                    self.dependencies["whisper"]["is_installed"] = True
                    return True
                    
            return False
        except:
            return False
            
    async def install_dependency(self, dependency_id: str) -> bool:
        """Install a dependency"""
        if dependency_id not in self.dependencies:
            return False
            
        # Get dependency info
        dependency = self.dependencies[dependency_id]
        
        # Show installation dialog
        await self.event_bus.emit_async("dependency.installation_started", {
            "dependency_id": dependency_id,
            "name": dependency["name"],
            "size_mb": dependency["install_size_mb"]
        })
        
        # Install based on dependency type
        if dependency_id == "ollama":
            return await self._install_ollama()
        elif dependency_id == "whisper":
            return await self._install_whisper()
            
        return False
        
    async def _install_ollama(self) -> bool:
        """Install Ollama"""
        try:
            import tempfile
            import os
            import aiohttp
            import asyncio
            import subprocess
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Download Ollama installer
                installer_path = os.path.join(temp_dir, "ollama-installer.exe")
                
                # Download with progress
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://ollama.com/download/windows", timeout=60) as resp:
                        if resp.status != 200:
                            return False
                            
                        total_size = int(resp.headers.get("content-length", 0))
                        downloaded = 0
                        
                        with open(installer_path, "wb") as f:
                            while True:
                                chunk = await resp.content.read(8192)
                                if not chunk:
                                    break
                                    
                                f.write(chunk)
                                downloaded += len(chunk)
                                
                                # Report progress
                                if total_size > 0:
                                    progress = downloaded / total_size * 100
                                    await self.event_bus.emit_async("dependency.download_progress", {
                                        "dependency_id": "ollama",
                                        "progress": progress
                                    })
                
                # Run installer silently
                await self.event_bus.emit_async("dependency.installation_progress", {
                    "dependency_id": "ollama",
                    "progress": 50,
                    "message": "Running Ollama installer..."
                })
                
                subprocess.run([installer_path, "/S"], check=True)
                
                # Wait for installation to complete
                await asyncio.sleep(5)
                
                # Check if installation succeeded
                if await self._check_ollama():
                    await self.event_bus.emit_async("dependency.installation_complete", {
                        "dependency_id": "ollama",
                        "success": True
                    })
                    return True
                else:
                    await self.event_bus.emit_async("dependency.installation_complete", {
                        "dependency_id": "ollama",
                        "success": False,
                        "error": "Installation failed. Please install Ollama manually."
                    })
                    return False
                    
        except Exception as e:
            await self.event_bus.emit_async("dependency.installation_complete", {
                "dependency_id": "ollama",
                "success": False,
                "error": str(e)
            })
            return False
            
    async def _install_whisper(self) -> bool:
        """Install Whisper models"""
        try:
            import os
            import torch
            import whisper
            
            # Create app data directory
            app_data = os.path.join(os.getenv('APPDATA'), "VPA", "whisper_models")
            os.makedirs(app_data, exist_ok=True)
            
            # Determine appropriate model size
            system_memory = psutil.virtual_memory().total / (1024 ** 3)  # GB
            
            if system_memory < 4:
                model_name = "tiny"  # ~75MB
            elif system_memory < 8:
                model_name = "base"  # ~150MB
            else:
                model_name = "small"  # ~500MB
                
            # Download model with progress
            await self.event_bus.emit_async("dependency.installation_progress", {
                "dependency_id": "whisper",
                "progress": 10,
                "message": f"Downloading {model_name} model..."
            })
            
            # Use whisper's download function
            whisper.load_model(model_name, download_root=app_data)
            
            # Check if installation succeeded
            if await self._check_whisper():
                await self.event_bus.emit_async("dependency.installation_complete", {
                    "dependency_id": "whisper",
                    "success": True
                })
                return True
            else:
                await self.event_bus.emit_async("dependency.installation_complete", {
                    "dependency_id": "whisper",
                    "success": False,
                    "error": "Installation failed. Please try again."
                })
                return False
                
        except Exception as e:
            await self.event_bus.emit_async("dependency.installation_complete", {
                "dependency_id": "whisper",
                "success": False,
                "error": str(e)
            })
            return False
```

### 3.3 First-Run Wizard

On first run, VPA will check dependencies and guide setup:

```python
class FirstRunWizard(QWizard):
    """First-run setup wizard"""
    
    def __init__(self, parent=None, dependency_manager=None, settings_manager=None):
        super().__init__(parent)
        self.dependency_manager = dependency_manager
        self.settings_manager = settings_manager
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup wizard UI"""
        self.setWindowTitle("VPA Setup Wizard")
        self.setMinimumSize(800, 600)
        
        # Welcome page
        welcome_page = QWizardPage()
        welcome_page.setTitle("Welcome to VPA")
        welcome_layout = QVBoxLayout(welcome_page)
        
        welcome_label = QLabel(
            "Welcome to Virtual Personal Assistant!\n\n"
            "This wizard will help you set up VPA for optimal performance "
            "on your system. We'll check your hardware, configure settings, "
            "and install necessary components.\n\n"
            "Click Next to continue."
        )
        welcome_label.setWordWrap(True)
        welcome_layout.addWidget(welcome_label)
        
        self.addPage(welcome_page)
        
        # System check page
        system_page = QWizardPage()
        system_page.setTitle("System Check")
        system_layout = QVBoxLayout(system_page)
        
        self.system_check_label = QLabel("Checking your system...")
        self.system_check_label.setWordWrap(True)
        system_layout.addWidget(self.system_check_label)
        
        self.system_details = QTextEdit()
        self.system_details.setReadOnly(True)
        system_layout.addWidget(self.system_details)
        
        self.addPage(system_page)
        
        # LLM selection page
        llm_page = QWizardPage()
        llm_page.setTitle("Language Model Selection")
        llm_layout = QVBoxLayout(llm_page)
        
        llm_label = QLabel(
            "Choose your preferred language model option.\n\n"
            "Local models run on your computer and work offline, but require more system resources.\n"
            "Cloud models require internet but use less local resources."
        )
        llm_label.setWordWrap(True)
        llm_layout.addWidget(llm_label)
        
        self.llm_local = QRadioButton("Local Model (Runs on your PC, works offline)")
        self.llm_cloud = QRadioButton("Cloud Model (Requires internet connection)")
        self.llm_hybrid = QRadioButton("Hybrid (Use local when offline, cloud when online)")
        
        llm_layout.addWidget(self.llm_local)
        llm_layout.addWidget(self.llm_cloud)
        llm_layout.addWidget(self.llm_hybrid)
        
        # Register field for selection
        self.llm_local.setChecked(True)
        
        llm_layout.addSpacing(20)
        
        self.llm_install_checkbox = QCheckBox("Download and install recommended local model now")
        llm_layout.addWidget(self.llm_install_checkbox)
        
        self.addPage(llm_page)
        
        # Voice input page
        voice_page = QWizardPage()
        voice_page.setTitle("Voice Input Configuration")
        voice_layout = QVBoxLayout(voice_page)
        
        voice_label = QLabel(
            "Configure voice input options.\n\n"
            "VPA can use your microphone to accept voice commands and transcribe your speech."
        )
        voice_label.setWordWrap(True)
        voice_layout.addWidget(voice_label)
        
        self.voice_enable = QCheckBox("Enable voice input")
        self.voice_download = QCheckBox("Download offline speech recognition model")
        
        voice_layout.addWidget(self.voice_enable)
        voice_layout.addWidget(self.voice_download)
        
        self.addPage(voice_page)
        
        # Finish page
        finish_page = QWizardPage()
        finish_page.setTitle("Setup Complete")
        finish_layout = QVBoxLayout(finish_page)
        
        finish_label = QLabel(
            "VPA is now configured and ready to use!\n\n"
            "Click Finish to start using VPA."
        )
        finish_label.setWordWrap(True)
        finish_layout.addWidget(finish_label)
        
        self.launch_checkbox = QCheckBox("Launch VPA when finished")
        self.launch_checkbox.setChecked(True)
        finish_layout.addWidget(self.launch_checkbox)
        
        self.addPage(finish_page)
        
        # Connect signals
        self.currentIdChanged.connect(self._on_page_changed)
        
    def _on_page_changed(self, page_id):
        """Handle page changes"""
        if page_id == 1:  # System check page
            # Run system check asynchronously
            QTimer.singleShot(0, self._run_system_check)
```

## 4. Packaging Strategy

### 4.1 Single-File Executable

The primary deployment will be a single-file executable:

1. **Main Installer**: Self-contained installer executable (~50-100MB)
2. **Embedded Python**: Include Python 3.10 runtime
3. **Required DLLs**: Bundle all necessary Windows DLLs

### 4.2 NSIS Installer Script

```nsis
; VPA Installer Script

!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "WinVer.nsh"
!include "x64.nsh"

; Application details
Name "Virtual Personal Assistant"
OutFile "VPA-Installer.exe"
InstallDir "$PROGRAMFILES\VPA"
InstallDirRegKey HKLM "Software\VPA" "Install_Dir"
RequestExecutionLevel admin

; Interface settings
!define MUI_ABORTWARNING
!define MUI_ICON "assets\icons\app_icon.ico"
!define MUI_UNICON "assets\icons\uninstall.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "assets\images\installer-welcome.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "assets\images\installer-header.bmp"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Language
!insertmacro MUI_LANGUAGE "English"

; Version information
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "Virtual Personal Assistant"
VIAddVersionKey "FileDescription" "VPA Installer"
VIAddVersionKey "LegalCopyright" "© 2025 VPA Project"
VIAddVersionKey "FileVersion" "1.0.0.0"
VIAddVersionKey "ProductVersion" "1.0.0.0"

; Check Windows version
Function .onInit
    ${IfNot} ${AtLeastWin10}
        MessageBox MB_OK|MB_ICONSTOP "Windows 10 or later is required to install VPA."
        Abort
    ${EndIf}
    
    ; Check 64-bit
    ${IfNot} ${RunningX64}
        MessageBox MB_OK|MB_ICONSTOP "VPA requires a 64-bit Windows installation."
        Abort
    ${EndIf}
    
    ; Check for .NET Framework
    ReadRegDword $0 HKLM "SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full" "Release"
    ${If} $0 < 528040 ; .NET 6.0
        MessageBox MB_YESNO|MB_ICONQUESTION "VPA requires .NET 6.0 or later, which is not installed. Would you like to download it now?" IDYES download_dotnet IDNO continue_without_dotnet
        download_dotnet:
            ExecShell "open" "https://dotnet.microsoft.com/en-us/download/dotnet/6.0"
            Abort
        continue_without_dotnet:
            ; Continue installation
    ${EndIf}
    
    ; Check for Visual C++ Redistributable
    ReadRegStr $0 HKLM "SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" "Version"
    ${If} $0 == ""
        MessageBox MB_YESNO|MB_ICONQUESTION "VPA requires the Visual C++ 2019 Redistributable, which is not installed. Would you like to download it now?" IDYES download_vcredist IDNO continue_without_vcredist
        download_vcredist:
            ExecShell "open" "https://aka.ms/vs/16/release/vc_redist.x64.exe"
            Abort
        continue_without_vcredist:
            ; Continue installation
    ${EndIf}
FunctionEnd

; Installation components
Section "VPA Core (required)" SecCore
    SectionIn RO
    
    ; Set output directory
    SetOutPath "$INSTDIR"
    
    ; Extract main application files
    File /r "dist\VPA\*.*"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\VPA"
    CreateShortcut "$SMPROGRAMS\VPA\VPA.lnk" "$INSTDIR\VPA.exe"
    CreateShortcut "$DESKTOP\VPA.lnk" "$INSTDIR\VPA.exe"
    
    ; Write registry keys
    WriteRegStr HKLM "Software\VPA" "Install_Dir" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VPA" "DisplayName" "Virtual Personal Assistant"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VPA" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VPA" "DisplayIcon" "$INSTDIR\VPA.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VPA" "DisplayVersion" "1.0.0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VPA" "Publisher" "VPA Project"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VPA" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VPA" "NoRepair" 1
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Ollama Integration" SecOllama
    ; Download and install Ollama
    DetailPrint "Downloading Ollama..."
    inetc::get "https://ollama.com/download/windows" "$TEMP\ollama-installer.exe" /END
    Pop $0
    ${If} $0 == "OK"
        DetailPrint "Installing Ollama..."
        ExecWait '"$TEMP\ollama-installer.exe" /S'
        DetailPrint "Ollama installation complete"
    ${Else}
        DetailPrint "Failed to download Ollama: $0"
        MessageBox MB_OK|MB_ICONINFORMATION "Ollama download failed. You can install it later from the VPA settings menu."
    ${EndIf}
SectionEnd

Section "Desktop Shortcut" SecDesktop
    CreateShortcut "$DESKTOP\VPA.lnk" "$INSTDIR\VPA.exe"
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} "Core VPA application files (required)."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecOllama} "Install Ollama for local language model support."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "Create a shortcut on your desktop."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller section
Section "Uninstall"
    ; Remove application files
    RMDir /r "$INSTDIR\*.*"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\VPA\*.*"
    RMDir "$SMPROGRAMS\VPA"
    Delete "$DESKTOP\VPA.lnk"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VPA"
    DeleteRegKey HKLM "Software\VPA"
    
    ; Remove installation directory
    RMDir /r "$INSTDIR"
SectionEnd
```

## 5. Update Mechanism

### 5.1 Automatic Updates

VPA will include an automatic update mechanism:

```python
class UpdateManager:
    """Manages application updates"""
    
    def __init__(self, settings_manager, event_bus):
        self.settings_manager = settings_manager
        self.event_bus = event_bus
        self.update_url = "https://api.vpa-project.com/updates/check"
        self.current_version = "1.0.0"
        
    async def check_for_updates(self, silent=False) -> Dict[str, Any]:
        """Check for available updates"""
        try:
            # Get current version
            current_version = self.current_version
            
            # Check update server
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.update_url, 
                    params={"version": current_version},
                    timeout=10
                ) as resp:
                    if resp.status != 200:
                        if not silent:
                            await self.event_bus.emit_async("update.check_failed", {
                                "error": f"Server returned status {resp.status}"
                            })
                        return {"available": False, "error": f"Server returned status {resp.status}"}
                        
                    data = await resp.json()
                    
                    if not data.get("available", False):
                        if not silent:
                            await self.event_bus.emit_async("update.not_available", {
                                "current_version": current_version
                            })
                        return {"available": False}
                        
                    # Update available
                    update_info = {
                        "available": True,
                        "version": data.get("version"),
                        "release_notes": data.get("release_notes"),
                        "download_url": data.get("download_url"),
                        "size_mb": data.get("size_mb", 0),
                        "is_critical": data.get("is_critical", False)
                    }
                    
                    if not silent:
                        await self.event_bus.emit_async("update.available", update_info)
                        
                    return update_info
                    
        except Exception as e:
            if not silent:
                await self.event_bus.emit_async("update.check_failed", {
                    "error": str(e)
                })
            return {"available": False, "error": str(e)}
            
    async def download_update(self, update_info: Dict[str, Any]) -> bool:
        """Download an available update"""
        try:
            # Create temporary directory
            import tempfile
            import os
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Download update file
                download_url = update_info["download_url"]
                installer_path = os.path.join(temp_dir, "vpa-update.exe")
                
                # Emit download started event
                await self.event_bus.emit_async("update.download_started", {
                    "version": update_info["version"],
                    "size_mb": update_info["size_mb"]
                })
                
                # Download with progress reporting
                async with aiohttp.ClientSession() as session:
                    async with session.get(download_url, timeout=600) as resp:
                        if resp.status != 200:
                            await self.event_bus.emit_async("update.download_failed", {
                                "error": f"Server returned status {resp.status}"
                            })
                            return False
                            
                        total_size = int(resp.headers.get("content-length", 0))
                        downloaded = 0
                        
                        with open(installer_path, "wb") as f:
                            while True:
                                chunk = await resp.content.read(8192)
                                if not chunk:
                                    break
                                    
                                f.write(chunk)
                                downloaded += len(chunk)
                                
                                # Report progress
                                if total_size > 0:
                                    progress = downloaded / total_size * 100
                                    await self.event_bus.emit_async("update.download_progress", {
                                        "progress": progress
                                    })
                
                # Download complete
                await self.event_bus.emit_async("update.download_complete", {
                    "installer_path": installer_path
                })
                
                # Run installer
                return await self._run_update_installer(installer_path)
                
        except Exception as e:
            await self.event_bus.emit_async("update.download_failed", {
                "error": str(e)
            })
            return False
            
    async def _run_update_installer(self, installer_path: str) -> bool:
        """Run the update installer"""
        try:
            import subprocess
            import os
            import sys
            
            # Create updater script
            app_dir = os.path.dirname(sys.executable)
            updater_script = os.path.join(app_dir, "update_helper.bat")
            
            # Write batch script to handle update
            with open(updater_script, "w") as f:
                f.write('@echo off\n')
                f.write('echo Updating VPA...\n')
                f.write(f'ping -n 3 127.0.0.1 > nul\n')  # Wait for app to close
                f.write(f'start "" "{installer_path}" /S\n')
                
            # Execute updater script and exit application
            subprocess.Popen(
                ["cmd.exe", "/c", updater_script],
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Signal application to shut down for update
            await self.event_bus.emit_async("application.exit_for_update")
            
            return True
            
        except Exception as e:
            await self.event_bus.emit_async("update.install_failed", {
                "error": str(e)
            })
            return False
```

### 5.2 Update Settings

Users can control update behavior:

```python
default_update_settings = {
    "update.check_automatically": True,
    "update.check_frequency_days": 1,
    "update.download_automatically": False,
    "update.install_automatically": False,
    "update.last_check": None,
    "update.notify_critical_only": False
}
```

## Conclusion

This Installation Requirements Specification provides a comprehensive plan for deploying the VPA application to end users. By creating a streamlined installation process, handling dependencies automatically, and implementing a robust update mechanism, VPA ensures a positive user experience from the first interaction.

The implementation includes system requirements detection, multiple installation options to suit different user needs, and transparent dependency management. This approach allows VPA to be easily deployed and maintained on a wide range of Windows systems.

---

*Document created on August 28, 2025*  
*Version: 1.0*
