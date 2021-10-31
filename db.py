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

    def commit(self):
        self.con.commit()

    def execute_query(self, query):
        self.cur.execute(query)
        result = self.cur.fetchall()
        return result

    def set_query(self, query):
        self.cur.execute(query)
        self.con.commit()

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

    def insert_entry(self, name, tele, exercise, count, exercises=("Core", "Pull Ups", "Run")):
        d = datetime.datetime.now()
        w = d.isocalendar()[1]
        self.cur.execute("SELECT DISTINCT tele from log WHERE week = ?", (w,))
        names = self.cur.fetchall()

        try:
            if tele not in names:
                for e in exercises:
                    if exercise != e:
                        self.cur.execute("INSERT INTO log(name, exercise, count, date, week, tele) VALUES(?,?,?,?,?,?)",
                                         (name, e, 0, d, w, tele))
            if count != 0:
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

        def calculate_position(series):
            participants = set([entry[0] for entry in series])
            exercises = sorted(list(set([entry[1] for entry in series])))
            output_list = []

            for participant in participants:
                lst = sorted(filter(lambda x: x[0] == participant, series), key=lambda x: x[1])
                out = [participant]
                ranking = prod([x[3] for x in lst])
                for entry in lst:
                    out.append(str(round(entry[2], 1)))
                out.append(ranking)
                output_list.append(out)

            output_list = sorted(output_list, key=lambda x: x[-1])
            s = "(" + ", ".join(exercises) + ") \n"

            for idx, entry in enumerate(output_list):
                s += str(idx + 1) + ". " + entry[0] + " "
                s += "(" + ", ".join(entry[1:-1]) + ") \n"

            return s

        cweek = datetime.datetime.now().isocalendar()[1]

        all_time_query = "SELECT a.name, a.exercise, a.count, RANK() OVER(PARTITION BY exercise ORDER BY count DESC) " \
                         "rank FROM (SELECT name, exercise, SUM(count) count FROM log GROUP BY name, exercise) a "

        week_query = "SELECT a.name, a.exercise, a.count, RANK() OVER(PARTITION BY exercise ORDER BY count DESC) rank "\
                     "FROM (SELECT name, exercise, SUM(count) count " \
                     "FROM log WHERE week = ? GROUP BY name, exercise " \
                     ") a"

        self.cur.execute(all_time_query)
        all_time = self.cur.fetchall()
        self.cur.execute(week_query, (cweek,))
        current_week = self.cur.fetchall()

        all_time_results = calculate_position(all_time)
        week_results = calculate_position(current_week)
        return week_results, all_time_results

    def drop_table(self, table):
        self.cur.execute("DELETE FROM log")
        self.con.commit()

    def get_history(self):
        cweek = datetime.datetime.now().isocalendar()[1]
        all_time_query = "SELECT exercise, SUM(count) FROM log GROUP BY exercise"
        week_query = "SELECT exercise, SUM(count)  FROM log WHERE week = ? GROUP BY exercise"

        self.cur.execute(all_time_query)
        all_time = self.cur.fetchall()
        self.cur.execute(week_query, (cweek,))
        current_week = self.cur.fetchall()

        s = "This week:\n"

        for ex, count in current_week:
            s += ex + ": " + str(count) + "\n"

        s += "\n \n"
        s += "All time: \n"
        for ex, count in all_time:
            s += ex + ": " + str(count) + "\n"
        return s

    def get_user_history(self, tele, offset=0, limit=5):
        query = "SELECT rowid, exercise, count, date FROM log WHERE tele = ? and count != 0 ORDER BY date DESC LIMIT 5 OFFSET ?"
        self.cur.execute(query, (tele, offset))
        results = self.cur.fetchall()

        return results
        '''
        results = [(str(entry[0]) + ".", entry[1], entry[2]) for entry in results]
        results = [" ".join([str(x) for x in entry]) for entry in results]

        s = f"Entries {0 + offset} to {offset + 10}: \n \n"

        r = "\n".join(results)

        return s + r
        '''

    def delete_entry(self, rowid):
        self.cur.execute("DELETE FROM log WHERE rowid = ?", (rowid,))
        self.con.commit()
