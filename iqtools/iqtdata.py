"""
Class for IQ Data
IQT format

Xaratustrah Aug-2015

"""

import logging as log
import numpy as np
from iqtools.iqbase import IQBase


class IQTData(IQBase):
    def __init__(self, filename):
        super().__init__(filename)

        # Additional fields in this subclass
        self.header = ''
        self.span = 0
        self.fft_points = 0
        self.level_offset = 0
        self.frame_length = 0
        self.gain_offset = 0
        self.max_input_level = 0
        self.scale = 0

    def read_samples(self, nsamples, offset=0):
        # TODO:
        pass

    def read(self, nframes=10, lframes=1024, sframes=0):
        """
        Read IQT Files
        :return:
        """
        # in iqt files, lframes is always fixed 1024 at the time of reading the file.
        # At the usage time, the lframe can be changed from time data

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
        header_dic = self.read_header(self.header)

        self.fft_points = int(header_dic['FFTPoints'])
        self.max_input_level = float(header_dic['MaxInputLevel'])
        self.level_offset = float(header_dic['LevelOffset'])
        self.frame_length = float(header_dic['FrameLength'])
        self.gain_offset = float(header_dic['GainOffset'])
        self.center = float(header_dic['CenterFrequency'])
        self.span = float(header_dic['Span'])
        self.nframes_tot = int(header_dic['ValidFrames'])
        self.date_time = header_dic['DateTime']

        self.nsamples_total = self.nframes_tot * self.fft_points
        self.fs = self.fft_points / self.frame_length

        self.scale = np.sqrt(np.power(
            10, (self.gain_offset + self.max_input_level + self.level_offset) / 10) / 20 * 2)

        log.info("Proceeding to read binary section, 32bit (4 byte) little endian.")

        frame_header_type = np.dtype(
            {'names': ['reserved1', 'validA', 'validP', 'validI', 'validQ', 'bins', 'reserved2', 'triggered',
                       'overLoad', 'lastFrame', 'ticks'],
             'formats': [np.int16, np.int16, np.int16, np.int16, np.int16, np.int16, np.int16,
                         np.int16, np.int16, np.int16, np.int32]})

        # 2 byte integer for Q, 2 byte integer for I
        frame_data_type = np.dtype((np.int16, 2 * lframes))
        frame_type = np.dtype({'names': ['header', 'data'],
                               'formats': [(frame_header_type, 1), (frame_data_type, 1)]})

        total_n_bytes = nframes * frame_type.itemsize
        start_n_bytes = sframes * frame_type.itemsize

        # prepare an empty array with enough room
        self.data_array = np.zeros(lframes * nframes, np.complex64)

        # Read n frames at once
        try:
            with open(self.filename, 'rb') as f:
                f.seek(data_offset + start_n_bytes)
                ba = f.read(total_n_bytes)
        except:
            log.error('File seems to end here!')
            return

        # print(len(ba))
        frame_array = np.fromstring(ba, dtype=frame_type)

        for i in range(frame_array.size):
            temp_array = np.zeros(2 * lframes, np.int16)
            temp_array[::2], temp_array[1::2] = frame_array[i]['data'][1::2], frame_array[i]['data'][::2]
            temp_array = temp_array.astype(np.float32)
            temp_array = temp_array.view(np.complex64)
            self.data_array[i * lframes:(i + 1) * lframes] = temp_array
        # and finally scale the data
        self.data_array = self.data_array * self.scale
        # todo: correction data block

    # def read_iq(self, nframes=10, lframes=1024, sframes=1):
    #     """
    #     Read Sony/Tektronix IQ Files
    #     :param nframes:
    #     :param lframes:
    #     :param sframes:
    #     :return:
    #     """
    #     # in iqt files, lframes is always fixed 1024 at the time of reading the file.
    #     # At the usage time, the lframe can be changed from time data
    #
    #     self.lframes = lframes
    #     self.nframes = nframes
    #
    #     data_offset = 0
    #     with open(self.filename, 'rb') as f:
    #         ba = f.read(1)
    #         data_offset += 1
    #         header_size_size = int(ba.decode('utf8'))
    #         ba = f.read(header_size_size)
    #         data_offset += header_size_size
    #         header_size = int(ba.decode('utf8'))
    #         ba = f.read(header_size)
    #         data_offset += header_size
    #
    #     self.header = ba.decode('utf8').split('\n')
    #     header_dic = self.read_header(self.header)
    #
    #     fft_points = int(header_dic['FFTPoints'])
    #     max_input_level = float(header_dic['MaxInputLevel'])
    #     level_offset = float(header_dic['LevelOffset'])
    #     frame_length = float(header_dic['FrameLength'])
    #     gain_offset = float(header_dic['GainOffset'])
    #     self.center = float(header_dic['CenterFrequency'])
    #     self.span = float(header_dic['Span'])
    #     self.nframes_tot = int(header_dic['ValidFrames'])
    #     self.date_time = header_dic['DateTime']
    #
    #     self.nsamples_total = self.nframes_tot * fft_points
    #     self.fs = fft_points / frame_length
    #
    #     # self.scale = np.sqrt(np.power(10, (gain_offset + max_input_level + level_offset) / 10) / 20 * 2)
    #     # todo: IQ support not finished

    @staticmethod
    def read_header(str):
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
