"""
Class for IQ Data
WAV formats

Xaratustrah Aug-2015

"""

import numpy as np
import time, os
from scipy.io import wavfile
from iqbase import IQBase


class WAVData(IQBase):
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

        # activate memory map
        try:
            fs, data = wavfile.read(self.filename, mmap=True)
        except:
            log.error('TDMS file seems to end here!')
            return

        all_data = data.astype(np.float32).view(np.complex64)[:, 0]
        self.fs = fs
        self.center = 0
        self.number_samples = len(all_data)
        self.nframes_tot = int(len(all_data) / lframes)
        self.date_time = time.ctime(os.path.getctime(self.filename))

        total_n_bytes = nframes * lframes
        start_n_bytes = (sframes - 1) * lframes

        self.data_array = all_data[start_n_bytes:start_n_bytes + total_n_bytes]
