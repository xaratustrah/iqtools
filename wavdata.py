"""
Class for IQ Data
WAV formats

Xaratustrah Aug-2015

"""

import numpy as np
import time, os
from scipy.io import wavfile
from logging import log
from iqbase import IQBase


class WAVData(IQBase):
    def __init__(self, filename):
        super().__init__(filename)

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
            '<font size="4" color="green">Date and Time:</font> {} <br>'.format(self.date_time) + '\n'

    def read(self, nframes=10, lframes=1024, sframes=1):
        """
        Read sound wave files.
        :param nframes:
        :param lframes:
        :param sframes:
        :return:
        """
        self.lframes = lframes
        self.nframes = nframes
        self.sframes = sframes

        # activate memory map
        try:
            fs, data = wavfile.read(self.filename, mmap=True)
        except:
            log.error('File seems to end here!')
            return

        all_data = data.astype(np.float32).view(np.complex64)[:, 0]
        self.fs = fs
        self.center = 0
        self.nsamples_total = len(all_data)
        self.nframes_tot = int(len(all_data) / lframes)
        self.date_time = time.ctime(os.path.getctime(self.filename))

        total_n_bytes = nframes * lframes
        start_n_bytes = (sframes - 1) * lframes

        self.data_array = all_data[start_n_bytes:start_n_bytes + total_n_bytes]
