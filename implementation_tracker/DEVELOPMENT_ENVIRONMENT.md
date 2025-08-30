# VPA Development Environment Setup

**Last Updated**: August 30, 2025

## Overview

This document outlines the development environment setup required for the Virtual Personal Assistant (VPA) project. All team members should follow these guidelines to ensure consistent development practices.

## Required Software

### Core Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | Primary programming language |
| Visual Studio Code | Latest | Recommended IDE |
| Git | Latest | Version control |
| Windows 10/11 | 21H2+ | Target OS platform |
| PowerShell Core | 7.3+ | Scripting and automation |

### Python Dependencies

Create a virtual environment and install the dependencies:

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Required Python Packages

Core packages:

```
PyQt6==6.5.0           # GUI framework
pydantic==2.0.3        # Data validation
pytest==7.3.1          # Testing framework
pytest-cov==4.1.0      # Coverage reporting
black==23.3.0          # Code formatting
pylint==2.17.4         # Static code analysis
SpeechRecognition==3.10.0  # Voice recognition
pyttsx3==2.90          # Text-to-speech
python-dotenv==1.0.0   # Environment variable management
loguru==0.7.0          # Logging
```

Additional packages by component:

```
# Audio system
pyaudio==0.2.13
webrtcvad==2.0.10
numpy==1.24.3

# Plugin system
importlib-metadata==6.6.0
yapsy==1.12.2

# Documentation
Sphinx==6.2.1
sphinx-rtd-theme==1.2.1
```

## Development Tools Configuration

### Visual Studio Code

#### Recommended Extensions

- Python (ms-python.python)
- Pylint (ms-python.pylint)
- Black Formatter (ms-python.black-formatter)
- GitLens (eamodio.gitlens)
- Python Test Explorer (littlefoxteam.vscode-python-test-adapter)
- Python Docstring Generator (njpwerner.autodocstring)

#### Workspace Settings

Create a `.vscode/settings.json` file with the following configuration:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.nosetestsEnabled": false,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".coverage": true,
        "htmlcov": true
    }
}
```

## Project Structure

```
VPA/
├── .venv/                 # Virtual environment (not in source control)
├── .github/               # GitHub actions and workflow configurations
├── docs/                  # Documentation
├── implementation_tracker/# Implementation tracking and status reports
├── planning_docs/         # Project planning documentation
├── scripts/               # Utility scripts for development
├── src/                   # Source code
│   ├── audio/             # Audio system components
│   ├── vpa/               # Core VPA components
│   │   ├── event_bus/     # Event bus system
│   │   ├── gui/           # GUI components
│   │   ├── plugin/        # Plugin system
│   │   └── settings/      # Settings management
│   └── main.py            # Application entry point
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── .gitignore             # Git ignore configuration
├── LICENSE                # Project license
├── README.md              # Project overview
└── requirements.txt       # Python dependencies
```

## Environment Variables

Create a `.env` file in the project root with the following variables:

```
# Development mode
VPA_DEV_MODE=True

# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
VPA_LOG_LEVEL=DEBUG

# Data directory
VPA_DATA_DIR=./data

# Audio settings
VPA_AUDIO_SAMPLE_RATE=16000
VPA_AUDIO_CHANNELS=1

# Plugin directory
VPA_PLUGIN_DIR=./plugins
```

## Development Workflow

1. **Branch Management**:
   - `main`: Production-ready code
   - `develop`: Integration branch for features
   - `feature/[name]`: Feature branches
   - `bugfix/[issue]`: Bug fix branches

2. **Commit Messages**:
   - Format: `[component] Brief description (#issue)`
   - Example: `[audio] Fix voice recognition delay (#42)`

3. **Code Review Process**:
   - All PRs require at least one review
   - PRs must pass all automated checks
   - PRs should include tests for new features

4. **Testing Standards**:
   - Unit test coverage: 90%+ (measured with pytest-cov)
   - Run tests before submitting PR: `pytest`
   - Check coverage: `pytest --cov=src tests/`

## Additional Resources

- [Python Style Guide (PEP 8)](https://peps.python.org/pep-0008/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Git Workflow Guide](../planning_docs/5_technical_standards/VERSION_CONTROL_STANDARDS.md)
- [Project Architecture](../planning_docs/1_architecture/ARCHITECTURE_OVERVIEW.md)

## Troubleshooting Common Issues

### Virtual Environment Activation Issues

If you encounter issues activating the virtual environment:

```powershell
# Check PowerShell execution policy
Get-ExecutionPolicy -List

# You may need to set the execution policy for the current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Audio Device Issues

If audio devices are not detected:

1. Verify device connections and system default settings
2. Run the audio diagnostics tool: `python scripts/audio_diagnostics.py`
3. Check for Windows permissions for microphone access

### GUI Rendering Issues

If GUI components fail to render:

1. Verify Qt dependencies are installed: `pip install PyQt6`
2. Check for screen scaling issues: Right-click on the application > Properties > Compatibility > Change high DPI settings

## Support

For environment setup support, contact the DevOps team through the project Slack channel (#vpa-devops).
