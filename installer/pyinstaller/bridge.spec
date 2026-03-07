# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

spec_dir = Path(SPEC).resolve().parent
entry_script = str((spec_dir.parent / "run_mock_openclaw_server.py").resolve())
project_root = str(spec_dir.parent.parent.resolve())

hiddenimports = collect_submodules("edge_tts")
hiddenimports += collect_submodules("faster_whisper")


a = Analysis(
    [entry_script],
    pathex=[project_root],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="sori-bridge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)
