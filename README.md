# Welcome to `iqtools`
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://xaratustrah.github.io/iqtools)[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7615693.svg)](https://doi.org/10.5281/zenodo.7615693)

<div style="margin-left:auto;margin-right:auto;text-align:center">
<img src="https://raw.githubusercontent.com/xaratustrah/iqtools/main/docs/img/icon.png" width="128">
</div>

Collection of code for working with offline complex valued time series data ([inphase and quadrature](https://en.wikipedia.org/wiki/In-phase_and_quadrature_components) or IQ Data) with numpy written for Python3.

## Installation and usage

### Quick instructions

There are many ways to install `iqtools` either fully or partly. One way to do a complete install is this:

#### TL;DR (for Linux and Mac):

Quick but full installation if you have `mamba` installed. Tested on Linux and Mac. First clone the repo, then go to the directory and run these commands.

```
mamba create -n my_env
mamba activate my_env
mamba install -y root pyqt pyfftw
pip install -r requirements.txt
pip install .
```

Where `my_env` can be any name you like.


#### Test your installation

You can test your installation by typing:

```bash
python3 -c 'import ROOT;import PyQt5;from iqtools import*'
```

If the command returns without any error, then you are good, i.e. you should be able to use the library, or run one of the user interfaces.

### Detailed installation instructions

#### Preparation

If you do not need to use `iqtools` with ROOT features, you can skip to the next section. If you like to use `iqtools` with ROOT features within PyROOT, please make sure you have a proper installation of ROOT and PyROOT in your python environment. There are several alternatives of how to install ROOT:

* System wide installation on Linux (Please refer to the web site of [PyROOT](https://root.cern/manual/python/) ). This approach is not recommended
* An easier way is to install ROOT using `conda-forge` as described [here](https://anaconda.org/conda-forge/root/) or [here](https://iscinumpy.gitlab.io/post/root-conda/).
* Most recommended is to use `mamba`. For that just install [mamba](https://mamba.readthedocs.io/en/latest/installation.html). Before installing, it is recommended to create a new mamba env and do your work there:

```
mamba create -n my_env
mamba activate my_env
mamba install root pyqt
```

Same goes with the installation of `pyqt`. If you are not interested in the GUI script, you can just ignore the installation of `pyqt` in the previous step. You will not be able to use the GUI, but you can still use the CLI and of course the library itself.

#### Installing packages

Clone the repository or download the source from [GitHUB](https://github.com/xaratustrah/iqtools). Then use `pip` for installing and uninstalling `iqtools`.

    pip install -r requirements.txt
    pip install .


### Windows

Under windows, ROOT / PyROOT needs to be installed in a different manner. Please refer to the installation instructions on the corresponding [web page](https://root.cern/) of the ROOT project. If you do not need the ROOT functions, you can still run the library, CLI and GUI under Windows. Specifically, it is recommended to download the latest version of [WinPython](https://winpython.github.io/) which contains the `PyQt` library. Just unpacking WinPython is enough, no installation is needed. After this, you can just follow the instructions above to install the requirements and packages via `pip`.

Some stand alone static versions of the `iqgui` for windows may be made available in the future in the release section for the corresponding tags.

### Quick usage

`iqtools` is a library that can be embedded in data analysis projects. You can use its full functionality in your own codes by importing it:

```python
from iqtools import *
```

and use it accordingly.

`iqtools` offers user interface which do not implement the full functionality of the library, but can be useful for quick access or conversions, so it can be run as a command line program for processing data file as well. For example:

    iqtools --help

The `iqgui` script is a graphical user interface (GUI) written in Qt with limited functionality, but nevertheless interesting features. You can run it by simply typing:

```bash
iqgui
```

A simple window will appear, where you can accesss some quick feartures. For more information on the GUI frontend please refer to the [documentation page](https://xaratustrah.github.io/iqtools).

<img src="https://raw.githubusercontent.com/xaratustrah/iqtools/main/docs/img/iqgui.png" width="512">

## Documentation

For more information please refer to the [documentation page](https://xaratustrah.github.io/iqtools).

## Citation for publications

If you are using this code in your publications, please refer to [DOI:10.5281/zenodo.7615693](https://doi.org/10.5281/zenodo.7615693) for citation, or cite as:

<small>
Shahab Sanjari. (2023). <i>iqtools: Collection of code for working with offline complex valued time series data in Python.</i> Zenodo. <a href="https://doi.org/10.5281/zenodo.7615693">https://doi.org/10.5281/zenodo.7615693</a>
</small>


## Licensing

Please see the file [LICENSE.md](./LICENSE.md) for further information about how the content is licensed.


## Acknowledgements

Many thanks to @tfoerst3r for providing help with the project structure and licensing issues and to @carlkl for helping with creating a static Windows version of the GUI.