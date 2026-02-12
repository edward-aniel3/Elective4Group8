# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Image Processing System
Builds a standalone Windows executable with all dependencies
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all necessary data files
datas = []

# Include Minecraft face overlay images
datas += [
    ('steve_face.png', '.'),
    ('alex_face.png', '.'),
]

# Collect OpenCV data files (for face detection, etc.)
datas += collect_data_files('cv2')

# Hidden imports - modules that PyInstaller might miss
hiddenimports = [
    'PIL._tkinter_finder',
    'numpy.core._methods',
    'numpy.lib.format',
    'cv2',
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
]

# Add all our modules
hiddenimports += [
    'background_remover',
    'puzzle_shuffle',
    'minecraft_filter',
    'mosaic_tile_effect',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # Exclude if not used
        'scipy',       # Exclude if not used
        'pandas',      # Exclude if not used
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ImageProcessingSystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path if you have one
)
