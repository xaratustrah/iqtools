#!/usr/bin/env python

"""
Script for determination of frequency stability and plot.

xaratustra Apr-2015
"""

import os, argparse, time
import numpy as np
import logging as log
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from iqtools import *


DELTA_F = 600.0  # single sided distance around the expected frequency in Hz
#F_MUST = 244913357.628  # expected frequency of mother ion in Hz
#F_MUST = 244911450.27923584
F_MUST = 244912100
TIME_START = 15  # starting time in seconds
DURATION = 120  # n of frames to read
P_NOISE = -96  # dBm of approximate noise level


def get_plot(infile, outfile):
    log.info('Processing file: {}.'.format(os.path.basename(infile)))
    data = np.genfromtxt(infile)
    data.sort(axis=0)
    first_time = data[0, 0]
    # first_freq = data[0, 1]
    avg = ((data[:, 2]).max() + (data[:, 2]).min()) / 2
    fig = plt.figure()
    plt.gcf().subplots_adjust(bottom=0.16, left=0.16)  # otherwise bottom is cut
    ax = fig.gca()
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2e'))
    ax.plot(data[:, 0] - first_time, (data[:, 2] - avg) / avg, 'r.')
    plt.xlabel('Injection times [s]')
    plt.ylabel('∂f/f [Hz]')
    plt.title('Revolution frequency of 142-Pm nuclei during GO2014')
    plt.grid(True)
    log.info('Writing to file: {}.pdf.'.format(os.path.basename(outfile)))
    plt.savefig('{}.pdf'.format(outfile))
    log.info('Done.')


def process_data(in_filename, out_filename):
    log.info('Processing file: {}.'.format(os.path.basename(in_filename)))
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
    f, p = get_pwelch(x1, fs1)
    # f, v, p = get_fft_50(x1, fs1)

    f_shifted = center1 + f

    lower_bound_freq_cut = np.abs(f_shifted - (F_MUST - DELTA_F)).argmin()
    upper_bound_freq_cut = np.abs(f_shifted - (F_MUST + DELTA_F)).argmin()

    # f_shifted_min = f_shifted.min()
    # f_shifted_max = f_shifted.max()

    f_shifted_cut = f_shifted[lower_bound_freq_cut:upper_bound_freq_cut]
    p_shifted_cut = p[lower_bound_freq_cut:upper_bound_freq_cut]

    max_power = get_dbm(p_shifted_cut.max())
    log.info('Found signal power: {} dBm.'.format(max_power))
    if max_power < P_NOISE:
        log.info('No peaks in file: {}. Skipping.\n'.format(os.path.basename(in_filename)))
        return

    log.info('Writing to file: {}.'.format(out_filename))
    tm_format = '%Y-%m-%dT%H:%M:%S'
    tm = time.strptime(datime[:19], tm_format)
    tm_format_number_only = '%Y%m%d%H%M%S'
    with open(out_filename, 'a') as f:
        f.write('{}\t{}\t{}\n'.format(time.mktime(tm), time.strftime(tm_format_number_only, tm),
                                      f_shifted_cut[p_shifted_cut.argmax()]))
    log.info('Done.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
    parser.add_argument('-o', '--outfile', nargs='+', help="Output file names")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', '--infile', nargs='+', help="Data filenames")
    group.add_argument('-p', '--plot', nargs='+', help="Filenames for plotting")

    args = parser.parse_args()

    if args.verbose:
        log.basicConfig(level=log.DEBUG)
        verbose = True

    if args.plot:
        get_plot(args.plot[0], args.outfile[0])
    else:
        for i in range(len(args.infile)):
            process_data(args.infile[i], args.outfile[0])
