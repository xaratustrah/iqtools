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
from iqdata import IQData

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
        self.loaded_file_type = None

        # fill combo box with names
        self.comboBox_color.addItems(['Jet', 'Blues', 'Cool', 'Copper', 'Hot', 'Gray'])

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
        self.pushButton_replot.clicked.connect(self.plot)

        self.actionChoose_file.triggered.connect(self.open_file_dialog)
        self.actionReplot.triggered.connect(self.plot)
        self.actionAbout.triggered.connect(self.showAboutDialog)
        self.actionQuit.triggered.connect(QCoreApplication.instance().quit)

        self.spinBox_lframes.valueChanged.connect(self.on_sframes_changed)
        self.verticalSlider_sframes.valueChanged.connect(self.on_sframes_changed)

    def plot(self):
        """
        Main plot function
        :return:
        """
        if not self.loaded_file_type:
            self.show_message('Please choose a valid file first.')
            return

        if self.loaded_file_type == 'tiq':
            self.iq_data.read_tiq(self.spinBox_nframes.value(), self.spinBox_lframes.value(),
                                  self.spinBox_sframes.value())

        if self.loaded_file_type == 'iqt':
            self.iq_data.read_iqt(self.spinBox_nframes.value(), self.spinBox_lframes.value(),
                                  self.spinBox_sframes.value())

        if self.loaded_file_type == 'wav':
            self.iq_data.read_wav(self.spinBox_nframes.value(), self.spinBox_lframes.value(),
                                  self.spinBox_sframes.value())

        self.textBrowser.clear()
        self.textBrowser.append(str(self.iq_data))
        xx, yy, zz = self.iq_data.get_spectrogram()

        delta_f = np.abs(np.abs(xx[0, 1]) - np.abs(xx[0, 0]))
        delta_t = np.abs(np.abs(yy[1, 0]) - np.abs(yy[0, 0]))

        self.mplWidget.canvas.ax.clear()

        if self.comboBox_color.currentText() == 'Jet':
            cmap = cm.jet
        if self.comboBox_color.currentText() == 'Blues':
            cmap = cm.Blues
        if self.comboBox_color.currentText() == 'Hot':
            cmap = cm.hot
        if self.comboBox_color.currentText() == 'Cool':
            cmap = cm.cool
        if self.comboBox_color.currentText() == 'Copper':
            cmap = cm.copper
        if self.comboBox_color.currentText() == 'Gray':
            cmap = cm.gray

        zz_dbm = IQData.get_dbm(zz)

        # Apply threshold
        zz_dbm[zz_dbm < self.verticalSlider_thld.value()] = 0

        # find the correct object in the matplotlib widget and plot on it
        sp = self.mplWidget.canvas.ax.pcolormesh(xx, yy, zz_dbm, cmap=cmap)
        cb = colorbar(sp)
        cb.set_label('Power Spectral Density [dBm/Hz]')
        # TODO: Colorbar doesn't show here.

        # Change frequency axis formatting
        self.mplWidget.canvas.ax.xaxis.set_major_formatter(FormatStrFormatter('%.0e'))
        self.mplWidget.canvas.ax.set_xlabel(
            "Delta f [Hz] @ {:.2e} [Hz] (resolution = {:.2e} [Hz])".format(self.iq_data.center, delta_f))
        self.mplWidget.canvas.ax.set_ylabel('Time [sec] (resolution = {:.2e} [s])'.format(delta_t))
        self.mplWidget.canvas.ax.set_title('Spectrogram')
        self.mplWidget.canvas.draw()

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
                                                   "IQ Files (*.tiq *.iqt);;Sound files (*.wav)")

        if not file_name:
            return

        self.iq_data = IQData(file_name)
        self.show_message('Loaded file: {}'.format(self.iq_data.file_basename))

        # make a dummy read to get the header
        if file_name.lower().endswith('tiq'):
            self.iq_data.read_tiq(1, 1, 1)
            self.loaded_file_type = 'tiq'

        if file_name.lower().endswith('iqt'):
            self.iq_data.read_iqt(1, 1, 1)
            self.loaded_file_type = 'iqt'

        if file_name.lower().endswith('wav'):
            self.iq_data.read_wav(1, 1, 1)
            self.loaded_file_type = 'wav'

        self.textBrowser.clear()
        self.textBrowser.append(str(self.iq_data))
        self.on_sframes_changed()

    def on_sframes_changed(self):
        """
        Take care of the changes in the frame size and set limits for GUI elements such as sliders
        :return:
        """
        if not self.loaded_file_type:
            return
        nf = self.spinBox_nframes.value()
        ns = self.iq_data.number_samples
        lf = self.spinBox_lframes.value()
        start = self.spinBox_sframes.value()
        self.spinBox_nframes.setMaximum(int(ns / lf))
        # allow for scrolling up to the last frame
        self.spinBox_sframes.setMaximum(int(ns / lf) - nf - 1)
        self.verticalSlider_sframes.setMaximum(int(ns / lf) - nf - 1)
        self.verticalSlider_sframes.setTickInterval(int(ns / lf / 10))
        self.lcdNumber_sframes.display(start * self.spinBox_lframes.value() / self.iq_data.fs)

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
                self.verticalSlider_sframes.setTickPosition(self.verticalSlider_sframes.tickPosition() + 10)
        else:
            event.ignore()
