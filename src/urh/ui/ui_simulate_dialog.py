# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SimulateDialog(object):
    def setupUi(self, SimulateDialog):
        SimulateDialog.setObjectName("SimulateDialog")
        SimulateDialog.resize(508, 374)
        SimulateDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(SimulateDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(SimulateDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.listViewSimulate = QtWidgets.QListView(SimulateDialog)
        self.listViewSimulate.setObjectName("listViewSimulate")
        self.verticalLayout.addWidget(self.listViewSimulate)
        self.label_2 = QtWidgets.QLabel(SimulateDialog)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.spinBox = QtWidgets.QSpinBox(SimulateDialog)
        self.spinBox.setObjectName("spinBox")
        self.verticalLayout.addWidget(self.spinBox)
        self.label_3 = QtWidgets.QLabel(SimulateDialog)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.spinBox_2 = QtWidgets.QSpinBox(SimulateDialog)
        self.spinBox_2.setObjectName("spinBox_2")
        self.verticalLayout.addWidget(self.spinBox_2)
        self.label_4 = QtWidgets.QLabel(SimulateDialog)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.comboBox = QtWidgets.QComboBox(SimulateDialog)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.verticalLayout.addWidget(self.comboBox)
        self.pushButton = QtWidgets.QPushButton(SimulateDialog)
        icon = QtGui.QIcon.fromTheme("media-playback-start")
        self.pushButton.setIcon(icon)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)

        self.retranslateUi(SimulateDialog)
        QtCore.QMetaObject.connectSlotsByName(SimulateDialog)

    def retranslateUi(self, SimulateDialog):
        _translate = QtCore.QCoreApplication.translate
        SimulateDialog.setWindowTitle(_translate("SimulateDialog", "Simulation settings"))
        self.label.setText(_translate("SimulateDialog", "Simulate:"))
        self.label_2.setText(_translate("SimulateDialog", "Repeat:"))
        self.spinBox.setSpecialValueText(_translate("SimulateDialog", "Infinite"))
        self.label_3.setText(_translate("SimulateDialog", "Timeout (in seconds):"))
        self.label_4.setText(_translate("SimulateDialog", "In case of an unexpected/overdue response:"))
        self.comboBox.setItemText(0, _translate("SimulateDialog", "Resend last message"))
        self.comboBox.setItemText(1, _translate("SimulateDialog", "Stop simulation"))
        self.comboBox.setItemText(2, _translate("SimulateDialog", "Restart simulation"))
        self.pushButton.setText(_translate("SimulateDialog", "Simulate"))

