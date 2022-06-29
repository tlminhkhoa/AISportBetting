import sqlite3
def create_table(c):
    ukBookmakers = ["sport888","betfred","betvictor","betfair","betclic","boylesports","casumo","coral","ladbrokes" ,"leovegas",
    "livescorebet","marathonbet","matchbook","paddypower","skybet","unibet","virginbet" ,"williamhill"]
    
    try:
        c.execute("""CREATE TABLE IF NOT EXISTS SoccerMatch(
  ID char(32) PRIMARY KEY, 
  sport_key varchar,
  sport_title varchar,
  commence_time_unix REAL,
  commence_time  char(20),
  home_team varchar,
  away_team varchar
)""")
        c.execute("""CREATE TABLE IF NOT EXISTS ResultTable(
  ID char(32) PRIMARY KEY,
  completed boolean ,
  home_team_score integer,
  away_team_score integer,
  result char(1),
  last_update char(20),
  FOREIGN KEY (ID) REFERENCES SoccerMatch(ID)
) """)

        for bookMaker in ukBookmakers:
            c.execute("""CREATE TABLE IF NOT EXISTS {}(
    id  char(32) PRIMARY KEY,
    last_update  char(20),
    homeOdd DECIMAL(4, 2),
    awayOdd DECIMAL(4, 2),
    drawOdd DECIMAL(4, 2),
    FOREIGN KEY (ID) REFERENCES SoccerMatch(ID)
        ) """.format(bookMaker)) 
    
    
        conn.commit()
    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    
    conn = sqlite3.connect('./DailyData/betting4.db')
    c = conn.cursor()
    create_table(c)
    c.close()
    conn.close()
