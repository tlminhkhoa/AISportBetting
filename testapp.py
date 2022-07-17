import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import sqlite3
import plotly.express as px
import pandas as pd

def getTrackBudgetData():
    conn = sqlite3.connect('./DailyData/SoccerData.db')
    c = conn.cursor()
    c.execute("""
    select currentDate, currentDate_timestamp,runningMoney,refillAmount,withdrawAmount,TotalBudget from BudgetTrack ;
    """)
    listData = c.fetchall()
    currentDate = []
    currentDate_timestamp = []
    runningMoney = []
    refillAmount = []
    withdrawAmount = []
    TotalBudget = []
    for tup in listData:
        currentDate.append(tup[0])
        currentDate_timestamp.append(tup[1])
        runningMoney.append(tup[2])
        refillAmount.append(tup[3])
        withdrawAmount.append(tup[4])
        TotalBudget.append(tup[5])

    df = pd.DataFrame(columns=["currentDate","currentDate_timestamp","runningMoney"])
    df["currentDate"] = currentDate
    df["currentDate_timestamp"] = currentDate_timestamp
    df["runningMoney"] = runningMoney    
    df["refillAmount"] = refillAmount   
    df["withdrawAmount"] = withdrawAmount 
    df["TotalBudget"] = TotalBudget    
    df["currentDate"] = pd.to_datetime(df["currentDate"])
    c.close()
    conn.close()
    
    return df

df = getTrackBudgetData()
todayData = df[df["currentDate_timestamp"] == max(df["currentDate_timestamp"])]
runningMoney =  int(todayData["runningMoney"])
refillAmount =  int(todayData["refillAmount"])
withdrawAmount =  int(todayData["withdrawAmount"])
TotalBudget =  int(todayData["TotalBudget"])
fig = px.area(df.sort_values(by = ["currentDate_timestamp"]), x="currentDate", y="runningMoney", template = "seaborn")


def getAmountData():
    conn = sqlite3.connect('./DailyData/SoccerData.db')
    c = conn.cursor()

    c.execute(
        """
        select PlaceBetTable.currentDate, PlaceBetTable.Gain from PlaceBetTable
        """
    )
    listData = c.fetchall()
    currentDate = []
    Gain = []

    for tup in listData:
        currentDate.append(tup[0])
        Gain.append(tup[1])

    df = pd.DataFrame(columns=["currentDate","Gain"])
    df["currentDate"] = currentDate
    df["Gain"] = Gain
    df["currentDate"] = pd.to_datetime(df["currentDate"])
    df = df.groupby(by=["currentDate"]).sum()
    return df

dfGain = getAmountData()

figAmount = px.line(dfGain ,title='Amount Gain Distribnution',  template = "seaborn")
figAmount.update_layout(
    margin=dict(l=0,r=0,b=0,t=0)
    )
# the style arguments for the main content page.
# CONTENT_STYLE = {
#     'margin-left': '0%',
#     'margin-right': '5%',
#     'padding': '20px 10p'
# }

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970',
    # "background":"#2A3F54"
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
                        html.H4(id='card_title_1', children=runningMoney, className='card-title',
                                style=CARD_TEXT_STYLE),
                        html.P(id='card_text_1', children=['runningMoney'], style=CARD_TEXT_STYLE),
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
                        html.H4(children = [withdrawAmount], className='card-title', style=CARD_TEXT_STYLE),
                        html.P(children = ['withdrawAmount'], style=CARD_TEXT_STYLE),
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
                        html.H4(children = [refillAmount], className='card-title', style=CARD_TEXT_STYLE),
                        html.P(children = ["refillAmount"], style=CARD_TEXT_STYLE),
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
                        html.H4(children = [TotalBudget], className='card-title', style=CARD_TEXT_STYLE),
                        html.P(children = ["TotalBudget"], style=CARD_TEXT_STYLE),
                    ]
                ),
            ]
        ),
        md=3
    )
])

# content_second_row = dbc.Row(
#     [
#         dbc.Col(
#             dcc.Graph(id='graph_1'), md=4
#         ),
#         dbc.Col(
#             dcc.Graph(id='graph_2'), md=4
#         ),
#         dbc.Col(
#             dcc.Graph(id='graph_3'), md=4
#         )
#     ]
# )

content_third_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(figure = fig , style = {"margin": "25px 50px 75px 25px"}), md=12,
        )
    ]
)

content_fourth_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(figure= figAmount,id='graph_5', style = {"margin": "25px 50px 25px 25px"}), md=6
        ),
        dbc.Col(
            dcc.Graph(id='graph_6',style = {"margin": "25px 50px 75px 25px"}), md=6
        )
    ]
)

content = html.Div(
    [
        html.H1('FootBall Bet DashBoard', style=TEXT_STYLE),
         html.Div(),
        html.Div(),
        content_first_row
        # ,
        # content_second_row
        ,
        content_third_row,
        content_fourth_row
    ]
    # style=CONTENT_STYLE
)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP] )
app.layout = html.Div([content], style = {"width":" 100%","background": "#F7F7F7"} )



if __name__ == '__main__':
    app.run_server(debug=True)