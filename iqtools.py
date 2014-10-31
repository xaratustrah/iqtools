#!/usr/bin/env python

"""
Collection of tools for dealing with IQ data. This code converts data in TIQ
format and extracts the data in numpy format

xaratustrah oct-2014
"""

import os, sys, argparse
import xml.etree.ElementTree as et
import matplotlib.pyplot as plt
import numpy as np
import logging as log
from scipy.signal import hilbert
from scipy.io import wavfile


verbose = False


def make_signal(f, fs, l = 1, nharm = 0, noise = True):
    """Make a sine signal with/without noise."""
    
    t = np.arange(0, l, 1/fs)
    x = np.zeros(len(t))
    for i in range(nharm + 2):
        x += np.sin (2 * np.pi * i * f * t)
        
    if noise: x += np.random.normal(0, 1, len(t))
    return t, x


def plot_hilbert(x):
    """Show Hilbert plot."""

    y = hilbert(x)
    I = np.real(x)
    Q = np.imag(x)
    plt.plot(I, Q)
    plt.grid(True)
    plt.xlabel('Real Part')
    plt.ylabel('Imag Part')
    return I, Q


def plot_fft(x, fs, c):
    """ Plots the fft of a power signal."""
    
    n = x.size
    ts = 1.0/fs
    f = np.fft.fftfreq(n, ts) + c
    y = np.fft.fft(x)/n
    plt.plot(f, 10*np.log10(pow(abs(y),2)), '.')
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Power Spectral Density [dB/Hz]")
    plt.grid(True)
    return f, y


def filename_wo_ext(filename):
    """Extracts the filename base"""
    
    return os.path.splitext(filename)[0]
    

def save_header(filename, ba):
    """Saves the header bytearray into a txt tile."""
    
    with open (filename_wo_ext(filename) + '.xml', 'wb') as f3 : 
        f3.write(ba)
    log.info("Header saved in an xml file.")


def save_data(filename, dic):
    """Saves the dictionary to a numpy file."""
    
    np.save(filename_wo_ext(filename) + '.npy', dic)


def save_audio(filename, afs, na):
    """ Save the singal as an audio wave """

    wavfile.write(filename_wo_ext(filename) + '.wav', afs, abs(na))


def read_tiq(filename, nframes = 10, lframes = 1024, sframes = 1):
    """Process the tiq input file."""
    
    filesize = os.path.getsize(filename)
    log.info("File size is {} bytes.".format(filesize))
    
    with open (filename) as f:
        line = f.readline()
    data_offset = int(line.split("\"")[1])

    with open(filename, 'rb') as f:
        ba = f.read(data_offset)

    xmltree = et.fromstring(ba)
    for elem in xmltree.iter(tag='{http://www.tektronix.com}Frequency'):
        center=float(elem.text)
    for elem in xmltree.iter(tag='{http://www.tektronix.com}MaxSpan'):
        span=float(elem.text)
    for elem in xmltree.iter(tag='{http://www.tektronix.com}Scaling'):
        scale=float(elem.text)
    for elem in xmltree.iter(tag='{http://www.tektronix.com}SamplingFrequency'):
        fs=float(elem.text)

    log.info("Center {0} Hz, span {1} Hz, sampling frequency {2} scale factor {3}.".format(center, span, fs, scale))
    log.info("Header size {} bytes.".format(data_offset))

    log.info("Proceeding to read binary section, 32bit (4 byte) little endian.")
    total_nbytes = 8 * nframes * lframes # 8 comes from 2 times 4 byte integer for I and Q
    start_nbytes = 8 * (sframes - 1 ) * lframes
    nframes_tot = int((filesize-data_offset)/8/lframes)
    log.info("Total number of frames: {0} = {1}s".format(nframes_tot, (filesize-data_offset)/8/fs))
    log.info("Frame length: {0} data points = {1}s".format(lframes, lframes/fs))
    log.info("Frame offset: {0} = {1}s".format(sframes, start_nbytes/fs))
    log.info("Reading {0} frames = {1}s.".format(nframes, total_nbytes/fs))

    header = ba

    with open (filename, 'rb') as f:
        f.seek(data_offset + start_nbytes)
        ba = f.read(total_nbytes)

    ar = np.fromstring(ba, dtype='<i4') # little endian 4 byte ints.
    ar = ar * scale  # return a numpy array of little endian 8 byte floats (known as doubles)
    ar = ar.view(dtype='c16')  # reinterpret the bytes as a 16 byte complex number, which consists of 2 doubles.


    log.info("Output complex array has a size of {}.".format(ar.size))
    dic = {'center': center, 'span': span, 'fs': fs, 'lframes': lframes, 'data': ar, 'nframes_tot': nframes_tot}

    return dic, header     # in order to read you may use: data = x.item()['data'] or data = x[()]['data'] other wise you get 0-d error


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, help = "Name of the input file.")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
    parser.add_argument("-n", "--nframes", nargs = '?', type=int, const = 10, help = "Number of frames, default is 10.")
    parser.add_argument("-l", "--lframes", nargs = '?', type=int, const = 1024, help = "Length of frames, default is 1024.")
    parser.add_argument("-s", "--sframes", nargs = '?', type=int, const = 1, help = "Starting frame, default is 1.")
    
    args = parser.parse_args()
    if args.verbose:
        log.basicConfig(level=log.DEBUG)
        verbose = True
        
    nframes = 10 if not args.nframes else args.nframes
    lframes = 1024 if not args.lframes else args.lframes
    sframes = 1 if not args.sframes else args.sframes
    
    log.info("File {} passed for processing.".format(args.filename))
    
    dic, header = read_tiq(args.filename, nframes, lframes, sframes)
    save_header (args.filename, header)
    save_data (args.filename, dic)
    
