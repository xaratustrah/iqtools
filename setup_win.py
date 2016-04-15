# !/usr/bin/env python
"""
IQGUI

-- GUI Application --

AUG 2015 Xaratustrah

"""

from distutils.core import setup
import py2exe
import matplotlib
from glob import glob
import PyQt5, spectrum
from version import __version__

NAME = 'iqgui'

packages = []

includes = ['sip',
            'atexit',
            'PyQt5',
            'PyQt5.QtWidgets',
            'PyQt5.QtCore',
            'PyQt5.QtGui',
            'numpy',
            'matplotlib',
            'matplotlib.backends.backend_qt5agg',
            'scipy.signal',
            'scipy.special._ufuncs_cxx',
            'scipy.linalg.cython_blas',
            'scipy.linalg.cython_lapack',
            'scipy.sparse.csgraph._validation',
            'pyTDMS',
            'spectrum',
            ]

excludes = ['pkg_resources',
            'doctest',
            'pdb',
            'optparse',
            'jsonschema',
            'tornado',
            'setuptools',
            'urllib2',
            'tkinter']

options = {
    'optimize': 2,
    'compressed': True,
    'includes': includes,
    'excludes': excludes,
    'packages': packages
}
    
qt_platform_plugins = [('platforms', glob(PyQt5.__path__[0] + r'\plugins\platforms\*.*'))]
spectrum_plugin = [('', glob(spectrum.__path__[0] + r'\mydpss.pyd'))]

data_files = []
data_files.extend(qt_platform_plugins)
data_files.extend(matplotlib.get_py2exe_datafiles())
data_files.extend(spectrum_plugin)

setup(
    name=NAME,
    version=__version__,
    url='https://github.com/xaratustrah/iq_suite',
    license='GPLv.3',
    zipfile=None,
    data_files=data_files,
    windows=[{
        'script': 'iqgui.py',
        'icon_resources': [(1, 'rsrc/icon.ico')],
    }],
    options={'py2exe': options}
)
