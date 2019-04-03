# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'timmu/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(790, 622)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayoutConfig = QtWidgets.QVBoxLayout()
        self.verticalLayoutConfig.setObjectName("verticalLayoutConfig")
        self.chbAutoStart = QtWidgets.QCheckBox(self.centralwidget)
        self.chbAutoStart.setObjectName("chbAutoStart")
        self.verticalLayoutConfig.addWidget(self.chbAutoStart)
        self.chbGenTimeclock = QtWidgets.QCheckBox(self.centralwidget)
        self.chbGenTimeclock.setObjectName("chbGenTimeclock")
        self.verticalLayoutConfig.addWidget(self.chbGenTimeclock)
        self.gridLayout.addLayout(self.verticalLayoutConfig, 13, 1, 1, 1)
        self.tblWorks = QtWidgets.QTableWidget(self.centralwidget)
        self.tblWorks.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tblWorks.setObjectName("tblWorks")
        self.tblWorks.setColumnCount(4)
        self.tblWorks.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tblWorks.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWorks.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWorks.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWorks.setHorizontalHeaderItem(3, item)
        self.gridLayout.addWidget(self.tblWorks, 16, 1, 1, 2)
        self.pgbProgress = QtWidgets.QProgressBar(self.centralwidget)
        self.pgbProgress.setProperty("value", 0)
        self.pgbProgress.setObjectName("pgbProgress")
        self.gridLayout.addWidget(self.pgbProgress, 11, 2, 1, 1)
        self.lblStatusCurrentText = QtWidgets.QLabel(self.centralwidget)
        self.lblStatusCurrentText.setObjectName("lblStatusCurrentText")
        self.gridLayout.addWidget(self.lblStatusCurrentText, 10, 0, 1, 1)
        self.treeWorks = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeWorks.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.treeWorks.setObjectName("treeWorks")
        self.gridLayout.addWidget(self.treeWorks, 16, 0, 1, 1)
        self.gridLayoutCurrentSession = QtWidgets.QGridLayout()
        self.gridLayoutCurrentSession.setObjectName("gridLayoutCurrentSession")
        self.verticalLayoutCurrentSessionLeft = QtWidgets.QVBoxLayout()
        self.verticalLayoutCurrentSessionLeft.setObjectName("verticalLayoutCurrentSessionLeft")
        self.lblCurrentSessionInfo = QtWidgets.QLabel(self.centralwidget)
        self.lblCurrentSessionInfo.setObjectName("lblCurrentSessionInfo")
        self.verticalLayoutCurrentSessionLeft.addWidget(self.lblCurrentSessionInfo)
        self.lblCurrentSessionInfo2 = QtWidgets.QLabel(self.centralwidget)
        self.lblCurrentSessionInfo2.setObjectName("lblCurrentSessionInfo2")
        self.verticalLayoutCurrentSessionLeft.addWidget(self.lblCurrentSessionInfo2)
        self.gridLayoutCurrentSession.addLayout(self.verticalLayoutCurrentSessionLeft, 3, 0, 1, 1)
        self.verticalLayoutCurrentSessionRight = QtWidgets.QVBoxLayout()
        self.verticalLayoutCurrentSessionRight.setObjectName("verticalLayoutCurrentSessionRight")
        self.lblCurrentSessionInfo3Text = QtWidgets.QLabel(self.centralwidget)
        self.lblCurrentSessionInfo3Text.setObjectName("lblCurrentSessionInfo3Text")
        self.verticalLayoutCurrentSessionRight.addWidget(self.lblCurrentSessionInfo3Text)
        self.lblCurrentSessionInfo3 = QtWidgets.QLabel(self.centralwidget)
        self.lblCurrentSessionInfo3.setObjectName("lblCurrentSessionInfo3")
        self.verticalLayoutCurrentSessionRight.addWidget(self.lblCurrentSessionInfo3)
        self.gridLayoutCurrentSession.addLayout(self.verticalLayoutCurrentSessionRight, 3, 1, 1, 1)
        self.gridLayout.addLayout(self.gridLayoutCurrentSession, 10, 1, 1, 2)
        self.horizontalLayoutButtons = QtWidgets.QHBoxLayout()
        self.horizontalLayoutButtons.setObjectName("horizontalLayoutButtons")
        self.btnStartStop = QtWidgets.QPushButton(self.centralwidget)
        self.btnStartStop.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnStartStop.sizePolicy().hasHeightForWidth())
        self.btnStartStop.setSizePolicy(sizePolicy)
        self.btnStartStop.setMinimumSize(QtCore.QSize(85, 28))
        self.btnStartStop.setAutoDefault(True)
        self.btnStartStop.setDefault(True)
        self.btnStartStop.setObjectName("btnStartStop")
        self.horizontalLayoutButtons.addWidget(self.btnStartStop)
        self.btnBreak = QtWidgets.QPushButton(self.centralwidget)
        self.btnBreak.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnBreak.sizePolicy().hasHeightForWidth())
        self.btnBreak.setSizePolicy(sizePolicy)
        self.btnBreak.setObjectName("btnBreak")
        self.horizontalLayoutButtons.addWidget(self.btnBreak)
        self.gridLayout.addLayout(self.horizontalLayoutButtons, 7, 2, 1, 1)
        self.verticalLayoutInputLabels = QtWidgets.QVBoxLayout()
        self.verticalLayoutInputLabels.setObjectName("verticalLayoutInputLabels")
        self.lblTypeText = QtWidgets.QLabel(self.centralwidget)
        self.lblTypeText.setObjectName("lblTypeText")
        self.verticalLayoutInputLabels.addWidget(self.lblTypeText)
        self.lblProjectNameText = QtWidgets.QLabel(self.centralwidget)
        self.lblProjectNameText.setObjectName("lblProjectNameText")
        self.verticalLayoutInputLabels.addWidget(self.lblProjectNameText)
        self.lblAddTimeText = QtWidgets.QLabel(self.centralwidget)
        self.lblAddTimeText.setObjectName("lblAddTimeText")
        self.verticalLayoutInputLabels.addWidget(self.lblAddTimeText)
        self.gridLayout.addLayout(self.verticalLayoutInputLabels, 7, 0, 1, 1)
        self.verticalLayoutLastSession = QtWidgets.QVBoxLayout()
        self.verticalLayoutLastSession.setObjectName("verticalLayoutLastSession")
        self.lblLastSessionInfo = QtWidgets.QLabel(self.centralwidget)
        self.lblLastSessionInfo.setObjectName("lblLastSessionInfo")
        self.verticalLayoutLastSession.addWidget(self.lblLastSessionInfo)
        self.lblLastSessionInfo2 = QtWidgets.QLabel(self.centralwidget)
        self.lblLastSessionInfo2.setObjectName("lblLastSessionInfo2")
        self.verticalLayoutLastSession.addWidget(self.lblLastSessionInfo2)
        self.gridLayout.addLayout(self.verticalLayoutLastSession, 14, 1, 1, 1)
        self.horizontalLayoutEstimate = QtWidgets.QHBoxLayout()
        self.horizontalLayoutEstimate.setObjectName("horizontalLayoutEstimate")
        self.spbEstimateValue = QtWidgets.QSpinBox(self.centralwidget)
        self.spbEstimateValue.setObjectName("spbEstimateValue")
        self.horizontalLayoutEstimate.addWidget(self.spbEstimateValue)
        self.cmbEstimateUnit = QtWidgets.QComboBox(self.centralwidget)
        self.cmbEstimateUnit.setObjectName("cmbEstimateUnit")
        self.horizontalLayoutEstimate.addWidget(self.cmbEstimateUnit)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayoutEstimate.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayoutEstimate, 11, 1, 1, 1)
        self.lblEstimate = QtWidgets.QLabel(self.centralwidget)
        self.lblEstimate.setObjectName("lblEstimate")
        self.gridLayout.addWidget(self.lblEstimate, 11, 0, 1, 1)
        self.spacerTop = QtWidgets.QLabel(self.centralwidget)
        self.spacerTop.setText("")
        self.spacerTop.setObjectName("spacerTop")
        self.gridLayout.addWidget(self.spacerTop, 8, 1, 1, 1)
        self.lblLastSessionText = QtWidgets.QLabel(self.centralwidget)
        self.lblLastSessionText.setObjectName("lblLastSessionText")
        self.gridLayout.addWidget(self.lblLastSessionText, 14, 0, 1, 1)
        self.verticalLayoutInputField = QtWidgets.QVBoxLayout()
        self.verticalLayoutInputField.setObjectName("verticalLayoutInputField")
        self.cmbType = QtWidgets.QComboBox(self.centralwidget)
        self.cmbType.setEnabled(True)
        self.cmbType.setObjectName("cmbType")
        self.verticalLayoutInputField.addWidget(self.cmbType)
        self.txtProject = QtWidgets.QComboBox(self.centralwidget)
        self.txtProject.setEditable(True)
        self.txtProject.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
        self.txtProject.setObjectName("txtProject")
        self.verticalLayoutInputField.addWidget(self.txtProject)
        self.txtAddTime = QtWidgets.QComboBox(self.centralwidget)
        self.txtAddTime.setEditable(True)
        self.txtAddTime.setMaxVisibleItems(5)
        self.txtAddTime.setObjectName("txtAddTime")
        self.verticalLayoutInputField.addWidget(self.txtAddTime)
        self.gridLayout.addLayout(self.verticalLayoutInputField, 7, 1, 1, 1)
        self.spacerButtom = QtWidgets.QLabel(self.centralwidget)
        self.spacerButtom.setText("")
        self.spacerButtom.setObjectName("spacerButtom")
        self.gridLayout.addWidget(self.spacerButtom, 15, 1, 1, 1)
        self.lblConfigText = QtWidgets.QLabel(self.centralwidget)
        self.lblConfigText.setObjectName("lblConfigText")
        self.gridLayout.addWidget(self.lblConfigText, 13, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 790, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionLoad = QtWidgets.QAction(MainWindow)
        self.actionLoad.setObjectName("actionLoad")
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionLoad)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Timmu"))
        self.chbAutoStart.setToolTip(_translate("MainWindow", "Start last Project after you start this program"))
        self.chbAutoStart.setText(_translate("MainWindow", "Auto-Start"))
        self.chbGenTimeclock.setToolTip(_translate("MainWindow", "for hledger"))
        self.chbGenTimeclock.setText(_translate("MainWindow", "gen. timeclock-File"))
        item = self.tblWorks.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Name"))
        item = self.tblWorks.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Start"))
        item = self.tblWorks.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "End"))
        item = self.tblWorks.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Duration"))
        self.lblStatusCurrentText.setText(_translate("MainWindow", "Current Session:"))
        self.treeWorks.headerItem().setText(0, _translate("MainWindow", "Projects"))
        self.lblCurrentSessionInfo.setText(_translate("MainWindow", "<Current Session>"))
        self.lblCurrentSessionInfo2.setText(_translate("MainWindow", "<Current Session 2>"))
        self.lblCurrentSessionInfo3Text.setText(_translate("MainWindow", "Total Time:"))
        self.lblCurrentSessionInfo3.setText(_translate("MainWindow", "<Current Session 3>"))
        self.btnStartStop.setText(_translate("MainWindow", "Start"))
        self.btnBreak.setText(_translate("MainWindow", "Break"))
        self.lblTypeText.setText(_translate("MainWindow", "Type:"))
        self.lblProjectNameText.setText(_translate("MainWindow", "Project Name:"))
        self.lblAddTimeText.setText(_translate("MainWindow", "Start Time:"))
        self.lblLastSessionInfo.setText(_translate("MainWindow", "<Last Session>"))
        self.lblLastSessionInfo2.setText(_translate("MainWindow", "<Last Session2>"))
        self.lblEstimate.setText(_translate("MainWindow", "Estimate:"))
        self.lblLastSessionText.setText(_translate("MainWindow", "Last Session:"))
        self.txtProject.setToolTip(_translate("MainWindow", "Project Name"))
        self.txtAddTime.setToolTip(_translate("MainWindow", "time like \"13:00\" or \"20 minutes ago\""))
        self.lblConfigText.setText(_translate("MainWindow", "Settings:"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionOpen.setText(_translate("MainWindow", "Open..."))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionLoad.setText(_translate("MainWindow", "Load"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))

