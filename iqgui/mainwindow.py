"""
IQGUI

-- GUI Application --

AUG 2015 Xaratustrah

"""

from matplotlib.colors import Normalize
from matplotlib.pyplot import colorbar
from matplotlib.ticker import FormatStrFormatter
import matplotlib.cm as cm
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QDialog
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt, QCoreApplication
import numpy as np
import json

from iqtools import *

from .mainwindow_ui import Ui_MainWindow
from .aboutdialog_ui import Ui_AbooutDialog
from iqtools.version import __version__

# force Matplotlib to use PyQt5 backend, call before importing pyplot and backends!
from matplotlib import use

use("Qt5Agg")


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
        self.comboBox_method.addItems(
            ['fft-2D', 'welch-2D', 'mtm-2D', 'fft-1D', 'fft-1D-avg', 'welch-1D'])
        self.comboBox_window.addItems(
            ['rectangular', 'bartlett', 'blackman', 'hamming', 'hanning'])
        self.comboBox_color.addItems(
            ['Viridis', 'Jet', 'Blues', 'Cool', 'Copper', 'Hot', 'Gray'])

        self.colormesh_xx = None
        self.colormesh_yy = None
        self.colormesh_zz = None
        self.colormesh_zz_dbm = None

        # plot data for writing to TXT Files

        self.plot_data_ff = np.array([])
        self.plot_data_pp = np.array([])

        # UI related stuff
        self.verticalSlider_thld_min.setValue(0)
        self.verticalSlider_thld_max.setValue(1000000)
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
        self.pushButton_replot.clicked.connect(
            self.on_pushButton_replot_clicked)

        # automatically connected by pyuic: https://stackoverflow.com/a/22875443
        self.pushButton_load_conf.clicked.connect(
            self.on_pushButton_load_conf_clicked_once)

        # automatically connected by pyuic: https://stackoverflow.com/a/22875443
        self.pushButton_save_conf.clicked.connect(
            self.on_pushButton_save_conf_clicked_once)
        self.pushButton_save_csv.clicked.connect(
            self.on_pushButton_save_csv)

        self.actionChoose_file.triggered.connect(self.open_file_dialog)
        self.actionReplot.triggered.connect(self.on_pushButton_replot_clicked)
        self.actionAbout.triggered.connect(self.showAboutDialog)
        self.actionQuit.triggered.connect(QCoreApplication.instance().quit)

        self.spinBox_lframes.valueChanged.connect(
            self.on_spinBox_lframe_changed)
        self.spinBox_nframes.valueChanged.connect(
            self.on_spinBox_nframe_changed)
        self.spinBox_sframes.valueChanged.connect(
            self.on_spinBox_sframe_changed)
        self.verticalSlider_sframes.valueChanged.connect(
            self.on_spinBox_sframe_changed)

        self.comboBox_color.currentIndexChanged.connect(
            self.on_comboBox_color_currentIndexChanged)

        self.verticalSlider_thld_min.valueChanged.connect(
            self.on_verticalSlider_thld_min_valueChanged)

        self.verticalSlider_thld_max.valueChanged.connect(
            self.on_verticalSlider_thld_max_valueChanged)

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
        elif self.comboBox_method.currentText() == 'welch-1D':
            self.method = 'welch-1D'
        elif self.comboBox_method.currentText() == 'fft-1D-avg':
            self.method = 'fft-1D-avg'
        else:
            self.method = 'fft-1D'

        self.iq_data.window = self.comboBox_window.currentText()

    def plot(self):
        """
        Main plot function
        :return:
        """
        # Empty status bar message
        self.show_message('')

        if not self.loaded_file_type:
            self.show_message('Please choose a valid file first.')
            return

        nframes = self.spinBox_nframes.value()
        lframes = self.spinBox_lframes.value()
        sframes = self.spinBox_sframes.value()

        # do the actual read
        try:
            self.iq_data.read(
                nframes=nframes, lframes=lframes, sframes=sframes)
        except ValueError as e:
            self.show_message(str(e))
            return

        self.check_combo_boxes()

        self.textBrowser.clear()
        self.textBrowser.append(str(self.iq_data))

        if self.checkBox_info.isChecked():
            info_txt = 'nframes = {}, lframes = {}, sframes = {}, method = {}'.format(
                nframes, lframes, sframes, self.method)
        else:
            info_txt = ""

        if self.method in ['mtm-2D', 'welch-2D', 'fft-2D']:
            # if you only like to change the color, don't calculate the spectrum again, just replot
            self.colormesh_xx, self.colormesh_yy, self.colormesh_zz = self.iq_data.get_power_spectrogram(
                nframes, lframes)

            delta_f = np.abs(
                np.abs(self.colormesh_xx[0, 1]) - np.abs(self.colormesh_xx[0, 0]))
            delta_t = np.abs(
                np.abs(self.colormesh_yy[1, 0]) - np.abs(self.colormesh_yy[0, 0]))

            # Apply threshold

            zz = self.colormesh_zz / np.max(self.colormesh_zz) * 1e6
            zz_min, zz_max = int(np.min(zz)), int(np.max(zz))

            mynorm = Normalize(vmin=self.verticalSlider_thld_min.value(
            ), vmax=self.verticalSlider_thld_max.value())

            # mask arrays for transparency in pcolormesh
            if self.checkBox_mask.isChecked():
                zzma = np.ma.masked_less_equal(
                    zz, self.verticalSlider_thld_min.value())
            else:
                zzma = zz

            # log version
            if self.checkBox_log.isChecked():
                zzma = IQBase.get_dbm(zzma)

            # use starting time
            starting_time = self.spinBox_sframes.value() * self.spinBox_lframes.value() / \
                self.iq_data.fs

            # find the correct object in the matplotlib widget and plot on it
            self.mplWidget.canvas.ax.clear()
            sp = self.mplWidget.canvas.ax.pcolormesh(self.colormesh_xx, self.colormesh_yy + starting_time, zzma,
                                                     cmap=self.cmap, norm=mynorm, shading='auto')
            # color bar is not needed now.
            # cb = colorbar(sp)
            # cb.set_label('Power Spectral Density [W/Hz]')

            # Change frequency axis formatting
            self.mplWidget.canvas.ax.xaxis.set_major_formatter(
                FormatStrFormatter('%.0e'))
            self.mplWidget.canvas.ax.set_xlabel(
                "Delta f [Hz] @ {:.2e} [Hz] (resolution = {:.2e} [Hz])".format(self.iq_data.center, delta_f))
            self.mplWidget.canvas.ax.set_ylabel(
                'Time [sec] (resolution = {:.2e} [s])'.format(delta_t))
            self.mplWidget.canvas.ax.set_title("")
            if self.checkBox_info.isChecked():
                self.mplWidget.canvas.ax.set_title(
                    'Spectrogram (File: {})'.format(self.iq_data.file_basename))
            # update plot variables for TXT export

            self.plot_data_ff = np.array([])
            self.plot_data_pp = np.array([])

        elif self.method == 'welch-1D':
            ff, pp = self.iq_data.get_pwelch()
            # update plot variables for TXT export

            self.plot_data_ff = ff
            self.plot_data_pp = pp

            delta_f = ff[1] - ff[0]

            self.mplWidget.canvas.ax.clear()
            # log version
            if self.checkBox_log.isChecked():
                pp = IQBase.get_dbm(pp)

            self.mplWidget.canvas.ax.plot(ff, pp)

            if self.checkBox_info.isChecked():
                self.mplWidget.canvas.ax.set_title(
                    'Spectrum (File: {})'.format(self.iq_data.file_basename))
            self.mplWidget.canvas.ax.set_xlabel(
                "Delta f [Hz] @ {:.2e} [Hz] (resolution = {:.2e} [Hz])".format(self.iq_data.center, delta_f))
            if self.checkBox_log.isChecked():
                self.mplWidget.canvas.ax.set_ylabel(
                    "Power Spectral Density [dBm/Hz]")
            else:
                self.mplWidget.canvas.ax.set_ylabel(
                    "Power Spectral Density [W/Hz]")

            self.mplWidget.canvas.ax.grid(True)

        else:  # this means self.method == 'fft-1D' or 'fft-1D-avg'
            if self.method == 'fft-1D-avg':
                ff, pp, _ = self.iq_data.get_fft(
                    nframes=nframes, lframes=lframes)
            else:
                ff, pp, _ = self.iq_data.get_fft()
            # update plot variables for TXT export

            self.plot_data_ff = ff
            self.plot_data_pp = pp

            delta_f = ff[1] - ff[0]
            self.mplWidget.canvas.ax.clear()
            # log version
            if self.checkBox_log.isChecked():
                pp = IQBase.get_dbm(pp)
            self.mplWidget.canvas.ax.plot(ff, pp)
            if self.checkBox_info.isChecked():
                self.mplWidget.canvas.ax.set_title(
                    'Spectrum (File: {})'.format(self.iq_data.file_basename))
            self.mplWidget.canvas.ax.set_xlabel(
                "Delta f [Hz] @ {:.2e} [Hz] (resolution = {:.2e} [Hz])".format(self.iq_data.center, delta_f))
            if self.checkBox_log.isChecked():
                self.mplWidget.canvas.ax.set_ylabel(
                    "Power Spectral Density [dBm/Hz]")
            else:
                self.mplWidget.canvas.ax.set_ylabel(
                    "Power Spectral Density [W/Hz]")
            self.mplWidget.canvas.ax.grid(True)

        # finish up plot 1D or 2D
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

    def write_plot_data_to_file(self, filename):
        write_spectrum_to_csv(
            self.plot_data_ff, self.plot_data_pp, filename, center=self.iq_data.center)

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
                                                   "IQ Files (*.tiq *.iqt);;XDAT files (*.xdat);;R3F files (*.r3f);;TDMS files(*.tdms);;TCAP files (*.dat);;Sound files (*.wav);;ASCII files (*.csv *.txt);;Raw binary files (*.bin)")

        if not file_name:
            self.show_message('User cancelled the dialog box.')
            return

        # special case of TCAP files which need an extra header file
        header_file_name = None
        if file_name.lower().endswith('.dat') or file_name.lower().endswith('.xdat'):
            self.show_message('Please choose a header file for this datafile.')
            header_file_name, _ = QFileDialog.getOpenFileName(self, "Please choose a header file...", '',
                                                              "TCAP header file (*.txt);;XDAT header file (*.xhdr)")
            if not header_file_name:
                self.show_message('User cancelled the dialog box.')
                return

        if not get_iq_object(file_name, header_file_name):
            self.show_message(
                'Datafile needs an additional header file which was not specified. Nothing to do.')
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
        self.spinBox_nframes.setValue(200)
        self.spinBox_lframes.setValue(1024)
        self.spinBox_sframes.setValue(1)

        # finally do an initial limit checking
        # todo: not sure if I need these following lines, they cause crash for very short IQT files
        # self.on_spinBox_lframe_changed()
        # self.on_spinBox_nframe_changed()
        # self.on_spinBox_sframe_changed()

    def on_spinBox_lframe_changed(self):
        if not self.loaded_file_type:
            return
        nf = self.spinBox_nframes.value()
        ns = self.iq_data.nsamples_total
        st = self.spinBox_sframes.value()

        self.spinBox_lframes.setMaximum(int(ns - st / nf))
        self.spinBox_lframes.setMinimum(1)

    def on_spinBox_nframe_changed(self):
        if not self.loaded_file_type:
            return
        lf = self.spinBox_lframes.value()
        ns = self.iq_data.nsamples_total
        st = self.spinBox_sframes.value()

        self.spinBox_nframes.setMaximum(int((ns - st) / lf))
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

        self.lcdNumber_sframes.display(
            st * self.spinBox_lframes.value() / self.iq_data.fs)

    def on_comboBox_color_currentIndexChanged(self):
        """
        This is the event listener for the combo box change
        :return:
        """
        pass

    def on_pushButton_replot_clicked(self):
        self.plot()

    def on_pushButton_save_conf_clicked_once(self):
        if self.loaded_file_type:
            suggest_file_name = self.iq_data.filename_wo_ext
        else:
            suggest_file_name = 'plot_config'

        file_name, _ = QFileDialog.getSaveFileName(self, "Choose files...", suggest_file_name,
                                                   "Config Files (*.json)")

        if not file_name:
            self.show_message('User cancelled the dialog box.')
            return

        data = {
            'lframes': self.spinBox_lframes.value(),
            'nframes': self.spinBox_nframes.value(),
            'sframes': self.spinBox_sframes.value(),
            'thld_min': self.verticalSlider_thld_min.value(),
            'thld_max': self.verticalSlider_thld_max.value(),
            'method': self.comboBox_method.currentText(),
            'color': self.comboBox_color.currentText(),
            'window': self.comboBox_window.currentText(),
            'log': self.checkBox_log.isChecked(),
            'mask': self.checkBox_mask.isChecked(),
            'info': self.checkBox_info.isChecked(),
            'file_name': suggest_file_name,
            'version': __version__,
        }

        with open(file_name, 'w') as outfile:
            json.dump(data, outfile)

    def on_pushButton_save_csv(self):
        if self.loaded_file_type:
            suggest_file_name = self.iq_data.filename_wo_ext
        else:
            self.show_message('Please choose a valid file first.')
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Choose files...", suggest_file_name,
                                                   "CSV Files (*.csv)")

        if not file_name:
            self.show_message('User cancelled the dialog box.')
            return
        self.write_plot_data_to_file(file_name)

    def on_pushButton_load_conf_clicked_once(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose files...", '',
                                                   "Config Files (*.json)")

        if not file_name:
            self.show_message('User cancelled the dialog box.')
            return

        with open(file_name, "r") as read_file:
            data = json.load(read_file)
        try:
            self.spinBox_lframes.setValue(data['lframes'])
            self.spinBox_nframes.setValue(data['nframes'])
            self.spinBox_sframes.setValue(data['sframes'])
            self.verticalSlider_thld_min.setValue(data['thld_min'])
            self.verticalSlider_thld_max.setValue(data['thld_max'])
            self.comboBox_method.setCurrentText(data['method'])
            self.comboBox_color.setCurrentText(data['color'])
            self.comboBox_window.setCurrentText(data['window'])
            self.checkBox_log.setChecked(data['log'])
            self.checkBox_mask.setChecked(data['mask'])
            self.checkBox_info.setChecked(data['info'])

        except KeyError as error:
            self.show_message('The config file seems to be damaged.')
            return

    def keyPressEvent(self, event):
        """
        Keypress event handler
        :return:
        """
        if type(event) == QKeyEvent:
            # here accept the event and do something
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:  # code enter key
                self.plot()
                event.accept()
            if event.key() == Qt.Key_Up:
                event.accept()
                self.verticalSlider_sframes.setTickPosition(
                    self.verticalSlider_sframes.tickPosition() + 10)
        else:
            event.ignore()

    def on_verticalSlider_thld_min_valueChanged(self):
        if self.verticalSlider_thld_min.value() >= self.verticalSlider_thld_max.value():
            self.verticalSlider_thld_min.setValue(
                self.verticalSlider_thld_max.value() - 10)

    def on_verticalSlider_thld_max_valueChanged(self):
        if self.verticalSlider_thld_max.value() <= self.verticalSlider_thld_min.value():
            self.verticalSlider_thld_max.setValue(
                self.verticalSlider_thld_min.value() + 10)
