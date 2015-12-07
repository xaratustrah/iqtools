#!/usr/bin/env python
"""
Collection of tools for dealing with IQ data. This code converts data in TIQ
format and extracts the data in numpy format

xaratustrah oct-2014
            mar-2015
            aug-2015
"""

import argparse, os
from pprint import pprint

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import logging as log
from scipy.signal import hilbert
from iqdata import IQData

# ------------ TOOLS ----------------------------

def make_test_signal(f, fs, length=1, nharm=0, noise=False):
    """Make a sine signal with/without noise."""

    t = np.arange(0, length, 1 / fs)
    x = np.zeros(len(t))
    for i in range(nharm + 2):
        x += np.sin(2 * np.pi * i * f * t)

    if noise:
        x += np.random.normal(0, 1, len(t))
    return t, x


def write_signal_as_binary(filename, x, fs, center):
    # 32-bit little endian floats
    # insert header
    x = np.insert(x, 0, complex(fs, center))
    x = x.astype(np.complex64)
    x.tofile(filename)


def write_signal_as_ascii(filename, x, fs, center):
    # insert ascii header which looks like a complex number
    x = np.insert(x, 0, complex(fs, center))
    with open(filename, 'w') as f:
        for i in range(len(x)):
            f.write('{}\t{}\n'.format(np.real(x[i]), np.imag(x[i])))


def make_analytical(x):
    """Make an analytical signal from the real signal"""

    yy = hilbert(x)
    ii = np.real(yy)
    qq = np.imag(yy)
    x_bar = np.vectorize(complex)(ii, qq)
    ins_ph = np.angle(x_bar) * 180 / np.pi
    return x_bar, ins_ph


def read_result_csv(filename):
    """
    Read special format CSV result file from RSA5100 series output
    :param filename:
    :return:
    """
    p = np.genfromtxt(filename, skip_header=63)
    with open(filename) as f:
        cont = f.readlines()
    for l in cont:
        l = l.split(',')
        if 'Frequency' in l and len(l) == 3:
            center = float(l[1])
        if 'XStart' in l and len(l) == 3:
            start = float(l[1])
        if 'XStop' in l and len(l) == 3:
            stop = float(l[1])
    f = np.linspace(start - center, stop - center, len(p))
    return f, p


def read_data_csv(filename):
    """
    Read special format CSV data file from RSA5100 series output.
    Please note that 50 ohm power termination is already considered
    for these data.
    :param filename:
    :return:
    """
    data = np.genfromtxt(filename, skip_header=10, delimiter=",")
    data = np.ravel(data).view(dtype='c16')  # has one dimension more, should use ravel
    return data

def parse_filename(filename):
    """
    Parses filenames of experimental data in the following format:
    58Ni26+_374MeVu_250uA_pos_0_0.tiq
    :param filename:
    :return:
    """
    filename = filename.split('_')
    descr = filename[0]
    energy = float(filename[1].replace('MeVu', 'e6'))
    current = float(filename[2].replace('uA', 'e-6'))
    return descr, energy, current

# ------------ PLOTTERS ----------------------------

def plot_hilbert(x_bar):
    """Show Hilbert plot."""

    plt.plot(np.real(x_bar), np.imag(x_bar))
    plt.grid(True)
    plt.xlabel('Real Part')
    plt.ylabel('Imag. Part')


def plot_frame_power(yy, frame_power):
    """
    Plot frame power, i.e. trapezoid along each time frame
    :param yy:
    :param frame_power:
    :return:
    """
    plt.plot(yy[:, 0], IQData.get_dbm(frame_power))
    plt.ylabel('Power [dBm]')
    plt.xlabel('Time [sec]')
    plt.title('Frame power')


