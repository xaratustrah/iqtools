# !/usr/bin/env python
"""
IQGUI

-- GUI Application --

AUG 2015 Xaratustrah
MAR 2016 Xaratustrah

libqcocoa.dylib problem solved using 'frameworks' adapted from:
https://github.com/sparsile/padulator/blob/f1a361b3ee6952c2720c41a91ffa68891597760a/setup.py

"""

from version import __version__
from setuptools import setup
from subprocess import call
import shutil, os

NAME = 'iqgui'

app = ['iqgui.py']

packages = ['zmq', 'spectrum']

includes = ['sip',
            'PyQt5',
            'PyQt5.QtWidgets',
            'PyQt5.QtCore',
            'PyQt5.QtGui',
            'numpy',
            'scipy',
            'matplotlib.backends.backend_qt5agg',
            'matplotlib',
            'atexit', ]

excludes = ['PyQt5.QtDesigner', 'PyQt5.QtNetwork', 'PyQt5.QtOpenGL', 'PyQt5.QtScript', 'PyQt5.QtTest', 'PyQt5.QtSql',
            'PyQt5.QtWebKit', 'PyQt5.QtXml', 'PyQt5.phonon', 'PyQt5.uic.port_v2']

resources = ['rsrc', ]

plist = dict(CFBundleName=NAME,
             CFBundleShortVersionString=__version__,
             CFBundleGetInfoString='%s %s' % (NAME, __version__),
             CFBundleExecutable=NAME,
             CFBundleIdentifier='org.%s.%s' % (NAME, NAME),
             )

QTDIR = '/opt/local/libexec/qt5'

options = {'argv_emulation': True,
           'includes': includes,
           'excludes': excludes,
           'packages': packages,
           'resources': resources,
           'plist': plist,
           'frameworks': ['%s/plugins/platforms/libqcocoa.dylib' % QTDIR],
           'iconfile': 'rsrc/icon.icns'}

data_files = ['rsrc/qt.conf']

setup(
    app=app,
    name=NAME,
    version=__version__,
    url='https://github.com/xaratustrah/iq_suite',
    license='GPLv.3',
    data_files=data_files,
    setup_requires=['py2app'],
    options={'py2app': options},
)

os.makedirs('dist/' + NAME + '.app/Contents/PlugIns/platforms', exist_ok=True)
shutil.copyfile('dist/' + NAME + '.app/Contents/Frameworks/libqcocoa.dylib',
                'dist/' + NAME + '.app/Contents/PlugIns/platforms/libqcocoa.dylib')

print('Now creating the disk image...')
command = 'hdiutil create {}_{}.dmg -volname {} -fs HFS+ -srcfolder dist/{}.app'.format(NAME, __version__, NAME, NAME)
command = command.split()
call(command)
