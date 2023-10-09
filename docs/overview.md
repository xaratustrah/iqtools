# Overview of `iqtools`

## Introduction

IQ data are usually results of measurements of quantities in scientific research such as physics experiments or other related fields in science and engineering. These data are usually acquired using radio frequency data acquisition systems or software defined radios ([SDR](https://en.wikipedia.org/wiki/Software-defined_radio)) involving one of the many methods of analog or digital [Hilbert transformation](https://en.wikipedia.org/wiki/Hilbert_transform) for the creation of [analytic signals](https://en.wikipedia.org/wiki/Analytic_signal), which in turn are easily processed in further stages. Applications include particle and fundamental physics, astrophysics, [software defined radio](https://en.wikipedia.org/wiki/Software-defined_radio) and many more in science and engineering.

`iqtools` allows direct usage of class file and tools within own scrips or iPython Notebook sessions. The library offers an extendable structure for adding further methods e.g. in spectral analysis or non-linear time series analysis.

## Code Components
`iqtools` is a library, but it also comes with a CLI and a GUI. The library is constructed as follows:

#### IQBase class and its sub classes
This class covers all required parameters to handle time domain IQ data and their representation in frequency domain. Cuts, slices etc. are also available. Also a set of windowing functions are available.

#### Filetype specific classes

There are several specific classes available for each file type, all sharing the common base.

#### Tools and plotters

Two separate module includes several tools like plotters and input / output routines for convenience.

## Supported file formats

#### [Tektronix<sup>&reg;</sup>](http://www.tek.com) binary file formats \*.IQT, \*.TIQ, \*.XDAT and \*.R3F

Data format from different generations of real time spectrum analyzers, including the 3000, 5000 and also 600 USB analyzer series. In the tools section, there is also support for the **\*.specan** data format which is the already converted trace format in the analyzer software.

#### [National Instruments<sup>&trade;</sup>](http://www.ni.com) \*.TDMS

Data format used in NI's [LabView<sup>&trade;</sup>](http://www.ni.com/labview/). Based on the python library [nptdms](https://github.com/adamreeve/npTDMS).

#### TCAP \*.DAT files
TCAP file format form the older HP E1430A systems. In this case, the header information is stored in a TXT file, while the data file is stored in blocks of 2GB sequentially. More information can be found in [this PhD thesis](http://www.worldcat.org/oclc/76566695).

#### LeCroy<sup>&reg;</sup> 584AM Data files
Reading data files from this old oscilloscope is possible with its own class.

#### Audio file \*.WAV

This data format is mostly useful for software defined radio applications. Left and right channels are treated as real and imaginary components respectively, file duration and sampling rate are determined automatically. Memory map is activated to avoid the whole file will be loaded in memory.

#### Raw binary \*.BIN, ASCII \*.CSV and \*.TXT

The binary files begin with a 32-bit integer for sampling rate, followed by a 32-bit float for the center frequency. The rest of the file contains real and imaginary parts each as a 32-bit floats. File size is automatically calculated. All data are little endian. The ASCII files are tab or space separated values with real and imaginary on every line. These data will later be treated as 32-bit floating point numbers. Lines beginning with # are considered as comments and are ignored. Here also the first line contains the a 32-bit integer for sampling rate, followed by a 32-bit float for the center frequency. Such files are used as a result of synthesis signals. See [examples section](examples.md) for more information.

#### GNU Radio format

You can read and write to files that originate from or need to be processed in [GNU Radio](http://gnuradio.org/). Please see [examples section](examples.md) for more information.

#### CERN ROOT format
[ROOT](https://root.cern/) is an extensive data analysis framework that is very popular in the physics community. `iqtools` has possibilities to interface with ROOT using the [uproot](https://uproot.readthedocs.io/en/latest/) library.  See [examples section](examples.md) for more information.
