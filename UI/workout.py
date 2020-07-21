
import pandas as pd
from UI.simple_widgets import AutoComplete, TableView, ListModel
from data.fitness import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
from database.db import Database as Db
import numpy as np 
import os
import glob
import json
import sqlite3
import sys



class MovementForm(QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self,movement, parent=None):
        QDialog.__init__(self, parent)
        self.movement = movement
        self.conn = sqlite3.connect('example.db')
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.vals = pd.read_sql_query('SELECT * FROM exercises', self.conn)
        buttonBox.accepted.connect(self.accept)
        self.exercises = []
        self.bodyParts = []
        self.getExerciseVals()
        self.isTimed = False
        self.formGroupBox = QGroupBox("Form layout")
        self.ExDropdown = AutoComplete(self.exercises)
        self.isTimerEnabled = QCheckBox("Enable Timer", self)
        self.isTimerEnabled.stateChanged.connect(self.clickBox)
        self.reps =  QSpinBox()
        self.weight =  QSpinBox()
        self.sets = QSpinBox()
        self.createFormGroupBox()


        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

    def getExerciseVals(self, filter= None):
        if filter == None:
            self.exercises = self.vals["name"].to_list()

          
    def createFormGroupBox(self):
        layout = QFormLayout()
        layout.addRow(QLabel("Exercise Name:"), self.ExDropdown)
        layout.addRow(QLabel("Reps:"),self.reps)
        layout.addRow(QLabel("Weight:"),self.weight)
        layout.addRow(QLabel("Sets:"),self.sets)
        layout.addRow(QLabel("Enable Timer:"), self.isTimerEnabled)
        self.formGroupBox.setLayout(layout)

    def clickBox(self, state):
        if state == QtCore.Qt.Checked:
            self.isTimed = True
        else:
            self.isTimed = False
    
    def accept(self):
        if self.ExDropdown.value() == -1:
            return
        else:      
            self.movement.name = self.ExDropdown.value()
            self.movement.load = self.weight.value()
            self.movement.reps = self.reps.value()
            self.movement.set = self.reps.value()
            self.movement.timed = self.isTimed
            self.close()

class SectionWidget(QWidget):
        def __init__(self, section, parent = None):
            QWidget.__init__(self, parent)
            self.parent = parent
            self.section = section
            self.order = self.section.order
            self.reps_l = QLabel("Section Reps")
            self.reps =  QSpinBox()
            self.l  = QVBoxLayout()
            self.movement_table = TableView(["Name", "Load", "Reps", "Sets", "Timed?"], self.section.movements, self.contextMenuEventMovement)
            self.add_movement_button = QPushButton("Add Movement",self)
            self.movement_table.setFrameShape(QFrame.NoFrame)
            self.l.addWidget(self.reps_l) 
            self.l.addWidget(self.reps) 
            self.l.addWidget(self.movement_table)
           
            self.l.addWidget(self.add_movement_button)
            
            self.add_movement_button.clicked.connect(self.add_movement)
            self.setLayout(self.l)
        
        def contextMenuEventMovement(self, event):
            menu = QMenu()
            deleteAction = menu.addAction("Delete Movement")
            action = menu.exec_( self.mapToGlobal(event.pos()))
            if action == deleteAction:
                i =  self.movement_table.indexAt(event.pos())
                self.section.movements.pop(i.row())
                self.movement_table.update_data(self.section.movements)
                self.movement_table.update()

        def contextMenuEvent(self, event):
            menu = QMenu(self)
            deleteAction = menu.addAction("Delete")
            move_dn_Action = menu.addAction("Move Down")
            move_up_Action = menu.addAction("Move Up")
            action = menu.exec_(self.mapToGlobal(event.pos()))
            if action == deleteAction:
                self.parent.w.sections.pop(self.order)
                self.setParent(None)
            elif action == move_dn_Action:
                self.parent.sectionWidgets.insert(self.order+1,self.parent.sectionWidgets.pop(self.order))
                self.parent.w.sections.insert(self.order+1,self.parent.w.sections.pop(self.order))
            elif action == move_up_Action:
                self.parent.sectionWidgets.insert(self.order-1,self.parent.sectionWidgets.pop(self.order))
                self.parent.w.sections.insert(self.order-1,self.parent.w.sections.pop(self.order))
            self.parent.redraw_sections()
           
        def add_movement(self):
            self.section.add_movement()
            dialog = MovementForm(self.section.movements[-1], parent=self)
            dialog.exec()
            self.movement_table.update_data(self.section.movements)


