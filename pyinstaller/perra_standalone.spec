# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = []

full_import_modules = [
    'perra',
    'socid_extractor',
    'arabic_reshaper',
    'pyvis',
    'reportlab.graphics.barcode',
    'xhtml2pdf',
    'curl_cffi',
    'pycountry',
    'alive_progress',
]

for module in full_import_modules:
    tmp_ret = collect_all(module)
    datas += tmp_ret[0]
    binaries += tmp_ret[1]
    hiddenimports += tmp_ret[2]

hiddenimports += [
    'socks',
    'bs4',
    'dateutil',
    'six',
    'bidi',
    'typing_extensions',
    'attrs',
    'aiohttp_socks',
    'aiodns',
    'xmind',
]

block_cipher = None


a = Analysis(
    ['perra_standalone.py'],
    pathex=['..'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='perra',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='perra',
)
