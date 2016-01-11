"""
Class for IQ Data
IQT format

Xaratustrah Aug-2015

"""

import logging as log
import numpy as np
from iqbase import IQBase


class IQTData(IQBase):
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
        header_dic = IQBase.text_header_parser(self.header)

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

    def read(self, nframes=10, lframes=1024, sframes=1):
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
        header_dic = IQBase.text_header_parser(self.header)

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
