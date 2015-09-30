iq_suite
============
<img src="https://raw.githubusercontent.com/xaratustrah/iq_suite/master/icon.svg" width="128">

Collection of code for working with offline complex valued time series data ([inphase and quadrature](https://en.wikipedia.org/wiki/In-phase_and_quadrature_components) or IQ Data)  with numpy written in Python. 

![iq_suite](https://raw.githubusercontent.com/xaratustrah/iq_suite/master/screenshot.png)

These data are usually results of measurements of quantities in physical experiments in fundamental research or other related fields in science and engineering. These data are usually a result of radio frequency data acquisition systems involving one of the many methods of analog or digital [Hilbert transformation](https://en.wikipedia.org/wiki/Hilbert_transform) for the creation of [analytic signals](https://en.wikipedia.org/wiki/Analytic_signal), which in turn are easily processed in further stages. Applications include particle and fundamental physics, astrophysics, [software defined radio](https://en.wikipedia.org/wiki/Software-defined_radio) and many more.

While the GUI program offers a limited graphical interface to visually inspect the data, the advanced usage allows direct programing using the class file and tools within own scrips or iPython Notebook sessions. The suite offers a extendible structure for adding further methods e.g. in spectral analysis or non-linear time series analysis.


Supported file formats are:

**[Tektronix<sup>&reg;</sup>](http://www.tek.com) binary file formats *.IQT and *.TIQ**

Data format from different generations of real time spectrum analyzers.

**Audio file *.wav**

This data format is mostly useful for software defined radio applications. Left and right channels are treated as real and imaginary components respectively, file duration and sampling rate are determined automatically. Memory map is activated to avoid the whole file will be loaded in memory.

**raw binary *.bin:**

This is a file that begins with a 32-bit integer for sampling rate, followed by a 32-bit float for the center frequency. The rest of the file contains real and imaginary parts each as a 32-bit floats. File size is automatically calculated. All data are little endian.

**ASCII text *.txt or *.csv:**

Tab, space or comma separated values, real and imaginary on every line. Lines beginning with # are considered as comments and are ignored. Each line contains real and imaginary part. These data will later be treated as 32-bit floating point numbers.


## Code Components

### IQData class
This class covers all required parameters to handle time domain IQ data and their representation in frequency domain. Cuts, slices etc. are also available.

### iqtools
Is a collection that uses the IQData class as main data type but additionally offers tools for plotting and accessing the data. Stand alone operation is also possible using
command line arguments.

### iqgui
This is a GUI written using the Qt5 bindings for quick showing of the spectrogram plots for visual analysis or inspection.


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

    cycler (0.9.0)
    pip (1.5.4)
    py2exe (0.9.2.2)
    pyparsing (2.0.3)
    python-dateutil (2.4.2)
    pytz (2015.4)
    setuptools (2.1)
    six (1.9.0)

**Compressing using UPX**

Using [UPX](http://upx.sourceforge.net/) the size of the resulting compilation under windows can be reduced by the following command:

	upx --best --lzma --compress-exports=0 --strip-relocs=0 *.pyd *.dll

