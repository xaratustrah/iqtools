"""
IQGUI

-- GUI Application --

AUG 2015 Xaratustrah


Many thanks to Matplotlib embedding examples:

github.com/Maduranga
and
http://blog.rcnelson.com/building-a-matplotlib-gui-with-qt-designer-part-2/
"""

# force Matplotlib to use PyQt5 backend, call before importing pyplot and backends!
from matplotlib import use
use("Qt5Agg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas,
                                                NavigationToolbar2QT as NavigationToolbar)
from PyQt5 import QtWidgets


class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class MatplotLibWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.canvas = MplCanvas()
        self.vbl = QtWidgets.QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

        # add matplotlib standard toolbar
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas,
                                         parent, coordinates=True)
        self.vbl.addWidget(self.toolbar)
