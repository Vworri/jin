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
        self.showFullScreen()
        self.setWindowIcon(QtGui.QIcon('UI/icons/laughingman.png'))
        self.vbox = QVBoxLayout()
        self.setWindowTitle("Tether") 
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        # Set up menu 
        self.mainMenu = self.menuBar()
        self.fileMenu = self.mainMenu.addMenu('File')
        self.editMenu = self.mainMenu.addMenu('Edit')
        self.set_up_edit_actions()
        self.set_up_file_actions()
        self.dash = Dashboard()
        self.tabs.addTab(self.dash, "Dashboard")
        self.todo = TodoList()
        self.fitness_workout = WorkoutManager(self)
        self.fitness_programs = ProgramManager(self)
        
        self.tabs.addTab(self.todo,"Todo")
        self.vbox.addWidget(self.tabs)

        window = QWidget();
        window.setLayout(self.vbox);
        self.setCentralWidget(window);

    def set_up_edit_actions(self):
        # Add Workout
        openWorkoutManager = QAction("Manage Workouts", self)
        openWorkoutManager.setShortcut("Ctrl+W")
        openWorkoutManager.setStatusTip('Add, Remove, and Update Workouts')
        openWorkoutManager.triggered.connect(self.open_workout_creator)
        self.editMenu.addAction(openWorkoutManager)
        # Add Program
        openProgramManager = QAction("Manage Workout Programs", self)
        openProgramManager.setShortcut("Ctrl+P")
        openProgramManager.setStatusTip('Add, Remove, and Update programs')
        openProgramManager.triggered.connect(self.open_program_creator)
        self.editMenu.addAction(openProgramManager)

    def set_up_file_actions(self):
        closeProgram = QAction("Close", self)
        closeProgram.setShortcut("Ctrl+Q")
        closeProgram.setStatusTip('Leave The App')
        closeProgram.triggered.connect(self.close_application)
        self.fileMenu.addAction(closeProgram)


    def open_workout_creator(self):
        if self.tabs.indexOf(self.fitness_workout) == -1:
            self.tabs.addTab(self.fitness_workout,"Workout Creator")
        self.tabs.setCurrentWidget (self.fitness_workout)

    def open_program_creator(self):
        if self.tabs.indexOf(self.fitness_programs) == -1:
            self.tabs.addTab(self.fitness_programs,"Program Creator")
        self.tabs.setCurrentWidget (self.fitness_programs)
    

    
       
    def close_application(self):
        sys.exit()
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = HelloWindow()
    mainWin.show()
    sys.exit( app.exec_() )