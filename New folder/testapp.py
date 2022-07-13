import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import sqlite3
import plotly.express as px
import pandas as pd
conn = sqlite3.connect('../DailyData/SoccerData.db')
c = conn.cursor()

c.execute("""
select currentDate, currentDate_timestamp,runningMoney from BudgetTrack ;
""")
listData = c.fetchall()
currentDate = []
currentDate_timestamp = []
runningMoney = []

for tup in listData:
    currentDate.append(tup[0])
    currentDate_timestamp.append(tup[1])
    runningMoney.append(tup[2])

df = pd.DataFrame(columns=["currentDate","currentDate_timestamp","runningMoney"])
df["currentDate"] = currentDate
df["currentDate_timestamp"] = currentDate_timestamp
df["runningMoney"] = runningMoney    
df["currentDate"] = pd.to_datetime(df["currentDate"])

fig = px.area(df.sort_values(by = ["currentDate_timestamp"]), x="currentDate", y="runningMoney", template = "seaborn")

c.close()
conn.close()




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
                        html.H4(id='card_title_1', children=[int(max(df["runningMoney"]))], className='card-title',
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
                        html.H4('Card Title 2', className='card-title', style=CARD_TEXT_STYLE),
                        html.P('Sample text.', style=CARD_TEXT_STYLE),
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
                        html.H4('Card Title 3', className='card-title', style=CARD_TEXT_STYLE),
                        html.P('Sample text.', style=CARD_TEXT_STYLE),
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
                        html.H4('Card Title 4', className='card-title', style=CARD_TEXT_STYLE),
                        html.P('Sample text.', style=CARD_TEXT_STYLE),
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
            dcc.Graph(figure = fig), md=12,
        )
    ]
)

content_fourth_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_5'), md=6
        ),
        dbc.Col(
            dcc.Graph(id='graph_6'), md=6
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