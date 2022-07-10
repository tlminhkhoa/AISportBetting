from cmath import e
import sqlite3
import pandas as pd
import time
import dateutil.parser
import datetime
import numpy as np

conn = sqlite3.connect('./DailyData/SoccerData.db')
c = conn.cursor()


def getKellyPositiveMatch(c):

    # get the lastest budget timestamp to find the last time we place bet
    c.execute("""
    SELECT max(currentDate_timestamp) from BudgetTrack;
    """)
    listData = c.fetchall()
    currentDate_timestamp = listData[0][0]
    print(currentDate_timestamp)
    today = datetime.datetime.now()
    date = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_timestamp = time.mktime(date.timetuple())
    # print(date_timestamp)
    c.execute(""" SELECT SoccerMatch.fixtureId, SoccerMatch.homeOdd, SoccerMatch.drawOdd, SoccerMatch.awayOdd ,SoccerMatch.commence_time , modelData.modelBet,modelData.KellyCriterion from SoccerMatch
    join modelData on modelData.fixtureId  = SoccerMatch.fixtureId
     where SoccerMatch.commence_timestamp > ? and modelData.KellyCriterion > 0.3 and SoccerMatch.commence_timestamp < ?;""", (currentDate_timestamp,today_timestamp,))
    
    listData = c.fetchall()
    print(listData)
    # print(currentDate_timestamp)
    fixtureIdList = []
    homeOddList = []
    drawOddList = []
    awayOddList = []
    commence_timeList = []
    modelBetList = []
    KellyCriterionList = []
    for tup in listData:
        fixtureIdList.append(tup[0])
        homeOddList.append(tup[1])
        drawOddList.append(tup[2])
        awayOddList.append(tup[3])
        commence_timeList.append(tup[4])
        modelBetList.append(tup[5])
        KellyCriterionList.append(tup[6])
    
    df = pd.DataFrame(columns=["fixtureId","B365H","B365D","B365A"])
    df["fixtureId"] = fixtureIdList
    df["B365H"] = homeOddList
    df["B365D"] = drawOddList
    df["B365A"] = awayOddList
    df["commence_time"] = commence_timeList
    df["modelBet"] = modelBetList
    df["KellyCriterion"] = KellyCriterionList
    
    return df



def stripIsoTime(row):
    date = str(dateutil.parser.isoparse(row["commence_time"]).replace(tzinfo=None).replace(hour=0, minute=0, second=0, microsecond=0))
    date_format = datetime.datetime.strptime(date,"%Y-%m-%d %H:%M:%S")
    row["currentDate"] = date_format
    return row

def addBetOdd(row):
    bet = row["modelBet"]
    if bet == "H":
        row["odd"] = row["B365H"]
    elif bet == "D":
        row["odd"]  = row["B365D"]
    else:
        row["odd"]  = row["B365A"]
    return row

def softmax(vector):
    e = np.exp(vector)
    return e / e.sum()

def addBetDateProprtion(df):
    
    df["commence_time"]= pd.to_datetime(df["commence_time"])
    df = df.sort_values(by = ["commence_time"], ascending=True)
    print(df)
    softmaxList =[]
    for date in df["currentDate"].unique():        
        data = df[df["currentDate"] == date]
        # print(date)
        # print(sum(softmax(data["KellyCriterion"])))
        softmaxList +=  list(softmax(data["KellyCriterion"]))
    df["betDatePortion"] = softmaxList

    return df

def InsertTheBet(c,df):
    
    for row in df.iterrows():
        data = row[1]
        try:
            c.execute(""" 
                        INSERT INTO PlaceBetTable VALUES(?,?,?,?,?,?,?)
                        """,(data["fixtureId"],str(data["currentDate"]),None,data["odd"],data["betDatePortion"],None,None))
        except Exception as e :
            print(data)
            print(e)
        conn.commit()

def GetDailyBet(c,conn):
    df = getKellyPositiveMatch(c)
    df = df.apply(stripIsoTime,axis=1)
    df = df.apply(addBetOdd,axis=1)
    df = addBetDateProprtion(df)
    InsertTheBet(c,df)

df = getKellyPositiveMatch(c)
df = df.apply(stripIsoTime,axis=1)
df = df.apply(addBetOdd,axis=1)
df = addBetDateProprtion(df)
InsertTheBet(c,df)
c.close()
conn.close()