#!/usr/bin/env python3.4

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

DELTA_F = 1000.0
F_MUST = 244911450.27923584
START = 1000
P_THRESH = 1e8


def main(in_filename, out_filename):
    dic1, _ = read_tiq(in_filename, 100, 1024, START)
    center1 = dic1['center']
    datime = dic1['DateTime']
    fs1 = dic1['fs']
    x1 = dic1['data']
    # f, p = get_pwelch(x1, fs1)
    f, v, p = get_fft_50(x1, fs1)

    if p.max() / p.min() < P_THRESH:
        print('No peaks in file {}. Ratio is {}.\n'.format(in_filename, p.max() / p.min()))
        return

    # F_MUST = f_shifted[p.argmax()]
    f_shifted = center1 + f

    f_shifted_cut = f_shifted[
                    np.abs(f_shifted - (F_MUST - DELTA_F)).argmin():np.abs(f_shifted - (F_MUST + DELTA_F)).argmin()]
    p_shifted_cut = p[np.abs(f_shifted - (F_MUST - DELTA_F)).argmin():np.abs(f_shifted - (F_MUST + DELTA_F)).argmin()]

    with open(out_filename, 'a') as f:
        f.write('{}\t{}\n'.format(datime[5:10], f_shifted_cut[p_shifted_cut.argmax()]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("in_filename", type=str, help="Name of the input file.")
    parser.add_argument("out_filename", type=str, help="Name of the output file.")
    args = parser.parse_args()
    main(args.in_filename, args.out_filename)
