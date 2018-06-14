"""
Class for IQ Data
TDMS format

Xaratustrah Aug-2015

"""

import os
import time
import logging as log
import numpy as np
from iqtools.iqbase import IQBase
import pytdms


class TDMSData(IQBase):
    def __init__(self, filename):
        super().__init__(filename)

        # Additional fields in this subclass
        self.tdms_first_rec_size = 0
        self.tdms_other_rec_size = 0
        self.tdms_nSamplesPerRecord = 0
        self.tdms_nRecordsPerFile = 0
        self.information_read = False

        self.rf_att = 0.0
        self.scale = 0.0

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
                'rf_att': self.rf_att,
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
            '<font size="4" color="green">RF Att.:</font> {} <br>'.format(self.rf_att) + '\n' + \
            '<font size="4" color="green">Date and Time:</font> {} <br>'.format(
                self.date_time) + '\n'

    def read_tdms_information(self, lframes=1):
        """
        Performs one read on the file in order to get the values
        :param lframes:
        :return:
        """
        # we need lframes here in order to calculate nframes_tot
        self.lframes = lframes

        # Usually size matters, but not in this case! because we only read 2 records, but anyway should be large enough.
        sz = os.path.getsize(self.filename)
        how_many = 0
        last_i_ff = 0
        last_q_ff = 0
        # We start with empty data
        objects = {}
        raw_data = {}

        # Read just 2 records in order to estimate the record sizes
        f = open(self.filename, "rb")
        while f.tell() < sz:
            try:
                objects, raw_data = pytdms.readSegment(
                    f, sz, (objects, raw_data))
            except:
                log.error('TDMS file seems to end here!')
                return

            if b"/'RecordData'/'I'" in raw_data and b"/'RecordData'/'Q'" in raw_data:
                # This record has both I and Q
                last_i = raw_data[b"/'RecordData'/'I'"][-1]
                last_q = raw_data[b"/'RecordData'/'Q'"][-1]
                offset = f.tell()

                if last_i_ff != last_i and last_q_ff != last_q:
                    how_many += 1
                    last_i_ff = last_i
                    last_q_ff = last_q
                    if how_many == 1:
                        self.tdms_first_rec_size = offset
                    if how_many == 2:
                        self.tdms_other_rec_size = offset - self.tdms_first_rec_size
                        break

        self.fs = float(objects[b'/'][3][b'IQRate'][1])
        self.rf_att = float(objects[b'/'][3][b'RFAttentuation'][1])
        self.center = float(objects[b'/'][3][b'IQCarrierFrequency'][1])
        self.date_time = time.ctime(os.path.getctime(self.filename))
        self.tdms_nSamplesPerRecord = int(
            objects[b'/'][3][b'NSamplesPerRecord'][1])
        self.tdms_nRecordsPerFile = int(
            objects[b'/'][3][b'NRecordsPerFile'][1])
        self.nsamples_total = self.tdms_nSamplesPerRecord * self.tdms_nRecordsPerFile
        self.nframes_tot = int(self.nsamples_total / lframes)

        self.information_read = True

    def read(self, nframes=1, lframes=1, sframes=1):
        """
        Read from TDMS Files: Check the amount needed corresponds to how many records. Then read those records only
        and from them return only the desired amount. This way the memory footprint is smallest passible and it is
        also fast.
        :param nframes:
        :param lframes:
        :param sframes:
        :return:
        """

        if not self.information_read:
            self.read_tdms_information(lframes)

        self.lframes = lframes
        self.nframes = nframes
        self.sframes = sframes

        total_n_bytes = nframes * lframes
        start_n_bytes = (sframes - 1) * lframes

        # let's see this amount corresponds to which start record
        # start at the beginning of
        start_record = int(start_n_bytes / self.tdms_nSamplesPerRecord) + 1
        starting_sample_within_start_record = start_n_bytes % self.tdms_nSamplesPerRecord

        # See how many records should we read, considering also the half-way started record?
        n_records = int((starting_sample_within_start_record +
                         total_n_bytes) / self.tdms_nSamplesPerRecord) + 1

        # that would be too much
        if start_record + n_records > self.tdms_nRecordsPerFile:
            return

        # instead of real file size find out where to stop
        absolute_size = self.tdms_first_rec_size + \
            (start_record + n_records - 2) * self.tdms_other_rec_size

        # We start with empty data
        objects = {}
        raw_data = {}

        f = open(self.filename, "rb")  # Open in binary mode for portability

        # While there's still something left to read
        while f.tell() < absolute_size:
            # loop until first record is filled up
            # we always need to read the first record.
            # don't jump if start record is 1, just go on reading
            if start_record > 1 and f.tell() == self.tdms_first_rec_size:
                # reached the end of first record, now do the jump
                f.seek(f.tell() + (start_record - 2)
                       * self.tdms_other_rec_size)
            if f.tell() == self.tdms_first_rec_size:
                log.info('Reached end of first record.')
            # Now we read record by record
            try:
                objects, raw_data = pytdms.readSegment(
                    f, absolute_size, (objects, raw_data))
            except:
                log.error('File seems to end here!')
                return
        # ok, now close the file
        f.close()

        # up to now, we have read only the amount of needed records times number of samples per record
        # this is of course more than what we actually need.

        # convert array.array to np.array
        ii = np.frombuffer(raw_data[b"/'RecordData'/'I'"], dtype=np.int16)
        qq = np.frombuffer(raw_data[b"/'RecordData'/'Q'"], dtype=np.int16)

        # get rid of duplicates at the beginning if start record is larger than one
        if start_record > 1:
            ii = ii[self.tdms_nSamplesPerRecord:]
            qq = qq[self.tdms_nSamplesPerRecord:]

        ii = ii[starting_sample_within_start_record:starting_sample_within_start_record + total_n_bytes]
        qq = qq[starting_sample_within_start_record:starting_sample_within_start_record + total_n_bytes]

        # Vectorized is slow, so do interleaved copy instead
        self.data_array = np.zeros(2 * total_n_bytes, dtype=np.float32)
        self.data_array[::2], self.data_array[1::2] = ii, qq
        self.data_array = self.data_array.view(np.complex64)
        gain = np.frombuffer(
            raw_data[b"/'RecordHeader'/'gain'"], dtype=np.float64)
        self.scale = gain[0]
        self.data_array = self.data_array * self.scale
        log.info("TDMS Read finished.")

    def read_complete_file(self):
        """
        Read a complete TDMS file
        :return:
        """

        if not self.information_read:
            self.read_tdms_information()

        objects, raw_data = pytdms.read(self.filename)

        # convert array.array to np.array
        ii = np.frombuffer(raw_data[b"/'RecordData'/'I'"], dtype=np.int16)
        qq = np.frombuffer(raw_data[b"/'RecordData'/'Q'"], dtype=np.int16)

        # Vectorized is slow, so do interleaved copy instead

        len = np.shape(ii)[0]
        self.data_array = np.zeros(2 * len, dtype=np.float32)
        self.data_array[::2], self.data_array[1::2] = ii, qq
        self.data_array = self.data_array.view(np.complex64)
        gain = np.frombuffer(
            raw_data[b"/'RecordHeader'/'gain'"], dtype=np.float64)
        self.scale = gain[0]
        self.data_array = self.data_array * self.scale
        log.info("TDMS Read finished.")
