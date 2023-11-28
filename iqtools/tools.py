"""
Collection of tools for the iqtools library

xaratustrah@github 2017
"""

import os
import logging as log
from scipy.signal import hilbert
from scipy.io import wavfile
import xml.etree.ElementTree as et
import numpy as np
import nibabel as nib
from bs4 import BeautifulSoup


import types
import uproot3
import uproot3_methods.classes.TH1

from .iqbase import IQBase
from .tcapdata import TCAPData
from .tdmsdata import TDMSData
from .bindata import BINData
from .iqtdata import IQTData
from .tiqdata import TIQData
from .csvdata import CSVData
from .wavdata import WAVData
from .xdatdata import XDATData
from .r3fdata import R3FData


# ------------ TOOLS ----------------------------

# ----------------------------
# general functions


def get_iq_object(filename, header_filename=None):
    """Return suitable object accorting to extension.

    Args:
        filename (str): File name
        header_filename (str, optional): Name of header file. Defaults to None.

    Returns:
        (iqbase): A derivative of a the iqbase class
    """    
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

    if file_extension.lower() == '.r3f':
        log.info('This is a R3F file.')
        iq_data = R3FData(filename)

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
    """Convert numbers to scientific notation

    Args:
        value (_type_): Input numher float or integer
        unit (str, optional): String showing the unit. Defaults to ''.
        decimal_place (int, optional): How many decimal places should be left
    unit The unit will be shown, otherwise powers of ten. Defaults to 2.

    Returns:
        (string): Formatted string of engineering notation
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
    """Make a sine signal with/without noise.

    Args:
        f (float): Desired signal frequency
        fs (float): Desired sampling frequency
        length (int, optional): Length in seconds. Defaults to 1.
        nharm (int, optional): No. of harmonics. Defaults to 0.
        noise (bool, optional): Add noise. Defaults to False.

    Returns:
        (tuple): tuple of ndarrays, time and frequency
    """    

    t = np.arange(0, length, 1 / fs)
    x = np.zeros(len(t))
    for i in range(nharm + 2):
        x += np.sin(2 * np.pi * i * f * t)

    if noise:
        x += np.random.normal(0, 1, len(t))
    return t, x


def shift_phase(x, phase):
    """Shift phase in frequency domain

    Args:
        x (ndarray): Complex or analytical signal
        phase (ndarray): Desired phase shift

    Returns:
        (ndarray): Shifted complex signal
    """    
    XX = np.fft.fft(x)
    angle = np.unwrap(np.angle(XX)) + phase
    YY = np.abs(XX) * np.exp(1j * angle)
    return np.fft.ifft(YY)


# ----------------------------
# functions related to spectrograms

def get_cplx_spectrogram(x, nframes, lframes):
    """Make a 2D FFT of complex valued data array

    Args:
        x (ndarray): Data array
        nframes (int, optional): Number of frames.
        lframes (int, optional): Length of each frame.

    Returns:
        (ndarray): Power meshgrid
    """    
    sig = np.reshape(x, (nframes, lframes))
    zz = np.fft.fft(sig, axis=1)
    return zz


def get_inv_cplx_spectrogram(zz, nframes, lframes):
    """Make an inverse 2D FFT of complex valued data array

    Args:
        zz (ndarray): Power meshgrid
        nframes (int, optional): Number of frames.
        lframes (int, optional): Length of each frame.

    Returns:
        (ndarray): Data array
    """    

    inv_zz = np.fft.ifft(zz, axis=1)
    inv_zz = np.reshape(inv_zz, (1, nframes * lframes))[0]
    return inv_zz


def get_concat_spectrogram(x1, y1, z1, x2, y2, z2, delta_y=None):
    """Concatenate two spectrograms

    Args:
        x1 (ndarray): Frequency meshgrid
        y1 (ndarray): Time meshgrid
        z1 (ndarray): Power meshgrid
        x2 (ndarray): Frequency meshgrid
        y2 (ndarray): Time meshgrid
        z2 (ndarray): Power meshgrid
        delta_y (int, optional): Start offset. Defaults to None.

    Returns:
        (tuple): Tuple of meshgrids
    """    
    if not delta_y:
        delta_y = y1[-1, 0] - y1[0, 0]
    return np.concatenate((x1, x2), axis=0), np.concatenate((y1, y2 + delta_y), axis=0), np.concatenate((z1, z2), axis=0)


def get_cut_spectrogram(xx, yy, zz, xcen=None, xspan=None, ycen=None, yspan=None, invert=False):
    """Show a section of the spectrogram.
    Here a section will be shown, either positive or negative, but a new meshgrid will be created.
    the positive version, i.e. invert = False, is similar to the get_zoomed_spectrogram functions
    with the difference that the mesh will be created anew.
    
    Args:
        xx (ndarray): Frequency meshgrid
        yy (ndarray): Time meshgrid
        zz (ndarray): Power meshgrid
        xcen (_type_, optional): Center in frequency. Defaults to None.
        xspan (_type_, optional): Frequency window. Defaults to None.
        ycen (_type_, optional): Center in time. Defaults to None.
        yspan (_type_, optional): Time window. Defaults to None.
        invert (bool, optional): Inverted section. Defaults to False.

    Returns:
        (tuple): Tuple of meshgrids
    """    

    if not xspan:
        xspanmask = (xx[0, :] != 0) | (xx[0, :] == 0)
    else:
        xspanmask = (xx[0, :] <= xcen + xspan /
                     2) & (xx[0, :] >= xcen - xspan / 2)

    if not yspan:
        yspanmask = (yy[:, 0] != 0) | (yy[:, 0] == 0)
    else:
        yspanmask = (yy[:, 0] <= ycen + yspan /
                     2) & (yy[:, 0] >= ycen - yspan / 2)

    if invert:
        xspanmask = np.invert(xspanmask)
        yspanmask = np.invert(yspanmask)

    # for clarification: this is how to use to masks after each other
    newz = zz[yspanmask][:, xspanmask]

    # need to create a new meshgrid due to cut, otherwise new data won't fit old mesh
    newx, newy = np.meshgrid(
        np.arange(np.shape(newz)[1]), np.arange(np.shape(newz)[0]))

    if np.shape(yy)[0] == 1:
        delta_y = 0
    else:
        delta_y = yy[1, 0] - yy[0, 0]
    newy = newy * delta_y
    delta_x = xx[0, 1] - xx[0, 0]
    newx = newx - newx[-1, -1] / 2
    newx = newx * delta_x

    return newx, newy, newz


def get_zoomed_spectrogram(xx, yy, zz, xcen=None, xspan=None, ycen=None, yspan=None):
    """Zoom into a section of the spectrogram

    Args:
        xx (ndarray): Frequency meshgrid
        yy (ndarray): Time meshgrid
        zz (ndarray): Power meshgrid
        xcen (_type_, optional): Center in frequency. Defaults to None.
        xspan (_type_, optional): Frequency window. Defaults to None.
        ycen (_type_, optional): Center in time. Defaults to None.
        yspan (_type_, optional): Time window. Defaults to None.

    Returns:
        (tuple): Tuple of meshgrids
    """    

    if not xspan:
        xspanmask = (xx[0, :] != 0) | (xx[0, :] == 0)
    else:
        xspanmask = (xx[0, :] <= xcen + xspan /
                     2) & (xx[0, :] >= xcen - xspan / 2)

    if not yspan:
        yspanmask = (yy[:, 0] != 0) | (yy[:, 0] == 0)
    else:
        yspanmask = (yy[:, 0] <= ycen + yspan /
                     2) & (yy[:, 0] >= ycen - yspan / 2)

    # based on https://github.com/numpy/numpy/issues/13255#issuecomment-479529731
    return xx[yspanmask][:, xspanmask], yy[yspanmask][:, xspanmask], zz[yspanmask][:, xspanmask]


def get_averaged_spectrogram(xa, ya, za, every):
    """Averages a spectrogram in time, given every such frames in n_time_frames
    example:
        
    * a spectrogram with 100 frames in time each 1024 bins in frequency will be averaged every 5 frames in time bin by bin, resulting in a new spectrogram
    with only 20 frames and same frame length as original.

    Args:
        xx (ndarray): Frequency meshgrid
        yy (ndarray): Time meshgrid
        zz (ndarray): Power meshgrid
        every (int): Averaging step

    Returns:
        (tuple): Tuple of meshgrids

    """    
    rows, cols = np.shape(za)
    dim3 = int(rows / every)

    # This is such an ndarray gymnastics I think I would never be
    # able to figure out ever again how I managed it,
    # but it works fine!

    zz = np.reshape(za, (dim3, every, cols))
    zz = np.average(zz, axis=1)

    yy = np.reshape(ya, (dim3, every, cols))
    yy = np.reshape(yy[:, every - 1, :].flatten(), (dim3, cols))

    return xa[:dim3], yy, zz

def get_cooled_spectrogram(xx, yy, zz, yy_idx, fill_with=0):
    """Software cool the spectrogram. Shifts rows to match the maximum of the selected time frame.
    After cooling / shifting, the frequency axis will have useless information. so it is left as just numbers.

    Args:
        xx (ndarray): Frequency meshgrid
        yy (ndarray): Time meshgrid
        zz (ndarray): Power meshgrid
        yy_idx (int): Selected time frame for searching the maximum
        fill_with (int, optional): Fill with this instead of zeros. Defaults to 0.

    Returns:
        (tuple): Tuple of meshgrids
    """    

    # make sure fill_with does not exceed the maximum in the row
    
    b = np.argmax(zz[yy_idx])
    z = np.ones((np.shape(zz)[0],b)) * fill_with
    w = np.concatenate((zz.T, z.T)).T
    newarr = np.zeros(np.shape(w))
    ii = 0
    # calculate distance and subtract in each row
    for row in w:
        diff =np.argmax(row) - b 
        newarr[ii] = np.roll(row, - diff)
        ii+=1
    
    xc, yc = np.meshgrid(np.arange(np.shape(newarr)[1]), np.arange(np.shape(newarr)[0]))
    # use the same time axis
    delta_y = yy[1][0] - yy[0][0]

    # 
    
    return xc, yc * delta_y, newarr    

# -----------------------------------------#
# functions related to input and output


def write_signal_to_bin(cx, filename, fs=1, center=0, write_header=True):
    """Write complex valued signal to raw binary file
    If write header is set to true, then the first 4 bytes of the file are 32-bit
    sampling Frequency and then follows the center frequency also in 32-bit. the
    Data follows afterwards in I, Q format each 32-bit as well.
    
    Args:
        cx (ndarray): Complex valued data array
        filename (string): File name
        fs (int, optional): Sampling frequency. Defaults to 1.
        center (int, optional): Center frequency. Defaults to 0.
        write_header (bool, optional): Whether the header should be written or not. Defaults to True.
    """    
    # 32-bit little endian floats
    # insert header
    if write_header:
        cx = np.insert(cx, 0, complex(fs, center))
    cx = cx.astype(np.complex64)
    cx.tofile(filename + '.bin')


def write_signal_to_csv(cx, filename, fs=1, center=0, delimiter='|'):
    """Write complex valued signal to CSV text file
    
    Args:
        cx (ndarray): Complex valued data array
        filename (string): File name
        fs (int, optional): Sampling frequency. Defaults to 1.
        center (int, optional): Center frequency. Defaults to 0.
    """    
    # insert ascii header which looks like a complex number
    cx = np.insert(cx, 0, complex(fs, center))
    with open(filename + '.csv', 'w') as f:
        for i in range(len(cx)):
            f.write('{}{}{}\n'.format(
                np.real(cx[i]), delimiter, np.imag(cx[i])))


def write_signal_to_wav(cx, filename, fs=1):
    """Write complex valued signal as audio WAV file
    
    Args:
        cx (ndarray): Complex valued data array
        filename (string): File name
        fs (int, optional): Sampling frequency. Defaults to 1.
    """    
    wavfile.write(filename + '.wav', fs,
                  abs(cx) / max(abs(cx)))


def make_analytical(x):
    """Makes an analytical signal using Hilbert transformation

    Args:
        x (ndarray): Real valued data array

    Returns:
        (ndarray): Complex valued data array
    """    

    yy = hilbert(x)
    ii = np.real(yy)
    qq = np.imag(yy)
    x_bar = np.vectorize(complex)(ii, qq)
    ins_ph = np.angle(x_bar) * 180 / np.pi
    return x_bar, ins_ph


def read_rsa_result_csv(filename):
    """Read special format CSV result file from RSA5000 series output

    Args:
        filename (string): File name

    Returns:
        (tuple): Arrays of frequency and power
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


