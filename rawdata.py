"""
Class for IQ Data
RAW formats

Xaratustrah Aug-2015

"""

import numpy as np
import time, os
from iqbase import IQBase


class RAWData(IQBase):
    def __init__(self, filename):
        super().__init__(filename)

    @property
    def dictionary(self):
        return {'center': self.center,
                'number_samples': self.number_samples,
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
                self.number_samples / self.fs) + '\n' + \
            '<font size="4" color="green">No. Samples:</font> {} <br>'.format(self.number_samples) + '\n' + \
            '<font size="4" color="green">Sampling rate:</font> {} <font size="4" color="green">[sps]</font><br>'.format(
                self.fs) + '\n' + \
            '<font size="4" color="green">Center freq.:</font> {} <font size="4" color="green">[Hz]</font><br>'.format(
                self.center) + '\n' + \
            '<font size="4" color="green">Span:</font> {} <font size="4" color="green">[Hz]</font><br>'.format(
                self.span) + '\n' + \
            '<font size="4" color="green">Date and Time:</font> {} <br>'.format(self.date_time) + '\n'

    def read(self, nframes=10, lframes=1024, sframes=1):
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

        self.lframes = lframes
        self.data_array = all_data[start_n_bytes:start_n_bytes + total_n_bytes]
