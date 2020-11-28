CREATE TABLE programs(
    name TEXT,
    daysNum INTEGER,
    workoutPath TEXT
)

####################################

CREATE TABLE workouts
(
    name Text,
    workout_text TEXT
)
####################################

CREATE UNIQUE INDEX idx_programKey 
ON programs (name, daysNum);

####################################
CREATE TABLE RoutineTasks(
Name TEXT,
TOD TEXT,
FREQUENCY TEXT,
FCOUNT INTEGER

)

####################################
CREATE TABLE UserInfo(
    username TEXT,
    password TEXT
)

####################################
CREATE TABLE Exercises(
    name TEXT,
    bodypart TEXT
)