# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

import mediapipe as mp
from PyInstaller.utils.hooks import collect_all

# Path to mediapipe module
mediapipe_path = os.path.dirname(mp.__file__)
cwd = os.getcwd()

datas = [
    # mediapipe modules
    (os.path.join(mediapipe_path, 'modules'),
     os.path.join('mediapipe', 'modules')),
    # images
    (os.path.join(cwd, 'src', 'super_mario_motion', 'images'), 'images'),
    # help doc
    (os.path.join(cwd, 'docs', 'help'), 'help'),
    # default fallback joblib
    (os.path.join(cwd, 'src', 'super_mario_motion', 'data'), 'data')
    ]

hiddenimports = [
    'PIL._tkinter_finder',
    "sklearn",
    "sklearn.pipeline",
    "sklearn.preprocessing",
    "sklearn.metrics",
    "sklearn.utils",
    "sklearn.base"
    ]

numpy_datas, numpy_binaries, numpy_hiddenimports = collect_all("numpy")

datas += numpy_datas
hiddenimports += numpy_hiddenimports
binaries = numpy_binaries

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib'],
    noarchive=False,
    optimize=0,
    )

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

if sys.platform == "darwin":
    exe = EXE(
        pyz,
        a.scripts,
        [],
        [],
        name='SuperMarioMotion',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=os.path.join(cwd, 'src', 'super_mario_motion', 'images', 'icon.png'),
        exclude_binaries=True,
        info_plist={
            'NSCameraUsageDescription': 'This application uses the camera for motion tracking.',
        }
    )

    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='SuperMarioMotion',
    )

    app = BUNDLE(
        coll,
        name='SuperMarioMotion.app',
        icon=os.path.join(cwd, 'src', 'super_mario_motion', 'images', 'icon.png'),
        info_plist={
            'NSCameraUsageDescription': 'This application uses the camera for motion tracking.',
        },
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name='SuperMarioMotion',
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
        icon=os.path.join(cwd, 'src', 'super_mario_motion', 'images', 'icon.png'),
    )

