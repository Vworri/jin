CREATE TABLE programs(
    name TEXT,
    daysNum INTEGER,
    workoutPath TEXT
)
####################################

CREATE UNIQUE INDEX idx_programKey 
ON programs (name, daysNum);

####################################
CREATE TABLE Dailys(
 time_of_day TEXT,
 todo TEXT[]
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