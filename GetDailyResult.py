from dateutil import parser
from datetime import datetime
import sqlite3
import pytz
import http.client
import json


def getMatchWithOutResult(c):
 
    c.execute('SELECT SoccerMatch.fixtureId,SoccerMatch.commence_time FROM Result join SoccerMatch on Result.fixtureId=SoccerMatch.fixtureId where Result.FTR is NULL ;')
    data = c.fetchall()

    count = 0
    idString = ""
    ListMatchUpdate = []
    for row in data:
        matchDate = parser.parse(row[1])
        now = datetime.now()
        now = pytz.utc.localize(now)
        if matchDate < now:
            idString =  str(row[0]) + "-" + idString
            count +=1
            if count == 10:
                ListMatchUpdate.append(idString[:-1])

                count = 0
                idString = ""
    ListMatchUpdate.append(idString[:-1])

    return ListMatchUpdate

def getResults(key,ListMatchUpdate):
    connHttp = http.client.HTTPSConnection("v3.football.api-sports.io")

    headers = {
            'x-rapidapi-host': "v3.football.api-sports.io",
            'x-rapidapi-key': key
            }

    returnList = []
    for matchUpdate in ListMatchUpdate:
        connHttp.request("GET", "/fixtures?ids={}".format(matchUpdate), headers=headers)
        res = connHttp.getresponse()
        if res.status != 200:
            print("Error " + matchUpdate)
        
        else:
            data = res.read()
            data = json.loads(data)
            returnList.append(data)

    connHttp.close()
    return returnList


def InsertUpdateResult(c,listData):
    for request in listData:
        responses = request["response"]

        for response in responses:
            fixtureID = response["fixture"]["id"]
            homeTeamName = response["teams"]["home"]["name"]
            awayTeamName = response["teams"]["away"]["name"]
            homeGoal = response["goals"]["home"]
            awayGoal = response["goals"]["away"]

            if awayGoal != None:
                if homeGoal > awayGoal:
                    FTR = "H"
                elif homeGoal < awayGoal:
                    FTR = "A"
                else:
                    FTR = "D"
                
                c.execute(""" 
                        UPDATE Result
                        SET home_goal = ?, away_goal= ? , FTR = ?
                        WHERE fixtureId = ?;
                        """,(homeGoal,awayGoal,FTR,fixtureID))

                c.execute(""" 
                        UPDATE Team
                        SET homeTeam = ?, awayTeam= ? 
                        WHERE fixtureId = ?;
                        """,(homeTeamName,awayTeamName,fixtureID))

def GetDailyResult(c,conn):
    ListMatchUpdate = getMatchWithOutResult(c)
    listData = getResults("337bf8dbb961deefafa31fc66c0c8806",ListMatchUpdate)
    InsertUpdateResult(c,listData)
    conn.commit() 

conn = sqlite3.connect('./DailyData/SoccerData.db')
c = conn.cursor()
key = "337bf8dbb961deefafa31fc66c0c8806"

ListMatchUpdate = getMatchWithOutResult(c)
listData = getResults(key,ListMatchUpdate)
InsertUpdateResult(c,listData)

conn.commit() 

c.close()
conn.close()
