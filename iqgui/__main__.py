#!/usr/bin/env python
"""
IQGUI

-- GUI Application --

AUG 2015 Xaratustrah

"""

import sys
from PyQt5.QtWidgets import QApplication
from iqgui.mainwindow import mainWindow

sys.setrecursionlimit(5000)


def main():
    """
    Start the application
    :return:
    """
    app = QApplication(sys.argv)
    form = mainWindow()
    form.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
