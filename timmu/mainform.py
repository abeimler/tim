from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QTreeWidgetItem, QTableWidgetItem

import re
from datetime import datetime, timedelta, date
import json

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
        self.tim.load()
        print(json.dumps(self.tim.data_map, indent=4, sort_keys=True, default=str))

        self.chbAutoStart.setChecked(self.tim.get_config_autostart())
        #self.chbAutoStop.setChecked(self.tim.get_config_autostop())
        self.chbGenTimeclock.setChecked(self.tim.get_config_gen_timeclock())
        
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

        self.updateProjectTreeData()
        self.updateProjectTableData()

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
        self.chbGenTimeclock.stateChanged.connect(self.changeGenTimeclock)
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
        
        self.updateCurrentSessionInfo()
        self.updateLastSessionInfo()

        self.updateEstimateProgress()

    def updateCurrentSessionInfo(self):
        name = self.timName()
        self.lblCurrentSessionInfo.setText(self.getStatusText(name))
        self.lblCurrentSessionInfo2.setText(self.getStatusText2(name))

    def updateLastSessionInfo(self):
        if self.currentTimName:
            if self.currentTimName != self.timBreakName() and self.currentProjectName:
                self.lblCurrentSessionInfo.setText(self.getStatusText(self.currentTimName))
                self.lblCurrentSessionInfo2.setText(self.getStatusText2(self.currentTimName))
        elif self.lastTimName:
            self.lblCurrentSessionInfo.setText(self.getStatusText(self.lastTimName))
            self.lblCurrentSessionInfo2.setText(self.getStatusText2(self.lastTimName))
            

    def updateWork(self):
        self.currentProjectName = self.txtProject.currentText().lower()
        self.currentType = self.cmbType.currentData().lower()

        self.updateUI()

    def saveTimeclock(self):
        if self.tim.get_config_gen_timeclock():
            self.tim.hledger_save()

    def clickedStartStop(self):
        if self.valid_time():
            self.currentTimName = self.timName()
            self.startStopWorkToggle()
            self.saveTimeclock()

            self.updateProjectTreeData()
            self.updateProjectTableData()

    def clickedBreak(self):
        if self.valid_time():
            self.currentTimName = self.timBreakName()
            self.startStopWorkToggle()
            self.saveTimeclock()

            self.updateProjectTreeData()
            self.updateProjectTableData()
    



    def changeType(self,index):
        self.currentType = self.cmbType.itemData(index).lower()
        self.currentTimName = self.timName()
        self.updateUIButtons()

    def changeAutoStart(self, state):
        if state == QtCore.Qt.Checked:
            self.tim.set_config_autostart(True)
        else:
            self.tim.set_config_autostart(False)

    def changeGenTimeclock(self, state):
        if state == QtCore.Qt.Checked:
            self.tim.set_config_gen_timeclock(True)
        else:
            self.tim.set_config_gen_timeclock(False)
    
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
        
        self.lblLastSessionInfo.setText(self.getStatusText(self.timName()))
        self.updateLastSessionInfo()
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

                    if self.currentEstimate != 0:
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
                self.pgbProgress.setMaximum(100)


    def updateEstimateProgress(self):
        name = self.timName()
        if name != "" and self.currentEstimate > 0:
            estimate_str = "00:00:00"
            if self.currentEstimateUnit == "hours":
                estimate_str = '{:02}:{:02}:{:02}'.format(int(self.currentEstimate), int(0), int(0))
            elif self.currentEstimateUnit == "minutes":
                estimate_str = '{:02}:{:02}:{:02}'.format(int(0), int(self.currentEstimate), int(0))

            if estimate_str:
                estimate = estimate_str.split(':')
                if len(estimate) >= 2:
                    hours = int(estimate[0])
                    minutes = int(estimate[1])
                    seconds = int(estimate[2]) if len(estimate) >= 3 else 0

                    if self.currentEstimate != 0:
                        dt_estimate = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                        dt_time = self.tim.total_time(name)

                        if dt_time.total_seconds() > dt_estimate.total_seconds():
                            self.pgbProgress.setMaximum(dt_estimate.total_seconds())
                            self.pgbProgress.setValue(dt_time.total_seconds())
                            return
                        else:
                            self.pgbProgress.setMaximum(dt_estimate.total_seconds())
                            self.pgbProgress.setValue(dt_time.total_seconds())   
                            return

        self.pgbProgress.setValue(0)   
        self.pgbProgress.setMaximum(100)

    def saveEstimate(self):
        if self.currentEstimate != 0:
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
                if self.tim.get_estimate(name) != estimate:
                    self.tim.set_estimate(name, estimate)

                self.updateEstimate()

    def getStatusText(self, name):
        data = self.tim.get_data(name)

        diff_str = str(data['delta'])
        total_time_str = data['delta_str']

        return "{0} ({1})".format(diff_str, total_time_str)

    def getStatusText2(self, name):
        data = self.tim.get_data(name)

        return "Entries Count: {0}".format(data['count'])
    
    def updateProjectNameSearch(self, pname):
        names = self.searchProjectNames(pname)
        names.add(pname)
        
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

    def updateProjectTableData(self):
        self.tblWorks.setColumnCount(4)
        self.tblWorks.setHorizontalHeaderLabels(['Name', 'Start', 'End', 'Duration'])

        self.tblWorks.setRowCount(len(self.tim.data['work']))

        self.date_format = "%d %b %Y %H:%M:%S";
        LOCAL_TIMEZONE = datetime.now().astimezone().tzinfo

        for index, work in enumerate(self.tim.data['work']):
            delta_str = self.tim.delta_str(work["start"], work["end"])
            start = self.tim.parse_isotime(work["start"]).astimezone(LOCAL_TIMEZONE).strftime(self.date_format)
            end = self.tim.parse_isotime(work["end"]).astimezone(LOCAL_TIMEZONE).strftime(self.date_format)

            self.tblWorks.setItem(index, 0, QTableWidgetItem(work["name"]))
            self.tblWorks.setItem(index, 1, QTableWidgetItem(start))
            self.tblWorks.setItem(index, 2, QTableWidgetItem(end))
            self.tblWorks.setItem(index, 3, QTableWidgetItem(delta_str)) 


        

    

    def updateProjectTreeData(self):
        keys = self.tim.data_map.keys()

        tree = []

        for work_name in keys:
            rootname = ""
            name = ""
            depth = 0
            for depth, n in enumerate(work_name.split(':')):
                rootname = name
                name = name + ":" + n if name != "" else n
                depth = depth+1

                finds = [i for i, t in enumerate(tree) if t.text(0) == n]

                if len(finds) == 0:
                    if depth == 1:
                        tree.append(QTreeWidgetItem([n]))
        
        self.treeWorks.addTopLevelItems(tree)