# -*- mode: python -*- ; coding: utf-8 -*-

# SPEC File for PyInstaller

block_cipher = None

import sys
sys.setrecursionlimit(5000)
__version__ = '4.0.6'

a = Analysis(['iqgui/__main__.py'],
             pathex=['F:\\git\\iqtools'],
             binaries=[],
             datas=[],
             hiddenimports=['iqtools'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
		  name=f'iqgui_{__version__}',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
		  icon='iqgui/rsrc/icon.ico',
		   )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name=f'iqgui_{__version__}',
)
