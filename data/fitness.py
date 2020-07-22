
from dataclasses import dataclass, field
from typing import List
from nltk.corpus import words
import json
from random import sample
from database.db import Database

class Movement:
    def __init__(self, m:dict= None):
        super().__init__()
        self.name:str 
        self.load: int
        self.reps: int
        self.sets: int 
        self.timed: bool
        if m != None:
            self.name =  m["name"]
            self.load =  m["load"]
            self.reps =  m["reps"]
            #not sure wtf is happening but the __dict__ keeps coming back strangely
            try:
                self.sets =  m["sets"]
            except KeyError:
                self.sets =  m["set"]
            self.timed = m["timed"]

class Section:
    def __init__(self, s:dict=None):
        super().__init__()
        self.order: int = -1
        self.reps: int = 12
        self.movements: List[Movement] = []
        if s != None:
            self.load_data(s)

    def add_movement(self):
        self.movements.append(Movement())
    
    def dump_data(self):
        s = {}
        s["order"] =  self.order
        s["reps"] = self.reps
        s["movements"] = []
        for m in self.movements:
             s["movements"].append(vars(m))
        return s

    def load_data(self, s):
        self.order = s["order"]
        self.reps = s["reps"]
        for m in s["movements"]:
            self.movements.append(Movement(m))

class Workout:
    db = Database()
    def __init__(self, w:dict= None):
        super().__init__()
        self.name: str = '_'.join(sample(words.words(),3))
        self.sections: List[Section] = []
        if type(w) == str:
            self.get_workout(w)
        elif w != None:
            self.load_data(w)


    @classmethod
    def get_workout_list(self):
        c = self.db.conn.cursor()
        c.execute("SELECT name from workouts")
        return self.db.make_list(c.fetchall())

    def add_section(self):
        s = Section()
        s.order = len(self.sections)
        self.sections.append(s)

    def dump_data(self):
        dump = {}
        dump["name"] = self.name
        dump["sections"] = []
        for s in self.sections:
            d = s.dump_data()
            dump["sections"].append(d)
        return dump
        
    def load_data(self, dump: dict):
        self.name = dump["name"]
        for s in dump["sections"]:
            sec = Section(s)
            self.sections.append(sec)

    def save_to_db(self):
        d = json.dumps(self.dump_data())
        c = self.db.conn.cursor()
        c.execute(f"DELETE FROM workouts where name = \'{self.name}\'")
        c.execute(f"INSERT INTO workouts VALUES(?, ?);",[self.name, d])
        self.db.conn.commit()


    def get_workout(self, name):
        c = self.db.conn.cursor()
        c.execute(f"SELECT workout_text from workouts where name = \'{name}\'")
        res = json.loads(c.fetchone()[0])
        self = self.load_data(res)
        return 
    
    def delete(self, name=None):
        c = self.db.conn.cursor()
        if name == None:
            c.execute(f"DELETE from  workouts where name = \'{self.name}\'")
        else:
            c.execute(f"DELETE from  workouts where name = \'{name}\'")
        self.db.conn.commit()
        del self

class ProgramDay:
    def __init__(self, day, w_path):
        super().__init__()
        self.day: int = day
        self.workout_path: str = w_path

class FitnessProgram:
    def __init__(self, name):
        super().__init__()
        self.name:str = name
        self.duration:int = 28
        self.sched: List[ProgramDay] = []
        self.db = Database()

    def initialize_program(self):
        for i in range(self.duration):
            pd = ProgramDay(i, "Rest")
            self.sched.append(pd)

    def dump_program(self):
        d = {}
        d["name"] = self.name
        d["sched"] = []
        for w in self.sched:
            d["sched"].append([w.day, w.workout_path])
        return d

    def get_sched(self):
        return [w.__dict__ for w in self.sched]

    def getPrograms(self, name:str=None):
        c = self.db.conn.cursor()
        if name != None:
            c.execute(f"SELECT * FROM programs WHERE name == {name}")
        else:
            c.execute(f"SELECT * FROM programs")
        return c.fetchall()

    def upsert_program(self):
        if len(self.sched) == self.duration:
            c = self.db.conn.cursor()
            c.execute(f"DELETE FROM programs where name = \'{self.name}\'")
            for w in self.sched:
                c.execute(f"INSERT INTO programs (name, daysNum, workoutPath) VALUES (\'{self.name}\',\'{w.day}\',\'{w.workout_path}\');")
            self.db.conn.commit()
        else:
            return -1

    def delete_program(self):
        c = self.db.conn.cursor()
        c.execute(f"DELETE FROM programs where name = \'{self.name}\'")
        self.db.conn.commit()

    