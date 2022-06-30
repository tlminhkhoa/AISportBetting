import sqlite3
def create_table(c):
    try:
        c.execute("""CREATE TABLE IF NOT EXISTS SoccerMatch(
  fixtureId  integer PRIMARY KEY,
  commence_time char(25),
  commence_timestamp integer,
  leagueId integer,
  leagueName varchar,
  homeOdd DECIMAL(4, 2),
  drawOdd DECIMAL(4, 2),
  awayOdd DECIMAL(4, 2)
  

)""")

        c.execute("""CREATE TABLE IF NOT EXISTS Team(
  fixtureId  integer PRIMARY KEY,
  homeTeam varchar,
  awayTeam varchar,
  FOREIGN KEY (fixtureId) REFERENCES SoccerMatch(fixtureId)
)""")   

        c.execute("""CREATE TABLE IF NOT EXISTS Result(
  fixtureId  integer PRIMARY KEY,
  home_goal integer,
  away_goal integer,
  FTR char(1),
  FOREIGN KEY (fixtureId) REFERENCES SoccerMatch(fixtureId)
)""")

  
        c.execute("""CREATE TABLE IF NOT EXISTS BudgetTrack(
  currentDate  char(25) PRIMARY KEY ,
  runningMoney real,
  refillCount integer,
  withdrawAmount integer,
  TotalBudget real
 ) """) 
    
        c.execute("""CREATE TABLE IF NOT EXISTS modelData(
  fixtureId  integer PRIMARY KEY,
  currentDate char(25),
  currentDate_timestamp integer,
  modelBet char(1),
  betToResult char(1),
  modelProba DECIMAL(7, 6),
  KellyCriterion DECIMAL(7, 6),
  betDatePortion DECIMAL(7, 6),
  BetAmount DECIMAL(7, 6),
  FOREIGN KEY (fixtureId) REFERENCES SoccerMatch(fixtureId)
  FOREIGN KEY (currentDate) REFERENCES BudgetTrack(currentDate)
 )""")
        conn.commit()
    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    
    # create the database
    conn = sqlite3.connect('./DailyData/SoccerData.db')
    c = conn.cursor()
    create_table(c)
    c.close()
    conn.close()
