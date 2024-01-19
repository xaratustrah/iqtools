"""
The base class for all other IQ Data

xaratustrah@github Aug-2015

"""

import os
import numpy as np
from scipy.signal import welch, find_peaks_cwt
from abc import ABCMeta, abstractmethod
from scipy.signal.windows import dpss
import pyfftw

def pmtm(signal, dpss, axis=-1):
    """Estimate the power spectral density of the input signal. This function is adopted from [this project](https://github.com/xaratustrah/multitaper) which was in turn a fork of [this project](https://github.com/nerdull/multitaper).

    Args:
        signal (ndarray): n-dimensional array of real or complex values
        dpss (ndarray): The Slepian matrix
        axis (int, optional): Axis along which to apply the Slepian windows. Default is the last one. Defaults to -1.

    Returns:
        (ndarray): The multitaper frame, shifted in the correct order
    """    
    # conversion to positive-only index
    axis_p = (axis + signal.ndim) % signal.ndim
    sig_exp_shape = list(signal.shape[:axis]) + [1] + list(signal.shape[axis:])
    tap_exp_shape = [1] * axis_p + \
        list(dpss.shape) + [1] * (signal.ndim - 1 - axis_p)
    signal_tapered = signal.reshape(
        sig_exp_shape) * dpss.reshape(tap_exp_shape)
    return np.fft.fftshift(np.mean(np.absolute(np.fft.fft(signal_tapered, axis=axis_p + 1))**2, axis=axis_p), axes=axis_p)

