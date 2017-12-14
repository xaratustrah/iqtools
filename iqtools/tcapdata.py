"""
Class for IQ Data
TCAP format

Xaratustrah Aug-2015



TCAP format information:

- Each file contains 15625 blocks

- Each block is 2^17=131072 BYTES of data + 88 bytes of header

- Each sample is 4 bytes = 32bits (2 I + 2 Q bytes), hence each block contains
32768 complex valued samples

- Sampling frequency is 312500 sps, thus the data of a block give a resolution
frequency of 312500 / 32768 = 9.5 Hz per block

- To double the frequency resolution one can take two consecutive blocks which
mean 4.7 Hz for two consecutive blocks

- Either from one block or two blocks a frame can be created.

- An FFT is done on each frame. 10 such FFTs can be averaged to reduce noise.

"""

import datetime
import os
import struct
import logging as log
import numpy as np
from iqtools.iqbase import IQBase


class TCAPData(IQBase):
    def __init__(self, filename, header_filename):
        super().__init__(filename)

        if not header_filename:
            log.info('No TCAP header filename provided.')

        self.header_filename = header_filename

        # Additional fields in this subclass
        self.tcap_scalers = None
        self.tcap_pio = None

        self.version = ''
        self.adc_range = 0
        self.block_count = 0
        self.block_size = 0
        self.frame_size = 0
        self.decimation = 0
        self.trigger_time = 0
        self.segment_blocks = 0

        self.fs = 10e6 / (2 ** self.decimation)  # usually 312500
        # center is usually 1.6e5

        self.text_header_parser()

    @property
    def dictionary(self):
        return {'center': self.center,
                'nsamples_total': self.nsamples_total,
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
                self.nsamples_total / self.fs) + '\n' + \
            '<font size="4" color="green">No. Samples:</font> {} <br>'.format(self.nsamples_total) + '\n' + \
            '<font size="4" color="green">Sampling rate:</font> {} <font size="4" color="green">[sps]</font><br>'.format(
                self.fs) + '\n' + \
            '<font size="4" color="green">Center freq.:</font> {} <font size="4" color="green">[Hz]</font><br>'.format(
                self.center) + '\n' + \
            '<font size="4" color="green">Date and Time:</font> {} <br>'.format(
                self.date_time) + '\n'

    def read(self, nframes=10, lframes=1024, sframes=1):
        """
        Read TCAP fiels *.dat
        :param nframes:
        :param lframes:
        :param sframes:
        :return:
        """

        BLOCK_HEADER_SIZE = 88
        BLOCK_DATA_SIZE = 2 ** 17
        BLOCK_SIZE = BLOCK_HEADER_SIZE + BLOCK_DATA_SIZE

        self.lframes = lframes
        self.nframes = nframes
        self.sframes = sframes

        filesize = os.path.getsize(self.filename)
        # each file contains 15625 blocks
        if not filesize == 15625 * BLOCK_SIZE:
            log.info(
                "File size does not match block sizes times total number of blocks. Aborting...")
            return

        # read header section
        with open(self.filename, 'rb') as f:
            tfp = f.read(12)
            pio = f.read(12)
            scalers = f.read(64)

        self.date_time = self.parse_tcap_tfp(tfp)
        self.tcap_pio = pio
        self.tcap_scalers = scalers

        data_section_size = self.frame_size - BLOCK_HEADER_SIZE
        n_iq_samples = data_section_size / 2 / 2  # two bytes for I and two bytes for Q
        self.nframes_tot = int(self.segment_blocks * n_iq_samples / nframes)
        self.nsamples_total = self.segment_blocks * n_iq_samples

        # 4 comes from 2 times 2 byte integer for I and Q
        total_n_bytes = 4 * nframes * lframes
        start_n_bytes = 4 * (sframes - 1) * lframes

        ba = bytearray()
        try:
            with open(self.filename, 'rb') as f:
                f.seek(BLOCK_HEADER_SIZE + start_n_bytes)
                for i in range(total_n_bytes):
                    if not f.tell() % BLOCK_SIZE:
                        log.info(
                            'File pointer before jump: {}'.format(f.tell()))
                        log.info(
                            "Reached end of block {}. Now skipoing header of block {}!".format(
                                int(f.tell() / BLOCK_SIZE),
                                int(
                                    f.tell() / BLOCK_SIZE) + 1))
                        f.seek(88, 1)
                        log.info('File pointer after jump: {}'.format(f.tell()))
                    # using bytearray.extend is much faster than using +=
                    ba.extend(f.read(1))
        except:
            log.error('File seems to end here!')
            return

        log.info('Total bytes read: {}'.format(len(ba)))

        # big endian 16 bit for I and 16 bit for Q
        self.data_array = np.frombuffer(ba, '>i2')
        self.data_array = self.data_array.astype(np.float32)
        self.data_array = self.data_array * self.scale
        self.data_array = self.data_array.view(np.complex64)

    def read_block(self, block_no):
        """
        Read the specified block between 1 and 15625.
        """
        BLOCK_HEADER_SIZE = 88
        BLOCK_DATA_SIZE = 2 ** 17
        BLOCK_SIZE = BLOCK_HEADER_SIZE + BLOCK_DATA_SIZE

        try:
            with open(self.filename, 'rb') as f:
                f.seek((block_no - 1) * BLOCK_SIZE)
                tfp = f.read(12)
                pio = f.read(12)
                scalers = f.read(64)
                ba = f.read(131072)
        except:
            log.error('File seems to end here!')
            return

        self.date_time = self.parse_tcap_tfp(tfp)
        self.tcap_pio = pio
        self.tcap_scalers = scalers

        log.info('Total bytes read: {}'.format(len(ba)))

        # big endian 16 bit for I and 16 bit for Q
        self.data_array = np.frombuffer(ba, '>i2')
        self.data_array = self.data_array.astype(np.float32)
        self.data_array = self.data_array * self.scale
        self.data_array = self.data_array.view(np.complex64)
        return self.data_array

    def get_frame(self, first, second):
        """
        Make a frame by connecting two blocks
        """
        array = np.zeros(2 * 32768, dtype=np.complex64)
        array[0:32768] = self.read_block(first)
        array[32768:] = self.read_block(second)
        return array

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
        #sem7 = (tfp[11] >> 4) & 0x0f

        year = int(self.file_basename[0:4])
        days = int(dh * 100 + dt * 10 + du)
        hours = int(ht * 10 + hu)
        minutes = int(mt * 10 + mu)
        seconds = int(st * 10 + su)
        microseconds = int(1000 * (sem1 * 1e-1 + sem2 * 1e-2 + sem3 *
                                   1e-3 + sem4 * 1e-4 + sem5 * 1e-5 + sem6 * 1e-6))
        ts = datetime.datetime(year, 1, 1, hours, minutes, seconds,
                               microseconds) + datetime.timedelta(days - 1)
        return ts.strftime('%Y-%m-%d %H:%M:%S')

    def text_header_parser(self):
        """
        Parse text headers
        Returns
        -------

        """
        dic = {}
        with open(self.header_filename) as f:
            for line in f:
                name, var = line.split()
                dic[name.strip()] = var
        self.version = dic['version']
        self.center = float(dic['center_freq'])
        self.adc_range = float(dic['adc_range'])
        self.scale = float(dic['data_scale'])
        self.block_count = int(dic['block_count'])
        self.block_size = int(dic['block_size'])
        self.frame_size = int(dic['frame_size'])
        self.decimation = int(dic['decimation'])
        self.trigger_time = float(dic['trigger_time'])
        self.segment_blocks = int(dic['segment_blocks'])
        return dic
