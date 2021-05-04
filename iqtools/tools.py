"""
Collection of tools

Xaratustrah
2017
"""

import os
import logging as log
from scipy.signal import hilbert
import xml.etree.ElementTree as et
import numpy as np

import types
import uproot3
import uproot3_methods.classes.TH1

from iqtools.iqbase import IQBase
from iqtools.tcapdata import TCAPData
from iqtools.tdmsdata import TDMSData
from iqtools.rawdata import RAWData
from iqtools.iqtdata import IQTData
from iqtools.tiqdata import TIQData
from iqtools.asciidata import ASCIIData
from iqtools.wavdata import WAVData
from iqtools.xdatdata import XDATData


# ------------ TOOLS ----------------------------
def get_iq_object(filename, header_filename=None):
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


def get_eng_notation(value, unit='', decimal_place=2):
    """
    Convert numbers to scientific notation
    Parameters
    ----------
    value input number float or integer
    decimal_place How many decimal places should be left
    unit The unit will be shown, otherwise powers of ten

    Returns
    -------

    """
    ref = {24: 'Y', 21: 'Z', 18: 'E', 15: 'P',
           12: 'T', 9: 'G', 6: 'M', 3: 'k', 0: '',
           -3: 'm', -6: 'u', -9: 'n', -12: 'p',
           -15: 'f', -18: 'a', -21: 'z', -24: 'y',
           }
    if value == 0:
        return '{}{}'.format(0, unit)
    flag = '-' if value < 0 else ''
    num = max([key for key in ref.keys() if abs(value) >= 10 ** key])
    if num == 0:
        mult = ''
    else:
        mult = ref[num] if unit else 'e{}'.format(num)
    return '{}{}{}{}'.format(flag, int(abs(value) / 10 ** num * 10 ** decimal_place) / 10 ** decimal_place, mult,
                             unit)


def make_test_signal(f, fs, length=1, nharm=0, noise=False):
    """Make a sine signal with/without noise."""

    t = np.arange(0, length, 1 / fs)
    x = np.zeros(len(t))
    for i in range(nharm + 2):
        x += np.sin(2 * np.pi * i * f * t)

    if noise:
        x += np.random.normal(0, 1, len(t))
    return t, x


def shift_phase(x, phase):
    """
    Shift phase in frequency domain
    x: complex or analytical signal
    phase: amount in radians

    returns: shifted complex signal
    """

    XX = np.fft.fft(x)
    angle = np.unwrap(np.angle(XX)) + phase
    YY = np.abs(XX) * np.exp(1j * angle)
    return np.fft.ifft(YY)


def write_signal_as_binary(filename, x, fs, center, write_header=False):
    """
    filename: name of the output filename
    x: data vector to write to filename
    fs: sampling Frequency
    center: center Frequency
    write_header: if set to true, then the first 4 bytes of the file are 32-bit
    sampling Frequency and then follows the center frequency also in 32-bit. the
    Data follows afterwards in I, Q format each 32-bit as well.
    """
    # 32-bit little endian floats
    # insert header
    if write_header:
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
    Read special format CSV result file from RSA5000 series output
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


def read_specan_xml(filename):
    """
    Read the resulting saved trace file Specan from the Tektronix RSA5000 series
    these files are produced while saving traces.
    :param filename:
    :return:
    """
    with open(filename, 'rb') as f:
        ba = f.read()
    xml_tree_root = et.fromstring(ba)
    for elem in xml_tree_root.iter(tag='Count'):
        count = int(elem.text)
    for elem in xml_tree_root.iter(tag='XStart'):
        start = float(elem.text)
    for elem in xml_tree_root.iter(tag='XStop'):
        stop = float(elem.text)
    for elem in xml_tree_root.iter(tag='XUnits'):
        xunits = elem.text
    for elem in xml_tree_root.iter(tag='YUnits'):
        yunits = elem.text
    for elem in xml_tree_root.iter(tag='y'):
        pwr = float(elem.text)
    p = np.zeros(count)
    i = 0
    for elem in xml_tree_root.iter(tag='y'):
        p[i] = float(elem.text)
        i += 1
    f = np.linspace(start, stop, count)

    return f, p, (xunits, yunits)


def read_data_csv(filename):
    """
    Read special format CSV data file from RSA5100 series output.
    Please note that 50 ohm power termination is already considered
    for these data.
    :param filename:
    :return:
    """
    data = np.genfromtxt(filename, skip_header=10, delimiter=",")
    # has one dimension more, should use ravel
    data = np.ravel(data).view(dtype='c16')
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


def write_spectrum_to_csv(ff, pp, filename, center=0):
    a = np.concatenate(
        (ff, pp, IQBase.get_dbm(pp)))
    b = np.reshape(a, (3, -1)).T
    np.savetxt(filename, b, header='Delta f [Hz] @ {:.2e} [Hz]|Power [W]|Power [dBm]'.format(
        center), delimiter='|')


def write_spectrum_to_root(ff, pp, filename, center=0, title=''):
    class MyTH1(uproot3_methods.classes.TH1.Methods, list):
        def __init__(self, low, high, values, title=""):
            self._fXaxis = types.SimpleNamespace()
            self._fXaxis._fNbins = len(values)
            self._fXaxis._fXmin = low
            self._fXaxis._fXmax = high
            values.insert(0, 0)
            values.append(0)
            for x in values:
                self.append(float(x))
            self._fTitle = title
            self._classname = "TH1F"

    th1f = MyTH1(center + ff[0], center + ff[-1], pp.tolist(), title=title)
    file = uproot3.recreate(filename + '.root', compression=uproot3.ZLIB(4))
    file["th1f"] = th1f
