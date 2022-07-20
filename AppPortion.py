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

    c.execute(""" select  SoccerMatch.commence_time ,SoccerMatch.commence_timestamp ,modelData.modelBet, Result.FTR , modelData.KellyCriterion , SoccerMatch.homeOdd,SoccerMatch.drawOdd, SoccerMatch.awayOdd,SoccerMatch.fixtureId , SoccerMatch.leagueName from SoccerMatch 
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
    fixtureId = []
    leagueName = [] 
    for tup in listData:
        commence_time.append(tup[0])
        commence_timestamp.append(tup[1])
        modelBet.append(tup[2])
        FTR.append(tup[3])
        KellyCriterion.append(tup[4])
        home.append(tup[5])
        draw.append(tup[6])
        away.append(tup[7])
        fixtureId.append(tup[8])
        leagueName.append(tup[9])
    betOdd = []



    df = pd.DataFrame(columns=["commence_time","commence_timestamp","modelBet", "FTR","KellyCriterion","home","draw","away","fixtureId","leagueName"])
    df["commence_time"] = commence_time
    df["commence_timestamp"] = commence_timestamp
    df["modelBet"] = modelBet
    df["FTR"] = FTR
    df["KellyCriterion"] = KellyCriterion
    df["home"] = home
    df["draw"] = draw
    df["away"] = away
    df["fixtureId"] = fixtureId
    df["leagueName"] = leagueName
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
    
    df = getTeam(df,c,conn)
    c.close()
    conn.close()
   
    return df

def getTeam(df,c,conn):
    homeTeam = []
    awayTeam = []
    for id in df["fixtureId"]:
        c.execute("""

        select homeTeam , awayTeam from Team where fixtureId = ?
        
        """,(id,))
        listData = c.fetchall()

        for tup in listData:
            homeTeam.append(tup[0])
            awayTeam.append(tup[1])

    df["homeTeam"] = homeTeam
    df["awayTeam"] = awayTeam

    return df

def createHeatMap(df):
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
    fig.update_layout(margin=dict(t=50, l=100))

    # add colorbar
    fig['data'][0]['showscale'] = True
    return fig

df = getBetDf()


TotalMoneyGain = round(sum(df["gain"]),2)
NumberOfBet = len(df)
modelAccuracy = ( round(sum(df["betToResult"])/NumberOfBet ,2) ) *100
lastDate = df[df["commence_timestamp"]  == max(df["commence_timestamp"])]["commence_date"]

dfBuget = df.copy()
dfBuget = dfBuget.groupby(by = ["commence_date"]).sum().reset_index()
dfBuget["budget"] = dfBuget["gain"].cumsum()
fig = px.area(dfBuget,x = "commence_date", y="budget", template = "seaborn")
fig.update_xaxes(title_text = "Date")
fig.update_yaxes(title_text = "Cumulative Gain")
fig.update_layout(
    title_text='Cumulative Gain'
)

dfgain = df.copy()
dfgain = dfgain.groupby(by = ["commence_date"]).sum().reset_index()
figLine = px.line(dfgain, x="commence_date",y= "gain",template = "seaborn")
figLine.update_xaxes(title_text = "Mean : {}, Std: {}".format(round(average(dfgain["gain"]),2), round(dfgain["gain"].std(),2)))
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


dfHist = df.copy()
figHist = px.histogram(df, x = "KellyCriterion" , color = "betToResult",template = "seaborn", marginal="box")
figHist.update_layout(
    height=500,
    title_text='Model accuracy to Kelly criterion'
)

figTable = ff.create_table(df[["commence_time","homeTeam","awayTeam","leagueName","modelBet","FTR","KellyCriterion","gain"]].sort_values(["commence_time"], ascending= False).head(8))

df_count_bet = df["modelBet"].value_counts().reset_index()
figPie = px.pie(df_count_bet,names="index",values = "modelBet",template = "seaborn")

df_count_FTR = df["FTR"].value_counts().reset_index()
figPieFTR = px.pie(df_count_FTR,names="index",values = "FTR",template = "seaborn")

figHeat = createHeatMap(df)

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970',
    "margin-top": 5,
    "margin-bottom" : 20
}

CARD_TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#4d74b2'
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
                        html.P(id='card_text_1', children=['Total Cumulative Gain'], style=CARD_TEXT_STYLE),
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
content_second_row_1 = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(figure = fig, style = {"margin": "25px 50px 75px 25px", "border-style" : "solid"}), md=12,
        )
    ]
)

content_second_row_2 = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(figure = figTable, style = {"margin": "25px 50px 75px 25px", "border-style" : "solid"}), md=12,
        )
    ]
)

content_third_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(figure = figLine, id='graph_5', style = {"margin": "25px 50px 25px 25px" , "border-style" : "solid"}), md=6
        ),
        dbc.Col(
            dcc.Graph(figure = figHist, id='graph_6', style = {"margin": "25px 50px 25px 25px" , "border-style" : "solid"}), md=6
        )
    ]
)

content_fourth_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(figure = figPie,style ={"margin": "25px 50px 25px 25px","border-style" : "solid"}, id='graph_1'), md=4
        ),
        dbc.Col(
            dcc.Graph(figure = figPieFTR,id='graph_2',style ={"margin": "25px 50px 25px 25px","border-style" : "solid"}), md=4
        ),
        dbc.Col(
            dcc.Graph(figure = figHeat, id='graph_3',style ={"margin": "25px 50px 25px 25px","border-style" : "solid"}), md=4
        )
    ]
)




content_fifth_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(figure = figHist, style = {"margin": "25px 50px 75px 25px", "border-style" : "solid"}), md=12,
        )
    ]
)

content = html.Div(
    [
        html.H1('Machine play football betting', style=TEXT_STYLE),
        html.H5('Khoa Tran', style=TEXT_STYLE),
        html.Hr(),
        html.Div("This app automatically find soccer matches and apply an algorithm to bide bookmaker"),
        html.Hr(),
        html.Div(),
        content_first_row,
        content_second_row_1,
        content_second_row_2,
        content_third_row,
        content_fourth_row
        # content_fifth_row,
        
    ]
    # style=CONTENT_STYLE
)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP] )
app.layout = html.Div([content], style = {"width":" 100%","background": "#F7F7F7"} )



if __name__ == '__main__':
    app.run_server(debug=True)