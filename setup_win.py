# !/usr/bin/env python
"""
IQGUI

-- GUI Application --

AUG 2015 Xaratustrah

"""

from distutils.core import setup
import py2exe
import matplotlib

name = 'iqgui'

version = '0.0.1'

pkgs = []

zipfile = "shared.lib"

includes = ['sip',
            'PyQt5',
            'PyQt5.QtWidgets',
            'PyQt5.QtCore',
            'PyQt5.QtGui',
            'numpy',
            'matplotlib.backends.backend_qt5agg'
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
    version=version,
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
