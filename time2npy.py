#!/usr/bin/env python

"""
This code converts data in TIQ format and extracts the data in numpy format
"""

import os, sys
from xml.dom import minidom
import xml.etree.ElementTree as et
import numpy as np
import matplotlib.pyplot as plt


def tiq2npy(filename, nframes, lframes, sframes):
    """
    Process the input file and return.
    """
    filesize = os.path.getsize(filename)
    log.info("File size is {} bytes.".format(filesize))
    filename_wo_ext = os.path.splitext(filename)[0]
    
    buf = bytearray(b'')
    ar = np.array([], dtype=complex)

    total_nbytes = 8 * nframes * lframes # 8 comes from 2 times 4 bit integer for I and Q
    start_nbytes = 8 * (sframes - 1 ) * lframes 
    global_counter = 0

    with open(filename, 'rb') as f:
        byte = f.read(1)
        global_counter += 1
        while byte != b'':
            buf += byte
            bufstr = buf.decode('utf-8')
            if (bufstr.endswith('</DataFile>')) :
                log.info("Found end of header section.")
                break
            byte = f.read(1)
            global_counter += 1

        xmltree = et.fromstring(bufstr)
        for elem in xmltree.iter(tag='{http://www.tektronix.com}Frequency'):
            center=float(elem.text)
        for elem in xmltree.iter(tag='{http://www.tektronix.com}MaxSpan'):
            span=float(elem.text)
        for elem in xmltree.iter(tag='{http://www.tektronix.com}Scaling'):
            scale=float(elem.text)
        for elem in xmltree.iter(tag='{http://www.tektronix.com}SamplingFrequency'):
            fs=float(elem.text)
        log.info("Center {0} Hz, span {1} Hz, sampling frequency {2} scale factor {3}.".format(center, span, fs, scale))
        log.info("Header size {} bytes.".format(global_counter))
        
        with open (filename_wo_ext + '.xml', 'w') as f3 : f3.write(bufstr)
        log.info("Header saved in an xml file.")
        
        log.info("Proceeding to read binary section, 32bit (4 byte) little endian.")

        global_counter = start_nbytes              # reset the global counter
        ba = f.read(4)
        global_counter += 4
        
        while ba != b'':
            I = int.from_bytes(ba, byteorder = 'little')

            ba = f.read(4)
            global_counter += 4
            Q = int.from_bytes(ba, byteorder = 'little')

            ar = np.append(ar, scale * complex(I, Q))
                
            if (global_counter >= total_nbytes - 1) : break
            else :
                ba = f.read(4)
                global_counter += 4
                
                sys.stdout.flush()
                sys.stdout.write('\rProgress: ' + str(int(global_counter*100/total_nbytes))+'%')
    print('\n')
    log.info("Output complex array has a size of {}.".format(ar.size))
    dic = {'center': center, 'span': span, 'fs': fs, 'scale':scale, 'data': ar}
    np.save(filename_wo_ext + '.npy', dic)

    # in order to read use: data = x.item()['data'] or data = x[()]['data'] other wise you get 0-d error
        
import argparse
import logging as log

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, help = "Name of the input file.")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
    parser.add_argument("-n", "--nframes", nargs = '?', type=int, const = 10, help = "Number of frames, default is 10.")
    parser.add_argument("-l", "--lframes", nargs = '?', type=int, const = 1024, help = "Length of frames, default is 1024.")
    parser.add_argument("-s", "--sframes", nargs = '?', type=int, const = 1024, help = "Starting frame, default is 1.")
    
    args = parser.parse_args()
    if args.verbose:
        log.basicConfig(level=log.DEBUG)
        
    nframes = 10 if not args.nframes else args.nframes
    lframes = 1024 if not args.lframes else args.lframes
    sframes = 1 if not args.sframes else args.sframes
    
    log.info("File {0} passed for processing.".format(args.filename))
    tiq2npy(args.filename, nframes, lframes, sframes)

