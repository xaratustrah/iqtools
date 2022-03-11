"""
Class for IQ Data
Tektronix (TM) X-COM XDATData

Xaratustrah Juli 2020

"""

import datetime
import os
import struct
import logging as log
import numpy as np
from .iqbase import IQBase
import xml.etree.ElementTree as et


class XDATData(IQBase):
    def __init__(self, filename, header_filename):
        super().__init__(filename)

        # Additional fields in this subclass
        self.center = 0
        self.acq_bw = 0
        self.date_time = ''

        self.header_filename = header_filename
        self.read_header()

    def read(self, nframes=10, lframes=1024, sframes=0):
        self.read_samples(nframes * lframes, offset=sframes * lframes)

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
            raise ValueError(
                "File size does not match total number of samples. Aborting...")

        if nsamples > self.nsamples_total - offset:
            raise ValueError(
                'Requested number of samples is larger than the available {} samples.'.format(self.nsamples_total))

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

    def read_header(self):
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