def plot_spectrogram_dbm(xx, yy, zz, cen=0.0, filename='', to_file=False):
    """
    Plot the calculated spectrogram
    :param xx:
    :param yy:
    :param zz:
    :param cen:
    :return:
    """
    delta_f = np.abs(np.abs(xx[0, 1]) - np.abs(xx[0, 0]))
    delta_t = np.abs(np.abs(yy[1, 0]) - np.abs(yy[0, 0]))
    sp = plt.pcolormesh(xx, yy, IQData.get_dbm(zz), cmap=cm.jet)
    cb = plt.colorbar(sp)
    plt.xlabel("Delta f [Hz] @ {} [Hz] (resolution = {:.2e} [Hz])".format(cen, delta_f))
    plt.ylabel('Time [sec] (resolution = {:.2e} [s])'.format(delta_t))
    plt.title('Spectrogram')
    cb.set_label('Power Spectral Density [dBm/Hz]')
    if to_file:
        plt.savefig(filename + '.png')


def plot_dbm_per_hz(f, p, cen=0.0, span=None, filename='', to_file=False):
    """Plot average power in dBm per Hz"""

    if not span:
        mask = (f != 0) | (f == 0)
    else:
        mask = (f <= span / 2) & (f >= -span / 2)
    plt.plot(f[mask], 10 * np.log10(p[mask] * 1000))
    plt.xlabel("Delta f [Hz] @ {} [Hz]".format(cen))
    plt.title(filename)
    plt.ylabel("Power Spectral Density [dBm/Hz]")
    plt.grid(True)
    if to_file:
        plt.savefig(filename + '.pdf')

# ------------ MAIN ----------------------------

verbose = False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, help="Name of the input file.")
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
    parser.add_argument("-x", "--xml", help="Write XML header to file.", action="store_true")
    parser.add_argument("-y", "--npy", help="Write dic to NPY file.", action="store_true")

    args = parser.parse_args()
    if args.verbose:
        log.basicConfig(level=log.DEBUG)
        verbose = True

    log.info("File {} passed for processing.".format(args.filename))

    iq_data = IQData(args.filename)
    _, file_extension = os.path.splitext(args.filename)

    if file_extension.lower() == '.txt' or file_extension.lower() == '.csv':
        log.info('This is an ASCII file.')
        iq_data.read_ascii(args.nframes, args.lframes, args.sframes)

    if file_extension.lower() == '.bin':
        log.info('This is a raw binary file.')
        iq_data.read_bin(args.nframes, args.lframes, args.sframes)

    if file_extension.lower() == '.iqt':
        log.info('This is an iqt file.')
        iq_data.read_iqt(args.nframes, args.lframes, args.sframes)

    if file_extension.lower() == '.iq':
        log.info('This is an iq file.')
        iq_data.read_iq(args.nframes, args.lframes, args.sframes)

    if file_extension.lower() == '.tiq':
        log.info('This is a tiq file.')
        iq_data.read_tiq(args.nframes, args.lframes, args.sframes)

    if file_extension.lower() == '.wav':
        log.info('This is a wav file.')
        iq_data.read_wav(args.nframes, args.lframes, args.sframes)

    if file_extension.lower() == '.tdms':
        log.info('This is a TDMS file.')
        iq_data.read_tdms_information(args.lframes)
        iq_data.read_tdms(args.nframes, args.lframes, args.sframes)

    if args.fft:
        log.info('Generating FFT plot.')
        f1, v1, p1 = iq_data.get_fft_50_ohm()
        plot_dbm_per_hz(f1, p1, iq_data.center, iq_data.span, iq_data.filename_wo_ext + '_psd_fft', True)

    if args.psd:
        log.info('Generating PSD plot.')
        f2, p2 = iq_data.get_pwelch()
        plot_dbm_per_hz(f2, p2, iq_data.center, iq_data.span, iq_data.filename_wo_ext + '_psd_welch', True)

    if args.spec:
        log.info('Generating spectrogram plot.')
        f2, p2 = iq_data.get_pwelch()
        x, y, z = iq_data.get_spectrogram()
        plot_spectrogram_dbm(x, y, z, iq_data.center, iq_data.filename_wo_ext + '_spectrogram', True)

    if args.xml:
        log.info('Saving header into xml file.')
        iq_data.save_header()

    if args.npy:
        log.info('Saving data dictionary in numpy format.')
        iq_data.save_data()

    if args.dic:
        log.info('Printing dictionary on the screen.')
        pprint(iq_data.dictionary)
