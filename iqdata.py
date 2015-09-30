"""
The fundamental class for IQ Data

Xaratustrah Aug-2015

"""

import os, time
import numpy as np
import xml.etree.ElementTree as et
import logging as log
from scipy.io import wavfile
from scipy.signal import welch, find_peaks_cwt


class IQData(object):
    """
    The main class definition
    """

    def __init__(self, filename):
        self.filename = filename
        self.file_basename = os.path.basename(filename)
        self.filename_wo_ext = os.path.splitext(filename)[0]
        self.acq_bw = 0.0
        self.center = 0.0
        self.date_time = ''
        self.number_samples = 0
        self.rbw = 0.0
        self.rf_att = 0.0
        self.fs = 0.0
        self.span = 0.0
        self.scale = 0.0
        self.header = None
        self.data_array = None
        self.lframes = 0
        self.nframes_tot = 0
        self.nframes = 0
        return

    @property
    def dictionary(self):
        return {'center': self.center, 'number_samples': self.number_samples, 'fs': self.fs,
                'nframes': self.nframes,
                'lframes': self.lframes, 'data': self.data_array,
                'nframes_tot': self.nframes_tot, 'DateTime': self.date_time, 'rf_att': self.rf_att,
                'span': self.span,
                'acq_bw': self.acq_bw,
                'file_name': self.filename, 'rbw': self.rbw}

    def __str__(self):
        return \
            '<font size="4" color="green">Record length:</font> {:.2e} <font size="4" color="green">[s]</font><br>'.format(
                self.number_samples / self.fs) + '\n' + \
            '<font size="4" color="green">No. Samples:</font> {} <br>'.format(self.number_samples) + '\n' + \
            '<font size="4" color="green">Sampling rate:</font> {} <font size="4" color="green">[sps]</font><br>'.format(
                self.fs) + '\n' + \
            '<font size="4" color="green">Center freq.:</font> {} <font size="4" color="green">[Hz]</font><br>'.format(
                self.center) + '\n' + \
            '<font size="4" color="green">Span:</font> {} <font size="4" color="green">[Hz]</font><br>'.format(
                self.span) + '\n' + \
            '<font size="4" color="green">Acq. BW.:</font> {} <br>'.format(self.acq_bw) + '\n' + \
            '<font size="4" color="green">RBW:</font> {} <br>'.format(self.rbw) + '\n' + \
            '<font size="4" color="green">RF Att.:</font> {} <br>'.format(self.rf_att) + '\n' + \
            '<font size="4" color="green">Date and Time:</font> {} <br>'.format(self.date_time) + '\n'
        # 'Scale factor: {}'.format(self.scale)

    def read_tdms(self, filename, meta_filename, nframes=0, lframes=0, sframes=0):
        """Some good friend will continue here"""
        # todo: returns a dictionary containing info e.g. complex array (c16), sampling rate etc...
        pass

    def read_ascii(self, nframes=10, lframes=1024, sframes=1):
        self.lframes = lframes
        self.nframes = nframes

        x = np.genfromtxt(self.filename, dtype=np.float32)
        self.fs = x[0,0]
        self.center = x[0,1]
        all_data = x[1:,:]
        all_data = all_data.view(np.complex64)[:, 0]
        self.number_samples = len(all_data)
        self.nframes_tot = int(self.number_samples / lframes)
        self.date_time = time.ctime(os.path.getctime(self.filename))

        total_n_bytes = nframes * lframes
        start_n_bytes = (sframes - 1) * lframes

        self.data_array = all_data[start_n_bytes:start_n_bytes + total_n_bytes]

    def read_wav(self, nframes=10, lframes=1024, sframes=1):
        """
        Read sound wave files.
        :param nframes:
        :param lframes:
        :param sframes:
        :return:
        """
        self.lframes = lframes
        self.nframes = nframes

        # activate memory map
        fs, data = wavfile.read(self.filename, mmap=True)

        all_data = data.astype(np.float32).view(np.complex64)[:, 0]
        self.fs = fs
        self.center = 0
        self.number_samples = len(all_data)
        self.nframes_tot = int(len(all_data) / lframes)
        self.date_time = time.ctime(os.path.getctime(self.filename))

        total_n_bytes = nframes * lframes
        start_n_bytes = (sframes - 1) * lframes

        self.data_array = all_data[start_n_bytes:start_n_bytes + total_n_bytes]

    def read_iq(self, nframes=10, lframes=1024, sframes=1):
        """
        Read Sony/Tektronix IQ Files
        :param nframes:
        :param lframes:
        :param sframes:
        :return:
        """
        # in iqt files, lframes is always fixed 1024 at the time of reading the file.
        # At the usage time, the lframe can be changed from time data

        self.lframes = lframes
        self.nframes = nframes

        data_offset = 0
        with open(self.filename, 'rb') as f:
            ba = f.read(1)
            data_offset += 1
            header_size_size = int(ba.decode('utf8'))
            ba = f.read(header_size_size)
            data_offset += header_size_size
            header_size = int(ba.decode('utf8'))
            ba = f.read(header_size)
            data_offset += header_size

        self.header = ba.decode('utf8').split('\n')
        header_dic = IQData.text_header_parser(self.header)

        fft_points = int(header_dic['FFTPoints'])
        max_input_level = float(header_dic['MaxInputLevel'])
        level_offset = float(header_dic['LevelOffset'])
        frame_length = float(header_dic['FrameLength'])
        gain_offset = float(header_dic['GainOffset'])
        self.center = float(header_dic['CenterFrequency'])
        self.span = float(header_dic['Span'])
        self.nframes_tot = int(header_dic['ValidFrames'])
        self.date_time = header_dic['DateTime']

        self.number_samples = self.nframes_tot * fft_points
        self.fs = fft_points / frame_length

        # self.scale = np.sqrt(np.power(10, (gain_offset + max_input_level + level_offset) / 10) / 20 * 2)
        # todo: IQ support not finished

    def read_iqt(self, nframes=10, lframes=1024, sframes=1):
        """
        Read IQT Files
        :param nframes:
        :param lframes:
        :param sframes:
        :return:
        """
        # in iqt files, lframes is always fixed 1024 at the time of reading the file.
        # At the usage time, the lframe can be changed from time data

        self.lframes = lframes
        self.nframes = nframes

        data_offset = 0
        with open(self.filename, 'rb') as f:
            ba = f.read(1)
            data_offset += 1
            header_size_size = int(ba.decode('utf8'))
            ba = f.read(header_size_size)
            data_offset += header_size_size
            header_size = int(ba.decode('utf8'))
            ba = f.read(header_size)
            data_offset += header_size

        self.header = ba.decode('utf8').split('\n')
        header_dic = IQData.text_header_parser(self.header)

        fft_points = int(header_dic['FFTPoints'])
        max_input_level = float(header_dic['MaxInputLevel'])
        level_offset = float(header_dic['LevelOffset'])
        frame_length = float(header_dic['FrameLength'])
        gain_offset = float(header_dic['GainOffset'])
        self.center = float(header_dic['CenterFrequency'])
        self.span = float(header_dic['Span'])
        self.nframes_tot = int(header_dic['ValidFrames'])
        self.date_time = header_dic['DateTime']

        self.number_samples = self.nframes_tot * fft_points
        self.fs = fft_points / frame_length

        self.scale = np.sqrt(np.power(10, (gain_offset + max_input_level + level_offset) / 10) / 20 * 2)

        log.info("Proceeding to read binary section, 32bit (4 byte) little endian.")

        frame_header_type = np.dtype(
            {'names': ['reserved1', 'validA', 'validP', 'validI', 'validQ', 'bins', 'reserved2', 'triggered',
                       'overLoad', 'lastFrame', 'ticks'],
             'formats': [np.int16, np.int16, np.int16, np.int16, np.int16, np.int16, np.int16,
                         np.int16, np.int16, np.int16, np.int32]})

        frame_data_type = np.dtype((np.int16, 2 * 1024))  # 2 byte integer for Q, 2 byte integer for I
        frame_type = np.dtype({'names': ['header', 'data'],
                               'formats': [(frame_header_type, 1), (frame_data_type, 1)]})

        total_n_bytes = nframes * frame_type.itemsize
        start_n_bytes = (sframes - 1) * frame_type.itemsize

        # prepare an empty array with enough room
        self.data_array = np.zeros(1024 * nframes, np.complex64)

        # Read n frames at once
        with open(self.filename, 'rb') as f:
            f.seek(data_offset + start_n_bytes)
            ba = f.read(total_n_bytes)

        frame_array = np.fromstring(ba, dtype=frame_type)

        for i in range(frame_array.size):
            temp_array = np.zeros(2 * 1024, np.int16)
            temp_array[::2], temp_array[1::2] = frame_array[i]['data'][1::2], frame_array[i]['data'][::2]
            temp_array = temp_array.astype(np.float32)
            temp_array = temp_array.view(np.complex64)
            self.data_array[i * 1024:(i + 1) * 1024] = temp_array
        # and finally scale the data
        self.data_array = self.data_array * self.scale
        # todo: correction data block

    def read_tiq(self, nframes=10, lframes=1024, sframes=1):
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

        filesize = os.path.getsize(self.filename)
        log.info("File size is {} bytes.".format(filesize))

        with open(self.filename) as f:
            line = f.readline()
        data_offset = int(line.split("\"")[1])

        with open(self.filename, 'rb') as f:
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

        with open(self.filename, 'rb') as f:
            f.seek(data_offset + start_n_bytes)
            ba = f.read(total_n_bytes)

        # return a numpy array of little endian 8 byte floats (known as doubles)
        self.data_array = np.fromstring(ba, dtype='<i4')  # little endian 4 byte ints.
        # Scale to retrieve value in Volts. Augmented assignment does not work here!
        self.data_array = self.data_array * self.scale
        self.data_array = self.data_array.view(
            dtype='c16')  # reinterpret the bytes as a 16 byte complex number, which consists of 2 doubles.

        log.info("Output complex array has a size of {}.".format(self.data_array.size))
        # in order to read you may use: data = x.item()['data'] or data = x[()]['data'] other wise you get 0-d error

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

    def get_fft(self, x=None):
        """ Get the FFT spectrum of a signal over a load of 50 ohm."""
        termination = 1  # in Ohms for termination resistor
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
        f, p_avg = welch(data, self.fs, nperseg=self.lframes)
        return np.fft.fftshift(f), np.fft.fftshift(p_avg)

    def get_spectrogram(self):
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
        x = self.data_array
        fs = self.fs
        nframes = self.nframes
        lframes = self.lframes

        # define an empty np-array for appending
        pout = np.array([])

        # go through the data array section wise and create a results array
        for i in range(nframes):
            f, p = self.get_pwelch(x[i * lframes:(i + 1) * lframes])
            pout = np.append(pout, p)

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
            fwhm, f_peak, _, _ = IQData.get_fwhm(xx[i, :], zz[i, :], skip=15)
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
            frame_power[i] = IQData.get_channel_power(xx[i, :], zz[i, :])

        # Flatten array for 2D plot
        return yy[:, 0], frame_power

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
        p_dbm = IQData.get_dbm(p)
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
        p_dbm = IQData.get_dbm(p)
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
    def text_header_parser(str):
        """
        Parses key = value from the file header
        :param str:
        :return: dictionary
        """
        dic = {}
        for line in str:
            name, var = line.partition("=")[::2]
            var = var.strip()
            var = var.replace('k', 'e3')
            var = var.replace('m', 'e-3')
            var = var.replace('u', 'e-6')
            # sometimes there is a string indicating day time:
            if 'PM' not in var and 'AM' not in var:
                var = var.replace('M', 'e6')
            dic[name.strip()] = var
        return dic
