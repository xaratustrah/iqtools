"""
Class for IQ Data
GNU Radio simple binary format reader

xaratustrah@github Aug-2018

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
