"""
Class for reading LeCroy 584AM files

Xaratustrah Sep-2018

many thanks to github.com/nerdull for reverse engineering
an old code by M. Hausmann from 1992

"""

import numpy as np
import struct
import datetime
import os
from iqtools.iqbase import IQBase


class LCData(IQBase):
    def __init__(self, filename):
        super().__init__(filename)
        self.fs = 4e9
        self.center = 0

    @property
    def dictionary(self):
        return {'center': self.center,
                'nsamples_total': self.nsamples_total,
                'fs': self.fs,
                'data': self.data_array,
                'DateTime': self.date_time,
                'file_name': self.filename}

    def __str__(self):
        return \
            '<font size="4" color="green">Record length:</font> {:.2e} <font size="4" color="green">[s]</font><br>'.format(
                self.nsamples_total / self.fs) + '\n' + \
            '<font size="4" color="green">No. Samples:</font> {} <br>'.format(self.nsamples_total) + '\n' + \
            '<font size="4" color="green">Sampling rate:</font> {} <font size="4" color="green">[sps]</font><br>'.format(
                self.fs) + '\n' + \
            '<font size="4" color="green">Center freq.:</font> {} <font size="4" color="green">[Hz]</font><br>'.format(
                self.center) + '\n' + \
            '<font size="4" color="green">Date and Time:</font> {} <br>'.format(
                self.date_time) + '\n'

    def read_complete_file(self):
        """
        Read a complete LeCroy file
        :return:
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
