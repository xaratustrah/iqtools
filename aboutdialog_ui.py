# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'aboutdialog.ui'
#
# Created: Tue Sep  8 00:47:22 2015
#      by: PyQt5 UI code generator 5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AbooutDialog(object):
    def setupUi(self, AbooutDialog):
        AbooutDialog.setObjectName("AbooutDialog")
        AbooutDialog.resize(422, 309)
        self.verticalLayout = QtWidgets.QVBoxLayout(AbooutDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(AbooutDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton_ok = QtWidgets.QPushButton(AbooutDialog)
        self.pushButton_ok.setObjectName("pushButton_ok")
        self.horizontalLayout.addWidget(self.pushButton_ok)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(AbooutDialog)
        self.pushButton_ok.pressed.connect(AbooutDialog.close)
        QtCore.QMetaObject.connectSlotsByName(AbooutDialog)

    def retranslateUi(self, AbooutDialog):
        _translate = QtCore.QCoreApplication.translate
        AbooutDialog.setWindowTitle(_translate("AbooutDialog", "Dialog"))
        self.label.setText(_translate("AbooutDialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:24pt; font-weight:600; text-decoration: underline;\">iqgui</span></p><p align=\"center\">A visualizer for IQ Data in frequency domain.</p><p align=\"center\">This program is a part of the <span style=\" font-weight:600;\">iq_suite</span> for visualization of IQ data.</p><p align=\"center\"><br/></p><p align=\"center\">Copyright (c) Shahab Sanjari 2015.</p><p align=\"center\">License: GPL V.2.</p><p align=\"center\"><br/></p></body></html>"))
        self.pushButton_ok.setText(_translate("AbooutDialog", "OK"))

