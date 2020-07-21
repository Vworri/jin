import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTime, QTimer, QDateTime
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QTabWidget
from PyQt5.QtCore import QSize , QDateTime  
from UI.simple_widgets import *
from UI.todo import *
from UI.workout import *
from UI.dashboard import Dashboard


class HelloWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setStyleSheet(open('/home/v/Projects/Tether/UI/style.css').read())
        self.setMinimumSize(QSize(640, 480))    
        self.showFullScreen()
        self.setWindowIcon(QtGui.QIcon('UI/icons/laughingman.png'))
        self.vbox = QVBoxLayout()
        self.setWindowTitle("Tether") 
        self.tabs = QTabWidget()
        # self.dash = Dashboard()
        self.todo = TodoList()
        self.fitness = WorkoutManager(self)
        self.tabs.addTab(self.fitness,"Fitness")
        # self.tabs.addTab(self.dash,"Dashboard")
        self.tabs.addTab(self.todo,"Todo")
        self.vbox.addWidget(self.tabs)
        self.setLayout(self.vbox)


       

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = HelloWindow()
    mainWin.show()
    sys.exit( app.exec_() )