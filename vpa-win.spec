# Minimal Windows spec for VPA (windowed). Preserves `python -m vpa` semantics.
# Zero-bloat: exclude archive/legacy/enterprise by default. Add-ons can be re-enabled via a separate spec if needed.

from PyInstaller.utils.hooks import collect_submodules
import os
import sys

# Add src to Python path for build
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

# Module discovery - exclude heavy optional domains
vpa_modules = [m for m in collect_submodules('vpa') 
               if not any(x in m for x in ['enterprise', 'archive', 'legacy', 'advanced_llm'])]

# Create small runner to emulate `python -m vpa`
runner_code = '''
import runpy
if __name__ == '__main__':
    runpy.run_module('vpa', run_name='__main__', alter_sys=True)
'''

# Write runner to temp file
with open('_vpa_runner.py', 'w') as f:
    f.write(runner_code)

block_cipher = None

a = Analysis(
    ['_vpa_runner.py'],  # Use runner instead of direct main
    pathex=[os.path.join(os.getcwd(), 'src')],
    binaries=[],
    datas=[
        ('config/default.yaml', 'config/'),
        ('.env.example', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=vpa_modules + [
        'vpa',
        'vpa.core',
        'vpa.core.app',
        'vpa.core.events', 
        'vpa.core.plugins',
        'vpa.core.feature_flags',
        'vpa.audio',
        'pyttsx3',
        'edge_tts',
        'pygame',
        'psutil',
        'aiohttp',
        'cryptography',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',  # Exclude tkinter if not using GUI
        'matplotlib',
        'numpy',
        'scipy',
        # Exclude heavy optional domains
        'vpa.enterprise',
        'vpa.advanced_llm',
        'archive',
        'legacy_archive_cleanup',
        'referencedocuments',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='vpa',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Console app for now
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='vpa',
)

# Cleanup runner after build
import atexit
atexit.register(lambda: os.remove('_vpa_runner.py') if os.path.exists('_vpa_runner.py') else None)
