import sys
import os
import subprocess

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5 import  uic

from timscript import Tim

title = "Timmy"
MainUI = os.path.dirname(os.path.realpath(__file__)) + "/main.ui" 

Ui_MainWindow, QtBaseClass = uic.loadUiType(MainUI)
class MainForm(QMainWindow,Ui_MainWindow):    
    def __init__(self):     
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.setWindowTitle(title)

        self.tim = Tim()

        self.init()
        self.initSignals()

        if self.tim.get_config_autostart():
            self.startWork()

    def closeEvent(self, event):
        self.stopWork()
        event.accept()

    def init(self):
        self.chbAutoStart.setChecked(self.tim.get_config_autostart())

        self.cmbType.addItem('Commission', 'comission')
        self.cmbType.addItem('Request', 'request')
        self.cmbType.addItem('ArtTrade', 'arttrade')
        self.cmbType.addItem('Private', 'private')

        self.currentTimName = self.tim.current_work()

        if self.currentTimName == "":
            self.currentTimName = self.tim.last_work()

        if self.currentTimName:
            names = self.currentTimName.split(':')
            if len(names) >= 2:
                if names[0] == 'artwork':
                    self.currentType = names[1]
                    index = self.cmbType.findData(self.currentType)
                    if ( index != -1 ):
                        self.cmbType.setCurrentIndex(index)

                    if len(names) == 3:
                        self.txtProject.setText(names[2])
                    elif len(names) > 3:
                        self.txtProject.setText( ":".join(names[2:-1]) )

        self.currentProjectName = self.txtProject.text().lower()
        self.currentType = self.cmbType.currentData().lower()

        self.updateUI()


    def initSignals(self):
        self.chbAutoStart.stateChanged.connect(self.changeChbAutoStart)
        self.txtProject.textChanged.connect(self.changeProjectName)
        self.cmbType.activated.connect(self.changeArt)
        self.btnStartStop.clicked.connect(self.clickedStartStop)
        self.btnBreak.clicked.connect(self.clickedBreak)

    def updateUI(self):
        self.cmbType.setEnabled(self.isNotWorking() and self.currentProjectName != "")
        self.txtProject.setEnabled(self.isNotWorking())
        self.btnBreak.setEnabled(self.isWorking() and not self.isBreak())
        self.btnStartStop.setEnabled(self.isWorking() or self.isBreak() or ((self.isNotWorking() or self.isBreak()) and self.currentProjectName != ""))

        if self.isWorking():
            self.btnStartStop.setText("Stop")
        else:
            self.btnStartStop.setText("Start")
        
        if self.currentTimName != self.timBreakName() and self.currentProjectName:
            diff = self.tim.diff(self.currentTimName)
            hours, remainder = divmod(diff.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            diff_str = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
            total_time_str = self.tim.total_time_str(self.currentTimName)
            self.lblStatus.setText("{0} ({1})".format(diff_str, total_time_str))

    def updateWork(self):
        self.currentProjectName = self.txtProject.text().lower()
        self.currentType = self.cmbType.currentData().lower()

        self.updateUI()


    def clickedStartStop(self):
        self.currentTimName = self.timName()
        self.startStopWorkToggle()
        

    def clickedBreak(self):
        self.currentTimName = self.timBreakName()
        self.startStopWorkToggle()
    

    def changeProjectName(self, str):
        self.currentProjectName = self.txtProject.text().lower()
        self.currentTimName = self.timName()

        if self.currentProjectName != "":
            self.cmbType.setEnabled(True)
        else:
            self.cmbType.setEnabled(False)

        self.btnStartStop.setEnabled(self.currentProjectName != "")


    def changeArt(self,index):
        self.currentType = self.cmbType.itemData(index).lower()
        self.currentTimName = self.timName()
        self.btnStartStop.setEnabled(self.currentType != "")

    def changeChbAutoStart(self, state):
        if state == QtCore.Qt.Checked:
            self.tim.set_config_autostart(True)
        else:
            self.tim.set_config_autostart(False)

    def timName(self):
        if self.currentProjectName == "":
            return ''

        prefix = 'artwork'
        return prefix + ":" + self.currentType + ":" + self.currentProjectName
    
    def timBreakName(self):
        return 'break'

    def isWorking(self):
        return self.tim.is_working() and self.currentTimName != self.timBreakName()

    def isBreak(self):
        return self.tim.is_working() and self.currentTimName == self.timBreakName()
    
    def isNotWorking(self):
        return not self.isWorking()

    def startStopWorkToggle(self):
        name = self.tim.current_work()
        time = self.tim.to_datetime(self.txtAddTime.text().lower())

        if self.currentTimName:
            if not name:
                self.tim.begin(self.currentTimName, time)
            else:
                if self.currentTimName != name:
                    self.tim.switch(self.currentTimName, time)
                else:
                    self.tim.end(time)
                    self.currentTimName = ""

            self.txtAddTime.clear()

        self.updateWork()

    def startWork(self):
        print(self.currentTimName)
        print(self.isWorking())
        print(self.isNotWorking())
        print(self.isBreak())
        time = self.tim.to_datetime(self.txtAddTime.text().lower())

        if self.currentTimName:
            if self.isNotWorking() and not self.isBreak():
                self.tim.begin(self.currentTimName, time)
            elif self.isBreak():
                self.tim.switch(self.currentTimName, time)

        self.txtAddTime.clear()

        self.updateWork()

    def stopWork(self):
        time = self.tim.to_datetime(self.txtAddTime.text().lower())

        if self.currentTimName:
            if self.isWorking() or self.isBreak():
                self.tim.end(time)

        self.txtAddTime.clear()

        self.updateWork()
    
def main():
    app = QApplication(sys.argv)
    w = MainForm()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()