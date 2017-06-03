#!/usr/bin/env python
"""
Collection of tools for dealing with IQ data. This code converts data in TIQ
format and extracts the data in numpy format

xaratustrah oct-2014
            mar-2015
            aug-2015
            jan-2016
"""

import argparse, sys, os
from pprint import pprint
import logging as log

from iqtools.tiqdata import TIQData
from iqtools.iqbase import IQBase
from iqtools.tcapdata import TCAPData
from iqtools.tdmsdata import TDMSData
from iqtools.rawdata import RAWData
from iqtools.iqtdata import IQTData
from iqtools.tiqdata import TIQData
from iqtools.asciidata import ASCIIData
from iqtools.wavdata import WAVData
from iqtools.version import __version__
from iqtools.plotters import *
from iqtools.tools import *


def get_iq_object(filename, header_filename):
    """
    Return suitable object accorting to extension.

    Parameters
    ----------
    filename

    Returns
    -------

    """
    # Object generation
    _, file_extension = os.path.splitext(filename)

    iq_data = None

    if file_extension.lower() == '.txt' or file_extension.lower() == '.csv':
        log.info('This is an ASCII file.')
        iq_data = ASCIIData(filename)

    if file_extension.lower() == '.bin':
        log.info('This is a raw binary file.')
        iq_data = RAWData(filename)

    if file_extension.lower() == '.wav':
        log.info('This is a wav file.')
        iq_data = WAVData(filename)

    if file_extension.lower() == '.iqt':
        log.info('This is an iqt file.')
        iq_data = IQTData(filename)

    if file_extension.lower() == '.iq':
        log.info('This is an iq file.')
        iq_data = IQTData(filename)

    if file_extension.lower() == '.tiq':
        log.info('This is a tiq file.')
        iq_data = TIQData(filename)

    if file_extension.lower() == '.tdms':
        log.info('This is a TDMS file.')
        iq_data = TDMSData(filename)

    if file_extension.lower() == '.dat':
        log.info('This is a TCAP file.')
        if not header_filename:
            log.info('TCAP files need a text header file as well. Aborting....')
            return None
        else:
            iq_data = TCAPData(filename, header_filename)
    return iq_data


# ------------ MAIN ----------------------------

def main():
    scriptname = 'iq_suite'
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, help="Name of the input file.")
    parser.add_argument("-hdr", "--header-filename", nargs='?', type=str, default=None,
                        help="Name of header file.")
    parser.add_argument("-l", "--lframes", nargs='?', type=int, const=1024, default=1024,
                        help="Length of frames, default is 1024.")
    parser.add_argument("-n", "--nframes", nargs='?', type=int, const=10, default=10,
                        help="Number of frames, default is 10.")
    parser.add_argument("-s", "--sframes", nargs='?', type=int, const=1, default=1,
                        help="Starting frame, default is 1.")
    parser.add_argument("-d", "--dic", help="Print dictionary to screen.", action="store_true")
    parser.add_argument("-f", "--fft", help="Plot FFT to file.", action="store_true")
    parser.add_argument("-p", "--psd", help="Plot PSD to file.", action="store_true")
    parser.add_argument("-g", "--spec", help="Plot spectrogram to file.", action="store_true")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
    parser.add_argument("-y", "--npy", help="Write dic to NPY file.", action="store_true")

    args = parser.parse_args()

    print('{} {}'.format(scriptname, __version__))

    if args.verbose:
        log.basicConfig(level=log.DEBUG)

    # here we go:

    log.info("File {} passed for processing.".format(args.filename))
    iq_data = get_iq_object(args.filename, args.header_filename)
    if not iq_data:
        print('Datafile needs an additional header file which was not specified. Nothing to do. Aborting...')
        sys.exit()

    iq_data.read(args.nframes, args.lframes, args.sframes)

    # Other command line arguments

    if args.fft:
        log.info('Generating FFT plot.')
        f1, v1, p1 = iq_data.get_fft()
        plot_dbm_per_hz(f1, p1, iq_data.center, iq_data.span, iq_data.filename_wo_ext + '_psd_fft.png', True)

    if args.psd:
        log.info('Generating PSD plot.')
        f2, p2 = iq_data.get_pwelch()
        plot_dbm_per_hz(f2, p2, iq_data.center, iq_data.span, iq_data.filename_wo_ext + '_psd_welch.png', True)

    if args.spec:
        log.info('Generating spectrogram plot.')
        x, y, z = iq_data.get_spectrogram()
        plot_spectrogram_dbm(x, y, z, iq_data.center, iq_data.filename_wo_ext + '_spectrogram.png', True)

    if args.npy:
        log.info('Saving data dictionary in numpy format.')
        iq_data.save_npy()

    if args.dic:
        log.info('Printing dictionary on the screen.')
        pprint(iq_data.dictionary)


# ----------------------------------------

if __name__ == "__main__":
    main()
