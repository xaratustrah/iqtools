iqtools
============
<img src="https://raw.githubusercontent.com/xaratustrah/iqtools/master/icon.png" width="128">

Collection of code for working with offline complex valued time series data ([inphase and quadrature](https://en.wikipedia.org/wiki/In-phase_and_quadrature_components) or IQ Data) with numpy written in Python. 

These data are usually results of measurements of quantities in physical experiments in fundamental research or other related fields in science and engineering. These data are usually a result of radio frequency data acquisition systems involving one of the many methods of analog or digital [Hilbert transformation](https://en.wikipedia.org/wiki/Hilbert_transform) for the creation of [analytic signals](https://en.wikipedia.org/wiki/Analytic_signal), which in turn are easily processed in further stages. Applications include particle and fundamental physics, astrophysics, [software defined radio](https://en.wikipedia.org/wiki/Software-defined_radio) and many more.

The usage allows direct programing using the class file and tools within own scrips or iPython Notebook sessions. The suite offers a extendible structure for adding further methods e.g. in spectral analysis or non-linear time series analysis.

A related project uses this library for a GUI representation and can be found [here](https://github.com/xaratustrah/iqgui).

## Code Components

### IQBase class
This class covers all required parameters to handle time domain IQ data and their representation in frequency domain. Cuts, slices etc. are also available. Also a set of windowing functions are available.

### iqtools
Is a collection of commandline tools and additional functions that uses the IQBase class as main data type but additionally offers tools for plotting and accessing the data. Stand alone operation is also possible using
command line arguments.


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

    import iqtools
    freq = 400 # in Hz
    center = 0 # in Hz
    fs = 10000 # samples per second
    duration = 3 # seconds
    t, x = make_test_signal(freq, fs, duration, nharm=3, noise=False)
    xbar, phase = make_analytical(x)
    write_signal_as_binary('test_signal.bin', xbar, fs, center)
    write_signal_as_ascii('test_signal.bin', xbar, fs, center)


## Install / Uninstall

    sudo python setup.py install --record files.txt

be careful with this one:

    cat files.txt | sudo xargs rm -rf
