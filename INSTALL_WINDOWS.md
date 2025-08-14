# VPA Windows Installation Guide

**VPA (Virtual Personal Assistant) - Windows x64 Distribution**  
**Version**: 0.1.0-Phase4  
**Build Date**: August 14, 2025  

---

## 🚀 **QUICK START** (2 Minutes)

### **Method 1: Download & Run** (Recommended)
```powershell
# 1. Download vpa.exe from GitHub Releases
# 2. Open PowerShell in download folder
# 3. Run the executable
.\vpa.exe --help
.\vpa.exe --gui     # Launch GUI mode (default)
.\vpa.exe --cli     # Launch CLI mode
```

### **Method 2: Build from Source** (Developers)
```powershell
git clone https://github.com/KarlBotha/VPA.git
cd VPA
python -m pip install -r requirements.txt
python -m PyInstaller vpa-win.spec
.\dist\vpa\vpa.exe --help
```

---

## 📦 **DISTRIBUTION DETAILS**

### **What You Get**
- **Single executable**: `vpa.exe` (~196MB)
- **No installation required**: Run directly from any folder
- **Self-contained**: All dependencies bundled
- **Zero configuration**: Works out-of-the-box

### **System Requirements**
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10 x64 | Windows 11 x64 |
| **RAM** | 128MB available | 512MB available |
| **Disk** | 200MB free space | 1GB free space |
| **Network** | Optional | Broadband (cloud features) |

### **Performance Expectations**
- **Cold start**: <300ms (excellent for packaged Python)
- **Help response**: ~275ms
- **Memory footprint**: 5.9MB baseline, grows with features
- **CPU usage**: <1% idle, scales with workload

---

## 🔧 **CONFIGURATION OPTIONS**

### **Basic Usage**
```powershell
# Default GUI mode
vpa.exe

# CLI mode with debug logging
vpa.exe --cli --log-level DEBUG

# Custom configuration
vpa.exe --config myconfig.yaml

# Version information
vpa.exe --version
```

### **Environment Variables** (Optional)
```powershell
# Enable enterprise features (if available)
$env:VPA_ENABLE_ENTERPRISE="1"
vpa.exe

# Enable advanced LLM features (if available)
$env:VPA_ENABLE_ADVANCED_LLM="1"
vpa.exe

# Custom log level
$env:VPA_LOG_LEVEL="INFO"
vpa.exe

# Custom config path
$env:VPA_CONFIG_PATH="C:\MyVPAConfig\config.yaml"
vpa.exe
```

### **Feature Gating**
VPA uses **environment-based feature flags** to control optional functionality:

| Flag | Purpose | Default |
|------|---------|---------|
| `VPA_ENABLE_ENTERPRISE` | Enterprise expansion domains | OFF |
| `VPA_ENABLE_ADVANCED_LLM` | Advanced LLM integrations | OFF |
| `VPA_ENABLE_GUI` | GUI components | ON |
| `VPA_ENABLE_VOICE` | Voice/TTS system | ON |

---

## 🎯 **COMMON USAGE SCENARIOS**

### **Scenario 1: Quick Test Run**
```powershell
# Download vpa.exe to Downloads folder
cd Downloads
.\vpa.exe --help
.\vpa.exe --version
```

### **Scenario 2: Development/Testing**
```powershell
# Enable all features for testing
$env:VPA_ENABLE_ENTERPRISE="1"
$env:VPA_ENABLE_ADVANCED_LLM="1"
$env:VPA_LOG_LEVEL="DEBUG"
.\vpa.exe --cli
```

### **Scenario 3: Production Deployment**
```powershell
# Copy exe to Program Files or dedicated folder
Copy-Item "vpa.exe" "C:\VPA\vpa.exe"
cd "C:\VPA"
.\vpa.exe --gui

# Optional: Create desktop shortcut
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$Home\Desktop\VPA.lnk")
$Shortcut.TargetPath = "C:\VPA\vpa.exe"
$Shortcut.Save()
```

### **Scenario 4: Custom Configuration**
```powershell
# Create configuration file
@"
vpa:
  log_level: INFO
  gui_enabled: true
  voice_enabled: true
  plugins:
    - audio
    - gui
"@ | Out-File -FilePath "vpa-config.yaml" -Encoding utf8

# Run with custom config
.\vpa.exe --config vpa-config.yaml
```

---

## 🔊 **AUDIO SETUP**

### **Audio System Requirements**
VPA includes **dual TTS engines** for maximum compatibility:

1. **Windows SAPI** (pyttsx3): Built-in Windows voices
2. **Edge-TTS** (cloud): Microsoft's premium voices (requires internet)

### **Audio Device Configuration**
```powershell
# Test audio system
.\vpa.exe --cli --log-level DEBUG

# If audio issues, check Windows audio devices:
# Settings > System > Sound > Choose your output device
# Ensure default audio device is functional
```

