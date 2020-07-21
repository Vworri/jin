from PyQt5.QtCore import QTime, QTimer, QDateTime
from PyQt5.QtCore import QSize , QDateTime  
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QDropEvent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


class DigitalClock(QLCDNumber):

    def __init__(self, parent=None):
        super(DigitalClock, self).__init__(parent)
        self.setSegmentStyle(QLCDNumber.Filled)
        self.setDigitCount(10)
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)
        self.showTime()
        self.setWindowTitle("Digital Clock")
        self.setMinimumHeight(60)

    def showTime(self):
        time = QTime.currentTime()
        text = time.toString('hh:mm:ss')
        if (time.second() % 2) == 0:
            text = text[:2] + ' ' + text[3:5]+' '+text[6:]
        self.display(text)

class DateTimeWidget(QWidget):
    def __init__(self):
        super(DateTimeWidget, self).__init__()
        self.vbox = QVBoxLayout()
        date = QLabel(QDateTime.currentDateTime().toString('ddd MMMM d yy'))
        self.vbox.addWidget(date)
        self.vbox.setAlignment(QtCore.Qt.AlignCenter) 
        self.vbox.addWidget(DigitalClock())
        self.vbox.setContentsMargins(0,0,0,0)
        self.setLayout(self.vbox)
        self.setFixedWidth(250)
        self.setFixedHeight(250)
        


class AutoComplete(QWidget):
    def __init__(self, values=[]):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        self.values = values

        # auto complete options                      
        completer = QCompleter(values)
        # create line edit and add auto complete                                
        self.lineedit = QLineEdit()
        self.lineedit.setCompleter(completer)
        layout.addWidget(self.lineedit, 0, 0)

    def value(self):
        if self.lineedit.text() in self.values:
            self.lineedit.setStyleSheet('QLineEdit { background-color: white }')
            return self.lineedit.text()
        else:
            self.lineedit.setStyleSheet('QLineEdit { background-color: red }')
            return -1

class TableView(QTableWidget):
    def __init__(self,cols, data, *args):
        QTableWidget.__init__(self, *args)
        self.data =[]
        self.setColumnCount(len(cols))
        self.setHorizontalHeaderLabels(cols)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        
        if data:
            self.data = data
            self.set_table()
        

    def dropEvent(self, event: QDropEvent):
        if not event.isAccepted() and event.source() == self:
            drop_row = self.drop_on(event)
            
            rows = sorted(set(item.row() for item in self.selectedItems()))
            rows_to_move = [[QTableWidgetItem(self.item(row_index, column_index)) for column_index in range(self.columnCount())]
                            for row_index in rows]
            self.data.insert(drop_row-1,self.data.pop(rows[0]))
            self.update_data(self.data)
        super().dropEvent(event)

   
    def is_below(self, pos, index):
            rect = self.visualRect(index)
            margin = 2
            if pos.y() - rect.top() < margin:
                return False
            elif rect.bottom() - pos.y() < margin:
                return True
            # noinspection PyTypeChecker
            return rect.contains(pos, True) and not (int(self.model().flags(index)) & Qt.ItemIsDropEnabled) and pos.y() >= rect.center().y()
    
    
    def drop_on(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return self.rowCount()

        return index.row() + 1 if self.is_below(event.pos(), index) else index.row()

    def set_table(self):
    
        self.set_data()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
 
    def set_data(self): 
        for row, item_list in enumerate(self.data):
            if self.rowCount() <= row:
                self.insertRow(row)
            for col, key in enumerate(item_list.__dict__):
                newitem = QTableWidgetItem(str(item_list.__dict__[key]))
                self.setItem(row, col, newitem)

    def update_data(self, data):
        self.clear()
        self.data = data
        self.set_table()
        

class Separator(QFrame):
    def __init__(self):
        QFrame.__init__(self)
        self.setFrameShape(QFrame.HLine)
        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Expanding)
        self.setLineWidth(3)

class ListModel(QtCore.QAbstractListModel):
    def __init__(self, *args, list_items=None, **kwargs):
        super(ListModel, self).__init__(*args, **kwargs)
        self.list_items = list_items or []
        self.tick = QtGui.QImage('/home/v/Projects/Tether/UI/icons/icons8-tick-box-64.png')
        self.untick = QtGui.QImage('/home/v/Projects/Tether/UI/icons/icons8-unchecked-checkbox-64.png')

    def data(self, index, role):
        if role == Qt.DisplayRole:
            _, text = self.list_items[index.row()]
            return text

        if role == Qt.DecorationRole:
            status, _ = self.list_items[index.row()]
            if status:
                return self.tick
            else:
                return self.untick

    def rowCount(self, index):
        return len(self.list_items)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    clock = DateTimeWidget()
    clock.show()
    sys.exit(app.exec_())