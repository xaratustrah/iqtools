#!/usr/bin/env python
"""
Collection of tools for dealing with IQ data. This code converts data in TIQ
format and extracts the data in numpy format

xaratustrah oct-2014
            mar-2015
            aug-2015
            jan-2016
            aug-2018
            nov-2019
            jul-2020
"""

import argparse
import sys
from pprint import pprint
import logging as log

from iqtools.version import __version__
from iqtools.plotters import *
from iqtools.tools import *


# ------------ MAIN ----------------------------

def main():
    scriptname = 'iqtools'
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
    parser.add_argument(
        "-d", "--dic", help="Print dictionary to screen.", action="store_true")
    parser.add_argument(
        "-f", "--fft", help="Plot FFT to file.", action="store_true")
    parser.add_argument(
        "-p", "--psd", help="Plot PSD to file.", action="store_true")
    parser.add_argument(
        "-g", "--spec", help="Plot spectrogram to file.", action="store_true")
    parser.add_argument("-v", "--verbose",
                        help="Increase output verbosity", action="store_true")
    parser.add_argument(
        "-y", "--npy", help="Write dic to NPY file.", action="store_true")
    parser.add_argument(
        "-r", "--raw", help="Write file to a raw format.", action="store_true")

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
        f1, p1, _ = iq_data.get_fft()
        plot_sectrum(f1, p1, iq_data.center, iq_data.span, dbm=False,
                     filename='{}_fft'.format(iq_data.filename_wo_ext))

    if args.psd:
        log.info('Generating PSD plot.')
        f2, p2 = iq_data.get_pwelch()
        plot_sectrum(f2, p2, iq_data.center, iq_data.span, dbm=True,
                     filename='{}_psd_welch'.format(iq_data.filename_wo_ext))

    if args.spec:
        iq_data.method = 'mtm'
        log.info('Generating spectrogram plot.')
        x, y, z = iq_data.get_spectrogram(iq_data.nframes, iq_data.lframes)
        plot_spectrogram(x, y, z, iq_data.center, cmap=cm.jet, dpi=300, dbm=False,
                         filename='{}_spectrogram'.format(iq_data.filename_wo_ext))

    if args.npy:
        log.info('Saving data dictionary in numpy format.')
        iq_data.save_npy()

    if args.dic:
        log.info('Printing dictionary on the screen.')
        pprint(iq_data.dictionary)

    if args.raw:
        log.info('Converting data to raw.')
        write_signal_as_binary(iq_data.filename_wo_ext + '.bin',
                               iq_data.data_array, iq_data.fs, iq_data.center, write_header=False)
        print('The sampling frequency is: {}'.format(iq_data.fs))

# ----------------------------------------


if __name__ == "__main__":
    main()
