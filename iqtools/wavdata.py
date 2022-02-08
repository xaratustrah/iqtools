"""
Class for IQ Data
WAV formats

Xaratustrah Aug-2015

"""

import numpy as np
import time
import os
from scipy.io import wavfile
from logging import log
from .iqbase import IQBase


class WAVData(IQBase):
    def __init__(self, filename):
        super().__init__(filename)

        # Additional fields in this subclass
        self.date_time = time.ctime(os.path.getctime(self.filename))

    def read(self, nframes=10, lframes=1024, sframes=0):
        self.read_samples(nframes * lframes, offset=sframes * lframes)

    def read_samples(self, nsamples, offset=0):

        # activate memory map
        try:
            fs, data = wavfile.read(self.filename, mmap=True)
        except:
            log.error('File seems to end here!')
            return
        all_data = data.astype(np.complex64)
        self.fs = fs
        self.center = 0
        self.nsamples_total = len(all_data)

        if nsamples > self.nsamples_total - offset:
            raise ValueError(
                'Requested number of samples is larger than the available {} samples.'.format(self.nsamples_total))

        self.data_array = all_data[offset:nsamples + offset]
