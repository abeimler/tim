from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QTreeWidgetItem, QTableWidgetItem

import re
from datetime import datetime, timedelta, date, timezone
import json

from .tim.timscript import Tim


class TimTableModel(QtCore.QAbstractTableModel): 
    def __init__(self, parent=None, *args): 
        super(TimTableModel, self).__init__()
        
        self.tim = Tim()

        self.works = []
        self.start_min = ""
        self.end_max = ""
        self.total_dura = ""

        
    def update(self, dataIn):
        self.tim = dataIn
        self.works = self.tim.data['work']
        if self.selected_work and self.selected_work in self.tim.data_map:
            work = self.tim.data_map[self.selected_work]
            self.works = work['work']

            self.start_min = min(self.works, key=lambda x: x['start'])['start']
            self.end_max = max(self.works, key=lambda x: x['end'])['end']
            self.total_dura = work['delta_str']
        else:
            self.start_min = ""
            self.end_max = ""
            self.total_dura = ""
     
    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.works) 
        
    def columnCount(self, parent=QtCore.QModelIndex()):
        return 4

    
    def headerData(self, rowcol, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            columns = [
                'Name', 
                'Start ({0})'.format(self._format_datetime(self.start_min)) if self.start_min else 'Start', 
                'End ({0})'.format(self._format_datetime(self.end_max)) if self.end_max else 'End', 
                'Duration ({0})'.format(self.total_dura) if self.total_dura else 'Duration'
            ]
            if rowcol < 4:
                return columns[rowcol]

        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            if rowcol < len(self.works):
                if 'index' in self.works[rowcol]:
                    return str(self.works[rowcol]['index']+1)
            return str(rowcol+1)

        return None
        
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            i = index.row()
            j = index.column()
            
            if i < len(self.works):
                data = self.works[i]
                start = self._format_datetime(data["start"])
                end = self._format_datetime(data["end"]) if 'end' in data else "on going"
                delta_str = self.tim.delta_str(data["start"], data["end"]) if 'end' in data else "not done, yet"

                if j == 0:
                    return data['name']
                elif j == 1:
                    return start
                elif j == 2:
                    return end
                elif j == 3:
                    return delta_str
        elif role == QtCore.Qt.EditRole or role == QtCore.Qt.UserRole:
            i = index.row()
            j = index.column()
            
            if i < len(self.works):
                data = self.works[i]
                start = self.tim.parse_isotime(data["start"])
                end = self.tim.parse_isotime(data["end"]) if 'end' in data else None
                delta = end - start if 'end' in data else None

                if j == 0:
                    return data['name']
                elif j == 1:
                    return start
                elif j == 2:
                    return end
                elif j == 3:
                    return delta
        
        return None
    
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ret = False
        if role == QtCore.Qt.EditRole:
            i = index.row()
            j = index.column()

            if i < len(self.works):
                index = i
                work = self.works[index]
                if 'index' in self.works:
                    index = self.works['index']
                    work = self.tim.data['work'][index]
                elif i < len(self.tim.data['work']):
                    index = i
                    work = self.tim.data['work'][index]

                if j == 0:
                    work['name'] = value
                    ret = True
                elif j == 1:
                    if self.tim.valid_engtime(value):
                        work['start'] = self.tim.parse_isotime_str(value)
                        ret = True
                elif j == 2:
                    if self.tim.valid_engtime(value):
                        work['end'] = self.tim.parse_isotime_str(value)
                        ret = True

                if ret:
                    self.tim.set_work(index, work)
                    self.update(self.tim)

                    self.dataChanged.emit(index, index)

        return ret

    def removeRows(self, row, count, parent):
        self.beginRemoveRows(parent, row, row+count-1)

        ret = False
        if row < len(self.works):
            index = row
            if 'index' in self.works:
                index = self.works['index']
            elif row < len(self.tim.data['work']):
                index = row

            ret = True
            self.tim.remove_work(range(row, row+count))
            self.update(self.tim)

        self.endRemoveRows()

        return ret

    def flags(self, index):
        flags = super(self.__class__, self).flags(index)
        flags |= QtCore.Qt.ItemIsEditable
        #flags |= QtCore.Qt.ItemIsSelectable
        flags |= QtCore.Qt.ItemIsEnabled
        #flags |= QtCore.Qt.ItemIsDragEnabled
        #flags |= QtCore.Qt.ItemIsDropEnabled
        return flags

    def sort(self, Ncol, order):
        try:
            self.layoutAboutToBeChanged.emit()

            if Ncol == 0:
                self.works = sorted(self.works, key=lambda k: k['name'], reverse=not order)
            elif Ncol == 1:
                self.works = sorted(self.works, key=lambda k: self.tim.parse_isotime(k['start']), reverse=not order)
            elif Ncol == 2:
                self.works = sorted(self.works, key=lambda k: self.tim.parse_isotime(k['end']) if 'end' in k else datetime.now(timezone.utc), reverse=not order)
            elif Ncol == 3:
                self.works = sorted(self.works, key=lambda k: self.tim.parse_isotime(k['end']) - self.tim.parse_isotime(k['start']) if 'end' in k else datetime.now(timezone.utc) - self.tim.parse_isotime(k['start']), reverse=not order)
            
            self.layoutChanged.emit()
        except Exception as e:
            print(e)
        
    def _format_datetime(self, at):
        self.date_format = "%d %b %Y %H:%M:%S";
        LOCAL_TIMEZONE = datetime.now().astimezone().tzinfo
        return self.tim.parse_isotime(at).astimezone(LOCAL_TIMEZONE).strftime(self.date_format)