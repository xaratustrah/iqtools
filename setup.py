# PyPI setup file

from setuptools import setup, find_packages
from barion.version import __version__
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

classifiers = [
    'Environment :: Console',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3 :: Only',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Topic :: Scientific/Engineering :: Physics',
    'Intended Audience :: Science/Research',

]

setup(
    name='iqtools',
    packages=find_packages(),
    version=__version__,
    description='Collection of tools for dealing with in phase / quadrature time series data.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Xaratustra',
    url='https://github.com/xaratustrah/iqtools',  # use the URL to the github repo
    download_url='https://github.com/xaratustrah/iqtools/tarball/{}'.format(
        __version__),
    entry_points={
        'console_scripts': [
            'iqtools = iqtools.__main__:main'
        ]
    },
    license='GPLv3',
    keywords=['physics', 'data', 'time series', ],  # arbitrary keywords
    classifiers=classifiers
)
