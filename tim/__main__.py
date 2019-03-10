import sys
import os
import subprocess

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5 import  uic

from timscript import Tim

MainUI = os.path.dirname(os.path.realpath(__file__)) + "/main.ui" 

Ui_MainWindow, QtBaseClass = uic.loadUiType(MainUI)
class MainForm(QMainWindow,Ui_MainWindow):    
    def __init__(self):     
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.tim = Tim()

        self.init()
        self.initSignals()

        if self.tim.get_config_autostart():
            self.startWork()


    def init(self):
        self.chbAutoStart.setChecked(self.tim.get_config_autostart())

        self.cmbArt.addItem('Commission', 'comission')
        self.cmbArt.addItem('Request', 'request')
        self.cmbArt.addItem('ArtTrade', 'arttrade')
        self.cmbArt.addItem('Private', 'private')

        self.currentTimName, self.currentDiff = self.tim.status()

        if self.currentTimName == "":
            self.currentTimName = self.tim.last_work()

            names = self.currentTimName.split(':')
            if len(names) >= 2:
                if names[0] == 'artwork':
                    self.currentArt = names[1]
                    index = self.cmbArt.findData(self.currentArt);
                    if ( index != -1 ):
                        self.cmbArt.setCurrentIndex(index);

                    if len(names) == 3:
                        self.txtProject.setText(names[2])
                    elif len(names) > 3:
                        self.txtProject.setText( ":".join(names[2:-1]) )

        self.currentProjectName = self.txtProject.text().lower()
        self.currentArt = self.cmbArt.currentData().lower()
        
        self.btnStartStop.setEnabled(self.currentProjectName != "")


    def initSignals(self):
        self.chbAutoStart.stateChanged.connect(self.changeChbAutoStart)
        self.txtProject.textChanged.connect(self.changeProjectName)
        self.cmbArt.activated.connect(self.changeArt)
        self.btnStartStop.clicked.connect(self.clickedStartStop)
        self.btnBreak.clicked.connect(self.clickedBreak)

    def updateWork(self):
        self.currentTimName, self.currentDiff = self.tim.status()

        names = self.currentTimName.split(':')
        if len(names) >= 2:
            if names[0] == 'artwork':
                self.currentArt = names[1]
                index = self.cmbArt.findData(self.currentArt);
                if ( index != -1 ):
                    self.cmbArt.setCurrentIndex(index);

                if len(names) == 3:
                    self.txtProject.setText(names[2])
                elif len(names) > 3:
                    self.txtProject.setText( ":".join(names[2:-1]) )
        
        self.currentProjectName = self.txtProject.text().lower()
        self.currentArt = self.cmbArt.currentData().lower()

        if self.isWorking():
            self.btnStartStop.setText("Stop");
        else:
            self.btnStartStop.setText("Start");

        self.cmbArt.setEnabled(self.isNotWorking() and self.currentProjectName != "")
        self.txtProject.setEnabled(self.isNotWorking())
        self.txtAddTime.setEnabled(self.isNotWorking())
        self.btnBreak.setEnabled(not self.isBreak())

        self.btnStartStop.setEnabled(self.currentProjectName != "")


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
            self.cmbArt.setEnabled(True);
        else:
            self.cmbArt.setEnabled(False);

        self.btnStartStop.setEnabled(self.currentProjectName != "")


    def changeArt(self,index):
        self.currentArt = self.cmbArt.itemData(index).lower()
        self.currentTimName = self.timName()
        self.btnStartStop.setEnabled(self.currentArt != "")

    def changeChbAutoStart(self, state):
        if state == QtCore.Qt.Checked:
            self.tim.set_config_autostart(True)
        else:
            self.tim.set_config_autostart(False)

    def timName(self):
        if self.currentProjectName == "":
            return ''

        prefix = 'artwork'
        return prefix + ":" + self.currentArt + ":" + self.currentProjectName
    
    def timBreakName(self):
        return 'break'

    def isWorking(self):
        return self.currentTimName != "" and self.currentTimName != self.timBreakName()

    def isBreak(self):
        name, diff = self.tim.status()
        return self.currentTimName != "" and name == self.timBreakName()
    
    def isNotWorking(self):
        return self.currentTimName == ""

    def startStopWorkToggle(self):
        name, diff = self.tim.status()
        time = self.tim.to_datetime(self.txtAddTime.text().lower())

        if self.isNotWorking():
            self.tim.begin(self.currentTimName, time)
        else:
            if self.currentTimName != name:
                self.tim.switch(self.currentTimName, time)
            else:
                self.tim.end(time)

        self.txtAddTime.clear();

        self.updateWork()

    def startWork(self):
        time = self.tim.to_datetime(self.txtAddTime.text().lower())

        if self.isNotWorking() and self.isBreak():
            self.tim.begin(self.currentTimName, time)
        elif self.isBreak() and self.currentTimName != self.timBreakName():
            self.tim.switch(self.currentTimName, time)

        self.txtAddTime.clear();

        self.updateWork()

def main():
    app = QApplication(sys.argv)
    w = MainForm()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()