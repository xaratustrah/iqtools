"""
Class for IQ Data
RAW formats

Xaratustrah Aug-2015

"""

import numpy as np
import time, os
from scipy.io import wavfile
from iqbase import IQBase

class RAWData(IQBase):
    def read_bin(self, nframes=10, lframes=1024, sframes=1):
        self.lframes = lframes
        self.nframes = nframes
        x = np.fromfile(self.filename, dtype=np.complex64)
        self.fs = float(np.real(x[0]))
        self.center = float(np.imag(x[0]))
        all_data = x[1:]
        self.number_samples = len(all_data)
        self.nframes_tot = int(self.number_samples / lframes)
        self.date_time = time.ctime(os.path.getctime(self.filename))

        total_n_bytes = nframes * lframes
        start_n_bytes = (sframes - 1) * lframes

        self.data_array = all_data[start_n_bytes:start_n_bytes + total_n_bytes]

    def read_ascii(self, nframes=10, lframes=1024, sframes=1):
        self.lframes = lframes
        self.nframes = nframes

        x = np.genfromtxt(self.filename, dtype=np.float32)
        self.fs = x[0, 0]
        self.center = x[0, 1]
        all_data = x[1:, :]
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

