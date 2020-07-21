import sys
import json
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget, QListView, QLineEdit, QVBoxLayout, QHBoxLayout
from PyQt5 import QtCore, QtWidgets, uic
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from os import path
from database.db import Database


class TodoModel(QtCore.QAbstractListModel):
    def __init__(self, *args, todos=None, **kwargs):
        super(TodoModel, self).__init__(*args, **kwargs)
        self.todos = todos or []
        self.tick = QImage('/home/v/Projects/Tether/UI/icons/icons8-tick-box-64.png')
        self.untick = QImage('/home/v/Projects/Tether/UI/icons/icons8-unchecked-checkbox-64.png')

    def data(self, index, role):
        if role == Qt.DisplayRole:
            _, text = self.todos[index.row()]
            return text

        if role == Qt.DecorationRole:
            status, _ = self.todos[index.row()]
            if status:
                return self.tick
            else:
                return self.untick

    def rowCount(self, index):
        return len(self.todos)


class TodoList(QWidget):
    def __init__(self):
        super(TodoList, self).__init__()

        self.todoView = QListView()
        self.todoEdit = QLineEdit('Task')
        self.addButton = QPushButton('Add')
        self.deleteButton = QPushButton('Delete')
        self.completeButton = QPushButton('Mark Complete')
        self.vbox = QVBoxLayout()
        self.hbox = QHBoxLayout()
        self.vbox.addWidget(self.todoView)
        self.vbox.addWidget(self.todoEdit )
        self.hbox.addWidget(self.addButton )
        self.hbox.addWidget(self.deleteButton)
        self.hbox.addWidget(self.deleteButton)
        self.hbox.addWidget(self.completeButton)
        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)
        self.tick = QImage('check.png')
        self.db_file = "data/" +time.strftime("%Y%m%d") + '.db'
        # set up daily checklist
        todos = self.auto_init()
        self.model = TodoModel(todos=todos)
        self.load()
        self.todoView.setModel(self.model)
        self.addButton.pressed.connect(self.add)
        self.deleteButton.pressed.connect(self.delete)
        self.completeButton.pressed.connect(self.complete)


    def auto_init(self):
        if path.exists(time.strftime("%Y%m%d") +'.db'):
            return []
        db = Database();
        cur = db.conn.cursor()
        todoList = []
        for todos in cur.execute(f"SELECT todo FROM dailys"):
            [todoList.append((False,todo)) for todo in todos[0].replace("[", "").replace("]", ",").replace("\'", "").split(",") if todo != ""] 
        return todoList


    def add(self):
        """
        Add an item to our todo list, getting the text from the QLineEdit .todoEdit
        and then clearing it.
        """
        text = self.todoEdit.text()
        if text: # Don't add empty strings.
            # Access the list via the model.
            self.model.todos.append((False, text))
            # Trigger refresh.        
            self.model.layoutChanged.emit()
            # Empty the input
            self.todoEdit.setText("")
            self.save()

    def delete(self):
        indexes = self.todoView.selectedIndexes()
        if indexes:
            # Indexes is a list of a single item in single-select mode.
            index = indexes[0]
            # Remove the item and refresh.
            del self.model.todos[index.row()]
            self.model.layoutChanged.emit()
            # Clear the selection (as it is no longer valid).
            self.todoView.clearSelection()
            self.save()

    def complete(self):
        indexes = self.todoView.selectedIndexes()
        if indexes:
            index = indexes[0]
            row = index.row()
            status, text = self.model.todos[row]
            self.model.todos[row] = (True, text)
            # .dataChanged takes top-left and bottom right, which are equal 
            # for a single selection.
            self.model.dataChanged.emit(index, index)
            # Clear the selection (as it is no longer valid).
            # self.todoView.clearSelection()
            self.save()

    def load(self):
        try:
            with open(f'{self.db_file}', 'r') as f:
                self.model.todos = json.load(f)
        except Exception:
            pass

    def save(self):
        with open(f'{self.db_file}', 'w') as f:
            data = json.dump(self.model.todos, f)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TodoList()
    window.show()
    sys.exit(app.exec_())