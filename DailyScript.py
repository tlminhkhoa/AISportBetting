import sqlite3
import datetime 
import time
import pandas as pd

import GetDailyMacth
import GetModelPrediction
import GetDailyBet
import GetDailyResult
import CheckBetResult

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

GetDailyMacth.getDailyMatch(c,conn)
try:
    GetModelPrediction.GetModelPrediction(c,conn)
except:
    print("all macth predicted")
GetDailyBet.GetDailyBet(c,conn)
GetDailyResult.GetDailyResult(c,conn)
CheckBetResult.CheckBetResult(c,conn)
conn.commit()
c.close()
conn.close()