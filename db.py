import sqlite3
import datetime
from math import prod

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
                'CREATE TABLE IF NOT EXISTS log('
                'name text, '
                'exercise text, '
                'count integer, '
                'date text, '
                'week integer, '
                'tele text)')

            self.con.commit()
            return True
        except Exception as e:
            print(e)
            return e

    def insert_entry(self, name, tele, exercise, count):
        d = datetime.datetime.now()
        w = d.isocalendar().week
        try:

            self.cur.execute("INSERT INTO log(name, exercise, count, date, week, tele) VALUES(?,?,?,?,?,?)",
                             (name, exercise, count, d, w, tele))
            self.con.commit()
            return True
        except Exception as e:
            print(e)
            return e
    
    def get_all(self):
        self.cur.execute("SELECT * FROM log ORDER BY ROWID DESC LIMIT 1")
        a = self.cur.fetchall()
        return a

    def get_leaderboards(self):
        def calculate_position(entries):
            all_cats = sorted(list(set([entry[1] for entry in entries])))
            all_participants = set([entry[0] for entry in entries])
            output_dict = dict([(name, {"ranking": 1}) for name in all_participants])
            output_list = []

            for cat in all_cats:
                leaders = sorted(filter(lambda x: x[1] == cat, entries), key=lambda x: x[2], reverse=True) #name, cat, count
                for idx, leader in enumerate(leaders):
                    output_dict[leader[0]][cat] = leader[2]
                    output_dict[leader[0]]["ranking"] *= idx + 1

            for participant in all_participants:
                lst = [participant]
                lst.extend([output_dict[participant][cat] for cat in all_cats])
                lst.append(output_dict[participant]["ranking"])
                output_list.append(lst)

            output_list = sorted(output_list, key=lambda x: x[-1])

            return all_cats, output_list

        cweek = datetime.datetime.now().isocalendar().week

        self.cur.execute("SELECT name, exercise, SUM(count) FROM log GROUP BY name, exercise")
        all_time = self.cur.fetchall()
        self.cur.execute("SELECT name, exercise, SUM(count) FROM log WHERE week = ? GROUP BY name, exercise", (cweek,))
        current_week = self.cur.fetchall()

        all_time_order, all_time_results = calculate_position(all_time)
        week_order, week_results = calculate_position(current_week)
        return week_order, week_results, all_time_order, all_time_results

    def drop_table(self, table):
        self.cur.execute("DROP TABLE log")
        self.con.commit()