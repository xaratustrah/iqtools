"""
Class for IQ Data
Tektronix X-COM XDATData

Xaratustrah Juli 2020

"""

import datetime
import os
import struct
import logging as log
import numpy as np
from iqtools.iqbase import IQBase
import xml.etree.ElementTree as et


class XDATData(IQBase):
    def __init__(self, filename, header_filename):
        super().__init__(filename)

        if not header_filename:
            log.info('No XDAT header filename provided.')

        self.header_filename = header_filename
        self.header_parser()

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

    def read_samples(self, nsamples, offset=0):
        """
        Read a specific number of samples
        Parameters
        ----------
        nsamples How many samples to read
        offset Either start from the beginning, i.e. 0 or start at a different offset.
        The X-COM XDAT format can be described as a 16 integer interlaced I & Q file. I and Q are each a 16 bit little endian integer. I & Q are interlaced together in a single file or memory buffer with order being I,Q.

        Returns
        -------

        """
        filesize = os.path.getsize(self.filename)
        # each file contains 15625 blocks
        if not filesize == 4 * self.nsamples_total:
            log.info(
                "File size does not match total number of samples. Aborting...")
            return

        assert nsamples < (self.nsamples_total - offset)

        total_n_bytes = 8 * nsamples  # 8 comes from 2 times 4 byte integer for I and Q
        start_n_bytes = 8 * offset

        try:
            with open(self.filename, 'rb') as f:
                f.seek(start_n_bytes)
                ba = f.read(total_n_bytes)
        except Exception as e:
            log.error(e + 'File seems to end here!')
            return

        # return a numpy array of little endian 8 byte floats (known as doubles)
        # little endian 4 byte ints.
        self.data_array = np.fromstring(ba, dtype='<i4')
        # Scale to retrieve value in Volts. Augmented assignment does not work here!
        self.data_array = self.data_array * self.scale
        self.data_array = self.data_array.view(
            dtype='c16')  # reinterpret the bytes as a 16 byte complex number, which consists of 2 doubles.

        log.info("Output complex array has a size of {}.".format(
            self.data_array.size))
        # in order to read you may use: data = x.item()['data'] or data = x[()]['data'] other wise you get 0-d error

    def header_parser(self):
        """
        Parse XDAT header file
        Returns
        -------

        """
        tree = et.parse(self.header_filename)
        root = tree.getroot()
        for feature in root.iter('recording'):
            self.center = float(feature.get('center_frequency'))
            self.scale = float(feature.get('acq_scale_factor'))
            self.acq_bw = float(feature.get('acquisition_bandwidth'))
            self.fs = float(feature.get('sample_rate'))
            self.date_time = feature.get('creation_time')

        for feature in root.iter('data'):
            self.nsamples_total = int(feature.get('samples'))
