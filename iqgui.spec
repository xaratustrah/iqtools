# -*- mode: python -*- ; coding: utf-8 -*-

# SPEC File for PyInstaller

block_cipher = None

import sys
sys.setrecursionlimit(5000)
from iqgui.version import __version__

a = Analysis(['iqgui/__main__.py'],
             pathex=['F:\\git\\iqgui'],
             binaries=[],
             datas=[],
             hiddenimports=[],
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
		  name='iqgui_{}'.format(__version__),
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
		  icon='rsrc/icon.ico',
		   )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='iqgui_{}'.format(__version__),
)
