"""
IQGUI

-- GUI Application --

AUG 2015 Xaratustrah

"""

from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt
import numpy as np
import matplotlib.cm as cm
from mainwindow_ui import Ui_MainWindow
from iqdata import IQData


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
        self.file_loaded = False

        # fill combo box with names
        self.comboBox_color.addItems(['Jet', 'Blues'])

        # UI related stuff
        self.connect_signals()

    def connect_signals(self):
        """
        Connects signals.
        :return:
        """
        self.pushButton_choose_file.clicked.connect(self.open_file_dialog)
        self.pushButton_replot.clicked.connect(self.plot)

        self.actionChoose_file.triggered.connect(self.open_file_dialog)
        self.actionReplot.triggered.connect(self.plot)

    def plot(self):

        if not self.file_loaded:
            self.show_message('Please choose a valid file first.')
            return

        _, _ = self.iq_data.read_tiq(self.spinBox_nframes.value(), self.spinBox_lframes.value(),
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

        sp = self.mplWidget.canvas.ax.pcolormesh(xx, yy, IQData.get_dbm(zz), cmap=cmap)
        # cb = self.mplWidget.canvas.colorbar(sp)
        # cb.set_label('Power Spectral Density [dBm/Hz]')
        self.mplWidget.canvas.ax.set_xlabel(
            "Delta f [Hz] @ {} [Hz] (resolution = {:.2e} [Hz])".format(self.iq_data.center, delta_f))
        self.mplWidget.canvas.ax.set_ylabel('Time [sec] (resolution = {:.2e} [s])'.format(delta_t))
        self.mplWidget.canvas.ax.set_title('Spectrogram')
        self.mplWidget.canvas.draw()

    def addmpl(self, fig):
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
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose files...", '',
                                                   "TIQ Files (*.tiq)")

        if not file_name:
            return

        if file_name.lower().endswith('tiq'):
            self.iq_data = IQData(file_name)
            self.show_message('Loaded file: {}'.format(self.iq_data.file_basename))
            self.textBrowser.clear()
            self.file_loaded = True

    def keyPressEvent(self, event):
        """
        Keypress event handler
        :return:
        """
        if type(event) == QKeyEvent:
            # here accept the event and do something
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:  # code enter key
                # self.do_calculate()
                self.plot()
                event.accept()
            if event.key() == Qt.Key_Up:
                print('up')
                event.accept()
        else:
            event.ignore()
