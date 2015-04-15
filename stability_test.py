#!/usr/bin/env python

"""
Script for determination of frequency stability.

xaratustra Apr-2015

usage:

find ./ -iname '*.TIQ' -exec ./freq_stabil.py {} ./graph.txt \;

then plot graph.txt
"""

import numpy as np
import os, argparse
from iqtools import *
import logging as log
import time


DELTA_F = 600.0  # single sided distance around the expected frequency in Hz
F_MUST = 244911450.27923584  # expected frequency of mother ion in Hz
TIME_START = 15  # starting time in seconds
DURATION = 120  # n of frames to read
P_THRESH = 1e8  # linear power threshold between noise and a signal


def main(in_filename, out_filename):
    # dummy read one frame to obtain the constants
    dic1, _ = read_tiq(in_filename, 1, 1024, 1)
    center1 = dic1['center']
    datime = dic1['DateTime']
    fs1 = dic1['fs']
    lframes1 = dic1['lframes']
    f_start = int(TIME_START * fs1 / lframes1)
    # read the real data
    log.info('Starting frame for {} seconds would be {}.'.format(TIME_START, f_start))
    dic1, _ = read_tiq(in_filename, DURATION, 1024, f_start)
    x1 = dic1['data']
    # f, p = get_pwelch(x1, fs1)
    f, v, p = get_fft_50(x1, fs1)

    if p.max() / p.min() < P_THRESH:
        log.info('No peaks in file {}, since the ratio is {} which is smaller than {}. Skipping.\n'.format(
            os.path.basename(in_filename), p.max() / p.min(), P_THRESH))
        return

    log.info('Processing file {}.\n'.format(os.path.basename(in_filename)))

    # F_MUST = f_shifted[p.argmax()]
    f_shifted = center1 + f

    f_shifted_cut = f_shifted[
                    np.abs(f_shifted - (F_MUST - DELTA_F)).argmin():np.abs(f_shifted - (F_MUST + DELTA_F)).argmin()]
    p_shifted_cut = p[np.abs(f_shifted - (F_MUST - DELTA_F)).argmin():np.abs(f_shifted - (F_MUST + DELTA_F)).argmin()]

    tm_format = '%Y-%m-%dT%H:%M:%S'
    tm = time.strptime(datime[:19], tm_format)
    tm_format_number_only = '%Y%m%d%H%M%S'
    with open(out_filename, 'a') as f:
        f.write('{}\t{}\t{}\n'.format(time.mktime(tm), time.strftime(tm_format_number_only, tm),
                                      f_shifted_cut[p_shifted_cut.argmax()]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("in_filename", type=str, help="Name of the input file.")
    parser.add_argument("out_filename", type=str, help="Name of the output file.")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
    args = parser.parse_args()
    if args.verbose:
        log.basicConfig(level=log.DEBUG)
        verbose = True

    main(args.in_filename, args.out_filename)
