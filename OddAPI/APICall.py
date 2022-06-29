import sqlite3
import requests
import datetime
import time


def getActiveSport(API_KEY):
    
    # Get active sport
    sports_response = requests.get(
    'https://api.the-odds-api.com/v4/sports', 
    params={
        'api_key': API_KEY
    }
    )

    if sports_response.status_code != 200:
        print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')

    print('Remaining requests', sports_response.headers['x-requests-remaining'])

    sport_obj = sports_response.json()

    # Only get soccer match
    soccerList = [] 
    for el in sport_obj:
        if el["group"] == "Soccer":
            soccerList.append(el["key"])

    return soccerList, sports_response.status_code


def getMatchData(API_KEY,SoccerLeague):

    # get the uk bookie and only moneyline 
    odds_response = requests.get(
    f'https://api.the-odds-api.com/v4/sports/{SoccerLeague}/odds',
    params={
        'api_key': API_KEY,
        'regions': "uk",
        'markets': "h2h",
        'oddsFormat': "decimal"
    })

    if odds_response.status_code != 200:
        print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')

    print('Remaining requests', odds_response.headers['x-requests-remaining'])          
    matchData = odds_response.json()

    return matchData, odds_response.status_code
    

def addSoccerMatch_Odd(c,matchData):

    for match in matchData:

        id = match["id"]
        sport_key = match["sport_key"]
        sport_title = match["sport_title"]
        commence_time = match["commence_time"]
        home_team = match["home_team"]
        away_team = match["away_team"]
        listBookMakers = match["bookmakers"]
        
        commence_time_unix = time.mktime(datetime.datetime.strptime(commence_time.replace("T"," ").replace("Z",""), "%Y-%m-%d %H:%M:%S").timetuple())

        try:
            c.execute(""" 
            INSERT INTO SoccerMatch VALUES(?,?,?,?,?,?,?)
            """,(id,sport_key,sport_title,commence_time_unix,commence_time,home_team,away_team))

        except Exception as e:
            print(str(e))

        

        addSoccerOdd(id,home_team,away_team,listBookMakers,c)


def addSoccerOdd(id,home_team,away_team,listBookMakers,c):

    for book in listBookMakers:
        namebook = book["key"]
        last_update = book["last_update"]
        marketsTemp = book["markets"]
        for el in marketsTemp[0]["outcomes"]:
            if el["name"] == home_team:
                homeOdd = el["price"]
            if el["name"] == away_team:
                awayOdd = el["price"]
            if el["name"] == "Draw":
                drawOdd = el["price"]

        try:
            order = """ INSERT INTO """+namebook+""" VALUES(?,?,?,?,?)""".format()
            c.execute(order,(id,last_update,homeOdd,awayOdd,drawOdd))
        except Exception as e:
            print(str(e))


if __name__ == "__main__":
    key = "f5c3c456eaeea3cfae87d491714fdd55"
    conn = sqlite3.connect('./DailyData/betting4.db')
    c = conn.cursor()
    # soccerList, statusActiveSport = getActiveSport(key)
    # if statusActiveSport == 200:
    #     for SoccerLeague in soccerList[:3]:
    #         matchData, statusMatchData = getMatchData(key,SoccerLeague)
    #         if statusMatchData == 200:
    #             addSoccerMatch_Odd(c,matchData)
    #     conn.commit()

    listOfResultSoccer = ["soccer_epl","soccer_france_ligue_one","soccer_germany_bundesliga","soccer_italy_serie_a","soccer_spain_la_liga",]

    for SoccerLeague in listOfResultSoccer:
       matchData, statusMatchData = getMatchData(key,SoccerLeague)
       if statusMatchData == 200:
        addSoccerMatch_Odd(c,matchData)
    conn.commit() 

    c.close()
    conn.close()