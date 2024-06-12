"""
Class for IQ Data
GNU Radio simple binary format reader

xaratustrah@github
Aug-2018
June 2024

"""

import numpy as np
import time
import os
from .iqbase import IQBase


class GRData(IQBase):
    def __init__(self, filename, fs, center=0, date_time=""):
        super().__init__(filename)
        # Additional fields in this subclass
        self.date_time = date_time
        self.center = center
        self.fs = fs
        # each complex64 sample is 8 bytes on disk
        self.nsamples_total = os.path.getsize(filename) / 8

    def read(self, nframes=10, lframes=1024, sframes=0):
        """Read a section of the file.

        Args:
            nframes (int, optional): Number of frames to be read. Defaults to 10.
            lframes (int, optional): Length of each frame. Defaults to 1024.
            sframes (int, optional): Starting frame. Defaults to 0.
        """        

        self.read_samples(nframes * lframes, offset=sframes * lframes)

    def read_samples(self, nsamples, offset=0):
        """Read samples.

        Args:
            nsamples (int): Number of samples to read from file
            offset (int, optional): _description_. Defaults to 0.

        Raises:
            ValueError: Raises if the requested number of samples is larger than available
        """        
        if nsamples > self.nsamples_total - offset:
            raise ValueError(
                'Requested number of samples is larger than the available {} samples.'.format(self.nsamples_total))

        x = np.fromfile(self.filename, dtype=np.complex64)
        self.data_array = x[offset:nsamples + offset]