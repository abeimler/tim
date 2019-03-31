from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow

import re
from datetime import datetime, timedelta, date

from .tim.timscript import Tim
from .ui_mainwindow import Ui_MainForm

class MainForm(QMainWindow,Ui_MainForm):    
    def __init__(self):     
        QMainWindow.__init__(self)
        Ui_MainForm.__init__(self)
        self.setupUi(self)

        self.tim = Tim()
        
        self.OTHER_WORK = "work"
        self.BREAK = 'break'

        self.init()
        self.initSignals()

        if self.tim.get_config_autostart():
            self.startWork()


    def closeEvent(self, event):
        self.stopWork()
        event.accept()

    def init(self):
        self.chbAutoStart.setChecked(self.tim.get_config_autostart())
        
        self.prefix = self.tim.get_config_prefix().lower()
        if self.prefix == "":
            self.tim.set_config_prefix('artwork')
            self.prefix = self.tim.get_config_prefix().lower()

        self.types = self.tim.get_config_types()
        if len(self.types) == 0:
            self.types = ['Commission', 'Request', 'ArtTrade', 'Private']
            self.tim.set_config_types(self.types)

        for ty in self.types:
            tyname = ty.capitalize()
            self.cmbType.addItem(tyname, self.prefix + ':' + ty.lower())

        self.cmbType.addItem('Other Work', self.OTHER_WORK)

        self.cmbEstimateUnit.addItem('Hours', 'hours')
        self.cmbEstimateUnit.addItem('Minute', 'minutes')
        
        self.txtAddTime.addItem('')
        self.txtAddTime.addItem('10 minutes ago')
        self.txtAddTime.addItem('30 minutes ago')
        self.txtAddTime.addItem('1 hour ago')
        self.txtAddTime.addItem('2 hours ago')


        self.currentTimName = self.tim.current_work()
        if self.currentTimName == "":
            self.currentTimName = self.tim.last_work()

        self.lastTimName = self.currentTimName

        pname = self.updateProjectNameFromCurrentTimName()
        self.txtProject.setCurrentText(pname)

        self.currentProjectName = self.txtProject.currentText().lower()
        self.currentType = self.cmbType.currentData().lower()
        self.currentEstimateUnit = self.cmbEstimateUnit.itemData(0)
        self.currentEstimate = 0
        
        self.updateProjectNameSearch(self.currentProjectName)

        self.updateUI()
        self.updateEstimate()

    def updateProjectNameFromCurrentTimName(self):
        if self.currentTimName:
            names = self.currentTimName.split(':')
            if len(names) >= 3:
                if names[0] == self.prefix:
                    self.currentType = names[1]
                    index = self.cmbType.findData(self.currentType)
                    if ( index != -1 ):
                        self.cmbType.setCurrentIndex(index)
            elif len(names) >= 2:
                if names[0] == self.OTHER_WORK:
                    self.currentType = names[0]
                    index = self.cmbType.findData(self.currentType)
                    if ( index != -1 ):
                        self.cmbType.setCurrentIndex(index)

            pname = ""
            if len(names) == 3:
                pname = names[2]
            elif len(names) > 3:
                pname = ":".join(names[2:])
            elif len(names) >= 2:
                pname = ":".join(names[1:])
            elif len(names) == 1:
                pname = names[0]

            return pname

        return ""

    def initSignals(self):
        self.chbAutoStart.stateChanged.connect(self.changeAutoStart)
        self.txtProject.currentTextChanged.connect(self.changeProjectName)
        self.txtProject.editTextChanged.connect(self.editProjectName)
        self.txtProject.currentIndexChanged.connect(self.changeProjectNameIndex)
        self.cmbType.activated.connect(self.changeType)
        self.btnStartStop.clicked.connect(self.clickedStartStop)
        self.btnBreak.clicked.connect(self.clickedBreak)
        self.cmbEstimateUnit.activated.connect(self.changeEstimateUnit)
        self.spbEstimateValue.valueChanged.connect(self.changeEstimate)
        self.txtProject.lineEdit().returnPressed.connect(self.editProjectNamePressEnter)

    
    def updateUIButtons(self):
        self.btnBreak.setEnabled(self.isWorking() and not self.isBreak() and self.valid_time())
        self.btnStartStop.setEnabled(self.isWorking() or self.isBreak() or ((self.isNotWorking() or self.isBreak()) and self.currentProjectName != "") and self.valid_time())

        if self.isWorking():
            self.btnStartStop.setText("Stop")
        else:
            self.btnStartStop.setText("Start")

    def updateUI(self):
        self.cmbType.setEnabled(self.isNotWorking() and self.currentProjectName != "")
        self.txtProject.setEnabled(self.isNotWorking())

        self.updateUIButtons()
        
        if self.currentTimName:
            if self.currentTimName != self.timBreakName() and self.currentProjectName:
                self.lblStatus.setText(self.getStatusText(self.currentTimName))
        elif self.lastTimName:
            self.lblStatus.setText(self.getStatusText(self.lastTimName))

        self.lblStatusName.setText(self.getStatusText(self.timName()))


    def updateWork(self):
        self.currentProjectName = self.txtProject.currentText().lower()
        self.currentType = self.cmbType.currentData().lower()

        self.updateUI()

    def clickedStartStop(self):
        if self.valid_time():
            self.currentTimName = self.timName()
            self.startStopWorkToggle()
        

    def clickedBreak(self):
        if self.valid_time():
            self.currentTimName = self.timBreakName()
            self.startStopWorkToggle()
    



    def changeType(self,index):
        self.currentType = self.cmbType.itemData(index).lower()
        self.currentTimName = self.timName()
        self.updateUIButtons()

    def changeAutoStart(self, state):
        if state == QtCore.Qt.Checked:
            self.tim.set_config_autostart(True)
        else:
            self.tim.set_config_autostart(False)

    
    def changeEstimateUnit(self,index):
        self.currentEstimateUnit = self.cmbEstimateUnit.itemData(index)
        self.saveEstimate()
        

    def changeEstimate(self, value):
        self.currentEstimate = value
        self.saveEstimate()
    
    def changeProjectName(self, pname):
        self.currentProjectName = pname.lower()
        self.currentTimName = self.timName()

        if self.currentProjectName:
            self.cmbType.setEnabled(True)
        else:
            self.cmbType.setEnabled(False)

        self.updateUIButtons()
        
        self.lblStatusName.setText(self.getStatusText(self.timName()))
        self.updateEstimate()

    def editProjectNamePressEnter(self):
        self.updateProjectNameSearch(self.currentProjectName)


    def editProjectName(self, pname):
        pass

    def changeProjectNameIndex(self, index):
        pass

    def startStopWorkToggle(self):
        name = self.tim.current_work()
        time = self.tim.to_datetime(self.txtAddTime.currentText().lower())

        if self.currentTimName:
            if not name:
                self.tim.begin(self.currentTimName, time)
            else:
                if self.currentTimName != name:
                    self.tim.switch(self.currentTimName, time)
                else:
                    self.tim.end(time)
                    self.lastTimName = self.currentTimName
                    self.currentTimName = ""

            self.clearTxtAddTime()

        self.updateWork()
    
    def valid_time(self):
        time = self.tim.parse_isotime(self.tim.to_datetime(self.txtAddTime.currentText().lower()))
        current_time = self.tim.current_work_start_time()
        return current_time is None or time >= current_time
    
    def timName(self):
        if self.currentProjectName == "":
            return ''

        return self.currentType + ":" + self.currentProjectName
    
    def timBreakName(self):
        return self.BREAK

    def isWorking(self):
        return self.tim.is_working() and self.currentTimName != self.timBreakName()

    def isBreak(self):
        return self.tim.is_working() and self.currentTimName == self.timBreakName()
    
    def isNotWorking(self):
        return not self.isWorking()

    def startWork(self):
        time = self.tim.to_datetime(self.txtAddTime.currentText().lower())

        if self.currentTimName:
            if self.isNotWorking() and not self.isBreak():
                self.tim.begin(self.currentTimName, time)
            elif self.isBreak():
                time_datetime = self.tim.parse_isotime(time)
                current_time = self.tim.current_work_start_time()
                if time_datetime >= current_time:
                    self.tim.switch(self.currentTimName, time)

        self.clearTxtAddTime()

        self.updateWork()

    def stopWork(self):
        time = self.tim.to_datetime(self.txtAddTime.currentText().lower())

        if self.currentTimName:
            if self.isWorking() or self.isBreak():
                time_datetime = self.tim.parse_isotime(time)
                current_time = self.tim.current_work_start_time()
                if time_datetime >= current_time:
                    self.tim.end(time)
                self.lastTimName = self.currentTimName
                self.currentTimName = ""

        self.clearTxtAddTime()

        self.updateWork()
    

    def updateEstimate(self):
        name = self.timName()
        if name:
            estimate_str = self.tim.get_estimate(name)

            if estimate_str:
                estimate = estimate_str.split(':')
                if len(estimate) >= 2:
                    hours = int(estimate[0])
                    minutes = int(estimate[1])
                    seconds = int(estimate[2]) if len(estimate) >= 3 else 0

                    if self.currentEstimateUnit == "hours":
                        self.currentEstimate = hours
                    elif self.currentEstimateUnit == "minutes":
                        self.currentEstimate = minutes

                    self.spbEstimateValue.setValue(self.currentEstimate)

                    dt_estimate = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                    dt_time = self.tim.total_time(name)

                    if dt_time.total_seconds() > dt_estimate.total_seconds():
                        self.pgbProgress.setMaximum(dt_estimate.total_seconds())
                        self.pgbProgress.setValue(dt_time.total_seconds())
                    else:
                        self.pgbProgress.setMaximum(dt_estimate.total_seconds())
                        self.pgbProgress.setValue(dt_time.total_seconds())   
            else:
                self.currentEstimate = 0
                self.spbEstimateValue.setValue(self.currentEstimate)

    def saveEstimate(self):
        hours = 0
        minutes = 0
        seconds = 0

        if self.currentEstimateUnit == "hours":
            hours = self.currentEstimate
        elif self.currentEstimateUnit == "minutes":
            minutes = self.currentEstimate
        
        name = self.timName()
        if name:
            estimate = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
            self.tim.set_estimate(name, estimate)

            self.updateEstimate()

    def getStatusText(self, name):
        diff = self.tim.diff(name)
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        diff_str = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
        total_time_str = self.tim.total_time_str(name)
        return "{0} ({1})".format(diff_str, total_time_str)
    
    def updateProjectNameSearch(self, pname):
        names = self.searchProjectNames(pname)
        
        self.txtProject.clear()
        for name in names:
            self.txtProject.addItem(name)

        self.txtProject.setCurrentText(pname)
            
                    
    def clearTxtAddTime(self):
        self.txtAddTime.clearEditText()

    def searchProjectNames(self, pname):
        ret = set()
        if pname:
            name =  self.currentType + ':' + pname
            rname = r'^' + name + r"(.*)$"
            
            works_by_name = list(filter(lambda d: re.search(rname, d['name']), self.tim.data['work']))

            for work in works_by_name:
                names = work['name'].split(':')
                if len(names) > 0:
                    if names[0] == self.prefix or (self.currentType == self.OTHER_WORK and names[0] == self.OTHER_WORK):
                        pname = ""
                        if len(names) == 3:
                            pname = names[2]
                        elif len(names) > 3:
                            pname = ":".join(names[2:])
                        elif len(names) >= 2:
                            pname = ":".join(names[1:])
                        elif len(names) == 1:
                            pname = names[0]

                        if pname:
                            ret.add(pname)

        return ret