"""
The fundamental class for IQ Data

Xaratustrah Aug-2015

"""

import logging as log
import os
import numpy as np
from scipy.io import wavfile
from scipy.signal import welch, find_peaks_cwt
from spectrum import dpss, pmtm
from abc import ABCMeta, abstractmethod


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
        self.nframes_tot = 0
        self.number_samples = 0
        self.data_array = None
        self.fs = 0.0
        self.center = 0.0

    @abstractmethod
    def read(self, nframes, lframes, sframes):
        pass

    def save_npy(self):
        """Saves the dictionary to a numpy file."""
        np.save(self.filename_wo_ext + '.npy', self.dictionary)

    def save_audio(self, afs):
        """ Save the singal as an audio wave """
        wavfile.write(self.filename_wo_ext + '.wav', afs, abs(self.data_array))

    def get_fft_freqs_only(self, x=None):
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
        v_peak_iq = np.fft.fft(data) / n
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
        f, p_avg = welch(data, self.fs, nperseg=data.size)
        return np.fft.fftshift(f), np.fft.fftshift(p_avg)

    def get_spectrogram(self, method='fft'):
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

        assert method in ['fft', 'welch', 'multitaper']

        x = self.data_array
        fs = self.fs
        nframes = self.nframes
        lframes = self.lframes

        # define an empty np-array for appending
        pout = np.zeros(nframes * lframes)

        if method == 'fft':
            # go through the data array section wise and create a results array
            for i in range(nframes):
                f, p, _ = self.get_fft(x[i * lframes:(i + 1) * lframes])
                pout[i * lframes:(i + 1) * lframes] = p

        elif method == 'welch':
            # go through the data array section wise and create a results array
            for i in range(nframes):
                f, p = self.get_pwelch(x[i * lframes:(i + 1) * lframes])
                pout[i * lframes:(i + 1) * lframes] = p

        elif method == 'multitaper':
            [tapers, eigen] = dpss(lframes, NW=2)
            f = self.get_fft_freqs_only(x[0:lframes])
            # go through the data array section wise and create a results array
            for i in range(nframes):
                p = pmtm(x[i * lframes:(i + 1) * lframes], e=tapers, v=eigen, method='adapt', show=False)
                pout[i * lframes:(i + 1) * lframes] = np.fft.fftshift(p[:, 0])

        # create a mesh grid from 0 to nframes -1 in Y direction
        xx, yy = np.meshgrid(f, np.arange(nframes))

        # fold the results array to the mesh grid
        zz = np.reshape(pout, (nframes, lframes))
        return xx, yy * lframes / fs, zz

    def get_dp_p_vs_time(self, xx, yy, zz):
        """
        Returns two arrays for plotting dp_p vs time
        :param xx: from spectrogram
        :param yy: from spectrogram
        :param zz: from spectrogram
        :return: Flattened array for 2D plot
        """
        gamma = 1.20397172736
        gamma_t = 1.34
        eta = (1 / gamma ** 2) - (1 / gamma_t ** 2)
        # Slices parallel to frequency axis
        n_time_frames = np.shape(xx)[0]
        dp_p = np.zeros(n_time_frames)
        for i in range(n_time_frames):
            fwhm, f_peak, _, _ = IQBase.get_fwhm(xx[i, :], zz[i, :], skip=15)
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
        f_peak_index = p_dbm.argmax()
        for i in range(f_peak_index, len(p_dbm)):
            if skip is not None and i < skip:
                continue
            if p_dbm[i] <= (f_peak - 3):
                p_p3db = p[i]
                f_p3db = f[i]
                break
        for i in range(f_peak_index, -1, -1):
            if skip is not None and f_peak_index - i < skip:
                continue
            if p_dbm[i] <= (f_peak - 3):
                p_m3db = p[i]
                f_m3db = f[i]
                break
        fwhm = f_p3db - f_m3db
        # return watt values not dbm
        return fwhm, f_peak, [f_m3db, f_p3db], [p_m3db, p_p3db]

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
        return f[peak_ind], p[peak_ind]

    @staticmethod
    def get_broad_peak_dbm(f, p):
        """
        Returns the maximum usually useful for a broad peak
        :param f:
        :param p:
        :return:
        """
        # return as an array for compatibility
        return [f[p.argmax()]], [p.max()]

    @staticmethod
    def get_dbm(watt):
        """ Converter
        :param watt: value in Watt
        :return: value in dBm
        """
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
