import sqlite3
import pandas as pd
conn = sqlite3.connect('./DailyData/SoccerData.db')
c = conn.cursor()

c.execute(""" select  SoccerMatch.commence_time ,SoccerMatch.commence_timestamp ,modelData.modelBet, Result.FTR , modelData.KellyCriterion , SoccerMatch.homeOdd,SoccerMatch.drawOdd, SoccerMatch.awayOdd from SoccerMatch 
    join modelData on SoccerMatch.fixtureId = modelData.fixtureId
    join Result on Result.fixtureId = SoccerMatch.fixtureId
    where modelData.KellyCriterion > 0.4

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
# print(df["gain"].cumsum())
# print(sum(df["gain"]))
# print(df["betToResult"].value_counts())
c.close()
conn.close()

from sklearn.metrics import confusion_matrix
import plotly.figure_factory as ff

z = confusion_matrix(df["modelBet"],df["FTR"],labels=["H", "D", "A"])

x = ["H", "D", "A"]
y =  ["H", "D", "A"]

# change each element of z to type string for annotations
z_text = [[str(y) for y in x] for x in z]

# set up figure 
fig = ff.create_annotated_heatmap(z, x=x, y=y, annotation_text=z_text, colorscale='Blues')

# add title
fig.update_layout(title_text='<i><b>Confusion matrix</b></i>',
                  #xaxis = dict(title='x'),
                  #yaxis = dict(title='x')
                 )

# add custom xaxis title
fig.add_annotation(dict(font=dict(color="black",size=14),
                        x=0.5,
                        y=-0.15,
                        showarrow=False,
                        text="Predicted value",
                        xref="paper",
                        yref="paper"))

# add custom yaxis title
fig.add_annotation(dict(font=dict(color="black",size=14),
                        x=-0.35,
                        y=0.5,
                        showarrow=False,
                        text="Real value",
                        textangle=-90,
                        xref="paper",
                        yref="paper"))

# adjust margins to make room for yaxis title
fig.update_layout(margin=dict(t=50, l=200))

# add colorbar
fig['data'][0]['showscale'] = True
fig.show()