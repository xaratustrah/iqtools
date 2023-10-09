"""
Collection of plotters

Xaratustrah
2017
"""

from .tools import *
from .iqbase import IQBase
from matplotlib.ticker import FormatStrFormatter
from matplotlib.colors import Normalize
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import subprocess
import struct
import os
import matplotlib
matplotlib.use('Agg')


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


def plot_spectrogram(xx, yy, zz, cen=0.0, cmap=cm.jet, dpi=300, dbm=False, filename=None, title='Spectrogram', zzmin=0, zzmax=1e6, mask=False, span=None, xlabel = None, ylabel = None):
    """
    Plot the calculated spectrogram
    :param xx: first dimension
    :param yy: second dimension
    :param zz: third dimension
    :param cen: center frequency
    :param cmap: color map
    :param dbm: if the results should be displayed in dBm scale
    :param title: this will be the title of the plot
    :param filename: if provided, the file will be written on disk
    :zzmin: minimum value for contrast lowest is 0
    :zzmin: maximum value for contrast highest is 1e6
    :return:
    """

    # Apply display threshold if zmin and zmax are provided, they must be different than the default values of 0 and 1e6
    # otherwise ignore them

    if zzmin >= 0 and zzmax <= 1e6 and zzmin < zzmax:
        zz = zz / np.max(zz) * 1e6
        mynorm = Normalize(vmin=zzmin, vmax=zzmax)

        # mask arrays for transparency in pcolormesh
        if mask:
            zz = np.ma.masked_less_equal(zz, zzmin)

    else:
        # pcolormesh ignores if norm is None
        mynorm = None

    if dbm:
        zz = IQBase.get_dbm(zz)

    # here comes span in [Hz]
    if not span:
        spanmask = (xx[0, :] != 0) | (xx[0, :] == 0)
    else:
        spanmask = (xx[0, :] <= span / 2) & (xx[0, :] >= -span / 2)

    sp = plt.pcolormesh(xx[:, spanmask], yy[:, spanmask],
                        zz[:, spanmask], cmap=cmap, norm=mynorm, shading='auto')
    cb = plt.colorbar(sp)

    ax = plt.gca()
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.0e'))

    delta_f = np.abs(np.abs(xx[0, 1]) - np.abs(xx[0, 0]))
    delta_t = np.abs(np.abs(yy[1, 0]) - np.abs(yy[0, 0]))
    
    if xlabel:
        plt.xlabel(xlabel)
    else:
        plt.xlabel(
        r"$\Delta f$ @ {} (resolution = {})".format(get_eng_notation(cen, unit='Hz'), get_eng_notation(delta_f, unit='Hz')))
    if ylabel:
        plt.ylabel(ylabel)
    else:
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
        spanmask = (f != 0) | (f == 0)
    else:
        spanmask = (f <= span / 2) & (f >= -span / 2)
    if dbm:
        plt.plot(f[spanmask], IQBase.get_dbm(p[spanmask]))
    else:
        plt.plot(f[spanmask], p[spanmask])

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
        iq_data = CSVData(filename)

    if file_extension.lower() == '.bin':
        log.info('This is a raw binary file.')
        iq_data = BINData(filename)

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