class WorkoutEditor(QWidget):
        def __init__(self, w:Workout=None, parent = None):
            QWidget.__init__(self, parent)
            self.parent = parent
            self.sectionWidgets = []
            if w == None:
                self.w = Workout()
            else:
                self.w = w
            self.setWindowTitle(self.w.name)
            
            
            self.name_l = QLabel("Workout Name")
            self.name =  QLineEdit()
            self.name.textChanged.connect(self.name_changed)
            self.name.setText(self.w.name)
            self.layout = QGridLayout() 
            self.add_section_button = QPushButton("Add Section",self)
            self.add_section_button.clicked.connect(self.add_section)
            self.save_workout_button = QPushButton("Save Workout",self)
            self.save_workout_button.clicked.connect(self.save_workout)
            self.layout.addWidget(self.name)
            self.layout.addWidget(self.add_section_button)
            self.layout.addWidget(self.save_workout_button)
            self.setLayout(self.layout)
            self.init_section()
            

        def init_section(self):
            for s in self.w.sections:
                self.sectionWidgets.append(SectionWidget(s, self))
                self.layout.addWidget(self.sectionWidgets[-1])
        
        def name_changed(self,text):
            self.w.name = text
            self.setWindowTitle(text)

        def redraw_sections(self):
            for s in self.sectionWidgets:
                self.layout.removeWidget(s)
            for ind, s in enumerate(self.sectionWidgets):
                s.order = ind
                self.w.sections[ind].order = ind
                self.layout.addWidget(s)
            self.update()
                    
        def add_section(self):
            self.w.add_section()
            self.sectionWidgets.append(SectionWidget(self.w.sections[-1], self))
            self.layout.addWidget(self.sectionWidgets[-1])

        def save_workout(self):
            workout = self.w.dump_data()
            with open(f"data/workouts/{self.w.name}.json", "w") as f:
                json.dump(workout, f)
            self.parent.get_workouts()
            self.setParent(None)


class ProgramEditor(QWidget):
        def __init__(self,program=None, parent = None):
            QWidget.__init__(self, parent)
            self.db = Db()
            self.layout = QHBoxLayout()
            if program != None:
                self.program = program
            else:
                self.program = FitnessProgram("PROGRAM")
                self.program.initialize_program()

            
            self.setLayout(self.layout)
            self.hookupWidgets()

        def hookupWidgets(self):
            self.durationW = QSpinBox()
            self.nameW = QLineEdit()
            self.program_table = TableView(["Day", "Workout Path"], self.program.sched)
            
            self.layout.addWidget(self.durationW)
            self.layout.addWidget(self.nameW)
            self.layout.addWidget(self.program_table)



class ProgramManager(QWidget):
        def __init__(self, parent = None):
            QWidget.__init__(self, parent)
            self.db = Db()
            self.add_button = QPushButton("Add Program")
            self.program_list = QListWidget()
            self.get_program_list()
            self.layout = QVBoxLayout()
            self.layout.addWidget(self.program_list)
            self.layout.addWidget(ProgramEditor(parent=self))
            self.setLayout(self.layout)


        def get_program_list(self):
            self.programs = self.db.make_list(self.db.getPrograms())
            R = [l[0]for l in self.programs]
            [self.program_list.insertItem(0,item) for item in np.unique(R)]
           


            
            

        

        




class WorkoutManager(QWidget):
        def __init__(self, parent = None):
            QWidget.__init__(self, parent)
            self.workouts_view =  QListWidget()
            self.workouts_view.clicked.connect(self.workout_selected)
            self.data_path = "data/workouts"
            self.new_workout_button = QPushButton("Create Workout")
            self.new_workout_button.clicked.connect(self.create_workout)
            self.get_workouts()
            self.workouts_view.installEventFilter(self)
            self.grid = QGridLayout()
            self.workout_editor_tabs = QTabWidget(self)
            self.workout_editor_tabs.setTabsClosable(True)
            self.workout_editor_tabs.tabCloseRequested.connect(self.close_workout_tab)
            self.grid.addWidget(self.workouts_view)
            self.grid.addWidget(self.new_workout_button)
            self.grid.addWidget(self.workout_editor_tabs)
            p = ProgramManager()
            self.grid.addWidget(p)
            self.setLayout(self.grid)
        
        def workout_selected(self, item):
            self.edit(item.row())

        def eventFilter(self, source, event):
            if (event.type() == QtCore.QEvent.ContextMenu and
                source is self.workouts_view):
                menu = QMenu()
                deleteAction = menu.addAction('delete')
                editAction = menu.addAction('edit')
                action = menu.exec_(self.mapToGlobal(event.pos()))
                gp = event.globalPos()
                lp = self.workouts_view.viewport().mapFromGlobal(gp)
                index = self.workouts_view.indexAt(lp)
                if action == deleteAction:
                    self.delete(index.row())
                if action == editAction:
                    self.edit(index.row())
                return True
            return super(WorkoutManager, self).eventFilter(source, event)

        def close_workout_tab(self,currentIndex):
            code = self.showDialog("Are you sure you want to close this tab? Changes will NOT be saved")
            if code == 0:
                self.workout_editor_tabs.removeTab(currentIndex)

        def showDialog(self, message):
            msgBox = QMessageBox(self)
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText(message)
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            returnValue = msgBox.exec()
            if returnValue == QMessageBox.Ok:
                return 0
            else:
                return -1
        def get_workouts(self):
            self.workout_paths = glob.glob(f"{self.data_path}/*.json")
            [self.workouts_view.insertItem(0, w) for w in self.workout_paths ]
            
        def delete(self, index:int):
            name = self.workout_paths[index]
            os.remove(f"{name}")
            del self.workout_paths[index]
            self.workouts_view.clear()
            self.get_workouts()

        def create_workout(self):
            w = Workout()
            workout_widget = WorkoutEditor(w, parent=self)
            self.workout_editor_tabs.addTab(workout_widget, w.name)

        def edit(self, index):
            name = self.workout_paths[index]
            with open(f"{name}") as f:
                w = json.load(f)
            work = Workout(w)
            workout_widget = WorkoutEditor(work, parent=self)
            self.workout_editor_tabs.addTab(workout_widget, work.name)
            



if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = WorkoutManager()
    window.show()
    sys.exit(app.exec_())