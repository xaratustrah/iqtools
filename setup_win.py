# !/usr/bin/env python
"""
IQGUI

-- GUI Application --

AUG 2015 Xaratustrah

"""

from distutils.core import setup
import py2exe
import matplotlib
from version import __version__

name = 'iqgui'

pkgs = []

zipfile = "shared.lib"

includes = ['sip',
            'PyQt5',
            'PyQt5.QtWidgets',
            'PyQt5.QtCore',
            'PyQt5.QtGui',
            'numpy',
            'matplotlib.backends.backend_qt5agg',
			'mainwindow'
			#'matplotlib.figure',
			#'matplotlib.cm',
			#'matplotlib.ticker',
			#'matplotlib.pyplot'
            ]

options = {'bundle_files': 2,
           'compressed': True,
           'includes': includes,
           'packages': pkgs
           }

datafiles = [("platforms", ["C:\\Python34\\Lib\\site-packages\\PyQt5\\plugins\\platforms\\qwindows.dll"]),
             ("", [r"c:\windows\syswow64\MSVCP100.dll", r"c:\windows\syswow64\MSVCR100.dll"])] + \
			 matplotlib.get_py2exe_datafiles()

setup(
    name=name,
    version=__version__,
    url='',
    license='',
    zipfile=None,
    data_files=datafiles,
    windows=[{
        'script': 'iqgui.py',
        #'icon_resources': [(1, 'icon.ico')],
        'dest_base': 'iqgui'
    }],
    options={'py2exe': options}
)

#------------ current package setup win -------------

# Current package setup under windows:

# Python 3.4.0 and PyQt5.5.0 both x64 versions. 
 
# matplotlib-1.4.3-cp34-none-win_amd64.whl
# numpy-1.10.0b1+mkl-cp34-none-win_amd64.whl
# scipy-0.16.0-cp34-none-win_amd64.whl

# cycler (0.9.0)
# fortranformat (0.2.5)
# pip (1.5.4)
# py2exe (0.9.2.2)
# pyparsing (2.0.3)
# python-dateutil (2.4.2)
# pytz (2015.4)
# scipy (0.16.0)
# setuptools (2.1)
# six (1.9.0)

#------------ errors + solutions --------

#Error:
#AttributeError: function 'Py_DecRef' not found

#Solution:
#do not bundle python interpreter: bundle_file : 2

#http://matplotlib.1069221.n5.nabble.com/AttributeError-function-Py-DecRef-not-found-td43449.html
#http://www.py2exe.org/index.cgi/SingleFileExecutable


#Error:
#raise zipimport.ZipImportError("can't find module %s" % fullname)

#Possible reason:
#http://stackoverflow.com/questions/29578210/zipimporter-cant-find-load-sub-modules

#Solution:
