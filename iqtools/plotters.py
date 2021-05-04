"""
Collection of plotters

Xaratustrah
2017
"""

import subprocess
import struct
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.ticker import FormatStrFormatter
from iqtools.iqbase import IQBase
from iqtools.tools import *


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
    plt.plot(yy[:, 0], IQBase.get_dbm(frame_power))
    plt.ylabel('Power [dBm]')
    plt.xlabel('Time [sec]')
    plt.title('Frame power')


def plot_spectrogram(xx, yy, zz, cen=0.0, cmap=cm.jet, dpi=300, dbm=False, filename=None, title='Spectrogram'):
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
    if dbm:
        sp = plt.pcolormesh(xx, yy, IQBase.get_dbm(zz), cmap=cmap)
    else:
        sp = plt.pcolormesh(xx, yy, zz, cmap=cmap, shading='auto')
    cb = plt.colorbar(sp)

    ax = plt.gca()
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.0e'))

    plt.xlabel(
        "Delta f @ {} (resolution = {})".format(get_eng_notation(cen, unit='Hz'), get_eng_notation(delta_f, unit='Hz')))
    plt.ylabel('Time [sec] (resolution = {})'.format(
        get_eng_notation(delta_t, 's')))
    plt.title(title)
    if dbm:
        cb.set_label('Power Spectral Density [dBm/Hz]')
    else:
        cb.set_label('Power Spectral Density')

    if filename is not None:
        plt.savefig(filename + '.png', dpi=dpi, bbox_inches='tight')
        plt.close()


def plot_spectrum(f, p, cen=0.0, span=None, dbm=False, filename=None, title='Spectrum'):
    """Plot average power in dBm per Hz"""

    if not span:
        mask = (f != 0) | (f == 0)
    else:
        mask = (f <= span / 2) & (f >= -span / 2)
    if dbm:
        plt.plot(f[mask], IQBase.get_dbm(p[mask]))
    else:
        plt.plot(f[mask], p[mask])

    ax = plt.gca()
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.0e'))

    plt.xlabel("Delta f [Hz] @ {}".format(get_eng_notation(cen, 'Hz')))
    plt.title(title)
    if dbm:
        plt.ylabel('Power Spectral Density [dBm/Hz]')
    else:
        plt.ylabel('Power Spectral Density')

    plt.grid(True)
    if filename is not None:
        plt.savefig(filename + '.png')  # , bbox_inches='tight')
        plt.close()


def plot_spectrogram_with_gnuplot(zz):
    """
    zz: reshaped data in form of a matrix for plotting

    based on https://stackoverflow.com/a/15885230/5177935

    """
    temp_file = 'foo.bin'
    with open(temp_file, 'wb') as foo:
        for (i, j), dat in np.ndenumerate(np.rot90(zz, 3)):
            s = struct.pack('4f', i, j, dat, dat)
            foo.write(s)

    gnuplot = subprocess.Popen(
        ['gnuplot'], stdin=subprocess.PIPE, universal_newlines=True)

    gnuplot.stdin.write("""
    set pm3d map;
    unset clabel;
    set terminal png size 1024,768;
    set palette defined (0 0.0 0.0 0.5, \
                         1 0.0 0.0 1.0, \
                         2 0.0 0.5 1.0, \
                         3 0.0 1.0 1.0, \
                         4 0.5 1.0 0.5, \
                         5 1.0 1.0 0.0, \
                         6 1.0 0.5 0.0, \
                         7 1.0 0.0 0.0, \
                         8 0.5 0.0 0.0 );
    """)
    gnuplot.stdin.write("set output '{}.png';".format(temp_file))
    gnuplot.stdin.write(
        "splot '{}' binary record=(10,-1) format='%float' u 1:2:3:4 w pm3d;".format(temp_file))
    # the following command needs terminating the process
    # os.remove(temp_file)


def plot_phase_shift(x, phase):
    """
    Plots the signal before and after the phase shift
    """
    plt.rcParams['axes.grid'] = True
    fig, axs = plt.subplots(2, 2, sharex=True, sharey=True)
    axs[0, 0].plot(np.real(x))
    axs[0, 1].plot(np.imag(x))
    axs[1, 0].plot(np.real(shift_phase(x, phase)))
    axs[1, 1].plot(np.imag(shift_phase(x, phase)))


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

    if file_extension.lower() == '.xdat':
        log.info('This is a XDAT file.')
        if not header_filename:
            log.info('XDAT files need a text header file as well. Aborting....')
            return None
        else:
            iq_data = XDATData(filename, header_filename)

    return iq_data
