import sqlite3
import datetime 
import time
conn = sqlite3.connect('./DailyData/SoccerData.db')
c = conn.cursor()

# check if the database is empty or not
c.execute("""SELECT count(*) FROM BudgetTrack""")
lenBudgetTrack = c.fetchall()
if lenBudgetTrack[0][0] == 0:

        # populate the budget track table with
    now = datetime.datetime.now()
    today = str(now.replace(hour=0, minute=0, second=0, microsecond=0))
    date_format = datetime.datetime.strptime(today,
                                            "%Y-%m-%d %H:%M:%S")
    date_sample  = time.mktime(date_format.timetuple())

    c.execute(""" 
                INSERT INTO BudgetTrack VALUES(?,?,?,?,?,?)
                """,(today,date_sample,100,0,0,100))

    conn.commit()

now = datetime.datetime.now()
today = str(now.replace(hour=0, minute=0, second=0, microsecond=0))
date_format = datetime.datetime.strptime("2022-06-28 00:00:00",
                                            "%Y-%m-%d %H:%M:%S")
date_sample  = time.mktime(date_format.timetuple())
print(date_format)
print(date_sample)
conn.commit()
c.close()
conn.close()