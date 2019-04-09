from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QTreeWidgetItem, QTableWidgetItem, QMessageBox, QErrorMessage

import re
from datetime import datetime, timedelta, date, timezone
import json

from .tim.timscript import Tim
from .ui_mainwindow import Ui_MainWindow
from .table import TimTableModel

class MainForm(QMainWindow,Ui_MainWindow):    
    def __init__(self):     
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
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

        self._status_update_timer = QtCore.QTimer(self)
        self._status_update_timer.setSingleShot(False)
        self._status_update_timer.timeout.connect(self._update_status)
        self._status_update_timer.start(1000)

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
        self.treeWorks.itemSelectionChanged.connect(self.changeSeletionTreeWork)

    def updateWindowTitle(self):
        self.setWindowTitle('Timmu ({0})'.format(self.currentProjectName))
    
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
        self.updateWindowTitle()
        

    def updateCurrentSessionInfo(self):
        name = self.timName()
        data = self.tim.get_data(name)
        if data['isstarted']:
            self.lblCurrentSessionInfo.setText(self.getStatusTextLastWork(name))
            self.lblCurrentSessionInfo2.setText(self.getStatusTextCount(name))
            self.lblCurrentSessionInfo3.setText(self.getStatusTextDelta(name))
        else:
            self.lblCurrentSessionInfo.setText(self.getStatusTextLastWork(''))
            self.lblCurrentSessionInfo2.setText(self.getStatusTextCount(''))
            self.lblCurrentSessionInfo3.setText(self.getStatusTextDelta(''))

    def updateLastSessionInfo(self):
        if self.lastTimName:
            self.lblLastSessionInfo.setText(self.lastTimName)
            self.lblLastSessionInfo2.setText(self.getStatusTextDelta(self.lastTimName))

    def _update_status(self):
        self.updateCurrentWork()

    def updateCurrentWork(self):
        name = self.timName()
        self.tim.update_map(name)
        self.updateCurrentSessionInfo()
        self.updateEstimateProgress()

    def updateWork(self):
        self.currentProjectName = self.txtProject.currentText().lower()
        self.currentType = self.cmbType.currentData().lower()

        self.updateUI()
        self.updateWindowTitle()

        self.updateCurrentSessionInfo()
        self.updateLastSessionInfo()

    def saveTimeclock(self):
        if self.tim.get_config_gen_timeclock():
            self.tim.hledger_save()

    def clickedStartStop(self):
        try:
            if self.valid_time():
                self.currentTimName = self.timName()
                self.startStopWorkToggle()
                self.saveTimeclock()

                self.updateCurrentSessionInfo()

                self.updateProjectTreeData()
                self.updateProjectTableData()
        except RuntimeError as e:
            error_dialog = QErrorMessage(self)
            error_dialog.showMessage(str(e))

    def clickedBreak(self):
        try:
            if self.valid_time():
                self.currentTimName = self.timBreakName()
                self.startStopWorkToggle()
                self.saveTimeclock()

                self.updateProjectTreeData()
                self.updateProjectTableData()
        except RuntimeError as e:
            error_dialog = QErrorMessage(self)
            error_dialog.showMessage(str(e))
    



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
        
        self.updateCurrentSessionInfo()
        self.updateEstimate()

    def editProjectNamePressEnter(self):
        self.updateProjectNameSearch(self.currentProjectName)


    def editProjectName(self, pname):
        pass

    def changeProjectNameIndex(self, index):
        pass

    def changeSeletionTreeWork(self):
        self.updateProjectTableData()

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
        try:
            time = self.tim.parse_isotime(self.tim.to_datetime(self.txtAddTime.currentText().lower()))
            current_time = self.tim.current_work_start_time()
            return current_time is None or time >= current_time
        except RuntimeError as e:
            return False
    
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
                        dt_time = self.tim.data_map[name]['delta']

                        if dt_time.total_seconds() > dt_estimate.total_seconds():
                            self.pgbProgress.setMaximum(dt_estimate.total_seconds())
                            self.pgbProgress.setValue(dt_time.total_seconds())
                        else:
                            self.pgbProgress.setMaximum(dt_estimate.total_seconds())
                            self.pgbProgress.setValue(dt_time.total_seconds())   
            else:
                self.currentEstimate = 0
                self.spbEstimateValue.setValue(self.currentEstimate)
                self.pgbProgress.setMaximum(0)


    def updateEstimateProgress(self):
        name = self.timName()
        if name != "" and self.currentEstimate > 0:
            estimate_str = "00:00:00"
            if self.currentEstimateUnit == "hours":
                estimate_str = '{:04}:{:02}:{:02}'.format(int(self.currentEstimate), int(0), int(0))
            elif self.currentEstimateUnit == "minutes":
                estimate_str = '{:04}:{:02}:{:02}'.format(int(0), int(self.currentEstimate), int(0))

            if estimate_str:
                estimate = estimate_str.split(':')
                if len(estimate) >= 2:
                    hours = int(estimate[0])
                    minutes = int(estimate[1])
                    seconds = int(estimate[2]) if len(estimate) >= 3 else 0

                    if self.currentEstimate != 0:
                        dt_estimate = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                        dt_time = self.tim.data_map[name]['delta']

                        if dt_time.total_seconds() > dt_estimate.total_seconds():
                            self.pgbProgress.setMaximum(dt_estimate.total_seconds())
                            self.pgbProgress.setValue(dt_time.total_seconds())
                            return
                        else:
                            self.pgbProgress.setMaximum(dt_estimate.total_seconds())
                            self.pgbProgress.setValue(dt_time.total_seconds())   
                            return

        self.pgbProgress.setValue(0)   
        self.pgbProgress.setMaximum(0)

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

    def getStatusTextLastWork(self, name):
        diff_str = '--:--:--'
        total_time_str = '0 hours'
        if name:
            data = self.tim.get_data(name)

            diff_str = str(data['last_work_delta'])
            total_time_str = data['last_work_delta_str']
        
        return "{0} ({1})".format(diff_str, total_time_str)

    def getStatusTextCount(self, name):
        count = 0
        if name:
            data = self.tim.get_data(name)
            count = data['count']

        return "Entries Count: {0}".format(count)

    def getStatusTextDelta(self, name):
        diff_str = '--:--:--'
        total_time_str = '0 hours'
        if name:
            data = self.tim.get_data(name)

            diff_str = str(data['delta'])
            total_time_str = data['delta_str']

        return "{0} ({1})".format(diff_str, total_time_str)
    
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

    def _format_datetime(self, dt):
        self.date_format = "%d %b %Y %H:%M:%S";
        LOCAL_TIMEZONE = datetime.now().astimezone().tzinfo
        return self.tim.parse_isotime(dt).astimezone(LOCAL_TIMEZONE).strftime(self.date_format)

    def updateProjectTableData(self):
        selected_work = ""
        selected = self.treeWorks.selectedItems()
        if len(selected) > 0:
            selected_work = selected[0].text(1)

        model = TimTableModel(self)
        model.selected_work = selected_work
        model.update(self.tim)

        self.tblWorks.setModel(model)

        self.tblWorks.resizeColumnsToContents()

        

    

    def updateProjectTreeData(self):
        keys = self.tim.data_map.keys()

        tree = []

        self.treeWorks.clear()

        for work_name in keys:
            
            names = work_name.split(':')
            if len(names) > 0:
                prefixname = names[0]
                typename = names[1] if len(names) >= 2 else ""
                projectname = names[2] if len(names) >= 3 else ""
                subprojectname = ':'.join(names[3:]) if len(names) >= 4 else ""

                roottree = list(filter(lambda t: t.text(0) == prefixname, tree))
                if len(roottree) == 0:
                    tree.append(QTreeWidgetItem([prefixname, prefixname]))
                    prefixitem = tree[0]
                else:
                    prefixitem = roottree[0]

                findtypechild = self._addChildProjectToTree(prefixitem, typename, prefixname + ":" + typename)
                findprojectchild = self._addChildProjectToTree(findtypechild, projectname, prefixname + ":" + typename + ":" + projectname)
                findsubprojectchild = self._addChildProjectToTree(findprojectchild, subprojectname, prefixname + ":" + typename + ":" + projectname + ":" + subprojectname)

        self.treeWorks.addTopLevelItems(tree)


    def _addChildProjectToTree(self, parent, projectname, fullprojectname):
        newchild = None
        if parent:
            findchild = None
            for i in range(parent.childCount()):
                parentchild = parent.child(i)

                if parentchild.text(0) == projectname:
                    findchild = parentchild
                    break

            if findchild is None and projectname != "":
                parent.addChild(QTreeWidgetItem([projectname, fullprojectname]))
                newchild = parent.child(parent.childCount()-1)
            else:
                newchild = findchild

        return newchild