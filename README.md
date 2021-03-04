iqtools
============
<img src="https://raw.githubusercontent.com/xaratustrah/iqtools/master/icon.png" width="128">

Collection of code for working with offline complex valued time series data ([inphase and quadrature](https://en.wikipedia.org/wiki/In-phase_and_quadrature_components) or IQ Data) with numpy written in Python.

These data are usually results of measurements of quantities in physical experiments in fundamental research or other related fields in science and engineering. These data are usually a result of radio frequency data acquisition systems involving one of the many methods of analog or digital [Hilbert transformation](https://en.wikipedia.org/wiki/Hilbert_transform) for the creation of [analytic signals](https://en.wikipedia.org/wiki/Analytic_signal), which in turn are easily processed in further stages. Applications include particle and fundamental physics, astrophysics, [software defined radio](https://en.wikipedia.org/wiki/Software-defined_radio) and many more.

The usage allows direct programming using the class file and tools within own scrips or iPython Notebook sessions. The library offers an extendable structure for adding further methods e.g. in spectral analysis or non-linear time series analysis. A related project uses this library for a GUI representation and can be found [here](https://github.com/xaratustrah/iqgui).

## Code Components

### IQBase class
This class covers all required parameters to handle time domain IQ data and their representation in frequency domain. Cuts, slices etc. are also available. Also a set of windowing functions are available.

### Filetype specific classes

There are several specific classes available for each file type, all sharing the common base.

### tools

A separate module includes several tools like input and output routines


### iqtools as a command line program

`iqtools` can be run as a command line program for processing data file as well. Type:

    iqtools --help

For more information.


## Supported file formats

#### [Tektronix<sup>&reg;</sup>](http://www.tek.com) binary file formats \*.IQT, \*.TIQ and \*.XDAT

Data format from different generations of real time spectrum analyzers, including the 3000, 5000 and 600 USB analyzer series.

In the tools section, there is also support for the **\*.specan** data format which is the already converted trace format in the analyzer software.

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

#### GNURadio: Reading GNURadio files
If you have a flow graph in gnuradio and like to save files, you can use the **file sink** block and save data. Using `iqtools` you can then import the data as usual, except that you have to provide the sampling rate. Here is an example to plot an spectrogram:

    import iqtools
    filename = './test.bin'
    iqdata = iqtools.GRData(filename, fs = 2.5e6, center=30e6)
    iqdata.read_complete_file()
    xx, yy, zz = iqdata.get_spectrogram(nframes=2000, lframes=1024)
    iqtools.plot_spectrogram(xx, yy, zz)

#### GNURadio: Writing GNURadio files

You can use the library interface or the command line interface to convert your data into complex64 (I and Q each 32-bit) for further use in [GNU Radio](http://gnuradio.org/).

    iqtools --verbose --lframes 1024 --nframes 1 --raw inputfile.tiq

The *sampling rate* and the *center frequency* will also be printed. Or within your program like:

    import iqtools
    filename = "inputfile.tiq"
    iq=TIQData(filename)
    iq.read_samples(1024*100)
    write_signal_as_binary('inputfile.bin', iq.data_array, iq.fs, iq.center, write_header=False)


Later the file can be imported using a `File Source` block in GNU-Radio. Use a `Throttle` block with the sampling rate of the data.

<img src="https://raw.githubusercontent.com/xaratustrah/iqtools/master/gnuradio1.png">
<img src="https://raw.githubusercontent.com/xaratustrah/iqtools/master/gnuradio2.png">

#### CERN ROOT: Writing to CERN ROOT format

1D spectra can be exported to ROOT histograms for later analysis in ROOT.

    from iqtools import *
    filename='foobar.tiq'
    dd = TIQData(filename)
    dd.read_samples(1024)
    ff, pp, _ = dd.get_fft()
    write_spectrum_to_root(ff, pp, filename, center=dd.center, title='spectrum')




## Install / Uninstall

#### Dependencies

This library depends on `numpy`, `pytdms` and `uproot`, which can be installed via `pip` and the [multitaper](https://github.com/xaratustrah/multitaper) library which can be installed using `python setup`.


#### Installation

    python setup.py install --record files.txt

You may need to use `sudo` in your case if needed.

#### Uninstall

Also be careful with this one:

    cat files.txt | sudo xargs rm -rf
