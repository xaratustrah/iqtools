"""
Class for IQ Data
RAW formats

Xaratustrah Aug-2015

"""

import numpy as np
import time
import os
from iqtools.iqbase import IQBase


class BINData(IQBase):
    def __init__(self, filename):
        super().__init__(filename)

        # Additional fields in this subclass
        self.date_time = time.ctime(os.path.getctime(self.filename))
        self.center = 0.0
        # each complex64 sample is 8 bytes on disk
        self.nsamples_total = os.path.getsize(filename) / 8

    def read(self, nframes=10, lframes=1024, sframes=0):
        self.read_samples(nframes * lframes, offset=sframes * lframes)

    def read_samples(self, nsamples, offset=0):
        """
        Read from binary file. needs the first value to be the header
        please check the function:
            write_signal_to_bin
        in the tools.
        """
        if nsamples > self.nsamples_total - offset:
            raise ValueError(
                'Requested number of samples is larger than the available {} samples.'.format(self.nsamples_total))

        x = np.fromfile(self.filename, dtype=np.complex64)
        self.fs = float(np.real(x[0]))
        self.center = float(np.imag(x[0]))
        all_data = x[1:]

        self.data_array = all_data[offset:nsamples + offset]
