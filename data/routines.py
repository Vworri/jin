from enum import Enum
from database.db  import Database as Db

class Frequency(Enum):
    DAILY: 0
    WEEKLY: 1
    MONTHLY: 2
    YEARLY: 4

class TimeOfDay(Enum):
    MORNING: 0
    EVENING: 1
    AFTERNOON: 2
    ANYTIME: 4


class Routine:
    def __init__(self):
        super().__init__()
        name: str 
        frequency: Frequency
        tod: TimeOfDay
        fcount: int = 1
        self.db = Db()

    def add_routine(self):
        c = self.db.conn.cursor()
        c.execute(f"DELETE FROM RoutineTasks where name = \'{self.name}\'")
        for w in self.sched:
            c.execute(f"INSERT INTO RoutineTasks (name, daysNum, workoutPath) VALUES (\'{self.name}\',\'{w.day}\',\'{w.workout_path}\');")
        self.db.conn.commit()





