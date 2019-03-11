# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'timmu/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from Qt import QtCore, QtGui, QtWidgets


class Ui_MainForm(object):
    def setupUi(self, MainForm):
        MainForm.setObjectName("MainForm")
        MainForm.resize(446, 227)
        self.gridLayoutWidget = QtWidgets.QWidget(MainForm)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(8, 10, 431, 210))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.lblDuration = QtWidgets.QLabel(self.gridLayoutWidget)
        self.lblDuration.setObjectName("lblDuration")
        self.gridLayout.addWidget(self.lblDuration, 3, 0, 1, 1)
        self.lblType = QtWidgets.QLabel(self.gridLayoutWidget)
        self.lblType.setObjectName("lblType")
        self.gridLayout.addWidget(self.lblType, 0, 0, 1, 1)
        self.lblEstimate = QtWidgets.QLabel(self.gridLayoutWidget)
        self.lblEstimate.setObjectName("lblEstimate")
        self.gridLayout.addWidget(self.lblEstimate, 4, 0, 1, 1)
        self.cmbEstimateUnit = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.cmbEstimateUnit.setObjectName("cmbEstimateUnit")
        self.gridLayout.addWidget(self.cmbEstimateUnit, 4, 2, 1, 1)
        self.spbEstimateValue = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.spbEstimateValue.setObjectName("spbEstimateValue")
        self.gridLayout.addWidget(self.spbEstimateValue, 4, 1, 1, 1)
        self.txtAddTime = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.txtAddTime.setEnabled(True)
        self.txtAddTime.setObjectName("txtAddTime")
        self.gridLayout.addWidget(self.txtAddTime, 2, 0, 1, 1)
        self.chbAutoStart = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.chbAutoStart.setObjectName("chbAutoStart")
        self.gridLayout.addWidget(self.chbAutoStart, 2, 3, 1, 1)
        self.txtProject = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.txtProject.setEnabled(True)
        self.txtProject.setText("")
        self.txtProject.setObjectName("txtProject")
        self.gridLayout.addWidget(self.txtProject, 1, 1, 1, 2)
        self.cmbType = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.cmbType.setEnabled(True)
        self.cmbType.setObjectName("cmbType")
        self.gridLayout.addWidget(self.cmbType, 0, 1, 1, 2)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.btnStartStop = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btnStartStop.setEnabled(True)
        self.btnStartStop.setDefault(True)
        self.btnStartStop.setObjectName("btnStartStop")
        self.gridLayout_2.addWidget(self.btnStartStop, 0, 0, 1, 1)
        self.btnBreak = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btnBreak.setEnabled(True)
        self.btnBreak.setObjectName("btnBreak")
        self.gridLayout_2.addWidget(self.btnBreak, 0, 1, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 2, 1, 1, 2)
        self.lblStatus = QtWidgets.QLabel(self.gridLayoutWidget)
        self.lblStatus.setText("")
        self.lblStatus.setObjectName("lblStatus")
        self.gridLayout.addWidget(self.lblStatus, 3, 1, 1, 2)
        self.lblProgress = QtWidgets.QLabel(self.gridLayoutWidget)
        self.lblProgress.setObjectName("lblProgress")
        self.gridLayout.addWidget(self.lblProgress, 5, 0, 1, 1)
        self.pgbProgress = QtWidgets.QProgressBar(self.gridLayoutWidget)
        self.pgbProgress.setProperty("value", 0)
        self.pgbProgress.setObjectName("pgbProgress")
        self.gridLayout.addWidget(self.pgbProgress, 5, 1, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 3, 1, 1)

        self.retranslateUi(MainForm)
        QtCore.QMetaObject.connectSlotsByName(MainForm)

    def retranslateUi(self, MainForm):
        _translate = QtCore.QCoreApplication.translate
        MainForm.setWindowTitle(_translate("MainForm", "Timmu"))
        self.lblDuration.setText(_translate("MainForm", "Duration"))
        self.lblType.setText(_translate("MainForm", "Type"))
        self.lblEstimate.setText(_translate("MainForm", "Estimate"))
        self.txtAddTime.setToolTip(_translate("MainForm", "time like \"13:00\" or \"20 minutes ago\""))
        self.txtAddTime.setPlaceholderText(_translate("MainForm", "20 minutes ago"))
        self.chbAutoStart.setText(_translate("MainForm", "Auto-Start"))
        self.txtProject.setToolTip(_translate("MainForm", "<html><head/><body><p>Name of the Project</p><p>(Account name is artwork:&lt;art&gt;:&lt;projectname&gt;)</p></body></html>"))
        self.txtProject.setPlaceholderText(_translate("MainForm", "Project Name"))
        self.btnStartStop.setText(_translate("MainForm", "Start"))
        self.btnBreak.setText(_translate("MainForm", "Break"))
        self.lblProgress.setText(_translate("MainForm", "Progress"))


