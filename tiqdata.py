"""
Class for IQ Data
TIQ format

Xaratustrah Aug-2015

"""

import os
import logging as log
import numpy as np
import xml.etree.ElementTree as et
from iqbase import IQBase


class TIQData(IQBase):
    def __init__(self, filename):
        super().__init__(filename)

        # Additional fields in this subclass
        self.acq_bw = 0.0
        self.rbw = 0.0
        self.rf_att = 0.0
        self.span = 0.0
        self.scale = 0.0
        self.header = ''

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
                'rf_att': self.rf_att,
                'span': self.span,
                'acq_bw': self.acq_bw,
                'file_name': self.filename,
                'rbw': self.rbw}

    def __str__(self):
        return \
            '<font size="4" color="green">Record length:</font> {:.2e} <font size="4" color="green">[s]</font><br>'.format(
                self.nsamples / self.fs) + '\n' + \
            '<font size="4" color="green">No. Samples:</font> {} <br>'.format(self.nsamples) + '\n' + \
            '<font size="4" color="green">Sampling rate:</font> {} <font size="4" color="green">[sps]</font><br>'.format(
                self.fs) + '\n' + \
            '<font size="4" color="green">Center freq.:</font> {} <font size="4" color="green">[Hz]</font><br>'.format(
                self.center) + '\n' + \
            '<font size="4" color="green">Span:</font> {} <font size="4" color="green">[Hz]</font><br>'.format(
                self.span) + '\n' + \
            '<font size="4" color="green">Acq. BW.:</font> {} <br>'.format(self.acq_bw) + '\n' + \
            '<font size="4" color="green">RBW:</font> {} <br>'.format(self.rbw) + '\n' + \
            '<font size="4" color="green">RF Att.:</font> {} <br>'.format(self.rf_att) + '\n' + \
            '<font size="4" color="green">Date and Time:</font> {} <br>'.format(self.date_time) + '\n'

    def read(self, nframes=10, lframes=1024, sframes=1):

        """Process the tiq input file.
        Following information are extracted, except Data offset, all other are stored in the dic. Data needs to be normalized over 50 ohm.

        AcquisitionBandwidth
        Frequency
        File name
        Data I and Q [Unit is Volt]
        Data_offset
        DateTime
        NumberSamples
        Resolution Bandwidth
        RFAttenuation (it is already considered in the data scaling, no need to use this value, only for info)
        Sampling Frequency
        Span
        Voltage Scaling
        """

        self.lframes = lframes
        self.nframes = nframes

        filesize = os.path.getsize(self.filename)
        log.info("File size is {} bytes.".format(filesize))

        with open(self.filename) as f:
            line = f.readline()
        data_offset = int(line.split("\"")[1])

        with open(self.filename, 'rb') as f:
            ba = f.read(data_offset)

        xml_tree_root = et.fromstring(ba)

        for elem in xml_tree_root.iter(tag='{http://www.tektronix.com}AcquisitionBandwidth'):
            self.acq_bw = float(elem.text)
        for elem in xml_tree_root.iter(tag='{http://www.tektronix.com}Frequency'):
            self.center = float(elem.text)
        for elem in xml_tree_root.iter(tag='{http://www.tektronix.com}DateTime'):
            self.date_time = str(elem.text)
        for elem in xml_tree_root.iter(tag='{http://www.tektronix.com}NumberSamples'):
            self.nsamples = int(elem.text)  # this entry matches (filesize - data_offset) / 8) well
        for elem in xml_tree_root.iter('NumericParameter'):
            if 'name' in elem.attrib and elem.attrib['name'] == 'Resolution Bandwidth' and elem.attrib['pid'] == 'rbw':
                self.rbw = float(elem.find('Value').text)
        for elem in xml_tree_root.iter(tag='{http://www.tektronix.com}RFAttenuation'):
            self.rf_att = float(elem.text)
        for elem in xml_tree_root.iter(tag='{http://www.tektronix.com}SamplingFrequency'):
            self.fs = float(elem.text)
        for elem in xml_tree_root.iter('NumericParameter'):
            if 'name' in elem.attrib and elem.attrib['name'] == 'Span' and elem.attrib['pid'] == 'globalrange':
                self.span = float(elem.find('Value').text)
        for elem in xml_tree_root.iter(tag='{http://www.tektronix.com}Scaling'):
            self.scale = float(elem.text)

        log.info("Center {0} Hz, span {1} Hz, sampling frequency {2} scale factor {3}.".format(self.center, self.span,
                                                                                               self.fs, self.scale))
        log.info("Header size {} bytes.".format(data_offset))

        log.info("Proceeding to read binary section, 32bit (4 byte) little endian.")
        log.info('Total number of samples: {}'.format(self.nsamples))
        log.info("Frame length: {0} data points = {1}s".format(lframes, lframes / self.fs))
        self.nframes_tot = int(self.nsamples / lframes)
        log.info("Total number of frames: {0} = {1}s".format(self.nframes_tot, self.nsamples / self.fs))
        log.info("Start reading at offset: {0} = {1}s".format(sframes, sframes * lframes / self.fs))
        log.info("Reading {0} frames = {1}s.".format(nframes, nframes * lframes / self.fs))

        self.header = ba

        total_n_bytes = 8 * nframes * lframes  # 8 comes from 2 times 4 byte integer for I and Q
        start_n_bytes = 8 * (sframes - 1) * lframes

        try:
            with open(self.filename, 'rb') as f:
                f.seek(data_offset + start_n_bytes)
                ba = f.read(total_n_bytes)
        except:
            log.error('File seems to end here!')
            return

        # return a numpy array of little endian 8 byte floats (known as doubles)
        self.data_array = np.fromstring(ba, dtype='<i4')  # little endian 4 byte ints.
        # Scale to retrieve value in Volts. Augmented assignment does not work here!
        self.data_array = self.data_array * self.scale
        self.data_array = self.data_array.view(
            dtype='c16')  # reinterpret the bytes as a 16 byte complex number, which consists of 2 doubles.

        log.info("Output complex array has a size of {}.".format(self.data_array.size))
        # in order to read you may use: data = x.item()['data'] or data = x[()]['data'] other wise you get 0-d error

    def save_header(self):
        """Saves the header byte array into a txt tile."""
        with open(self.filename_wo_ext + '.xml', 'wb') as f3:
            f3.write(self.header)
        log.info("Header saved in an xml file.")
