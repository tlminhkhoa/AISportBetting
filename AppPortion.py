from datetime import date
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import sqlite3
from numpy import average
import plotly.express as px
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import plotly.figure_factory as ff



def getBetDf():
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


    def addGain(row):
        if row["betToResult"] == False:
            row["gain"] = -row["KellyCriterion"]
        else:
            row["gain"] = row["KellyCriterion"]*(row["betOdd"]-1)
        return row

    df = df.apply(addGain, axis = 1)
    df["commence_time"] = pd.to_datetime(df["commence_time"])
    df["commence_date"] = df["commence_time"].apply(lambda x: x.date())
    df = df.sort_values(["commence_timestamp"])
    
    return df

df = getBetDf()
TotalMoneyGain = round(sum(df["gain"]),2)
NumberOfBet = len(df)
modelAccuracy = ( round(sum(df["betToResult"])/NumberOfBet ,2) ) *100
lastDate = df[df["commence_timestamp"]  == max(df["commence_timestamp"])]["commence_date"]

dfBuget = df.copy()
dfBuget = dfBuget.groupby(by = ["commence_date"]).sum().reset_index()
dfBuget["budget"] = dfBuget["gain"].cumsum()
fig = px.area(dfBuget,x = "commence_date", y="budget", template = "seaborn")


dfgain = df.copy()
dfgain = dfgain.groupby(by = ["commence_date"]).sum().reset_index()
figLine = px.line(dfgain, x="commence_date",y= "gain",template = "seaborn")
figLine.add_hline(y=0,line_dash="dot")
figLine.add_shape( # add a horizontal "target" line
    type="line", line_width=3, opacity=1, line_dash="dot",
    x0=0, x1=1, xref="paper", y0=0, y1=0, yref="y"
)
figLine.update_traces(textposition='top center')
figLine.update_layout(
    height=500,
    title_text='Gain distribution by date'
)

figLine.add_annotation(text = "Mean : {}".format(round(average(dfgain["gain"]),2)),font=dict(size=15) , showarrow = False , align="right" , xref='paper', yref='paper',
                x=1,
                y=0.25, )
figLine.add_annotation(text = "Std : {}".format(round(dfgain["gain"].std(),2)),font=dict(size=15) , showarrow = False , align="right" , xref='paper', yref='paper',
                x=1,
                y=0.1, )

dfHist = df.copy()
figHist = px.histogram(df, x = "KellyCriterion" , color = "betToResult",template = "seaborn", marginal="box")
figHist.update_layout(
    height=500,
    title_text='Model accuracy to Kelly criterion'
)

figTable = ff.create_table(df[["commence_time","modelBet","FTR","betToResult","gain"]].sort_values(["commence_time"], ascending= False).head(5))

figPie = px.pie(df["betToResult"].value_counts().reset_index(),names= ["Correct","Wrong "],values = "betToResult",template = "seaborn")


TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970',
    "margin-top": 5,
    "margin-bottom" : 20
}

CARD_TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#0074D9'
}

style = {"width":" 100%","background": "#F7F7F7"}

content_first_row = dbc.Row([
    dbc.Col(
        dbc.Card(
            [

                dbc.CardBody(
                    [
                        html.H4(id='card_title_1', children= str(TotalMoneyGain) + " Unit", className='card-title',
                                style=CARD_TEXT_STYLE),
                        html.P(id='card_text_1', children=['Total Money Gain'], style=CARD_TEXT_STYLE),
                    ]
                )
            ]
        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [

                dbc.CardBody(
                    [
                        html.H4(children = str(NumberOfBet) + " bets", className='card-title', style=CARD_TEXT_STYLE),
                        html.P(children = "Number of bet make", style=CARD_TEXT_STYLE),
                    ]
                ),
            ]

        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4(children = str(modelAccuracy) + " %", className='card-title', style=CARD_TEXT_STYLE),
                        html.P(children = "Model Accuracy", style=CARD_TEXT_STYLE),
                    ]
                ),
            ]

        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4(children = lastDate, className='card-title', style=CARD_TEXT_STYLE),
                        html.P(children = ["Last day play"], style=CARD_TEXT_STYLE),
                    ]
                ),
            ]
        ),
        md=3
    )
])

content_second_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(figure = figPie,style ={"margin": "25px 50px 25px 25px","border-style" : "solid"}, id='graph_1'), md=4
        ),
        dbc.Col(
            dcc.Graph(id='graph_2',style ={"margin": "25px 50px 25px 25px","border-style" : "solid"}), md=4
        ),
        dbc.Col(
            dcc.Graph(id='graph_3',style ={"margin": "25px 50px 25px 25px","border-style" : "solid"}), md=4
        )
    ]
)

content_third_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(figure = fig, style = {"margin": "25px 50px 75px 25px", "border-style" : "solid"}), md=12,
        )
    ]
)

content_fourth_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(figure = figLine, id='graph_5', style = {"margin": "25px 50px 25px 25px" , "border-style" : "solid"}), md=6
        ),
        dbc.Col(
            dcc.Graph(figure = figHist, id='graph_6',style = {"margin": "25px 50px 75px 25px", "border-style" : "solid"}), md=6
        )
    ]
)
content_fifth_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(figure = figTable, style = {"margin": "25px 50px 75px 25px", "border-style" : "solid"}), md=12,
        )
    ]
)

content = html.Div(
    [
        html.H1('Machine play football betting', style=TEXT_STYLE),
        html.H5('Khoa Tran', style=TEXT_STYLE),
         html.Hr(),
        html.Div(),
        content_first_row,
        content_third_row,
        content_fourth_row,
        content_fifth_row,
        content_second_row
    ]
    # style=CONTENT_STYLE
)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP] )
app.layout = html.Div([content], style = {"width":" 100%","background": "#F7F7F7"} )



if __name__ == '__main__':
    app.run_server(debug=True)