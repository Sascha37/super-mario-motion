# -*- mode: python ; coding: utf-8 -*-
import mediapipe as mp
import os
from PyInstaller.utils.hooks import collect_data_files

# Path to mediapipe module
mediapipe_path = os.path.dirname(mp.__file__)
cwd = os.getcwd()

datas = [
    #mediapipe modules
    (os.path.join(mediapipe_path, 'modules'), os.path.join('mediapipe', 'modules')),
    #images
    (os.path.join(cwd,'src','super_mario_motion', 'images'), 'images'),
    #help doc
    (os.path.join(cwd,'docs','help'), 'help')
    #default fallback joblib
    (os.path.join(cwd,'docs'), 'data')
]

hiddenimports = [
    'PIL._tkinter_finder',
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
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
