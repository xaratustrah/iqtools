# PyPI setup file
# thanks to https://stackoverflow.com/a/23265673/5177935
#

from setuptools import setup, find_packages
from iqtools.version import __version__

long_description = ''

try:
    from pypandoc import convert

    read_md = lambda f: convert(f, 'rst', 'md')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

classifiers = [
    'Environment :: Console',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Topic :: Scientific/Engineering :: Physics'

]

setup(
    name='iqtools',
    packages=find_packages(),
    version=__version__,
    description='Collection of tools for dealing with in phase / quadrature time series data.',
    long_description=read_md('README.md'),
    author='Xaratustra',
    url='https://github.com/xaratustrah/iqtools',  # use the URL to the github repo
    download_url='https://github.com/xaratustrah/iqtools/tarball/{}'.format(__version__),
    entry_points={
        'console_scripts': [
            'iqtools = iqtools.__main__:main'
        ]
    },
    license='GPLv2',
    keywords=['physics', 'data', 'time series', ],  # arbitrary keywords
    classifiers=classifiers
)
