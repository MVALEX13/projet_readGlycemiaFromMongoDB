import sqlite3
from datetime import datetime,date,time

class DataBase_class:

    database_name = 'glycemia.db'
    database_days_list = list()                         # list of all the days of the database for which we have data
    most_recent_datetime = datetime(1970, 1,1)          # default date




    def __init__(self):
        self.FillDatabaseDaysList()
        self.GetMostRecentDateTime()




    def CreateDataBase(self):

        # connection with a db
        conn = sqlite3.connect( self.database_name )

        # instanciation of a tool for SQL statement
        cur = conn.cursor()

        # construction of tables
        cur.execute('DROP TABLE IF EXISTS days')
        cur.execute('''CREATE TABLE days(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            day DATE
        )
        ''')
        cur.execute('DROP TABLE IF EXISTS glycemia')
        cur.execute('''CREATE TABLE glycemia(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            time TIME,
            glycemia INTEGER,
            day_id INTEGER NOT NULL,
            FOREIGN KEY (day_id) REFERENCES days(id)
        )
        ''')

        # close the existing connection
        conn.close()





    ### 
    #  The 2 methods below update the attributs value 'database_days_list' et 'most_recent_datetime' reepectively
    #  by reading the SQlite db
    ###
    def FillDatabaseDaysList(self):

        ## connection with the db
        conn = sqlite3.connect(self.database_name)

        ## retrieve all the data from the days table
        cur = conn.cursor()
        res = cur.execute('SELECT day FROM days')
        days_list = res.fetchall()                     # retrieve all the data from the precedent SQL statement
        
        self.database_days_list = [elmt[0] for elmt in days_list]

    def GetMostRecentDateTime(self):
        ## connection with the db
        conn = sqlite3.connect(self.database_name)

        ## retrieve all the data from the days table
        cur = conn.cursor()

        res = cur.execute('SELECT time FROM glycemia ORDER BY id DESC LIMIT 1')
        last_time_str = res.fetchone()[0]     
        last_time = time.fromisoformat(last_time_str)      

        res = cur.execute('SELECT day_id FROM glycemia ORDER BY id DESC LIMIT 1')
        last_day_id = res.fetchone()[0]

        res = cur.execute('SELECT day FROM days WHERE id = ?',(last_day_id,))
        last_day_str = res.fetchone()[0]
        last_day = date.fromisoformat(last_day_str)

        self.most_recent_datetime = datetime.combine(last_day,last_time)
        




    ###
    #   This method insert a list of days in the SQLite days table
    ###
    def InsertDaysinDaysTable(self, days2insert_list):

        # connection with the db
        conn = sqlite3.connect(self.database_name)

        # instanciation of a tool for SQL statement
        cur = conn.cursor()

        for day in days2insert_list:
            cur.execute('INSERT INTO days (day) VALUES (?);', (day,))
    
        conn.commit()
        conn.close()








    ###
    #   Update the SQlite "days" table 
    ###
    def UpdateDaysTable(self, glycemia_dict):

        ## fill days_list with the new days for which we have records
        new_days_list = list()
        for key in glycemia_dict:

            # retrieve the date from key datatime object then convert it in str format
            day = key.date()
            day_str = day.isoformat()

            if (day_str not in new_days_list) and (day_str not in self.database_days_list):
                new_days_list.append(day_str)
        

        ## actualisation of the database_days_list
        for day in new_days_list:
            self.database_days_list.append(day)


        ## filling days SQL table
        self.InsertDaysinDaysTable(new_days_list)



    ###
    #   Update the SQlite "glycemia" table 
    ###
    def UpdateGlycemiaTable(self, glycemia_dict):

        # connection with the db
        conn = sqlite3.connect(self.database_name)

        # instanciation of a tool for SQL statement
        cur = conn.cursor()

        for key in glycemia_dict:
            
            # key is a datatime object. We insert only new data in the SQL table
            if key > self.most_recent_datetime:
                # retrieve the date from key datatime object then convert it in str format
                day = key.date()
                day_str = day.isoformat()

                # retrieve the time from key datatime object then convert it in str format
                time = key.time()
                time_str = time.isoformat(timespec='minutes')

                # retrieve the glycemia
                glycemia = glycemia_dict.get(key)

                res = cur.execute( 'SELECT id FROM days WHERE day = ?;', (day_str,) )
                day_id = res.fetchone()[0]

                cur.execute('INSERT INTO glycemia (day_id,time,glycemia) VALUES (?,?,?);', (day_id, time_str, glycemia) )
                conn.commit()
        
        conn.close()




    def GetDayRecords(self, day_date):

        glycemia_dict = dict()

        # connection with the db
        conn = sqlite3.connect(self.database_name)

        # instanciation of a tool for SQL statement
        cur = conn.cursor()

        day_str = day_date.isoformat()

        res = cur.execute( 'SELECT id FROM days WHERE day = ?;', (day_str,) )
        day_id = res.fetchone()[0]

        res = cur.execute('SELECT * FROM glycemia WHERE day_id = ?;',(day_id,)).fetchall()
        for row in res:
            hour_time = time.fromisoformat(row[1])
            t = datetime.combine(day_date,hour_time)
            glycemia_dict[t] = row[2]
        
        return glycemia_dict








        
        