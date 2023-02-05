"""
Class for TIQ format

xaratustrah@github Aug-2015

"""

import os
import logging as log
import numpy as np
import xml.etree.ElementTree as et
from .iqbase import IQBase


class TIQData(IQBase):
    def __init__(self, filename):
        super().__init__(filename)

        # Additional fields in this subclass
        self.date_time = ''
        self.span = 0.0
        self.center = 0.0
        self.acq_bw = 0.0
        self.rf_att = 0.0
        self.rbw = 0.0
        self.data_offset = 0

        self.header = ''
        self.read_header()

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

        total_n_bytes = 8 * nsamples  # 8 comes from 2 times 4 byte integer for I and Q
        start_n_bytes = 8 * offset

        # file might have the correcct size, but the data not copied fully
        try:
            with open(self.filename, 'rb') as f:
                f.seek(self.data_offset + start_n_bytes)
                ba = f.read(total_n_bytes)
        except:
            log.error('File seems to end here!')
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
        """Parse TIQ header
        The following information are extracted. Data needs to be normalized over 50 ohm.

        AcquisitionBandwidth
        Frequency
        File name
        Data I and Q [Unit is Volt]
        Data Offset
        DateTime
        NumberSamples
        Resolution Bandwidth
        RFAttenuation (it is already considered in the data scaling, no need to use this value, only for info)
        Sampling Frequency
        Span
        Voltage Scaling
        """

        ba = bytearray('', encoding='UTF-8')
        b = b''
        with open(self.filename, 'rb') as f:
            while b != b'\n':
                b = f.read(1)
                ba.extend(b)

        self.data_offset = int(ba.decode().split("\"")[1])

        with open(self.filename, 'rb') as f:
            ba = f.read(self.data_offset)
        self.header = ba
        xml_tree_root = et.fromstring(ba)

        self.date_time = [e.text for e in xml_tree_root.iter(
            '*') if 'DateTime' in e.tag][0]
        self.center = float([e.text for e in xml_tree_root.iter(
            '*') if 'Frequency' in e.tag and 'Sampling' not in e.tag][0])
        self.acq_bw = float([e.text for e in xml_tree_root.iter(
            '*') if 'AcquisitionBandwidth' in e.tag][0])
        self.nsamples_total = int(
            [e.text for e in xml_tree_root.iter('*') if 'NumberSamples' in e.tag][0])
        self.rf_att = float([e.text for e in xml_tree_root.iter(
            '*') if 'RFAttenuation' in e.tag][0])
        self.fs = float([e.text for e in xml_tree_root.iter(
            '*') if 'SamplingFrequency' in e.tag][0])
        self.scale = float(
            [e.text for e in xml_tree_root.iter('*') if 'Scaling' in e.tag][0])

        for elem in xml_tree_root.iter('NumericParameter'):
            if 'name' in elem.attrib and elem.attrib['name'] == 'Span' and (elem.attrib['pid'] == 'specanrange' or elem.attrib['pid'] == 'globalrange'):
                self.span = float(elem.find('Value').text)

        self.rbw = 0.0
        for elem in xml_tree_root.iter('NumericParameter'):
            if 'name' in elem.attrib and elem.attrib['name'] == 'Resolution Bandwidth' and elem.attrib['pid'] == 'fmtRBW':
                self.rbw = float(elem.find('Value').text)

    def save_header(self):
        """Saves the header byte array into a txt tile.
        """        

        with open(self.filename_wo_ext + '.xml', 'wb') as f3:
            f3.write(self.header)
        log.info("Header saved in an xml file.")
