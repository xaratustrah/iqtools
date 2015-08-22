iq_suite
============

![barion](https://raw.githubusercontent.com/xaratustrah/iq_suite/master/screenshot.png)

Collection of code for working with IQ Time data with numpy. While the GUI program offers a limited graphical way to view data, the advanced usage allows direct programing using the class file and tools within own scrips or iPython Notebook sessions.


#### IQData class
This class covers all required parameters to handle time domain IQ data and their representation in frequency domain. Cuts, slices etc. are also available.

#### iqtools
Is a collection that uses the IQData class as main data type but additionally offers tools for plotting and accessing the data. Stand alone operation is also possible using
command line arguments.

#### iqgui
This is a GUI written using the Qt5 bindings for quick showing of the spectrogram plots for visual analysis or inspection.

