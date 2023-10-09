"""
Class for IQ Data
CSV and TXT formats

xaratustrah@github Aug-2015

"""

import numpy as np
import time
import os
from .iqbase import IQBase


class CSVData(IQBase):
    def __init__(self, filename):
        super().__init__(filename)

        # Additional fields in this subclass
        self.center = 0.0
        self.date_time = time.ctime(os.path.getctime(self.filename))
        self.nsamples_total = sum(1 for line in open(filename)) - 1

    def read(self, nframes=10, lframes=1024, sframes=0):
        """Read a section of the file.

        Args:
            nframes (int, optional): Number of frames to be read. Defaults to 10.
            lframes (int, optional): Length of each frame. Defaults to 1024.
            sframes (int, optional): Starting frame. Defaults to 0.
        """        
        self.read_samples(nframes * lframes, offset=sframes * lframes)

    def read_samples(self, nsamples, offset=0):
        """Read samples. Requries the first line to be the header.
        Please also check the function:
            write_signal_to_csv
        in the `tools`.

        Args:
            nsamples (int): Number of samples to read from file
            offset (int, optional): _description_. Defaults to 0.

        Raises:
            ValueError: Raises if the requested number of samples is larger than available
        """        

        if nsamples > self.nsamples_total - offset:
            raise ValueError(
                'Requested number of samples is larger than the available {} samples.'.format(self.nsamples_total))

        x = np.genfromtxt(self.filename, dtype=np.float32, delimiter='|')
        self.fs = x[0, 0]
        self.center = x[0, 1]
        all_data = x[1:, :]
        all_data = all_data.view(np.complex64)[:, 0]

        self.data_array = all_data[offset:nsamples + offset]
