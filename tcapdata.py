"""
Class for IQ Data
TCAP format

Xaratustrah Aug-2015

"""

import datetime
import os
import struct
import logging as log
import numpy as np
from iqbase import IQBase


class TCAPData(IQBase):
    def __init__(self, filename):
        super().__init__(filename)

        # Additional fields in this subclass
        self.tcap_scalers = None
        self.tcap_pio = None
        self.information_read = False

    @property
    def dictionary(self):
        return {'center': self.center,
                'nsamples': self.nsamples,
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
                self.nsamples / self.fs) + '\n' + \
            '<font size="4" color="green">No. Samples:</font> {} <br>'.format(self.nsamples) + '\n' + \
            '<font size="4" color="green">Sampling rate:</font> {} <font size="4" color="green">[sps]</font><br>'.format(
                self.fs) + '\n' + \
            '<font size="4" color="green">Center freq.:</font> {} <font size="4" color="green">[Hz]</font><br>'.format(
                self.center) + '\n' + \
            '<font size="4" color="green">Date and Time:</font> {} <br>'.format(self.date_time) + '\n'

    def read_tcap_information(self, header_filename):
        """
        Read tcap information from separate filename
        Returns
        -------

        """
        self.information_read = True

    def read(self, nframes=10, lframes=1024, sframes=1):
        """
        Read TCAP fiels *.dat
        :param nframes:
        :param lframes:
        :param sframes:
        :return:
        """

        if not self.information_read:
            self.read_tcap_information(lframes)

        BLOCK_HEADER_SIZE = 88
        BLOCK_DATA_SIZE = 2 ** 17
        BLOCK_SIZE = BLOCK_HEADER_SIZE + BLOCK_DATA_SIZE

        self.lframes = lframes
        self.nframes = nframes
        filesize = os.path.getsize(self.filename)
        if not filesize == 15625 * BLOCK_SIZE:
            log.info("File size does not match block sizes times total number of blocks. Aborting...")
            return

        # read header section
        with open(self.filename, 'rb') as f:
            tfp = f.read(12)
            pio = f.read(12)
            scalers = f.read(64)

        # self.header = header
        # self.parse_tcap_header(header)
        self.date_time = self.parse_tcap_tfp(tfp)

        self.tcap_pio = pio
        self.tcap_scalers = scalers

        self.fs = 312500
        self.center = 1.6e5
        self.scale = 6.25e-2
        self.nframes_tot = int(15625 * 32768 / nframes)
        self.nsamples = 15625 * 32768

        total_n_bytes = 4 * nframes * lframes  # 4 comes from 2 times 2 byte integer for I and Q
        start_n_bytes = 4 * (sframes - 1) * lframes

        ba = bytearray()
        try:
            with open(self.filename, 'rb') as f:
                f.seek(BLOCK_HEADER_SIZE + start_n_bytes)
                for i in range(total_n_bytes):
                    if not f.tell() % 131160:
                        log.info('File pointer before jump: {}'.format(f.tell()))
                        log.info(
                            "Reached end of block {}. Now skipoing header of block {}!".format(
                                int(f.tell() / BLOCK_SIZE),
                                int(
                                    f.tell() / BLOCK_SIZE) + 1))
                        f.seek(88, 1)
                        log.info('File pointer after jump: {}'.format(f.tell()))
                    ba.extend(f.read(1))  # using bytearray.extend is much faster than using +=
        except:
            log.error('File seems to end here!')
            return

        log.info('Total bytes read: {}'.format(len(ba)))

        self.data_array = np.frombuffer(ba, '>i2')  # big endian 16 bit for I and 16 bit for Q
        self.data_array = self.data_array.astype(np.float32)
        self.data_array = self.data_array * self.scale
        self.data_array = self.data_array.view(np.complex64)

    def parse_binary_tcap_header(self, ba):
        version = ba[0:8]
        center_freq_np = np.fromstring(ba[8:16], dtype='>f8')[0]
        center_freq = struct.unpack('>d', ba[8:16])[0]
        adc_range = struct.unpack('>d', ba[16:24])[0]
        data_scale = struct.unpack('>d', ba[24:32])[0]
        block_count = struct.unpack('>Q', ba[32:40])[0]
        block_size = struct.unpack('>I', ba[40:44])[0]
        frame_size = struct.unpack('>I', ba[44:48])[0]
        decimation = struct.unpack('>H', ba[48:50])[0]
        config_flags = struct.unpack('>H', ba[50:52])[0]
        trigger_time = ba[500:512]
        # self.fs = 10**7 / 2 ** decimation

    def parse_tcap_tfp(self, ba):
        """
        Parses the TFP Header of TCAP DAT Files. This information is coded in BCD. The
        following table was taken form the original TCAP processing files in C.
         * +------------+---------------+---------------+---------------+---------------+
         * | bit #      | 15 - 12       | 11 - 8        | 7 - 4         | 3 - 0         |
         * +------------+---------------+---------------+---------------+---------------+
         * | timereg[0] | not defined   | not defined   | status        | days hundreds |
         * | timereg[1] | days tens     | days units    | hours tens    | hours units   |
         * | timereg[2] | minutes tens  | minutes units | seconds tens  | seconds units |
         * | timereg[3] | 1E-1 seconds  | 1E-2 seconds  | 1E-3 seconds  | 1E-4 seconds  |
         * | timereg[4] | 1E-5 seconds  | 1E-6 seconds  | 1E-7 seconds  | not defined   |
         * +------------+---------------+---------------+---------------+---------------+

         here we read the first 12 bytes ( 24 nibbles ) in the tfp byte array list. First 2 bytes
         should be ignored.

        :return:
        """
        tfp = list(ba)

        dh = (tfp[3] >> 0) & 0x0f

        dt = (tfp[4] >> 4) & 0x0f
        du = (tfp[4] >> 0) & 0x0f

        ht = (tfp[5] >> 4) & 0x0f
        hu = (tfp[5] >> 0) & 0x0f

        mt = (tfp[6] >> 4) & 0x0f
        mu = (tfp[6] >> 0) & 0x0f

        st = (tfp[7] >> 4) & 0x0f
        su = (tfp[7] >> 0) & 0x0f

        sem1 = (tfp[8] >> 4) & 0x0f
        sem2 = (tfp[8] >> 0) & 0x0f
        sem3 = (tfp[9] >> 4) & 0x0f
        sem4 = (tfp[9] >> 0) & 0x0f

        sem5 = (tfp[10] >> 4) & 0x0f
        sem6 = (tfp[10] >> 0) & 0x0f
        sem7 = (tfp[11] >> 4) & 0x0f

        days = dh * 100 + dt * 10 + du
        hours = ht * 10 + hu
        minutes = mt * 10 + mu
        seconds = st * 10 + su + sem1 * 1e-1 + sem2 * 1e-2 + sem3 * 1e-3 + sem4 * 1e-4 + sem5 * 1e-5 + sem6 * 1e-6 + sem7 * 1e-7

        ts_epoch = seconds + 60 * (minutes + 60 * (hours + 24 * days))
        ts = datetime.datetime.fromtimestamp(ts_epoch).strftime('%Y-%m-%d %H:%M:%S')
        return ts
