# Welcome to `iqtools`
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://xaratustrah.github.io/iqtools)[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7615693.svg)](https://doi.org/10.5281/zenodo.7615693)

<div style="margin-left:auto;margin-right:auto;text-align:center">
<img src="https://raw.githubusercontent.com/xaratustrah/iqtools/main/docs/img/icon.png" width="128">
</div>

Collection of code for working with offline complex valued time series data ([inphase and quadrature](https://en.wikipedia.org/wiki/In-phase_and_quadrature_components) or IQ Data) with numpy written for Python3.


## Installation
Clone the repository or download the source from [GitHUB](https://github.com/xaratustrah/iqtools). Then use `pip` for installing and uninstalling `iqtools`.

    pip install -r requirements.txt
    pip install .

If you like to use `iqtools` with ROOT features within PyROOT, please make sure you have a proper installation of ROOT and PyROOT in your python environment. Please refer to the web site of [PyROOT](https://root.cern/manual/python/). An alternative, much easier way is to install ROOT using `conda-forge` as described [here](https://anaconda.org/conda-forge/root/) or [here](https://iscinumpy.gitlab.io/post/root-conda/).

## Quick usage

`iqtools` is a library that can be embedded in data analysis projects. It also has a GUI and CLI for quick access or conversions, so it can be run as a command line program for processing data file as well. Type:

    iqtools --help

## Documentation

For more information please refer to the [documentation page](https://xaratustrah.github.io/iqtools).

## Citation for publications

If you are using this code in your publications, please refer to [DOI:10.5281/zenodo.7615693](https://doi.org/10.5281/zenodo.7615693) for citation, or cite as:

<small>
Shahab Sanjari. (2023). <i>iqtools: Collection of code for working with offline complex valued time series data in Python.</i> Zenodo. <a href="https://doi.org/10.5281/zenodo.7615693">https://doi.org/10.5281/zenodo.7615693</a>
</small>