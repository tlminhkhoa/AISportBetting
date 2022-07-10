import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import sqlite3

conn = sqlite3.connect('./DailyData/SoccerData.db')
c = conn.cursor()

c.execute("""
select * from BudgetTrack ;
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

df = pd.DataFrame(columns=["currentDate","currentDate_timestamp","runningMoney","refillAmount","withdrawAmount","TotalBudget"])
df["currentDate"] = currentDate
df["currentDate_timestamp"] = currentDate_timestamp
df["runningMoney"] = runningMoney
df["refillAmount"] = refillAmount
df["withdrawAmount"] = withdrawAmount
df["TotalBudget"] = TotalBudget
c.close()
conn.close()

df["currentDate"] = pd.to_datetime(df["currentDate"])

app = dash.Dash()

fig = px.line(df.sort_values(by = ["currentDate_timestamp"]), x="currentDate", y="TotalBudget")



app.layout = html.Div(
            className="content", style = {"width":" 100%","background": "#F7F7F7"},
            children=[

            html.Div(
                className="left_menu",style ={"width": "15%","position": "absolute","top": "0","left": "0","height": "100vh","z-index": "999","background":"#2A3F54"
},
                children=[
                    html.Div(
                        'This is the left menu'
                    ),
                ]
            ),

            html.Div(
                className="right_content",style = {"width":"85%","position":"absolute","top": "0","right": "0"},
                children=[
                    html.Div(
                        className="top_metrics", style = {"background": "#EAEAEA","height": "200px","width":"100%","position":"relative","top": "0","right": "0"},
                        children=[
                        'This is top metrics'
                        ]
                    ),
                    html.Div(
                        children = ['This down top metrics',
                        dcc.Graph(figure = fig)]
                    ),
                ]
            )
            ])



if __name__ == '__main__':
    app.run_server(debug=True)