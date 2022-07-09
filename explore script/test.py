import sqlite3
import pandas as pd
conn = sqlite3.connect('../DailyData/SoccerData.db')
c = conn.cursor()

c.execute(""" select  PlaceBetTable.currentDate,PlaceBetTable.betToResult ,modelData.KellyCriterion, PlaceBetTable.betOdd,PlaceBetTable.fixtureId from PlaceBetTable 
    join modelData on PlaceBetTable.fixtureId = modelData.fixtureId
    where modelData.KellyCriterion > 0

""")
listData = c.fetchall()
currentDate = []
betToResult = []
KellyCriterion = []
betOdd = []

for tup in listData:
    currentDate.append(tup[0])
    betToResult.append(tup[1])
    KellyCriterion.append(tup[2])
    betOdd.append(tup[3])

df = pd.DataFrame(columns=["currentDate","betToResult","KellyCriterion"])
df["currentDate"] = currentDate
df["betToResult"] = betToResult
df["KellyCriterion"] = KellyCriterion
df["betOdd"] = betOdd

df.dropna(inplace=True)


# df["betToResult"].astype("int32")
df["betToResult"] = df["betToResult"].astype(str).astype(int)

def addGain(row):
    if row["betToResult"] == 0:
        row["gain"] = -row["KellyCriterion"]
    else:
        row["gain"] = row["KellyCriterion"]*(row["betOdd"]-1)
    return row

df = df.apply(addGain, axis = 1)
print(df)
print(sum(df["gain"]))
c.close()
conn.close()


# import datetime
# import time

# today = datetime.datetime.now()
# date = today.replace(hour=0, minute=0, second=0, microsecond=0)
# date = time.mktime(date.timetuple())
# print(date)
