"""
IQGUI

-- GUI Application --

AUG 2015 Xaratustrah

"""

from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QDialog
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt, QCoreApplication
import numpy as np
from mainwindow_ui import Ui_MainWindow
from aboutdialog_ui import Ui_AbooutDialog
from iqbase import IQBase
from iqtools import get_iq_object
# force Matplotlib to use PyQt5 backend, call before importing pyplot and backends!
from matplotlib import use

use("Qt5Agg")
import matplotlib.cm as cm
from matplotlib.ticker import FormatStrFormatter
from matplotlib.pyplot import colorbar
from version import __version__


class mainWindow(QMainWindow, Ui_MainWindow):
    """
    The main class for the GUI window
    """

    def __init__(self):
        """
        The constructor and initiator.
        :return:
        """
        # initial setup
        super(mainWindow, self).__init__()
        self.setupUi(self)

        # instance of data
        self.iq_data = None
        self.loaded_file_type = False

        self.cmap = None
        self.method = None

        # fill combo box with names
        self.comboBox_method.addItems(['fft-2D', 'welch-2D', 'mtm-2D', 'tfr-2D', 'fft-1D', 'welch-1D'])
        self.comboBox_window.addItems(['rectangular', 'bartlett', 'blackman', 'hamming', 'hanning'])
        self.comboBox_color.addItems(['Viridis', 'Jet', 'Blues', 'Cool', 'Copper', 'Hot', 'Gray'])

        self.colormesh_xx = None
        self.colormesh_yy = None
        self.colormesh_zz = None
        self.colormesh_zz_dbm = None

        # UI related stuff
        self.connect_signals()

    def showAboutDialog(self):
        """
        Show about dialog
        :return:
        """
        about_dialog = QDialog()
        about_dialog.ui = Ui_AbooutDialog()
        about_dialog.ui.setupUi(about_dialog)
        about_dialog.ui.labelVersion.setText('Version: {}'.format(__version__))
        about_dialog.exec_()
        about_dialog.show()

    def connect_signals(self):
        """
        Connects signals.
        :return:
        """
        self.pushButton_choose_file.clicked.connect(self.open_file_dialog)
        self.pushButton_replot.clicked.connect(self.on_pushButton_replot_clicked)

        self.actionChoose_file.triggered.connect(self.open_file_dialog)
        self.actionReplot.triggered.connect(self.on_pushButton_replot_clicked)
        self.actionAbout.triggered.connect(self.showAboutDialog)
        self.actionQuit.triggered.connect(QCoreApplication.instance().quit)

        self.spinBox_lframes.valueChanged.connect(self.on_spinBox_lframe_changed)
        self.spinBox_nframes.valueChanged.connect(self.on_spinBox_nframe_changed)
        self.spinBox_sframes.valueChanged.connect(self.on_spinBox_sframe_changed)
        self.verticalSlider_sframes.valueChanged.connect(self.on_spinBox_sframe_changed)

        self.comboBox_color.currentIndexChanged.connect(self.on_comboBox_color_currentIndexChanged)

    def check_combo_boxes(self):
        if self.comboBox_color.currentText() == 'Viridis':
            self.cmap = cm.viridis
        if self.comboBox_color.currentText() == 'Jet':
            self.cmap = cm.jet
        if self.comboBox_color.currentText() == 'Blues':
            self.cmap = cm.Blues
        if self.comboBox_color.currentText() == 'Hot':
            self.cmap = cm.hot
        if self.comboBox_color.currentText() == 'Cool':
            self.cmap = cm.cool
        if self.comboBox_color.currentText() == 'Copper':
            self.cmap = cm.copper
        if self.comboBox_color.currentText() == 'Gray':
            self.cmap = cm.gray

        if self.comboBox_method.currentText() == 'fft-2D':
            self.method = 'fft-2D'
            self.iq_data.method = 'fft'
        elif self.comboBox_method.currentText() == 'welch-2D':
            self.method = 'welch-2D'
            self.iq_data.method = 'welch'
        elif self.comboBox_method.currentText() == 'mtm-2D':
            self.method = 'mtm-2D'
            self.iq_data.method = 'mtm'
        elif self.comboBox_method.currentText() == 'tfr-2D':
            self.method = 'tfr-2D'
        elif self.comboBox_method.currentText() == 'welch-1D':
            self.method = 'welch-1D'
        else:
            self.method = 'fft_1D'

        self.iq_data.window = self.comboBox_window.currentText()

    def plot(self, replot=True):
        """
        Main plot function
        :return:
        """
        # Empty status bar message
        self.show_message('')

        if not self.loaded_file_type:
            self.show_message('Please choose a valid file first.')
            return

        # do the actual read

        self.iq_data.read(self.spinBox_nframes.value(), self.spinBox_lframes.value(),
                          self.spinBox_sframes.value())

        self.check_combo_boxes()

        self.textBrowser.clear()
        self.textBrowser.append(str(self.iq_data))

        info_txt = 'nframes = {}, lframes = {}, sframes = {}, method = {}'.format(self.iq_data.nframes,
                                                                                  self.iq_data.lframes,
                                                                                  self.iq_data.sframes,
                                                                                  self.method)

        if self.method in ['mtm-2D', 'welch-2D', 'fft-2D']:
            # if you only like to change the color, don't calculate the spectrum again, just replot
            if replot:
                self.colormesh_xx, self.colormesh_yy, self.colormesh_zz = self.iq_data.get_spectrogram()

            delta_f = np.abs(np.abs(self.colormesh_xx[0, 1]) - np.abs(self.colormesh_xx[0, 0]))
            delta_t = np.abs(np.abs(self.colormesh_yy[1, 0]) - np.abs(self.colormesh_yy[0, 0]))

            # Apply threshold
            self.colormesh_zz_dbm = IQBase.get_dbm(self.colormesh_zz)
            self.colormesh_zz_dbm[self.colormesh_zz_dbm < self.verticalSlider_thld.value()] = 0

            # find the correct object in the matplotlib widget and plot on it
            self.mplWidget.canvas.ax.clear()
            sp = self.mplWidget.canvas.ax.pcolormesh(self.colormesh_xx, self.colormesh_yy, self.colormesh_zz_dbm,
                                                     cmap=self.cmap)
            cb = colorbar(sp)
            cb.set_label('Power Spectral Density [dBm/Hz]')
            # TODO: Colorbar doesn't show here.

            # Change frequency axis formatting
            self.mplWidget.canvas.ax.xaxis.set_major_formatter(FormatStrFormatter('%.0e'))
            self.mplWidget.canvas.ax.set_xlabel(
                "Delta f [Hz] @ {:.2e} [Hz] (resolution = {:.2e} [Hz])".format(self.iq_data.center, delta_f))
            self.mplWidget.canvas.ax.set_ylabel('Time [sec] (resolution = {:.2e} [s])'.format(delta_t))
            self.mplWidget.canvas.ax.set_title('Spectrogram (File: {})'.format(self.iq_data.file_basename))

        elif self.method == 'tfr-2D':
            self.show_message('Waiting for carlkl@GitHUB to port libtfr to Python 3 :-)')
            return

        elif self.method == 'welch-1D':
            ff, pp = self.iq_data.get_pwelch()
            delta_f = ff[1] - ff[0]
            self.mplWidget.canvas.ax.clear()
            self.mplWidget.canvas.ax.plot(ff, IQBase.get_dbm(pp))
            self.mplWidget.canvas.ax.set_title('Spectrum (File: {})'.format(self.iq_data.file_basename))
            self.mplWidget.canvas.ax.set_xlabel(
                "Delta f [Hz] @ {:.2e} [Hz] (resolution = {:.2e} [Hz])".format(self.iq_data.center, delta_f))
            self.mplWidget.canvas.ax.set_ylabel("Power Spectral Density [dBm/Hz]")
            self.mplWidget.canvas.ax.grid(True)

        else:  # this means self.method == 'fft-1D'
            ff, pp, _ = self.iq_data.get_fft()
            delta_f = ff[1] - ff[0]
            self.mplWidget.canvas.ax.clear()
            self.mplWidget.canvas.ax.plot(ff, IQBase.get_dbm(pp))
            self.mplWidget.canvas.ax.set_title('Spectrum (File: {})'.format(self.iq_data.file_basename))
            self.mplWidget.canvas.ax.set_xlabel(
                "Delta f [Hz] @ {:.2e} [Hz] (resolution = {:.2e} [Hz])".format(self.iq_data.center, delta_f))
            self.mplWidget.canvas.ax.set_ylabel("Power Spectral Density [dBm/Hz]")
            self.mplWidget.canvas.ax.grid(True)

        # finish up plot
        self.mplWidget.canvas.ax.text(0.5, 0.995, info_txt,
                                      horizontalalignment='center',
                                      verticalalignment='top',
                                      fontsize=12,
                                      transform=self.mplWidget.canvas.ax.transAxes)
        self.mplWidget.canvas.draw()
        self.mplWidget.canvas.show()

    def addmpl(self, fig):
        """
        Add plot widget
        :param fig:
        :return:
        """
        self.canvas = FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()

    def show_message(self, message):
        """
        Implementation of an abstract method:
        Show text in status bar
        :param message:
        :return:
        """
        self.statusbar.showMessage(message)

    def show_message_box(self, text):
        """
        Display a message box.
        :param text:
        :return:
        """
        reply = QMessageBox.question(self, 'Message',
                                     text, QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            return True
        else:
            return False

    def open_file_dialog(self):
        """
        Open file dialog
        :return:
        """
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose files...", '',
                                                   "IQ Files (*.tiq *.iqt);;TDMS files(*.tdms);;TCAP files (*.dat);;Sound files (*.wav);;ASCII files (*.csv *.txt);;Raw binary files (*.bin)")

        if not file_name:
            self.show_message('User cancelled the dialog box.')
            return

        # special case of TCAP files which need an extra header file
        header_file_name = None
        if file_name.lower().endswith('.dat'):
            self.show_message('Please choose a header file for this datafile.')
            header_file_name, _ = QFileDialog.getOpenFileName(self, "Please choose a header file...", '',
                                                              "TCAP Header file (*.txt)")
            if not header_file_name:
                self.show_message('User cancelled the dialog box.')
                return

        if not get_iq_object(file_name, header_file_name):
            self.show_message('Datafile needs an additional header file which was not specified. Nothing to do.')
            return

        # Now all the above has succeeded, we can finally create the object.
        # not sure if it is needed to delete the memory before. But anyway do it after all dialog boxes are done.
        self.iq_data = None
        self.iq_data = get_iq_object(file_name, header_file_name)

        self.show_message('Loaded file: {}'.format(self.iq_data.file_basename))

        # make a dummy read to get the header
        self.iq_data.read(1, 1, 1)

        self.loaded_file_type = True
        self.textBrowser.clear()
        self.textBrowser.append(str(self.iq_data))

        # set some initial values for the spin boxes
        self.spinBox_nframes.setValue(10)
        self.spinBox_lframes.setValue(1024)
        self.spinBox_sframes.setValue(1)
        # finally do an initial limit checking
        self.on_spinBox_lframe_changed()
        self.on_spinBox_nframe_changed()
        self.on_spinBox_sframe_changed()

    def on_spinBox_lframe_changed(self):
        if not self.loaded_file_type:
            return
        nf = self.spinBox_nframes.value()
        ns = self.iq_data.nsamples_total
        st = self.spinBox_sframes.value()

        self.spinBox_lframes.setMaximum(int(ns - st) / nf)
        self.spinBox_lframes.setMinimum(1)

    def on_spinBox_nframe_changed(self):
        if not self.loaded_file_type:
            return
        lf = self.spinBox_lframes.value()
        ns = self.iq_data.nsamples_total
        st = self.spinBox_sframes.value()

        self.spinBox_nframes.setMaximum(int(ns - st) / lf)
        self.spinBox_nframes.setMinimum(1)

    def on_spinBox_sframe_changed(self):
        if not self.loaded_file_type:
            return
        ns = self.iq_data.nsamples_total
        nf = self.spinBox_nframes.value()
        lf = self.spinBox_lframes.value()
        st = self.spinBox_sframes.value()

        self.spinBox_sframes.setMaximum(int(ns / lf) - nf - 1)
        self.spinBox_sframes.setMinimum(1)

        self.verticalSlider_sframes.setMaximum(int(ns / lf) - nf - 1)
        self.verticalSlider_sframes.setMinimum(1)
        self.verticalSlider_sframes.setTickInterval(int(ns / lf / 10))

        self.lcdNumber_sframes.display(st * self.spinBox_lframes.value() / self.iq_data.fs)

    def on_comboBox_color_currentIndexChanged(self):
        """
        This is the event listener for the combo box change
        :return:
        """
        if not self.loaded_file_type:
            self.show_message('Please choose a valid file first.')
            return
        self.plot(replot=False)

    def on_pushButton_replot_clicked(self):
        self.plot(replot=True)

    def keyPressEvent(self, event):
        """
        Keypress event handler
        :return:
        """
        if type(event) == QKeyEvent:
            # here accept the event and do something
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:  # code enter key
                self.plot(replot=True)
                event.accept()
            if event.key() == Qt.Key_Up:
                event.accept()
                self.verticalSlider_sframes.setTickPosition(self.verticalSlider_sframes.tickPosition() + 10)
        else:
            event.ignore()
