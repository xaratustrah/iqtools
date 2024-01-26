"""
Collection of plotters

xaratustrah@github
2017
"""

from .tools import *
from .iqbase import IQBase
from matplotlib.ticker import FormatStrFormatter
from matplotlib.colors import Normalize
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import subprocess
import struct
import os
import matplotlib
matplotlib.use('Agg')


# ------------ PLOTTERS ----------------------------


def plot_hilbert(x_bar):
    """Shows the Hilbert plot

    Args:
        x_bar (ndarray): Complex valued data array
    """    

    plt.plot(np.real(x_bar), np.imag(x_bar))
    plt.grid(True)
    plt.xlabel('Real Part')
    plt.ylabel('Imag. Part')


def plot_frame_power(yy, frame_power):
    """Plot frame power, i.e. trapezoid along each time frame

    Args:
        yy (ndarray): Time meshgrid
        frame_power (ndarray): Array describing the frame power
    """    
    plt.plot(yy[:, 0], IQBase.get_dbm(frame_power))
    plt.ylabel('Power [dBm]')
    plt.xlabel('Time [sec]')
    plt.title('Frame power')


def plot_spectrogram(xx, yy, zz, cen=0.0, cmap=cm.jet, dpi=300, dbm=False, filename=None, title='Spectrogram', zzmin=0, zzmax=1e6, mask=False, span=None, decimal_place=2):
    """Plot the calculated spectrogram. For the coordinates, it also accepts sparse matrices.


    Args:
        xx (ndarray): Frequency meshgrid, can be sparse
        yy (ndarray): Time meshgrid, can be sparse
        zz (ndarray): Power meshgrid
        cen (float, optional): Center frequency. Defaults to 0.0.
        cmap (string, optional): Matplotlib.colormap. Defaults to cm.jet.
        dpi (int, optional): Resolution for PNG output. Defaults to 300.
        dbm (bool, optional): Display in dBm scale. Defaults to False.
        filename (str, optional): File name. Defaults to None, in which case nothing will be saved to file.
        title (str, optional): Title of the plot. Defaults to 'Spectrogram'.
        zzmin (int, optional): Color contrast min. Defaults to 0.
        zzmax (int, optional): Color contrast max. Defaults to 1e6.
        mask (bool, optional): Mask out values less than this, for cleaner histograms. Defaults to False.
        span (float, optional): Show only a frequency window. Defaults to None.
        decimal_place (int, optional): Limit display of decimal places of all numbers in the plot. Defaults to 2.
    """    
    # Apply display threshold if zmin and zmax are provided, they must be different than the default values of 0 and 1e6
    # otherwise ignore them

    if zzmin >= 0 and zzmax <= 1e6 and zzmin < zzmax:
        zz = zz / np.max(zz) * 1e6
        mynorm = Normalize(vmin=zzmin, vmax=zzmax)

        # mask arrays for transparency in pcolormesh
        if mask:
            zz = np.ma.masked_less_equal(zz, zzmin)

    else:
        # pcolormesh ignores if norm is None
        mynorm = None

    if dbm:
        zz = IQBase.get_dbm(zz)

    # here comes span in [Hz]
    if not span:
        spanmask = (xx[0, :] != 0) | (xx[0, :] == 0)
    else:
        spanmask = (xx[0, :] <= span / 2) & (xx[0, :] >= -span / 2)
    xx = xx[:, spanmask]
    zz = zz[:, spanmask]
    # we have to check yy before, make sure it is sparse or not
    yy = yy[:,spanmask] if np.shape(yy)[1] > 1 else yy
    
    # here comes the plot
    sp = plt.pcolormesh(xx, yy, zz, cmap=cmap, norm=mynorm, shading='auto')
    
    # here is the color bar
    cb = plt.colorbar(sp, format=f'%.{decimal_place}e')

    ax = plt.gca()
    ax.xaxis.set_major_formatter(FormatStrFormatter(f'%.{decimal_place}e'))

    delta_f = np.abs(np.abs(xx[0, 1]) - np.abs(xx[0, 0]))
    delta_t = np.abs(np.abs(yy[1, 0]) - np.abs(yy[0, 0]))

    plt.xlabel(
        "Delta f [Hz] @ {} (resolution = {})".format(get_eng_notation(cen, unit='Hz', decimal_place=decimal_place), get_eng_notation(delta_f, unit='Hz', decimal_place=decimal_place)))
    plt.ylabel('Time [sec] (resolution = {})'.format(
        get_eng_notation(delta_t, 's', decimal_place=decimal_place)))
    plt.title(title)

    if dbm:
        cb.set_label('Power Spectral Density a.u. [dBm/Hz]')
    else:
        cb.set_label('Power Spectral Density a.u.')

    if filename is not None:
        plt.savefig(filename + '.png', dpi=dpi, bbox_inches='tight')
        plt.close()


