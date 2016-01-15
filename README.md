iq_suite
============
<img src="https://raw.githubusercontent.com/xaratustrah/iq_suite/master/rsrc/icon.png" width="128">

Collection of code for working with offline complex valued time series data ([inphase and quadrature](https://en.wikipedia.org/wiki/In-phase_and_quadrature_components) or IQ Data)  with numpy written in Python. 

![iq_suite](https://raw.githubusercontent.com/xaratustrah/iq_suite/master/rsrc/screenshot.png)

These data are usually results of measurements of quantities in physical experiments in fundamental research or other related fields in science and engineering. These data are usually a result of radio frequency data acquisition systems involving one of the many methods of analog or digital [Hilbert transformation](https://en.wikipedia.org/wiki/Hilbert_transform) for the creation of [analytic signals](https://en.wikipedia.org/wiki/Analytic_signal), which in turn are easily processed in further stages. Applications include particle and fundamental physics, astrophysics, [software defined radio](https://en.wikipedia.org/wiki/Software-defined_radio) and many more.

While the GUI program offers a limited graphical interface to visually inspect the data, the advanced usage allows direct programing using the class file and tools within own scrips or iPython Notebook sessions. The suite offers a extendible structure for adding further methods e.g. in spectral analysis or non-linear time series analysis.

## Code Components

### IQBase class
This class covers all required parameters to handle time domain IQ data and their representation in frequency domain. Cuts, slices etc. are also available.

### iqtools
Is a collection of commandline tools and additional functions that uses the IQBase class as main data type but additionally offers tools for plotting and accessing the data. Stand alone operation is also possible using
command line arguments.

### iqgui
This is a GUI written using the Qt5 bindings for quick showing of the spectrogram plots for visual analysis or inspection.

## Supported file formats

#### [Tektronix<sup>&reg;</sup>](http://www.tek.com) binary file formats \*.IQT and \*.TIQ

Data format from different generations of real time spectrum analyzers.

#### [National Instruments<sup>&trade;</sup>](http://www.ni.com) \*.TDMS

Data format used in NI's [LabView<sup>&trade;</sup>](http://www.ni.com/labview/). Based on the python library [pyTDMS](http://sourceforge.net/projects/pytdms/) by [Floris van Vugt](http://www.florisvanvugt.com).

#### TCAP \*.DAT files
TCAP file format form the older HP E1430A systems. In this case, the header information is stored in a TXT file, while the data file is stored in blocks of 2GB sequentially. More information can be found in [this PhD thesis](http://www.worldcat.org/oclc/76566695).

#### Audio file \*.WAV

This data format is mostly useful for software defined radio applications. Left and right channels are treated as real and imaginary components respectively, file duration and sampling rate are determined automatically. Memory map is activated to avoid the whole file will be loaded in memory.

#### raw binary \*.BIN, ASCII \*.CSV and \*.TXT 

The binary files begin with a 32-bit integer for sampling rate, followed by a 32-bit float for the center frequency. The rest of the file contains real and imaginary parts each as a 32-bit floats. File size is automatically calculated. All data are little endian. The ASCII files are tab or space separated values with real and imaginary on every line. These data will later be treated as 32-bit floating point numbers. Lines beginning with # are considered as comments and are ignored. Here also the first line contains the a 32-bit integer for sampling rate, followed by a 32-bit float for the center frequency. Such files are used as a result of synthesis signals. For example you can create a synthetic signal like the following: 

    from iqtools import *
    freq = 400 # in Hz
    center = 0 # in Hz
    fs = 10000 # samples per second
    duration = 3 # seconds
    t, x = make_test_signal(freq, fs, duration, nharm=3, noise=False)
    xbar, phase = make_analytical(x)
    write_signal_as_binary('test_signal.bin', xbar, fs, center)
    write_signal_as_ascii('test_signal.bin', xbar, fs, center)

The resulting file can be read by library, or by using **iqgui**.

## Installation

#### Usage under Linux and OSX

Usage under Linux and OSX is pretty straight forward.

#### Building GUI under windows

Building iqgui under windows has been tested using a minimal python installation under Win7 64 bit:

Python 3.4.0 and PyQt5.5.0 both x64 versions, directly from their respective official websites. Following packages were installed from [Ch. Gohlke](http://www.lfd.uci.edu/~gohlke/pythonlibs/)'s website: 

    matplotlib-1.5.0rc1-cp34-none-win_amd64
    numpy-1.10.0b1+mkl-cp34-none-win_amd64.whl
    scipy-0.16.0-cp34-none-win_amd64.whl

Following packages where installed using **pip**:

    pip (1.5.4)
    py2exe (0.9.2.2)
    setuptools (2.1)
    spectrum (0.6.1)

For the pyTDMS, the [package](https://pypi.python.org/pypi/pyTDMS/0.0.2) in PyPI is **not** used, because it refers to an old version. Instead it is provided as a single file here in the repository.

The spectrum package needs a compiler to build. Usually one needs MS Visual ot GCC. I use [mingwpy](https://anaconda.org/carlkl/mingwpy) by [carlkl](https://github.com/carlkl). You can go to the file list, and choose the one wheel file that you need, donwload and install locally. If during the compilation you get the error message

	cannot find vcvarsal.bat

then you still need to tell the system that your compiler is `gcc`. For that you need to find out where is your home directory in your `msys` or other shell you are using. For that type

	cd
	pwd

Then you should see your home directory. Then you should create a file there with the name: `pydistutils.cfg` with the following content:

	[build]
	compiler = mingw32
	[build_ext]
	compiler = mingw32

After that the compiliation should work like a charm. Note that in the current version of the spectrum, the mtm.py needs a patch. Replace the following line:

	p = os.path.abspath(os.path.dirname(__file__))

with:

	if hasattr(sys, 'frozen'):
		p = os.path.abspath(os.path.dirname(sys.executable))
	else:
		p = os.path.abspath(os.path.dirname(__file__))
	
then perform the compilation. Note there is also a ready made package for spectrum that can be found [here](https://anaconda.org/carlkl/spectrum).

**Compressing using UPX**

Using [UPX](http://upx.sourceforge.net/) the size of the resulting compilation under windows can be reduced by the following command:

	upx --best --lzma --compress-exports=0 --strip-relocs=0 *.pyd *.dll

## Acknowledgements
I am thankful to [carlkl](https://github.com/carlkl) for his valuable help in making a stand alone binary under MS Windows and also for fruitful discussions and suggestions.