### **Voice Selection** (GUI Mode)
- **Settings** → **Audio** → **Voice Selection**
- Choose from 13 available voices
- Test voices with sample text
- Adjust speech rate and volume

---

## 🌐 **EXTERNAL INTEGRATIONS**

### **API Keys** (Optional)
For cloud-based features, you may need API keys:

```powershell
# Set environment variables for API keys
$env:OPENAI_API_KEY="your-openai-key-here"
$env:GOOGLE_API_KEY="your-google-key-here"
$env:MICROSOFT_API_KEY="your-microsoft-key-here"

# Then run VPA
.\vpa.exe
```

### **OAuth Setup** (GUI)
Some features may require OAuth authentication:
1. Launch VPA in GUI mode: `.\vpa.exe --gui`
2. Navigate to **Settings** → **Integrations**
3. Follow OAuth setup wizard for desired services
4. Credentials are stored securely locally

---

## 🚨 **TROUBLESHOOTING**

### **Common Issues**

#### **Issue**: "Application failed to start"
```powershell
# Solution: Check Windows version and architecture
winver  # Should show Windows 10+ x64
.\vpa.exe --help  # Test basic functionality
```

#### **Issue**: "Module not found" errors
```powershell
# Solution: Enable required feature flags
$env:VPA_ENABLE_ENTERPRISE="1"
$env:VPA_ENABLE_ADVANCED_LLM="1"
.\vpa.exe --log-level DEBUG
```

#### **Issue**: Audio/TTS not working
```powershell
# Solution: Verify audio devices and drivers
# 1. Test Windows audio: Control Panel > Sound
# 2. Update audio drivers
# 3. Try different audio device as default
.\vpa.exe --cli --log-level DEBUG  # Check audio system logs
```

#### **Issue**: Slow startup (>5 seconds)
```powershell
# Solution: This is normal for first run or after Windows updates
# Subsequent runs should be much faster due to caching
# If persistent, check:
# - Available RAM (need 128MB+)
# - Disk space (need 200MB+)
# - Antivirus exclusions (add vpa.exe if needed)
```

#### **Issue**: High memory usage
```powershell
# This is expected behavior:
# - Baseline: ~6MB (core features only)
# - With enterprise: +50-100MB (ML models)
# - With advanced LLM: +100-500MB (transformer models)
# - Monitor with: Get-Process -Name "vpa" | Select-Object WS
```

### **Debug Mode**
```powershell
# Maximum verbosity for troubleshooting
$env:VPA_LOG_LEVEL="DEBUG"
.\vpa.exe --cli --log-level DEBUG > debug_log.txt 2>&1

# Review debug_log.txt for detailed error information
```

### **Performance Profiling**
```powershell
# Measure startup time
Measure-Command { .\vpa.exe --help }

# Monitor memory usage
Get-Process -Name "vpa" | Select-Object ProcessName,WS,CPU

# Check disk usage
Get-ChildItem .\dist\vpa\ | Measure-Object -Property Length -Sum
```

---

## 📞 **SUPPORT & COMMUNITY**

### **Getting Help**
1. **Documentation**: Check `README.md` and inline `--help`
2. **GitHub Issues**: [Report bugs/feature requests](https://github.com/KarlBotha/VPA/issues)
3. **Debug Logs**: Always include `--log-level DEBUG` output
4. **System Info**: Include Windows version, RAM, and error messages

### **Contributing**
```powershell
# Development setup (source code)
git clone https://github.com/KarlBotha/VPA.git
cd VPA
python -m pip install -r requirements.txt
python -m pytest tests/  # Run test suite
python src/main.py --help  # Run from source
```

### **Release Updates**
- **GitHub Releases**: New builds published automatically
- **Version Check**: `.\vpa.exe --version` shows current version
- **Upgrade**: Download new `vpa.exe` and replace existing file

---

## ⚡ **ADVANCED USAGE**

### **Automation & Scripting**
```powershell
# Batch operations
.\vpa.exe --cli --config batch-config.yaml

# Integration with other tools
$result = & .\vpa.exe --cli --query "weather today" | ConvertFrom-Json
Write-Output "Weather: $($result.response)"

# Scheduled execution (Task Scheduler)
schtasks /create /tn "VPA Daily" /tr "C:\VPA\vpa.exe --cli --task daily_summary" /sc daily /st 09:00
```

### **Enterprise Deployment**
```powershell
# Group Policy deployment
# 1. Copy vpa.exe to \\domain\sysvol\scripts\vpa\
# 2. Create GPO with startup script: \\domain\sysvol\scripts\vpa\vpa.exe --cli
# 3. Configure environment variables via GPO
```

### **Development Integration**
```powershell
# VS Code integration
# 1. Add vpa.exe to PATH: $env:PATH += ";C:\VPA"
# 2. Use in integrated terminal: vpa --help
# 3. Configure as external tool in tasks.json
```

---

*Installation complete! VPA is ready to use. Run `.\vpa.exe --help` to explore available commands and options.*
