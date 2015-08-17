"""
The fundamental class for IQ Data

Xaratustrah Aug-2015

"""

import os
import numpy as np
import xml.etree.ElementTree as et
import logging as log
from scipy.io import wavfile
from scipy.signal import welch, find_peaks_cwt


class IQData(object):
    """
    The main class definition
    """

    def __init__(self):
        self.filename = ''
        self.filename_wo_ext = ''
        self.acq_bw = 0.0
        self.center = 0.0
        self.date_time = ''
        self.number_samples = 0
        self.rbw = 0.0
        self.rf_att = 0.0
        self.fs = 0.0
        self.span = 0.0
        self.scale = 0.0
        self.dictionary = {}
        self.header = None
        self.data_array = None
        self.lframes = 0
        self.nframes_tot = 0
        self.nframes = 0
        return

    def read_iqt(self, filename):
        # todo: to be done
        return None

    def read_tdms(self, filename, meta_filename, nframes=0, lframes=0, sframes=0):
        """Some good friend will continue here"""

        # todo: returns a dictionary containing info e.g. complex array (c16), sampling rate etc...
        return None

    def read_tiq(self, filename, nframes=10, lframes=1024, sframes=1):
        """Process the tiq input file.
        Following information are extracted, except Data offset, all other are stored in the dic. Data needs to be normalized over 50 ohm.

        AcquisitionBandwidth
        Frequency
        File name
        Data I and Q [Unit is Volt]
        Data_offset
        DateTime
        NumberSamples
        Resolution Bandwidth
        RFAttenuation (it is already considered in the data scaling, no need to use this value, only for info)
        Sampling Frequency
        Span
        Voltage Scaling
        """

        self.lframes = lframes
        self.nframes = nframes
        self.filename = filename
        self.filename_wo_ext = os.path.splitext(filename)[0]

        filesize = os.path.getsize(filename)
        log.info("File size is {} bytes.".format(filesize))

        with open(filename) as f:
            line = f.readline()
        data_offset = int(line.split("\"")[1])

        with open(filename, 'rb') as f:
            ba = f.read(data_offset)

        xml_tree_root = et.fromstring(ba)

        for elem in xml_tree_root.iter(tag='{http://www.tektronix.com}AcquisitionBandwidth'):
            self.acq_bw = float(elem.text)
        for elem in xml_tree_root.iter(tag='{http://www.tektronix.com}Frequency'):
            self.center = float(elem.text)
        for elem in xml_tree_root.iter(tag='{http://www.tektronix.com}DateTime'):
            self.date_time = str(elem.text)
        for elem in xml_tree_root.iter(tag='{http://www.tektronix.com}NumberSamples'):
            self.number_samples = int(elem.text)  # this entry matches (filesize - data_offset) / 8) well
        for elem in xml_tree_root.iter('NumericParameter'):
            if 'name' in elem.attrib and elem.attrib['name'] == 'Resolution Bandwidth' and elem.attrib['pid'] == 'rbw':
                self.rbw = float(elem.find('Value').text)
        for elem in xml_tree_root.iter(tag='{http://www.tektronix.com}RFAttenuation'):
            self.rf_att = float(elem.text)
        for elem in xml_tree_root.iter(tag='{http://www.tektronix.com}SamplingFrequency'):
            self.fs = float(elem.text)
        for elem in xml_tree_root.iter('NumericParameter'):
            if 'name' in elem.attrib and elem.attrib['name'] == 'Span' and elem.attrib['pid'] == 'globalrange':
                self.span = float(elem.find('Value').text)
        for elem in xml_tree_root.iter(tag='{http://www.tektronix.com}Scaling'):
            self.scale = float(elem.text)

        log.info("Center {0} Hz, span {1} Hz, sampling frequency {2} scale factor {3}.".format(self.center, self.span,
                                                                                               self.fs, self.scale))
        log.info("Header size {} bytes.".format(data_offset))

        log.info("Proceeding to read binary section, 32bit (4 byte) little endian.")
        log.info('Total number of samples: {}'.format(self.number_samples))
        log.info("Frame length: {0} data points = {1}s".format(lframes, lframes / self.fs))
        self.nframes_tot = int(self.number_samples / lframes)
        log.info("Total number of frames: {0} = {1}s".format(self.nframes_tot, self.number_samples / self.fs))
        log.info("Start reading at offset: {0} = {1}s".format(sframes, sframes * lframes / self.fs))
        log.info("Reading {0} frames = {1}s.".format(nframes, nframes * lframes / self.fs))

        self.header = ba

        total_n_bytes = 8 * nframes * lframes  # 8 comes from 2 times 4 byte integer for I and Q
        start_n_bytes = 8 * (sframes - 1) * lframes

        with open(filename, 'rb') as f:
            f.seek(data_offset + start_n_bytes)
            ba = f.read(total_n_bytes)

        # return a numpy array of little endian 8 byte floats (known as doubles)
        self.data_array = np.fromstring(ba, dtype='<i4')  # little endian 4 byte ints.
        # Scale to retrieve value in Volts. Augmented assignment does not work here!
        self.data_array = self.data_array * self.scale
        self.data_array = self.data_array.view(
            dtype='c16')  # reinterpret the bytes as a 16 byte complex number, which consists of 2 doubles.

        log.info("Output complex array has a size of {}.".format(self.data_array.size))
        self.dictionary = {'center': self.center, 'number_samples': self.number_samples, 'fs': self.fs,
                           'nframes': self.nframes,
                           'lframes': self.lframes, 'data': self.data_array,
                           'nframes_tot': self.nframes_tot, 'DateTime': self.date_time, 'rf_att': self.rf_att,
                           'span': self.span,
                           'acq_bw': self.acq_bw,
                           'file_name': self.filename, 'rbw': self.rbw}

        # in order to read you may use: data = x.item()['data'] or data = x[()]['data'] other wise you get 0-d error
        return self.dictionary, self.header

    def save_header(self):
        """Saves the header byte array into a txt tile."""
        with open(self.filename_wo_ext + '.xml', 'wb') as f3:
            f3.write(self.header)
        log.info("Header saved in an xml file.")

    def save_data(self):
        """Saves the dictionary to a numpy file."""
        np.save(self.filename_wo_ext + '.npy', self.dictionary)

    def save_audio(self, afs):
        """ Save the singal as an audio wave """
        wavfile.write(self.filename_wo_ext + '.wav', afs, abs(self.data_array))

    def get_fft_50_ohm(self):
        """ Get the FFT spectrum of a signal over a load of 50 ohm."""

        x = self.data_array
        n = x.size
        ts = 1.0 / self.fs
        f = np.fft.fftfreq(n, ts)
        v_peak_iq = np.fft.fft(x) / n
        v_rms = abs(v_peak_iq) / np.sqrt(2)
        p_avg = v_rms ** 2 / 50
        return np.fft.fftshift(f), np.fft.fftshift(v_peak_iq), np.fft.fftshift(p_avg)
        # return f, v_peak_iq, p_avg

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
        f, p_avg = welch(data, self.fs, nperseg=1024)
        return np.fft.fftshift(f), np.fft.fftshift(p_avg)

    def get_spectrogram(self):
        x = self.data_array
        fs = self.fs
        nframes = self.nframes
        lframes = self.lframes

        # define an empty array for appending
        pout = np.array([])
        frame_power = np.array([])

        # go through the array section wise and create a results array
        for i in range(nframes):
            f, p = self.get_pwelch(x[i * lframes:(i + 1) * lframes])
            pout = np.append(pout, p)
            frame_power = np.append(frame_power, IQData.get_channel_power(f, p))

        # create a mesh grid from 0 to n-1 in Y direction
        xx, yy = np.meshgrid(f, np.arange(nframes))

        # fold the results array to the mesh grid
        zz = np.reshape(pout, (nframes, lframes))
        return xx, yy * lframes / fs, zz, frame_power

    @staticmethod
    def get_fwhm(f, p):
        """f and p are arrays of points correponing to the original data, whereas
        the f_peak and p_peak are arrays of containing the coordinates of the peaks only
        """
        a = IQData.get_dbm(p)
        peak = a.max()
        f_p3db = 0
        f_m3db = 0
        p_p3db = 0
        p_m3db = 0
        peak_index = a.argmax()
        for i in range(peak_index, len(a)):
            if a[i] <= (peak - 3):
                p_p3db = a[i]
                f_p3db = f[i]
                break
        for i in range(peak_index, -1, -1):
            if a[i] <= (peak - 3):
                p_m3db = a[i]
                f_m3db = f[i]
                break
        return [f_m3db, f_p3db], [p_m3db, p_p3db]

    @staticmethod
    def get_narrow_peaks_dbm(f, p, accuracy=50):
        p_dbm = 10 * np.log10(p * 1000)
        peak_ind = find_peaks_cwt(p_dbm, np.arange(1, accuracy))
        return f[peak_ind], p_dbm[peak_ind]

    @staticmethod
    def get_broad_peak_dbm(f, p):
        p_dbm = IQData.get_dbm(p)
        # return as an array for compatibility
        return [f[p_dbm.argmax()]], [p_dbm.max()]

    @staticmethod
    def get_dbm(watt):
        """ Converter
        :param watt: value in Watt
        :return: value in dBm
        """
        return 10 * np.log10(watt * 1000)

    @staticmethod
    def get_watt(dbm):
        """ Converter
        :param watt: value in dBm
        :return: value in Watt
        """
        return 10 ** (dbm / 10) / 1000

    @staticmethod
    def get_channel_power(f, p):
        """ Return total power in band in Watts
        Input: average power in Watts
        """
        return np.trapz(p, x=f)

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

    @staticmethod
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

    @staticmethod
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
