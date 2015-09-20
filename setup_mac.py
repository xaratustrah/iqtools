#!/usr/bin/env python
# coding=utf-8

from version import __version__
from setuptools import setup, find_packages

build_py2app = dict(
    argv_emulation=True,
    includes=[
        'PyQt5',
        'numpy',
        'scipy',
        'PyQt5.QtWidgets',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'numpy',
        'matplotlib.backends.backend_qt5agg',
        'matplotlib',
        'sip'
    ],
    excludes=[
    ],
    resources=[
    ],
    plist=dict(
        CFBundleName="iqgui",
        CFBundleShortVersionString=__version__,
        CFBundleGetInfoString="iqgui %s" % __version__,
        CFBundleExecutable="iqgui",
        CFBundleIdentifier="org.iqgui.iqgui",
    ),
    # iconfile='pathomx/static/icon.icns',
    qt_plugins=[
    ],
)

setup(

    name='iqgui',
    version=__version__,
    author='',
    packages=find_packages(),
    include_package_data=True,
    app=['iqgui.py'],
    options={
        'py2app': build_py2app,
    },
    setup_requires=['py2app'],
)
