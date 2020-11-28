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


class ProgramDayForm(QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.get_workouts()
        self.workout_dropdown = AutoComplete(self.workouts)
        self.formGroupBox = QGroupBox()
        self.createFormGroupBox()
        self.setLayout(self.layout)
        self.selected = None

    def get_workouts(self):
        w = Workout()
        self.workouts = [e[0] for e in w.get_workout_list()]

    def createFormGroupBox(self):
        self.layout = QFormLayout()
        self.layout.addRow(QLabel("Workout Name:"), self.workout_dropdown)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(buttonBox)

    def accept(self):
        if self.workout_dropdown.value() == -1:
            return
        else:
            self.selected = self.workout_dropdown.value()
            self.close()


class MovementForm(QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self, movement, parent=None):
        QDialog.__init__(self, parent)
        self.movement = movement
        self.conn = sqlite3.connect("example.db")
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.vals = pd.read_sql_query("SELECT * FROM exercises", self.conn)
        buttonBox.accepted.connect(self.accept)
        self.exercises = []
        self.bodyParts = []
        self.getExerciseVals()
        self.isTimed = False
        self.formGroupBox = QGroupBox("Form layout")
        self.ExDropdown = AutoComplete(self.exercises)
        self.isTimerEnabled = QCheckBox("Enable Timer", self)
        self.isTimerEnabled.stateChanged.connect(self.clickBox)
        self.reps = QSpinBox()
        self.weight = QSpinBox()
        self.sets = QSpinBox()
        self.createFormGroupBox()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

    def getExerciseVals(self, filter=None):
        if filter == None:
            self.exercises = self.vals["name"].to_list()

    def createFormGroupBox(self):
        layout = QFormLayout()
        layout.addRow(QLabel("Exercise Name:"), self.ExDropdown)
        layout.addRow(QLabel("Reps:"), self.reps)
        layout.addRow(QLabel("Weight:"), self.weight)
        layout.addRow(QLabel("Sets:"), self.sets)
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
    def __init__(self, section, parent=None):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.section = section
        self.order = self.section.order
        self.order_w = QLCDNumber()
        self.order_w.display(self.order)
        self.reps_l = QLabel("Section Reps")
        self.setMinimumHeight(750)
        self.reps = QSpinBox()
        self.l = QVBoxLayout()
        self.v = QHBoxLayout()
        self.movement_table = TableView(
            ["Name", "Load", "Reps", "Sets", "Timed?"],
            self.section.movements,
            self.contextMenuEventMovement,
        )

        self.add_movement_button = QPushButton("Add Movement", self)
        self.movement_table.setFrameShape(QFrame.NoFrame)
        self.movement_table.itemChanged.connect(self.update_movements)
        self.l.addWidget(self.reps_l)
        self.l.addWidget(self.reps)
        self.l.addWidget(self.movement_table)
        self.l.addWidget(self.add_movement_button)
        self.add_movement_button.clicked.connect(self.add_movement)
        self.v.addWidget(self.order_w)
        self.v.addLayout(self.l)
        self.setLayout(self.v)

    def update_movements(self, item):
        key = self.movement_table.get_data_key(item.column()).lower()
        self.parent.w.sections[self.order].movements[item.row()].__dict__[
            key
        ] = item.text()
        self.section.movements[item.row()].__dict__[key] = item.text()

    def contextMenuEventMovement(self, event):
        menu = QMenu()
        deleteAction = menu.addAction("Delete Movement")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == deleteAction:
            i = self.movement_table.indexAt(event.pos())
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
            self.parent.sectionWidgets.insert(
                self.order + 1, self.parent.sectionWidgets.pop(self.order)
            )
            self.parent.w.sections.insert(
                self.order + 1, self.parent.w.sections.pop(self.order)
            )
        elif action == move_up_Action:
            self.parent.sectionWidgets.insert(
                self.order - 1, self.parent.sectionWidgets.pop(self.order)
            )
            self.parent.w.sections.insert(
                self.order - 1, self.parent.w.sections.pop(self.order)
            )
        self.order_w.display(self.order)
        self.parent.redraw_sections()

    def add_movement(self):
        self.section.add_movement()
        dialog = MovementForm(self.section.movements[-1], parent=self)
        dialog.exec()
        self.movement_table.update_data(self.section.movements)


class WorkoutEditor(QWidget):
    def __init__(self, w: Workout = None, parent=None):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.sectionWidgets = []
        if w == None:
            self.w = Workout()
        else:
            self.w = w
        self.setWindowTitle(self.w.name)
        self.name_l = QLabel("Workout Name")
        self.name = QLineEdit()
        self.name.textChanged.connect(self.name_changed)
        self.name.setText(self.w.name)
        self.layout = QVBoxLayout()
        self.section_layout = QVBoxLayout()
        self.add_section_button = QPushButton("Add Section", self)
        self.add_section_button.clicked.connect(self.add_section)
        self.save_workout_button = QPushButton("Save Workout", self)
        self.save_workout_button.clicked.connect(self.save_workout)


        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(self.section_layout)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)


        self.layout.addWidget(self.name)
        self.layout.addWidget(self.scrollArea)
        self.layout.addWidget(self.add_section_button)
        self.layout.addWidget(self.save_workout_button)
        self.setLayout(self.layout)
        self.init_section()

    def init_section(self):
        self.sectionWidgets = []
        for s in self.w.sections:
            self.sectionWidgets.append(SectionWidget(s, self))
            self.section_layout.addWidget(self.sectionWidgets[-1])

    def name_changed(self, text):
        self.w.name = text
        self.setWindowTitle(text)

    def redraw_sections(self):
        for s in self.sectionWidgets:
            self.section_layout.removeWidget(s)
        self.init_section()
        for ind, s in enumerate(self.sectionWidgets):
            s.order = ind
            self.w.sections[ind].order = ind
            self.section_layout.addWidget(s)
        self.update()

    def add_section(self):
        self.w.add_section()
        self.sectionWidgets.append(SectionWidget(self.w.sections[-1], self))
        self.section_layout.addWidget(self.sectionWidgets[-1])

    def save_workout(self):
        self.w.save_to_db()
        self.parent.get_workouts()
        self.setParent(None)


