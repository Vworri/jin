import sqlite3
import json
import pandas as pd


class Database:
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('example.db')

    def create(self):
        c = self.conn.cursor()
        with open("/home/v/Projects/Tether/database/scripts/settings.sql", "r") as f:
            commands = f.read().split("####################################")
            for command in commands:
                try:
                    c.execute(command)
                except (sqlite3.OperationalError):
                    print(command[:25])

    def fill_defaults(self):
        c = self.conn.cursor()
        with open("/home/v/Projects/Tether/config.json") as f:
            defaults = json.load(f)
            usename = defaults["userInfo"]["username"]
            c.execute(f"INSERT INTO UserInfo VALUES (\'{usename}\', '')")
            for entry in defaults["workout_schedule"]:
                days = defaults["workout_schedule"][entry]
                c.execute(f"INSERT INTO workout_schedule VALUES(\'{entry}\', \'{days}\')")
            for entry in defaults["routines"]:
                action = defaults["routines"][entry]
                unit = action["unit"]
                length = action["length"]
                c.execute(f"INSERT INTO routines VALUES(\'{entry}\',\'{unit}\', {length})")
            for entry in defaults["dailys"]:
                action = defaults["dailys"][entry]
                c.execute(f"INSERT INTO dailys VALUES(\'{entry}\',\"{action}\")")
        ex_df = pd.read_csv("/home/v/Projects/Tether/data/exercises.csv",  skipinitialspace=True)

        ex_df.to_sql("Exercises", con=self.conn, if_exists='append', index=False)
        self.conn.commit()

    def get_daily_checklist(self, tod):
        c = self.conn.cursor()
        c.execute(f"SELECT todo FROM dailys WHERE time_of_day == {tod}")
        return c.fetchone()
    
    def getExercises(self):
        df = pd.read_sql_query('SELECT * FROM exercises', self.conn)
        return df

    def make_list(self, res):
        r = []
        [r.append(list(e)) for e in res]
        return r

    

if __name__ == '__main__':
    d = Database()
    d.create
    d.fill_defaults()
    d.getExercises()
            