def plot_spectrum(f, p, cen=0.0, span=None, dbm=False, filename=None, title='Spectrum'):
    """Plots 2D spectrum in dBm per Hz

    Args:
        f (ndarray): Frequency array
        p (ndarray): Power array
        cen (float, optional): Center frequency. Defaults to 0.0.
        span (float, optional): Frequency window. Defaults to None.
        dbm (bool, optional): Display in dBm scale. Defaults to False.
        filename (str, optional): File name. Defaults to None, in which case nothing will be saved to file.
        title (str, optional): Title of the plot. Defaults to 'Spectrogram'.
    """    

    if not span:
        spanmask = (f != 0) | (f == 0)
    else:
        spanmask = (f <= span / 2) & (f >= -span / 2)
    if dbm:
        plt.plot(f[spanmask], IQBase.get_dbm(p[spanmask]))
    else:
        plt.plot(f[spanmask], p[spanmask])

    ax = plt.gca()
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.0e'))

    plt.xlabel("Delta f [Hz] @ {}".format(get_eng_notation(cen, 'Hz')))
    plt.title(title)
    if dbm:
        plt.ylabel('Power Spectral Density [dBm/Hz]')
    else:
        plt.ylabel('Power Spectral Density')

    plt.grid(True)
    if filename is not None:
        plt.savefig(filename + '.png')  # , bbox_inches='tight')
        plt.close()


def plot_spectrogram_with_gnuplot(zz):
    """Plots using external instance of [GNUPlot](http://www.gnuplot.info/). Data is reshaped in form of a matrix for plotting. Idea based on [this post on SO](https://stackoverflow.com/a/15885230/5177935)

    Args:
        zz (ndarray): Power meshgrid
    """    
    temp_file = 'foo.bin'
    with open(temp_file, 'wb') as foo:
        for (i, j), dat in np.ndenumerate(np.rot90(zz, 3)):
            s = struct.pack('4f', i, j, dat, dat)
            foo.write(s)

    gnuplot = subprocess.Popen(
        ['gnuplot'], stdin=subprocess.PIPE, universal_newlines=True)

    gnuplot.stdin.write("""
    set pm3d map;
    unset clabel;
    set terminal png size 1024,768;
    set palette defined (0 0.0 0.0 0.5, \
                         1 0.0 0.0 1.0, \
                         2 0.0 0.5 1.0, \
                         3 0.0 1.0 1.0, \
                         4 0.5 1.0 0.5, \
                         5 1.0 1.0 0.0, \
                         6 1.0 0.5 0.0, \
                         7 1.0 0.0 0.0, \
                         8 0.5 0.0 0.0 );
    """)
    gnuplot.stdin.write("set output '{}.png';".format(temp_file))
    gnuplot.stdin.write(
        "splot '{}' binary record=(10,-1) format='%float' u 1:2:3:4 w pm3d;".format(temp_file))
    # the following command needs terminating the process
    # os.remove(temp_file)


def plot_phase_shift(x, phase):
    """Plots the signal before and after the phase shift

    Args:
        x (ndarray): Data array
        phase (float): Phase shift
    """    
    plt.rcParams['axes.grid'] = True
    fig, axs = plt.subplots(2, 2, sharex=True, sharey=True)
    axs[0, 0].plot(np.real(x))
    axs[0, 1].plot(np.imag(x))
    axs[1, 0].plot(np.real(shift_phase(x, phase)))
    axs[1, 1].plot(np.imag(shift_phase(x, phase)))
