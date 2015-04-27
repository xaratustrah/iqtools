#!/usr/bin/env python

"""
Script for determination of frequency stability and plot.

xaratustra Apr-2015
"""

import os
import argparse
import time
import logging as log

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from iqtools import *


A_SPAN = 1000.0  # double sided analysis span in Hz
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
    plt.ylabel('delta_f/f [Hz]')
    plt.title('Revolution frequency of 142-Pm nuclei during GO2014')
    plt.grid(True)
    log.info('Writing to file: {}.pdf.'.format(os.path.basename(outfile)))
    plt.savefig('{}.pdf'.format(outfile))
    log.info('Done.\n')


def process_data(in_filename, out_filename, f_estimate, save_plot):
    log.info('Processing file: {}.'.format(os.path.basename(in_filename)))
    iq_data = IQData()
    # dummy read one frame to obtain the constants
    _, _ = iq_data.read_tiq(in_filename, 1, 1024, 1)
    center1 = iq_data.center
    datime = iq_data.date_time
    fs1 = iq_data.fs
    log.info('Sampling frequency {} /s.'.format(fs1))
    lframes1 = iq_data.lframes
    f_start = int(TIME_START * fs1 / lframes1)
    # read the real data
    log.info('Starting frame for {} seconds would be {}.'.format(TIME_START, f_start))
    _, _ = iq_data.read_tiq(in_filename, DURATION, 1024, f_start)
    x1 = iq_data.data_array
    f, p = get_pwelch(x1, fs1)

    log.info('Searching peaks {} Hz around {} Hz.'.format(A_SPAN, f_estimate))
    f_centered = shift_to_center(f, center1)
    f_centered_masked, p_masked = zoom_in_freq(f_centered, p, center=f_estimate, span=A_SPAN)

    # np.savetxt('test_p.out', p_masked)

    max_power = get_dbm(p_masked.max())
    if max_power < P_NOISE:
        log.info('No peaks in file: {}. Skipping.\n'.format(os.path.basename(in_filename)))
        # no peaks found, return the previous value
        return f_estimate

    log.info('Signal power in this range: {} dBm.'.format(max_power))

    final_frequency = f_centered_masked[p_masked.argmax()]
    log.info('Peak frequency is: {} Hz'.format(final_frequency))

    log.info('Writing to file: {}.'.format(out_filename))
    tm_format = '%Y-%m-%dT%H:%M:%S'
    tm = time.strptime(datime[:19], tm_format)
    tm_format_number_only = '%Y%m%d%H%M%S'

    if save_plot:
        log.info('Writing a plot of a file on disk.')
        fig = plt.figure()
        ax = fig.gca()
        ax.plot(f_centered, 10 * np.log10(p * 1000), '.')
        ax.plot(final_frequency, max_power, 'rv')
        ax.grid(True)
        plt.draw()
        in_filename_wo_ext = os.path.splitext(os.path.basename(in_filename))[0]
        out_filename_wo_ext = os.path.splitext(os.path.basename(out_filename))[0]
        if not os.path.exists(out_filename_wo_ext):
            os.mkdir(out_filename_wo_ext)
        plt.savefig('{0}/{1}.png'.format(out_filename_wo_ext, in_filename_wo_ext))
        log.info('File {}.png was saved in {}.'.format(in_filename_wo_ext, out_filename_wo_ext))

    with open(out_filename, 'a') as f:
        f.write('{}\t{}\t{}\n'.format(time.mktime(tm), time.strftime(tm_format_number_only, tm), final_frequency))

    log.info('Remembering this frequency for the next time.')
    log.info('Done.\n')

    return final_frequency


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
    parser.add_argument("-s", "--save_plot", help="Save output plot", action="store_true")
    parser.add_argument('-o', '--outfile', nargs='+', help="Output file names")
    parser.add_argument('-f', '--f_estimate', nargs='+', help="Estimated frequency")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', '--infile', nargs='+', help="Data filenames")
    group.add_argument('-p', '--plot', nargs='+', help="Filenames for plotting")

    args = parser.parse_args()

    internal_estimate = 0

    verbose = False
    if args.verbose:
        log.basicConfig(level=log.DEBUG)
        verbose = True

    save_plot = False
    if args.save_plot:
        save_plot = True

    if args.plot:
        get_plot(args.plot[0], args.outfile[0])
    else:
        for i in range(len(args.infile)):
            if internal_estimate == 0:
                log.info('First time call. Using the frequency estimate {} Hz given in the command line.'.format(
                    args.f_estimate[0]))
                internal_estimate = float(args.f_estimate[0])
            log.info(
                'Calculation using frequency estimate {} Hz.'.format(internal_estimate))
            internal_estimate = process_data(args.infile[i], args.outfile[0], internal_estimate, save_plot)
