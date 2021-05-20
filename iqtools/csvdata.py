"""
Class for IQ Data
CSV and TXT formats

Xaratustrah Aug-2015

"""

import numpy as np
import time
import os
from iqtools.iqbase import IQBase


class CSVData(IQBase):
    def __init__(self, filename):
        super().__init__(filename)

        # Additional fields in this subclass
        self.center = 0.0
        self.date_time = time.ctime(os.path.getctime(self.filename))
        self.nsamples_total = sum(1 for line in open(filename)) - 1

    def read(self, nframes=10, lframes=1024, sframes=0):
        self.read_samples(nframes * lframes, offset=sframes * lframes)

    def read_samples(self, nsamples, offset=0):
        if nsamples > self.nsamples_total - offset:
            raise ValueError(
                'Requested number of samples is larger than the available {} samples.'.format(self.nsamples_total))

        x = np.genfromtxt(self.filename, dtype=np.float32, delimiter='|')
        self.fs = x[0, 0]
        self.center = x[0, 1]
        all_data = x[1:, :]
        all_data = all_data.view(np.complex64)[:, 0]

        self.data_array = all_data[offset:nsamples + offset]