def read_rsa_specan_xml(filename):
    """Read the resulting saved trace file Specan from the Tektronix RSA5000 series
    these files are produced while saving traces.

    Args:
        filename (string): File name

    Returns:
        (tuple): Arrays of frequency, power, and values of units
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
    """Read special format CSV data file from RSA5100 series output.
    Please note that 50 ohm power termination is already considered
    for these data.

    Args:
        filename (string): File name

    Returns:
        (ndarray): ndarray of data
    """    
    data = np.genfromtxt(filename, skip_header=10, delimiter=",")
    # has one dimension more, should use ravel
    data = np.ravel(data).view(dtype='c16')
    return data


def parse_filename(filename):
    """Parses filenames of experimental data in the following format:
    
        58Ni26+_374MeVu_250uA_pos_0_0.tiq

    Args:
        filename (string): File name

    Returns:
        (tuple): Tuple of strings for description, energy and current
    """    
    filename = filename.split('_')
    descr = filename[0]
    energy = float(filename[1].replace('MeVu', 'e6'))
    current = float(filename[2].replace('uA', 'e-6'))
    return descr, energy, current


def write_timedata_to_npy(iq_obj, filename):
    """Saves the iq object to a npy format.

    Args:
        iq_obj (iqbase): iq object
        filename (string): Output file name
    """    
    np.save(filename + '.npy', vars(iq_obj))


def write_spectrum_to_csv(ff, pp, filename, center=0, delimiter = '|'):
    """Writes 1D spectrum to text CSV format. First column will be frequency, second linear power and third logarithmic power.

    Args:
        ff (ndarray): Frequency data array
        pp (ndarray): Power data array
        filename (string): Output file name
        center (float, optional): Center frequency. Defaults to 0.
    """    
    a = np.concatenate(
        (ff, pp, IQBase.get_dbm(pp)))
    b = np.reshape(a, (3, -1)).T
    np.savetxt(filename + '.csv', b, header='Delta f [Hz] @ {:.2e} [Hz]|Power [W]|Power [dBm]'.format(
        center), delimiter=delimiter)


def write_spectrogram_to_nifti(zz, filename):
    """Writes spectrogram to a NIFTI file.

    Args:
        zz (ndarray): Power meshgrid
        filename (string): File name
    """    
    # normalize to 1
    b = np.expand_dims(zz, axis=2)
    b = b/b.max()
    img = nib.Nifti1Image(b, affine=np.eye(4))
    nib.save(img, f'{filename}.nii.gz')

def remove_plot_content_from_spectrogram_svg(input_filename, output_filename):
    """Removes plot content from an existing SVG file. This function is specifically useful if you like to have an empty spectrogram plot for publication purposes.

    Args:
        input_filename (string): Input file name
        output_filename (string): Output file name
    """    
    soup = BeautifulSoup(open(input_filename).read(),features="xml")
    for element in soup.find_all('g', {"id" : "QuadMesh_1"}):
        element.decompose()
    with open(output_filename, "w") as file:
        file.write(str(soup))


# --------------------------------
# ROOT related functions

def write_timedata_to_root(iq_obj):
    """Writes time data to a root TTree.
    The structure of the root files in this case is like this: there are two
    trees inside, one tree has only one branch with an integer in it, which
    is the sampling rate, and another tree with a branch which is the center
    frequency. the other tree also has a branch in it, which contains the time
    series, which correspond to the power of the signal, meaning **(I^2+Q^2)**.
    The distance between the time samples is **1/(sampling_rate)**.

    Args:
        iq_obj (iqbase): iq object
    """    
    
    with uproot3.recreate(iq_obj.filename_wo_ext + '.root') as f:
        f['t_f_samp'] = uproot3.newtree(
            {'f_samp': uproot3.newbranch(np.int32, title='Sampling frequency'),
             })
        f['t_f_center'] = uproot3.newtree(
            {'f_center': uproot3.newbranch(np.int32, title='Center frequency'),
             })
        f['t_timedata'] = uproot3.newtree(
            {'timedata': uproot3.newbranch(np.float64, title='Time domain signal power')})

        f['t_f_samp'].extend({'f_samp': np.array([int(iq_obj.fs)])})
        f['t_f_center'].extend({'f_center': np.array([int(iq_obj.center)])})

        f['t_timedata'].extend({'timedata': np.abs(iq_obj.data_array)**2})


def write_spectrum_to_root(ff, pp, filename, center=0, title=''):
    """Write spectrum to a ROOT file using objects of TH class

    Args:
        ff (ndarray): Frequency data array
        pp (ndarray): Power data array
        filename (string): Output file name
        center (float, optional): Center frequency. Defaults to 0.
        title (str, optional): Title of ROOT histogram. Defaults to ''.
    """    
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

def get_root_th2d(xx, yy, zz, name='', title=''):
    """Convert spectrpgram to CERN ROOT TH2 Object

    Args:
        xx (ndarray): Frequency meshgrid
        yy (ndarray): Time meshgrid
        zz (ndarray): Power meshgrid
        name (str, optional): Name of TH object. Defaults to ''.
        title (str, optional): Title of TH object. Defaults to ''.

    Returns:
        (TH-object): ROOT Histogram
    """    
    from ROOT import TH2D
    h = TH2D(name, title, np.shape(xx)[
             1], xx[0, 0], xx[0, -1], np.shape(yy)[0], yy[0, 0], yy[-1, 0])
    for j in range(np.shape(yy)[0]):
        for i in range(np.shape(xx)[1]):
            h.SetBinContent(i, j, zz[j, i])
    return h

