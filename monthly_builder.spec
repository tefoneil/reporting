# -*- mode: python ; coding: utf-8 -*-

# PyInstaller spec file for Monthly Reporting Builder
# Creates a single executable file with all dependencies bundled

import sys
import os

block_cipher = None

# Main script analysis
a = Analysis(
    ['monthly_builder.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # Include JSON data files
        ('docs/frozen_legacy_list.json', 'docs'),
        # Include any other required data files
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        # Ensure all GUI dependencies are included
        'FreeSimpleGUI',
        'matplotlib.backends.backend_tkagg',
        'PIL._tkinter_finder',
        # Excel processing
        'openpyxl.cell._writer',
        'openpyxl.workbook.external_link.external',
        # Word document processing
        'docx.oxml.ns',
        'docx.oxml.parser',
        # Data analysis
        'pandas.plotting._matplotlib',
        'pandas.io.formats.style',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary packages to reduce size
        'tkinter.test',
        'test',
        'unittest',
        'pydoc',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove duplicate binaries
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Monthly_Report_Builder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window - GUI only
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Add icon if available (uncomment and provide icon file)
    # icon='icon.ico',
    # Add version info
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)