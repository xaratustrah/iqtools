"""
Collection of plotters

Xaratustrah
2017
"""

import matplotlib.pyplot as plt
import matplotlib.cm as cm
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


def plot_spectrogram_dbm(xx, yy, zz, cen=0.0, filename='', to_file=False, cmap=cm.jet):
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
    sp = plt.pcolormesh(xx, yy, IQBase.get_dbm(zz), cmap=cmap)
    cb = plt.colorbar(sp)
    plt.xlabel(
        "Delta f @ {} (resolution = {})".format(get_eng_notation(cen, unit='Hz'), get_eng_notation(delta_f, unit='Hz')))
    plt.ylabel('Time [sec] (resolution = {})'.format(get_eng_notation(delta_t, 's')))
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

    plt.plot(f[mask], IQBase.get_dbm(p[mask]))
    plt.xlabel("Delta f [Hz] @ {}".format(get_eng_notation(cen, 'Hz')))
    plt.title(filename)
    plt.ylabel("Power Spectral Density [dBm/Hz]")
    plt.grid(True)
    if to_file:
        plt.savefig(filename)
        plt.close()


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
