import sqlite3
import pandas as pd
import pickle
import numpy as np

conn = sqlite3.connect('./DailyData/SoccerData.db')
c = conn.cursor()


def getUnpredictedMatch(c):

    c.execute('SELECT SoccerMatch.fixtureId,SoccerMatch.homeOdd,SoccerMatch.drawOdd,SoccerMatch.awayOdd FROM modelData join SoccerMatch on modelData.fixtureId=SoccerMatch.fixtureId where modelData.modelBet is NULL ;')
    listData = c.fetchall()

    fixtureIdList = []
    homeOddList = []
    drawOddList = []
    awayOddList = []
    for tup in listData:
        fixtureIdList.append(tup[0])
        homeOddList.append(tup[1])
        drawOddList.append(tup[2])
        awayOddList.append(tup[3])

    df = pd.DataFrame(columns=["fixtureId","B365H","B365D","B365A"])
    df["fixtureId"] = fixtureIdList
    df["B365H"] = homeOddList
    df["B365D"] = drawOddList
    df["B365A"] = awayOddList

    return df

def softmax(vector):
    e = np.exp(vector)
    return e / e.sum()

def AddKellyCriterion(row):
    bet = row["bet"]
    if bet == "H":
        odd = row["B365H"]
    elif bet == "D": 
        odd = row["B365D"] 
    else: 
        odd = row["B365A"]
        
    B = odd - 1
    P = row["modelProba"]
    Q = 1- P
    row["KellyCriterion"] = (B*P - Q)/B
    return row

def addModelData(df,model):
    
    predictProba =[]
    Proba = []
    for el in clf.predict_proba(df[["B365H","B365D","B365A"]]):
        choose = max(el)
        indexChoice = list(el).index(choose)

        if indexChoice == 0:
            predictProba.append("A")
        if indexChoice == 1:
            predictProba.append("D")
        if indexChoice == 2:
            predictProba.append("H")
        
        Proba.append(choose)

    df["bet"] = predictProba
    df["modelProba"] = Proba

    df = df.apply(AddKellyCriterion,axis =1)

    # only get KellyCriterion > 0
    df = df[df["KellyCriterion"] > 0]

    # df["betDatePortion"]= softmax(df["KellyCriterion"])
    
    return df

filename = 'finalized_model.sav'
clf = pickle.load(open(filename, 'rb'))


df = getUnpredictedMatch(c)
print(addModelData(df,clf))


c.close()
conn.close()
