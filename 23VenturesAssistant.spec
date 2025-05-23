# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=['.'],
    binaries=[
        ('whisper.cpp/build/bin/whisper-cli', 'whisper-cli'),
    ],
    datas=[
        ('modules', 'modules'),
        ('models', 'models'),
        ('meetings', 'meetings'),
        ('.env', '.'),
        ('whisper.cpp/build/bin/whisper-cli', 'whisper-cli'),  # Add Whisper binary
    ],
    hiddenimports=['faiss', 'llama_cpp', 'sentence_transformers', 'spacy'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='23VenturesAssistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86_64',
    codesign_identity=None,
    entitlements_file=None,
)
