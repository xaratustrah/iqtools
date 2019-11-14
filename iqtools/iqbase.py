"""
The fundamental class for IQ Data

Xaratustrah Aug-2015

"""

import os
import numpy as np
from scipy.io import wavfile
from scipy.signal import welch, find_peaks_cwt
from abc import ABCMeta, abstractmethod
from scipy.signal.windows import dpss
from multitaper import *


class IQBase(object):
    """
    The main class definition
    """
    __metaclass__ = ABCMeta

    def __init__(self, filename):
        # fields required in all subclasses

        self.filename = filename
        self.file_basename = os.path.basename(filename)
        self.filename_wo_ext = os.path.splitext(filename)[0]
        self.date_time = ''
        self.lframes = 0
        self.nframes = 0
        self.sframes = 0
        self.nframes_tot = 0
        self.nsamples_total = 0
        self.data_array = None
        self.fs = 0.0
        self.center = 0.0

        self.window = 'rectangular'
        self.method = 'fft'

    @abstractmethod
    def read(self, nframes, lframes, sframes):
        pass

    def get_window(self, n=None):
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

    def save_npy(self):
        """Saves the dictionary to a numpy file."""
        np.save(self.filename_wo_ext + '.npy', self.dictionary)

    def save_audio(self, afs):
        """ Save the singal as an audio wave """
        wavfile.write(self.filename_wo_ext + '.wav', afs, abs(self.data_array))

    def get_fft_freqs_only(self, x=None):
        """
        Deliver the FFT frequencies only
        """
        if x is None:
            data = self.data_array
        else:
            data = x
        n = data.size
        ts = 1.0 / self.fs
        f = np.fft.fftfreq(n, ts)
        return np.fft.fftshift(f)

    def get_fft(self, x=None):
        """ Get the FFT spectrum of a signal over a load of 50 ohm."""
        termination = 50  # in Ohms for termination resistor
        if x is None:
            data = self.data_array
        else:
            data = x
        n = data.size
        ts = 1.0 / self.fs
        f = np.fft.fftfreq(n, ts)
        v_peak_iq = np.fft.fft(data * self.get_window(n)) / n
        v_rms = abs(v_peak_iq) / np.sqrt(2)
        p_avg = v_rms ** 2 / termination
        return np.fft.fftshift(f), np.fft.fftshift(p_avg), np.fft.fftshift(v_peak_iq)

    def get_pwelch(self, x=None):
        """
        Create the power spectral density using Welch method
        :param x: if available the data segment, otherwise the whole data will be taken
        :return: fft and power in Watts
        """
        if x is None:
            data = self.data_array
        else:
            data = x
        n = data.size
        f, p_avg = welch(data * self.get_window(n), self.fs,
                         nperseg=data.size, return_onesided=False)
        return np.fft.fftshift(f), np.fft.fftshift(p_avg)

    def get_spectrogram(self, nframes, lframes):
        """
        Go through the data frame by frame and perform transformation. They can be plotted using pcolormesh
        x, y and z are ndarrays and have the same shape. In order to access the contents use these kind of
        indexing as below:

        #Slices parallel to frequency axis
        nrows = np.shape(x)[0]
        for i in range (nrows):
            plt.plot(x[i,:], z[i,:])

        #Slices parallel to time axis
        ncols = np.shape(y)[1]
        for i in range (ncols):
            plt.plot(y[:,i], z[:, i])

        :return: frequency, time and power for XYZ plot,
        """

        assert self.method in ['fft', 'welch', 'mtm']

        # define an empty np-array for appending
        pout = np.zeros(nframes * lframes)

        if self.method == 'fft':
            sig = np.reshape(self.data_array, (nframes, lframes))
            zz = np.abs(np.fft.fftshift(np.fft.fft(sig, axis=1)))

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
        xx = xx - xx[-1, -1] / 2
        xx = xx * self.fs / lframes

        return xx, yy, zz

    def get_dp_p_vs_time(self, xx, yy, zz, eta):
        """
        Returns two arrays for plotting dp_p vs time
        :param xx: from spectrogram
        :param yy: from spectrogram
        :param zz: from spectrogram
        :return: Flattened array for 2D plot
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
        """
        Returns two arrays for plotting frame power vs time
        :param xx: from spectrogram
        :param yy: from spectrogram
        :param zz: from spectrogram
        :return: Flattened array for 2D plot
        """
        # Slices parallel to frequency axis
        n_time_frames = np.shape(xx)[0]
        frame_power = np.zeros(n_time_frames)
        for i in range(n_time_frames):
            frame_power[i] = IQBase.get_channel_power(xx[i, :], zz[i, :])

        # Flatten array for 2D plot
        return yy[:, 0], frame_power

    def get_time_average_vs_frequency(self, xx, yy, zz):
        """
        Returns the time average for each frequency bin
        :param xx:
        :param yy:
        :param zz:
        :return:
        """
        # Slices parallel to time axis (second dimension of xx is needed)
        n_frequency_frames = np.shape(xx)[1]
        f_slice_average = np.zeros(n_frequency_frames)
        for i in range(n_frequency_frames):
            f_slice_average[i] = np.average(zz[:, i])
        # Flatten array fro 2D plot (second dimension of xx is needed)
        return xx[0, :], f_slice_average

    @staticmethod
    def get_fwhm(f, p, skip=None):
        """
        Return the full width at half maximum.
        f and p are arrays of points corresponding to the original data, whereas
        the f_peak and p_peak are arrays of containing the coordinates of the peaks only
        :param f:
        :param p:
        :param skip: Sometimes peaks have a dip, skip this number of bins, use with care or visual inspection
        :return:
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
        """
        Find narrow peaks and return them
        :param f:
        :param p:
        :param accuracy:
        :return:
        """
        # convert to dbm for convenience
        p_dbm = IQBase.get_dbm(p)
        peak_ind = find_peaks_cwt(p_dbm, np.arange(1, accuracy))
        # return the watt value, not dbm
        return np.array(f[peak_ind]), np.array(p[peak_ind])

    @staticmethod
    def get_broad_peak_dbm(f, p):
        """
        Returns the maximum usually useful for a broad peak
        :param f:
        :param p:
        :return:
        """
        # return as an array for compatibility
        return np.array([f[p.argmax()]]), np.array([p.max()])

    @staticmethod
    def get_dbm(watt):
        """ Converter
        :param watt: value in Watt
        :return: value in dBm
        """
        if isinstance(watt, np.ndarray):
            watt[watt <= 0] = 10 ** -30
        return 10 * np.log10(np.array(watt) * 1000)

    @staticmethod
    def get_watt(dbm):
        """ Converter
        :param watt: value in dBm
        :return: value in Watt
        """
        return 10 ** (np.array(dbm) / 10) / 1000

    # @staticmethod
    # def get_channel_power(f, p):
    #     """ Return total power in band in Watts
    #     Input: average power in Watts
    #     """
    #     return np.trapz(p, x=f)

    def get_channel_power(self, f, p):
        """ Return total power in band in Watts
        Input: average power in Watts
        """
        summ = 0
        nbw = self.rbw * 5
        for i in range(np.size(p)):
            summ += p[i]
        # ACQ bandwidth here is a better measure.
        # correct formula uses NBW
        final = summ / np.size(p) * self.acq_bw / nbw
        return final

    @staticmethod
    def zoom_in_freq(f, p, center=0, span=1000):
        """
        Cut the frequency domain data
        :param f:
        :param p:
        :param center:
        :param span:
        :return:
        """
        low = center - span / 2
        high = center + span / 2
        mask = (f > low) & (f < high)
        return f[mask], p[mask]

    @staticmethod
    def shift_cut_data_time(x, val):
        """
        Handy tool to shift and cut data in time domain
        :param f:
        :param center:
        :return:
        """
        return x[:-val], x[val:]

    @staticmethod
    def shift_to_center_frequency(f, center):
        """
        Handy tool to shift frequency to center
        :param f:
        :param center:
        :return:
        """
        return center + f