class IQBase(object):
    # Abstract class
    __metaclass__ = ABCMeta

    def __init__(self, filename):

        # fields required in all subclasses
        # primary fileds

        self.filename = filename
        self.data_array = None
        self.scale = 1
        self.nsamples_total = 0
        self.fs = 0.0

        # secondary fileds
        self.file_basename = os.path.basename(filename)
        self.filename_wo_ext = os.path.splitext(filename)[0]
        self.window = 'rectangular'
        self.method = 'npfft'

    def __str__(self):
        return self.dic2htmlstring(vars(self))

    def dic2htmlstring(self, dic):
        """Converts a dictionary to an HTML string

        Args:
            dic (dictionary): Dictionary of values

        Returns:
            (string): HTML String
        """        
        outstr = ''
        if 'filename' in dic:
            outstr += '<font size="4" color="green">File name:</font> {} <font size="4" color="green"></font><br>\n'.format(
                self.filename)
        if 'nsamples_total' in dic:
            outstr += '<font size="4" color="green">Record length:</font> {:.2e} <font size="4" color="green">[s]</font><br>\n'.format(
                self.get_record_length())
        if 'nsamples_total' in dic:
            outstr += '<font size="4" color="green">No. Samples:</font> {} <br>\n'.format(
                self.nsamples_total)
        if 'fs' in dic:
            outstr += '<font size="4" color="green">Sampling rate:</font> {} <font size="4" color="green">[sps]</font><br>\n'.format(
                self.fs)
        if 'center' in dic:
            outstr += '<font size="4" color="green">Center freq.:</font> {} <font size="4" color="green">[Hz]</font><br>\n'.format(
                self.center)
        if 'span' in dic:
            outstr += '<font size="4" color="green">Span:</font> {} <font size="4" color="green">[Hz]</font><br>\n'.format(
                self.span)
        if 'acq_bw' in dic:
            outstr += '<font size="4" color="green">Acq. BW.:</font> {} <br>\n'.format(
                self.acq_bw)
        if 'rbw' in dic:
            outstr += '<font size="4" color="green">RBW:</font> {} <br>\n'.format(
                self.rbw)
        if 'rf_att' in dic:
            outstr += '<font size="4" color="green">RF Att.:</font> {} <br>\n'.format(
                self.rf_att)
        if 'date_time' in dic:
            outstr += '<font size="4" color="green">Date and Time:</font> {} <br>\n'.format(
                self.date_time)
            return outstr

    def get_record_length(self):
        """Returns the record length

        Returns:
            (float): record length
        """        
        return self.nsamples_total / self.fs

    @abstractmethod
    def read(self, nframes, lframes, sframes):
        """Abstract method
        """        
        pass

    @abstractmethod
    def read_samples(self, nsamples, offset):
        """Abstract method
        """        
        pass

    def get_window(self, n=None):
        """Return a suitable windowing function for FFT

        Args:
            n (int, optional): Window length. Defaults to None.

        Returns:
            (ndarray): FFT Window
        """        
        if not n:
            n = self.lframes
        assert self.window in ['rectangular',
                               'bartlett', 'blackman', 'hamming', 'hanning']
        if self.window == 'rectangular':
            return np.ones(n)
        elif self.window == 'bartlett':
            return np.bartlett(n)
        elif self.window == 'blackman':
            return np.blackman(n)
        elif self.window == 'hamming':
            return np.hamming(n)
        else:
            return np.hanning(n)

    def get_fft_freqs_only(self, x=None):
        """Return FFT frequencies only

        Args:
            x (ndarray, optional): Complex valued data array. Defaults to None, in which 
            case object's own data_array is used.

        Returns:
            (ndarray): Frequency values
        """        
        if x is None:
            data = self.data_array
        else:
            data = x
        n = data.size
        ts = 1.0 / self.fs
        f = np.fft.fftfreq(n, ts)
        return np.fft.fftshift(f)

    def get_fft(self, x=None, nframes=0, lframes=0):
        """Calculate FFT. If nframes and lframes are provided then it
        Reshapes the data to a 2D matrix, performs FFT in the horizontal
        direction i.e. for each row, then averages in frequency domain in the
        vertical direction, for every bin. The result is a flattened 1D
        array that can be plotted using the frequencies.

        Otherwise it is just the standard 1D FFT

        Args:
            x (ndarray, optional): Complex valued data array. Defaults to None.
            nframes (int, optional): Number of frames. Defaults to 0.
            lframes (int, optional): Length of frames. Defaults to 0.

        Returns:
            (tuple): Tuple of ndarrays, frequency, power and voltage
        """        

        if nframes and lframes:
            nf = nframes
            lf = lframes
        else:
            nf = 1
            lf = len(self.data_array)
            # overwrite
            if x is not None:
                lf = len(x)

        if x is None:
            data = self.data_array
        else:
            data = x

        termination = 50  # in Ohms for termination resistor
        data = np.reshape(data, (nf, lf))
        freqs = self.get_fft_freqs_only(data[0])
        v_peak_iq = np.fft.fft(
            data * self.get_window(lf), axis=1)
        v_peak_iq = np.average(v_peak_iq, axis=0) / lf * nf
        v_rms = abs(v_peak_iq) / np.sqrt(2)
        p_avg = v_rms ** 2 / termination
        # freqs is already fft shifted
        return freqs, np.fft.fftshift(p_avg), np.fft.fftshift(v_peak_iq)

    def get_pwelch(self, x=None):
        """ Create the power spectral density using Welch method

        Args:
            x (ndarray, optional): if available the data segment, otherwise the whole data will be taken. Defaults to None.

        Returns:
            (tuple): FFT and power in Watts
        """        
        if x is None:
            data = self.data_array
        else:
            data = x
        n = data.size
        f, p_avg = welch(data * self.get_window(n), self.fs,
                         nperseg=data.size, return_onesided=False)
        return np.fft.fftshift(f), np.fft.fftshift(p_avg)

    def get_power_spectrogram(self, nframes, lframes):
        """Get power spectrogram. Go through the data frame by frame and perform transformation. They can be plotted using pcolormesh
        x, y and z are ndarrays and have the same shape. In order to access the contents use these kind of
        indexing as below:
        
        ```
        #Slices parallel to frequency axis
        nrows = np.shape(x)[0]
        for i in range (nrows):
            plt.plot(x[i,:], z[i,:])

        #Slices parallel to time axis
        ncols = np.shape(y)[1]
        for i in range (ncols):
            plt.plot(y[:,i], z[:, i])
        ```

        Args:
            nframes (int): Number of time frames, i.e. rows of matrix
            lframes (int): Number of frequency bins, i.e. number of columns of matrix

        Returns:
            (tuple): time, frequency and power as mesh grids
        """

        assert self.method in ['npfft', 'fftw', 'welch', 'mtm']

        # define an empty np-array for appending
        pout = np.zeros(nframes * lframes)

        if self.method == 'npfft':
            sig = np.reshape(self.data_array, (nframes, lframes))
            # fft must return power, so needs to be squared
            zz = np.abs(np.fft.fftshift(np.fft.fft(sig, axis=1), axes=1)) ** 2

        elif self.method == 'fftw':
            pyfftw.config.NUM_THREADS = 4
            pyfftw.config.PLANNER_EFFORT = 'FFTW_MEASURE'

            qq = pyfftw.empty_aligned([nframes, lframes], dtype='complex64')
            qq [:,:] = np.reshape(self.data_array, (nframes, lframes))
            zz = np.abs(np.fft.fftshift(pyfftw.interfaces.numpy_fft.fft(qq, axis=1), axes=1)) ** 2

        elif self.method == 'welch':
            # go through the data array section wise and create a results array
            for i in range(nframes):
                f, p = self.get_pwelch(
                    self.data_array[i * lframes:(i + 1) * lframes] * self.get_window(lframes))
                pout[i * lframes:(i + 1) * lframes] = p
            # fold the results array to the mesh grid
            zz = np.reshape(pout, (nframes, lframes))

        elif self.method == 'mtm':
            mydpss = dpss(M=lframes, NW=4, Kmax=6)
            #f = self.get_fft_freqs_only(x[0:lframes])
            sig = np.reshape(self.data_array, (nframes, lframes))
            zz = pmtm(sig, mydpss, axis=1)

        # create a mesh grid from 0 to nframes -1 in Y direction
        xx, yy = np.meshgrid(np.arange(lframes), np.arange(nframes))
        yy = yy * lframes / self.fs
        # center the frequencies around zero
        xx = xx - xx[-1, -1] / 2
        xx = xx * self.fs / lframes

        return xx, yy, zz

    def get_dp_p_vs_time(self, xx, yy, zz, eta):
        """Returns two arrays for plotting dp_p vs time

        Args:
            xx (ndarray): Frequency meshgrid
            yy (ndarray): Time meshgrid
            zz (ndarray): Power meshgrid
            eta (float): _description_

        Returns:
            (ndarray): Flattened array for 2D plot
        """        
        # Slices parallel to frequency axis
        n_time_frames = np.shape(xx)[0]
        dp_p = np.zeros(n_time_frames)
        for i in range(n_time_frames):
            fwhm, f_peak, _, _ = IQBase.get_fwhm(xx[i, :], zz[i, :], skip=20)
            dp_p[i] = fwhm / (f_peak + self.center) / eta

        # Flatten array for 2D plot
        return yy[:, 0], dp_p

    def get_frame_power_vs_time(self, xx, yy, zz):
        """Returns two arrays for plotting frame power vs time

        Args:
            xx (ndarray): Frequency meshgrid
            yy (ndarray): Time meshgrid
            zz (ndarray): Power meshgrid
            eta (float): _description_

        Returns:
            (ndarray): Flattened array for 2D plot
        """        
        # Slices parallel to frequency axis
        n_time_frames = np.shape(xx)[0]
        frame_power = np.zeros(n_time_frames)
        for i in range(n_time_frames):
            frame_power[i] = self.get_channel_power(xx[i, :], zz[i, :])

        # Flatten array for 2D plot
        return yy[:, 0], frame_power

    @staticmethod
    def get_frame_sum_vs_time(yy, zz):
        """Return sum of the values in frame

        Args:
            yy (ndarray): Time meshgrid
            zz (ndarray): Power meshgrid

        Returns:
            (float): Sum
        """        
        summ = np.zeros(np.shape(zz)[0])
        for i in range(len(summ)):
            summ[i] = np.sum(zz[i, :])
        return yy[:, 0], summ

    @staticmethod
    def get_fwhm(f, p, skip=None):
        """Return the full width at half maximum.
        f and p are arrays of points corresponding to the original data, whereas
        the f_peak and p_peak are arrays of containing the coordinates of the peaks only

        Args:
            f (ndarray): _description_
            p (ndarray): _description_
            skip (int, optional): Sometimes peaks have a dip, skip this number of bins, use with care or visual inspection. Defaults to None.

        Returns:
            (float): Full width at half maximum
        """        
        p_dbm = IQBase.get_dbm(p)
        f_peak = p_dbm.max()
        f_p3db = 0
        f_m3db = 0
        p_p3db = 0
        p_m3db = 0
        index_p3db = 0
        index_m3db = 0
        f_peak_index = p_dbm.argmax()
        for i in range(f_peak_index, len(p_dbm)):
            if skip is not None and i < skip:
                continue
            if p_dbm[i] <= (f_peak - 3):
                p_p3db = p[i]
                f_p3db = f[i]
                index_p3db = i
                break
        for i in range(f_peak_index, -1, -1):
            if skip is not None and f_peak_index - i < skip:
                continue
            if p_dbm[i] <= (f_peak - 3):
                p_m3db = p[i]
                f_m3db = f[i]
                index_m3db = i
                break
        fwhm = f_p3db - f_m3db
        # return watt values not dbm
        return fwhm, f_peak, np.array([index_m3db, index_p3db]), np.array([f_m3db, f_p3db]), np.array([p_m3db, p_p3db])

    @staticmethod
    def get_sigma_estimate(f, p):
        """Gets an estimate for sigma. Could be used for more precise fitting.

        Args:
            f (ndarray): ndarray of frequencies
            p (ndarray): ndarray of powers

        Returns:
            (float): Estimage of sigma
        """        
        p_peak = p.max()
        f_peak_index = p.argmax()
        f_peak = f[f_peak_index]
        idx_phm = 0
        idx_mhm = 0
        rng_max = int(len(f) - len(f) / 4)
        rng_min = int(len(f) - 3 * len(f) / 4)

        for i in range(rng_max, rng_min, -1):
            if p[i] >= p_peak / 2:
                idx_phm = i
                break

        for i in range(rng_min, rng_max):
            if p[i] >= p_peak / 2:
                idx_mhm = i
                break

        return f_peak_index, idx_phm - idx_mhm, idx_mhm, idx_phm

    @staticmethod
    def get_narrow_peaks_dbm(f, p, accuracy=50):
        """Find narrow peaks and return them

        Args:
            f (ndarray): ndarray of frequencies
            p (ndarray): ndarray of powers
            accuracy (int, optional): A number to adjust sensitivity of the peak finder. Defaults to 50.

        Returns:
            (ndarray): ndarray of peaks and their indexes
        """        
        # convert to dbm for convenience
        p_dbm = IQBase.get_dbm(p)
        peak_ind = find_peaks_cwt(p_dbm, np.arange(1, accuracy))
        # return the watt value, not dbm
        return np.array(f[peak_ind]), np.array(p[peak_ind])

    @staticmethod
    def get_broad_peak_dbm(f, p):
        """Returns the maximum usually useful for a broad peak

        Args:
            f (ndarray): ndarray of frequencies
            p (ndarray): ndarray of powers

        Returns:
            (ndarray): Coordinates of the peak
        """        
        # return as an array for compatibility
        return np.array([f[p.argmax()]]), np.array([p.max()])

    @staticmethod
    def get_dbm(watt):
        """Convert Watt to dBm

        Args:
            watt (float): Value in Watts

        Returns:
            (float): Value in dBm
        """        
        if isinstance(watt, np.ndarray):
            watt[watt <= 0] = 10 ** -30
        return 10 * np.log10(np.array(watt) * 1000)

    @staticmethod
    def get_watt(dbm):
        """Convert dBm to Watts

        Args:
            dbm (float): Value in dBm

        Returns:
            (float): Value in Watts
        """        
        return 10 ** (np.array(dbm) / 10) / 1000

    def get_channel_power(self, f, p, span=None):
        """Return total power in band in Watts, considering noise bandwidth

        Args:
            f (ndarray): ndarray of frequencies
            p (ndarray): ndarray of powers
            span (float, optional): Frequency window. Defaults to None.

        Returns:
            (float): Channel power
        """        
        if not span:
            mask = (f != 0) | (f == 0)
        else:
            mask = (f <= span / 2) & (f >= -span / 2)

        # based on agilent application note on RBW and ENBW
        # for typical FFT based analysers
        #nbw = self.rbw * 5
        nbw = self.rbw * 1.056
        summ = np.sum(p[mask])
        # ACQ bandwidth here is a better measure.
        # correct formula uses NBW
        # final = summ / np.size(p) * self.acq_bw / nbw
        final = summ / nbw
        return final

    def downsample_and_average(self, every=2):
        """Downsampling and averaging in the time domain. This function overrides the data array and also the sampling
        frequency, allowing further operations to be performed smoothly. If you do not want this behaviour, please make a copy of the object first.

        Args:
            every (int, optional): Defaults to 2. How many samples to average in time domain.

        """
        assert len(self.data_array) % every == 0
        self.data_array = np.mean(np.reshape(self.data_array, (int(len(self.data_array) / every), every)), axis= 1)
        self.fs = self.fs / every

    @staticmethod
    def zoom_in_freq(f, p, center=0, span=1000):
        """Cut the frequency domain data

        Args:
            f (ndarray): ndarray of frequencies
            p (ndarray): ndarray of powers
            center (float, optional): Center index. Defaults to 0.
            span (float, optional): Frequency window. Defaults to 1000.

        Returns:
            (tuple): Frequency and power
        """        
        low = center - span / 2
        high = center + span / 2
        mask = (f > low) & (f < high)
        return f[mask], p[mask]

    @staticmethod
    def shift_cut_data_time(x, val):
        """Handy tool to shift and cut data in time domain

        Args:
            x (ndarray): Data array
            val (int): Shift index

        Returns:
            (tuple): Shift and cut version
        """        
        return x[:-val], x[val:]

    @staticmethod
    def shift_to_center_frequency(f, center):
        """Just return the shifted frequency to center

        Args:
            f (ndarray): Array of frequencies
            center (float): Center frequency

        Returns:
            (ndarray): Shifted array of frequencies
        """        
        return center + f
