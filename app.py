import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTime, QTimer, QDateTime
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QTabWidget
from PyQt5.QtCore import QSize , QDateTime  
from UI.simple_widgets import *
from UI.todo import *
from UI.workout import *
from UI.dashboard import Dashboard
import qtmodern.styles
import qtmodern.windows



class HelloWindow(QMainWindow):
    def __init__(self):
        QWidget.__init__(self)
        self.setStyleSheet(open('/home/v/Projects/Tether/UI/style.css').read())
        self.setMinimumSize(QSize(640, 480))    
        # self.showFullScreen()
        self.setWindowIcon(QtGui.QIcon('UI/icons/laughingman.png'))
        self.vbox = QVBoxLayout()
        self.setWindowTitle("Tether") 
        self.tabs = QTabWidget()
        # self.dash = Dashboard()
        self.todo = TodoList()
        self.fitness_workout = WorkoutManager(self)
        self.fitness_programs = ProgramManager(self)
        self.tabs.addTab(self.fitness_workout,"Fitness")
        self.tabs.addTab(self.fitness_programs,"Dashboard")
        self.tabs.addTab(self.todo,"Todo")
        self.vbox.addWidget(self.tabs)
        
        window = QWidget();
        window.setLayout(self.vbox);
        self.setCentralWidget(window);


       

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = HelloWindow()
    mainWin.show()
    sys.exit( app.exec_() )