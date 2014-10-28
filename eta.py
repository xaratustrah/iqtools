#!/usr/bin/env python
"""
Plot the PSD maximum at different cooling energies.

xaratustrah oct-2014
"""

import os
import numpy as np
from pylab import psd
import matplotlib.pyplot as plt
from read_tiq import *

def do_it(filename):

    dic1,_ = read_tiq(filename, 1, 1024, 1)
    center1 = dic1['center']
    fs1 = dic1['fs']
    nframes_tot = dic1['nframes_tot']

    naf = nacnt = np.array([])

    for i in range (1, nframes_tot, 100):
        dic1,_ = read_tiq(filename, 1, 1024, i)
        x1 = dic1['data']
        Pxx1, freqs1 = psd(x1, NFFT = 1024, Fs = fs1, noverlap=512)
        naf = np.append(naf, freqs1[Pxx1.argmax()])
        nacnt = np.append(nacnt, i)

    naf = naf + center1
    fig = plt.figure()
    ax  = fig.add_subplot(1,1,1)
    ax.plot(nacnt, naf, 'r.')
    ax.annotate('ISO at: {} [MHz]'.format(naf.max()/1.0e6), xy=(nacnt[naf.argmax()], naf.max()), xycoords='data',  xytext=(0.5, 0.5), textcoords='figure fraction', arrowprops=dict(width=1, headwidth=5, edgecolor = 'blue', facecolor='blue', shrink=0.05))
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Frame Number')
    plt.title('File: ' + filename.split('/')[3])
    plt.grid(True)
    fig.savefig(os.path.splitext(filename)[0]+'.pdf')
    plt.show()

if __name__ == "__main__":
    if (len(sys.argv) == 2):
        do_it(sys.argv[1])
    else:
        print ('Please provide a filename!')
