from dash import Dash, dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import dash
from functools import reduce
from pathlib import Path

dash.register_page(__name__)

# 从原始数据文件读取并合并虚拟货币数据
virtual_dir = Path("datas/virtual")
csv_files = sorted(virtual_dir.glob("*历史数据.csv"))

dfs = []
for csv_file in csv_files:
    # 从文件名提取显示名: "Bitcoin (BTC)历史数据.csv" -> "Bitcoin (BTC)"
    display_name = csv_file.stem.replace("历史数据", "")

    df_temp = pd.read_csv(csv_file)
    df_temp = df_temp.rename(columns={'日期': 'date', '收盘': display_name})
    dfs.append(df_temp[['date', display_name]])

# 外连接合并所有货币数据
df = reduce(
    lambda left, right: pd.merge(left, right, on='date', how='outer'),
    dfs
)
df = df.sort_values('date')

fig = px.line(
    df,
    x="date",
    y=df.columns,
    hover_data={"date": "|%B %d, %Y"},
    title='virtual chart',
)
fig.update_layout(
    height=1000,
    yaxis_title='USD(美元)',
)
fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1month", step="month", stepmode="backward"),
            dict(count=6, label="6month", step="month", stepmode="backward"),
            dict(count=1, label="1year", step="year", stepmode="backward"),
            dict(count=3, label="3year", step="year", stepmode="backward"),
            dict(count=5, label="5year", step="year", stepmode="backward"),
            dict(count=10, label="10year", step="year", stepmode="backward"),
            dict(count=20, label="20year", step="year", stepmode="backward"),
            dict(step="all")
        ])
    )
)

layout = html.Div([
    html.H4("加密货币走势，关注变化，而不是价格"),
    dcc.Graph(figure=fig)
])
