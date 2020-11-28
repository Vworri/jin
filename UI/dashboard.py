from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QTabWidget
from UI.simple_widgets import *
from PyQt5.QtCore import QTime, QTimer, QDateTime
from API.garmin import GarminData



class Schedule(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(Schedule, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])



class Dashboard(QWidget):
    def __init__(self):
        super(Dashboard, self).__init__()
    
        gridLayout = QGridLayout() 
        gridLayout.setColumnStretch(1, 4)
        gridLayout.setColumnStretch(2, 4)    
        self.setLayout(gridLayout)  
        self.clock = DateTimeWidget()
        gridLayout.addWidget(self.clock, 0, 0)

class DayView(QWidget):
    def __init__(self):
        super(DayView, self).__init__()
    

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec_())