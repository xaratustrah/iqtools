# IQGUI

`iqgui` is a simple GUI front end for the `iqtools` library. It offers only limited set of features of the library, nevertheless these features may come in handy for quick checks. The main window looks like this:

<img src="https://raw.githubusercontent.com/xaratustrah/iqtools/main/docs/img/iqgui.png" width="1024">

## Features:

The GUI has several features:

#### Setting pane
Here you can set:

- number of points per frame
- number of frames to be considered for plotting
- the start frame
  
The equivalent time is displayed. The analysis method can also be selected from: standard FFT, multi-taper estimation, also in 1D or 2D variations. The windowing function can also be selected. The colour map settings allow for different colour contrasts. This is sometimes useful to improve the visual perception of week signals in noise.

All of these settings can be saved for future use using the Save Config button. This allows you to use the same visual settings for a series of plots.

The actual plotting is done by pressing the `Plot` button or the `Enter` key.



#### Info pane

The info pane shows the information about the file.

#### Sliders

* Sliders: The GUI offers 3 sliders. Using these sliders you can 
  * Left slider moves the start time, i.e. you can move in time
  * The middle slider sets the minimum contrast
  * The right slider sets the maximum contrast


#### Plot pane

This is the standard Matplotlib plot widget that allows different operations, including zoom, pan exporting the pictures and many more.



## Advanced hints:

Some additional information, in case you are interested in creating a Windows binary from scratch, you can achieve this by using the [PyInstaller](https://pyinstaller.org/en/stable/) package. The best result can be achieved by using the [WinPython](http://winpython.github.io/) package, which already includes PyQt5 library. Since none of the ROOT functions are needed from within `iqgui`, this variant of WinPython should be enough for running or building a static windows binary of `iqgui`. The rest is done using PyInstaller.

Note that WinPython is a huge package, so in order to make a smaller binary, you might like to first create an empty virtual environment. Run the Power Shell from the WinPython directory, `cd`to the place you have unpacked `iqtools`, then:

```bash
virtualenv VIR1
.\VIR1\Scripts\activate
pip install --upgrade pyinstaller==5.7.0 -r requirements.txt 
pyinstaller iqgui.spec
deactivate
```
Where `VIR1` could actually be any name. The resulting files and the EXE file will be in the `dist` directory.
