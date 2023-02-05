"""
Class for reading LeCroy 584AM files

xaratustrah@github Sep-2018

Many thanks to [github.com/nerdull](https://www.github.com/nerdull) for reverse engineering
an old code by M. Hausmann from 1992

"""

import numpy as np
import struct
import datetime
import os
from .iqbase import IQBase


class LCData(IQBase):
    def __init__(self, filename):
        super().__init__(filename)

        # fixed features
        self.fs = 4e9
        self.center = 0

        # Additional fields in this subclass
        self.date_time = time.ctime(os.path.getctime(self.filename))

    def read(self, nframes=10, lframes=1024, sframes=0):
        """Read a section of the file.

        Args:
            nframes (int, optional): Number of frames to be read. Defaults to 10.
            lframes (int, optional): Length of each frame. Defaults to 1024.
            sframes (int, optional): Starting frame. Defaults to 0.
        """        

        self.read_samples(nframes * lframes, offset=sframes * lframes)

    def read_complete_file(self):
        """Reads a complete file.

        Returns:
            ndarray: Returns the complete data array
        """        

        filesize = os.path.getsize(self.filename)
        with open(self.filename, 'rb') as f:
            file_data = f.read()
        # 45th byte determines the endianness
        # one = little endian
        biglit = ''
        if struct.unpack_from('b', file_data, 45)[0]:
            biglit = '<'
        else:
            biglit = '>'

        hdr_len = struct.unpack_from(
            '{}I'.format(biglit), file_data, 47)[0] + 11
        self.nsamples_total = struct.unpack_from(
            '{}I'.format(biglit), file_data, 71)[0]

        self.vert_gain = struct.unpack_from(
            '{}f'.format(biglit), file_data, 167)[0]
        self.vert_offset = struct.unpack_from(
            '{}f'.format(biglit), file_data, 171)[0]
        self.horiz_interval = struct.unpack_from(
            '{}f'.format(biglit), file_data, 187)[0]
        self.horiz_offset = struct.unpack_from(
            '{}f'.format(biglit), file_data, 191)[0]
        self.vert_unit = struct.unpack_from('c', file_data, 207)[
            0].decode("utf-8")
        self.horiz_unit = struct.unpack_from('c', file_data, 255)[
            0].decode("utf-8")

        sec, mt, hr, dd, mm, yy = struct.unpack_from(
            '{}dbbbbI'.format(biglit), file_data, 307)
        try:
            dt_obj = datetime.datetime(yy, mm, dd, hr, mt, int(
                sec), int((sec - int(sec)) * 1e6))
            self.date_time = dt_obj.strftime("%Y-%m-%d_%H:%M:%S.%f")
        except ValueError:
            self.date_time = ''

        self.data_array = np.frombuffer(
            file_data, np.int8, offset=hdr_len) * self.vert_gain
        return self.data_array


# ------------------------

# Class tester

if __name__ == '__main__':
    import sys
    import os
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    filename = sys.argv[1]
    mydata = LCData(filename)
    mydata.read_complete_file()
    tt = np.arange(mydata.nsamples_total) * 1 / mydata.fs * 1e6
    plt.plot(tt, mydata.data_array)
    plt.grid()
    plt.xlabel('Time [us]')
    plt.ylabel('Voltage [v]')
    plt.title('{}{}'.format(os.path.basename(filename), mydata.date_time))
    plt.savefig('{}.png'.format(filename), dpi=600)
    print(mydata)
