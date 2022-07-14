import sqlite3
import pandas as pd
conn = sqlite3.connect('../DailyData/SoccerData.db')
c = conn.cursor()

c.execute(""" select  SoccerMatch.commence_time ,SoccerMatch.commence_timestamp ,modelData.modelBet, Result.FTR , modelData.KellyCriterion , SoccerMatch.homeOdd,SoccerMatch.drawOdd, SoccerMatch.awayOdd from SoccerMatch 
    join modelData on SoccerMatch.fixtureId = modelData.fixtureId
    join Result on Result.fixtureId = SoccerMatch.fixtureId
    where modelData.KellyCriterion > 0.3

""")
listData = c.fetchall()
commence_time = []
commence_timestamp = []
modelBet = []
FTR = []
KellyCriterion = []
home = []
draw = []
away = []
for tup in listData:
    commence_time.append(tup[0])
    commence_timestamp.append(tup[1])
    modelBet.append(tup[2])
    FTR.append(tup[3])
    KellyCriterion.append(tup[4])
    home.append(tup[5])
    draw.append(tup[6])
    away.append(tup[7])

betOdd = []



df = pd.DataFrame(columns=["commence_time","commence_timestamp","modelBet", "FTR","KellyCriterion","home","draw","away"])
df["commence_time"] = commence_time
df["commence_timestamp"] = commence_timestamp
df["modelBet"] = modelBet
df["FTR"] = FTR
df["KellyCriterion"] = KellyCriterion
df["home"] = home
df["draw"] = draw
df["away"] = away

def addbetOdd(row):
    if row["modelBet"] == "H":
        row["betOdd"] = row["home"]
    elif row["modelBet"] == "D":
        row["betOdd"] = row["draw"]
    else:
        row["betOdd"] = row["away"]
    return row

df = df.apply(addbetOdd,axis =1 )

df["betToResult"] = df["modelBet"] == df["FTR"]  
df.dropna(inplace=True)


# df["betToResult"].astype("int32")
# print(df)
# df["betToResult"] = df["betToResult"].astype(str).astype(int)

def addGain(row):
    if row["betToResult"] == False:
        row["gain"] = -row["KellyCriterion"]
    else:
        row["gain"] = row["KellyCriterion"]*(row["betOdd"]-1)
    return row

df = df.apply(addGain, axis = 1)
print(df)
print(sum(df["gain"]))
# print(df["betToResult"].value_counts())
c.close()
conn.close()


# import datetime
# import time

# today = datetime.datetime.now()
# date = today.replace(hour=0, minute=0, second=0, microsecond=0)
# date = time.mktime(date.timetuple())
# print(date)
