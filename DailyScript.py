import sqlite3
import datetime 
import time
import pandas as pd

import GetDailyMacth
import GetModelPrediction
import GetDailyResult


conn = sqlite3.connect('./DailyData/SoccerData.db')
c = conn.cursor()

GetDailyMacth.getDailyMatch(c,conn)
try:
    GetModelPrediction.GetModelPrediction(c,conn)
except:
    print("all macth predicted")

GetDailyResult.GetDailyResult(c,conn)

conn.commit()
c.close()
conn.close()