class WorkoutManager(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        parent.statusBar()
        self.workouts_view = QListWidget()
        self.workouts_view.clicked.connect(self.workout_selected)
        self.new_workout_button = QPushButton("Create Workout")
        self.new_workout_button.clicked.connect(self.create_workout)
        self.get_workouts()
        self.workouts_view.installEventFilter(self)
        self.workout_panel = QVBoxLayout()
        self.grid = QHBoxLayout()
        self.workout_editor_tabs = QTabWidget(self)
        self.splitter  = QSplitter(QtCore.Qt.Horizontal)
        self.splitter.setSizes([50,200])
        self.workout_editor_tabs.setTabsClosable(True)
        self.workout_editor_tabs.tabCloseRequested.connect(self.close_workout_tab)
        self.workout_panel.addWidget(self.workouts_view)
        self.workout_panel.addWidget(self.new_workout_button)
        self.workouts_view_w = QWidget()
        self.workouts_view_w.setLayout(self.workout_panel);
        self.splitter.addWidget(self.workouts_view_w)
        self.splitter.addWidget(self.workout_editor_tabs)
        self.splitter.setSizes([100,200])
        self.grid.addWidget(self.splitter)
        self.setLayout(self.grid)

    def workout_selected(self, item):
        self.edit(item.row())

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.ContextMenu and source is self.workouts_view:
            menu = QMenu()
            deleteAction = menu.addAction("delete")
            editAction = menu.addAction("edit")
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

    def close_workout_tab(self, currentIndex):
        code = self.showDialog(
            "Are you sure you want to close this tab? Changes will NOT be saved"
        )
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
        w = Workout()
        self.workout_names = w.get_workout_list()
        self.workouts_view.clear()
        [self.workouts_view.insertItem(0, n[0]) for n in self.workout_names]

    def delete(self, index: int):
        name = self.workout_names[index -1][0]
        w = Workout()
        w.delete(name)
        self.workouts_view.clear()
        self.get_workouts()

    def create_workout(self):
        w = Workout()
        workout_widget = WorkoutEditor(w, parent=self)
        self.workout_editor_tabs.addTab(workout_widget, w.name)

    def edit(self, index):
        name = self.workout_names[index][0]
        work = Workout(name)
        workout_widget = WorkoutEditor(work, parent=self)
        self.workout_editor_tabs.addTab(workout_widget, work.name)

class ProgramEditor(QWidget):
    def __init__(self, program=None, parent=None):
        QWidget.__init__(self, parent)
        self.db = Db()
        self.layout = QVBoxLayout()
        if program != None:
            self.program = program
        else:
            self.program = FitnessProgram("PROGRAM")
            self.program.initialize_program()

        self.setLayout(self.layout)
        self.hookupWidgets()

    def hookupWidgets(self):
        self.name_l = QLabel("Program Name")
        self.duration_l = QLabel("Program Duration")
        self.durationW = QSpinBox()
        self.nameW = QLineEdit()
        self.nameW.setText(self.program.name)
        self.durationW.setValue(self.program.duration)
        self.nameW.textChanged.connect(self.name_callback)
        self.durationW.valueChanged.connect(self.duration_callback)
        self.program_table = TableView(
            ["Day", "Workout Path"],
            self.program.sched,
            self.contextMenuEventWorkoutTable,
        )
        self.program_table.itemDoubleClicked.connect(self.update_days_workout)
        self.save_button = QPushButton("Save Program")
        self.save_button.clicked.connect(self.save_program)
        self.layout.addWidget(self.durationW)
        self.layout.addWidget(self.nameW)
        self.layout.addWidget(self.program_table)
        self.layout.addWidget(self.save_button)

    def duration_callback(self, val):
        if val > len(self.program.sched):
            for i in range(self.program.duration, val):
                self.program.sched.append(ProgramDay(i, "rest"))
        else:
            while (
                val < len(self.program.sched)
                and self.program.sched[-1].workout_path.lower() == "rest"
            ):
                self.program.sched.pop(-1)

        self.program.duration = len(self.program.sched)
        self.program_table.update_data(self.program.sched)

    def name_callback(self, text):
        self.program.name = text

    def contextMenuEventWorkoutTable(self, event):
        menu = QMenu()
        deleteAction = menu.addAction("Remove Workout")
        setWorkoutAction = menu.addAction("Set Workout")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == deleteAction:
            i = self.program_table.indexAt(event.pos())
            self.program.sched[i.row()].workout_path = "REST"
            self.program_table.update_data(self.program.sched)
            self.program_table.update()

    def update_days_workout(self, item):
        p = ProgramDayForm(self)
        p.exec()
        self.program.sched[item.row()].workout_path = p.selected
        self.program_table.update_data(self.program.sched)

    def save_program(self):
        for i, d in enumerate(self.program_table.data):
            d.day = i
        self.program.sched = self.program_table.data
        self.program.upsert_program()


class ProgramManager(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.db = Db()

        self.splitter  = QSplitter(QtCore.Qt.Horizontal)
        self.splitter.setSizes([50,200])


        self.add_button = QPushButton("Create Workout Program")
        self.program_list = QListWidget()
        self.program_list.clicked.connect(self.handle_program_select)
        self.get_program_list()
        self.current_program = None
        self.current_program_edit = ProgramEditor(self.current_program, parent=self)
        self.layout = QVBoxLayout()
        
        self.program_list.installEventFilter(self)

        self.splitter.addWidget(self.program_list)
        self.splitter.addWidget(self.current_program_edit)
        self.splitter.setSizes([100,200])

        self.layout.addWidget(self.splitter)


        self.setLayout(self.layout)

    def get_program_list(self):
        self.programs = self.db.make_list(FitnessProgram("").getPrograms())
        R = [l[0] for l in self.programs]
        self.program_list.clear()
        [self.program_list.insertItem(0, item) for item in np.unique(R)]

    def handle_program_select(self):
        program_name = self.program_list.currentItem().text()
        self.get_program_list()
        p = list(filter(lambda x: x[0] == program_name, self.programs))

        self.load_program(p)

    def load_program(self, program: []):
        self.current_program = FitnessProgram(program[0][0])
        self.current_program.duration = len(program)
        self.current_program.sched = [ProgramDay(x[1], x[2]) for x in program]
        p = ProgramEditor(self.current_program, parent=self)
        self.current_program_edit = p
        self.splitter.replaceWidget(1,self.current_program_edit)
        return

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.ContextMenu and source is self.program_list):
            menu = QMenu()
            addAction = menu.addAction("add program")
            action = menu.exec_(self.mapToGlobal(event.pos()))
            if action == addAction:
                self.current_program = FitnessProgram("PROGRAM")
                self.current_program.initialize_program()
                p = ProgramEditor(self.current_program, parent=self)
                
                self.current_program_edit = p
                self.splitter.replaceWidget(1,self.current_program_edit)
            return True

        return super(QWidget, self).eventFilter(source, event)

class WorkoutPlayer(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.db = Db()
    
    def timer_element(self)



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = WorkoutManager()
    window.show()
    sys.exit(app.exec_())
