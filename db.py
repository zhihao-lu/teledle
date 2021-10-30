import sqlite3
import datetime

class Database:
    '''
    Initializing database.db file and connecting to the file
    '''
    def __init__(self):
        self.con = sqlite3.connect(
            'database.db', check_same_thread=False)
        self.cur = self.con.cursor()

    '''
    Initializing commit function
    '''
    def commit(self):
      self.con.commit()

    '''
    Initializing tables which only needs to be called once at the start of the program
    '''
    def create_tables(self):
        try:
            self.cur.execute(
                'CREATE TABLE IF NOT EXISTS log(name text, exercise text, count integer, date text, week integer)')

            self.con.commit()
            return True
        except Exception as e:
            print(e)
            return e

    def insert_entry(self, name, exercise, count, d, date_format=""):
        # d = datetime.strptime(d, date_format)
        # week = datetime.date(d).isocalendar().week
        try:

            self.cur.execute("INSERT INTO log(name, exercise, count, date, week) VALUES(?,?,?,?,?)",
                             (name, exercise, count, d, 1))
            self.con.commit()
            return True
        except Exception as e:
            print(e)
            return e
    
    def get_all(self):
      self.cur.execute("SELECT * FROM log LIMIT 1")
      a = self.cur.fetchall()
      return a