"""
Class for IQ Data
GNU Radio simple binary format reader

Xaratustrah Aug-2018

"""

import numpy as np
import time
import os
from iqtools.iqbase import IQBase


class GRData(IQBase):
    def __init__(self, filename, fs, center=0, date_time=""):
        super().__init__(filename)
        self.fs = fs
        self.center = center
        self.date_time = date_time

    @property
    def dictionary(self):
        return {'center': self.center,
                'nsamples_total': self.nsamples_total,
                'fs': self.fs,
                'nframes': self.nframes,
                'lframes': self.lframes,
                'data': self.data_array,
                'nframes_tot': self.nframes_tot,
                'DateTime': self.date_time,
                'file_name': self.filename}

    def __str__(self):
        return \
            '<font size="4" color="green">Record length:</font> {:.2e} <font size="4" color="green">[s]</font><br>'.format(
                self.nsamples_total / self.fs) + '\n' + \
            '<font size="4" color="green">No. Samples:</font> {} <br>'.format(self.nsamples_total) + '\n' + \
            '<font size="4" color="green">Sampling rate:</font> {} <font size="4" color="green">[sps]</font><br>'.format(
                self.fs) + '\n' + \
            '<font size="4" color="green">Center freq.:</font> {} <font size="4" color="green">[Hz]</font><br>'.format(
                self.center) + '\n' + \
            '<font size="4" color="green">Date and Time:</font> {} <br>'.format(
                self.date_time) + '\n'

    def read_complete_file(self):
        """
        Read a complete TDMS file
        :return:
        """
        filesize = os.path.getsize(self.filename)
        self.nsamples_total = filesize / 8
        self.data_array = np.fromfile(self.filename, dtype=np.complex64)

    def read_samples(self, nsamples, offset=0):
        """
        Read a specific number of samples
        Parameters
        ----------
        nsamples How many samples to read
        offset either start from the beginning, i.e. 0 or start at a different sample offset.
        0 means first sample, i.e. byte 0 to 7 since each sample is 8 bytes = 64 bits complex
        1 mean byte 8 to 15
        and so on...

        Returns
        -------

        """
        # TODO:
        pass
