import sqlite3
import requests
import datetime
import time
import http.client
import json

def getOdd(key,date):
    # location is Toronto
    timeZone = "America/Toronto"
    # bet365 ID is 8
    bookMakerID = 8
    # h2h ID is 1
    bet = 1

    returnList = []

    conn = http.client.HTTPSConnection("v3.football.api-sports.io")

    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': key
        }


    conn.request("GET", "/odds?date={}&timezone={}&bet={}&bookmaker={}&page=1".format(date,timeZone,bet,bookMakerID), headers=headers)
    res = conn.getresponse()
    if res.status != 200:
        print("Error Page 1")
    else:
        data = res.read()
        data = json.loads(data)
        returnList.append(data)
        totalPage = int(data["paging"]["total"])

        # since data return maybe in multiple page
        for page in range(2,totalPage+1):
            conn.request("GET", "/odds?date={}&timezone={}&bet={}&bookmaker={}&page={}".format(date,timeZone,bet,bookMakerID,page), headers=headers)
            res = conn.getresponse()
            if res.status != 200:
                print("Error Page {}".format(page))
            else:
                data = res.read()
                data = json.loads(data)
                returnList.append(data)
    conn.close()
    return returnList
    
def InsertMatch(c,returnOddList):
    for el in returnOddList:
        responses = el["response"]
        for response in responses:
            # print(response["bookmakers"])
            fixtureID = response["fixture"]["id"]
            commence_time = response["fixture"]["date"]
            commence_timestamp = response["fixture"]["timestamp"]
            leagueId = response["league"]["id"]
            leagueName = response["league"]["name"]
            homeOdd = response["bookmakers"][0]["bets"][0]["values"][0]["odd"]
            drawOdd = response["bookmakers"][0]["bets"][0]["values"][1]["odd"]
            awayOdd = response["bookmakers"][0]["bets"][0]["values"][2]["odd"]

            try:
                c.execute(""" 
                INSERT INTO SoccerMatch VALUES(?,?,?,?,?,?,?,?)
                """,(fixtureID,commence_time,commence_timestamp,leagueId,leagueName,homeOdd,drawOdd,awayOdd))

                # insert fixtureID for the other tables
                c.execute(""" 
                INSERT INTO Team VALUES(?,?,?)
                """,(fixtureID,None,None))

                c.execute(""" 
                INSERT INTO Result VALUES(?,?,?,?)
                """,(fixtureID,None,None,None))

                c.execute(""" 
                INSERT INTO modelData VALUES(?,?,?,?)
                """,(fixtureID,None,None,None,None,None,None,None))

            except Exception as e:
                print(str(e))
                print((fixtureID,commence_time,commence_timestamp,leagueId,leagueName,homeOdd,drawOdd,awayOdd))


import sqlite3

conn = sqlite3.connect('./DailyData/SoccerData.db')
c = conn.cursor()

from datetime import date
today = date.today()

returnOddList = getOdd("337bf8dbb961deefafa31fc66c0c8806",str(today))
InsertMatch(c,returnOddList)

conn.commit() 

c.close()
conn.close()