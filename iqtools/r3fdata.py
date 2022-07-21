"""
Class for R3F Data

Xaratustrah Jul-2022

"""

import os
import numpy as np
from .iqbase import IQBase


class R3FData(IQBase):
    def __init__(self, filename):
        super().__init__(filename)

        # Additional fields in this subclass
        self.date_time = ''
        self.center = 0.0
        self.acq_bw = 0.0
        
        self.read_header()
        self.cplx_adc_data = self.read_all_blocks()


    
    def read(self, nframes=10, lframes=1024, sframes=0):
        self.read_samples(nframes * lframes, offset=sframes * lframes)

    def read_samples(self, nsamples, offset=0):
        self.data_array = self.cplx_adc_data[offset : offset + nsamples]
    
    
    def read_all_blocks(self):
        return self.read_blocks(self.nblocks)

        
    def read_blocks(self, nblocks=1):

        # each block contains 8178 samples each 2 bytes + an additional 28 byte footer making a total size of 16384
        # since fs is fixed to 112msps, each block will be ca. 73us long
        
        adc_data = np.zeros(nblocks * 8178)
        f = open(self.filename, 'rb')
        f.seek(16384) # jump header
        for ii in range(nblocks):
            #print(ii)
            ba = f.read(16384)
            # 16 bit signed integer little endian
            # since we divide 16384 by 2, then we ignore the last 14 not 28
            adc_data[ii * 8178 : (ii+1) * 8178] = np.frombuffer(ba, dtype='<i2')[:-14]
        
        size = len(adc_data)
        xaxis = np.linspace(0,size * 1/self.fs, size)
        lo_i = np.sin(self.center * (2*np.pi) * xaxis)
        lo_q = np.cos(self.center * (2*np.pi)* xaxis)
        del(xaxis)
        ii = adc_data * lo_i
        qq = adc_data * lo_q
        del(lo_i)
        del(lo_q)
        c = np.reshape(np.concatenate((ii, qq)), (2, -1)).T
        result = 1j*c[...,1]; result += c[...,0]
        return result

    def read_header(self):
        
            size = os.path.getsize(self.filename)

            # file size must be multiple integer of 16384
            assert not size % 2**14

            # first block is header
            self.nblocks = int(size / 2**14) - 1

            self.nsamples_total = self.nblocks * 8178

            f = open(self.filename, 'rb')
            
            f.seek(1024)
            ref_level = np.frombuffer(f.read(8), dtype='<f8')[0] # dBm
            self.center = np.frombuffer(f.read(8), dtype='<f8')[0] # Hz
            
            f.seek(2048 + 4+ 6*4 + 8)
            self.fs = np.frombuffer(f.read(8), dtype='<f8')[0] # samples / s
            self.acq_bw = np.frombuffer(f.read(8), dtype='<f8')[0]
            f.seek(2048 + 4 + 6*4 + 8 + 8 + 8 + 4 + 4 + 7*4 + 8 + 8 + 7* 4 + 4 + 8)
            
            dt = np.frombuffer(f.read(7 * 4), dtype='<i4')
            self.date_time = f'{dt[0]}y{dt[1]}m{dt[2]}d{dt[3]}h{dt[4]}m{dt[5]}s{dt[6]}'
            f.close()
        
        