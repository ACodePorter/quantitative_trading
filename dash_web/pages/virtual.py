from dash import Dash, dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import dash
from functools import reduce
from pathlib import Path

dash.register_page(__name__)

# 从原始数据文件读取并合并虚拟货币数据
virtual_dir = Path("datas/raw/virtual")
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


# Layout 必须在回调函数之前定义
layout = html.Div([
    html.H4("决定一个币涨幅空间的是市值（Market Cap），而不是单价。计算公式：市值=单价×流通供应量。"),
    # 视图模式选择器
    html.Div([
        html.Label("视图模式：", className='fw-bold me-2'),
        dcc.RadioItems(
            id="view-mode",
            options=[
                {"label": "归一化 (收益率比较)", "value": "normalized"},
                {"label": "对数坐标", "value": "log"},
                {"label": "线性坐标", "value": "linear"},
            ],
            value="normalized",  # 默认归一化（用户最关注）
            inline=True,
            className='mb-3'
        )
    ], className='d-flex align-items-center my-3'),
    dcc.Graph(id="virtual-chart")
])


@callback(
    Output("virtual-chart", "figure"),
    Input("view-mode", "value"),
)
def update_virtual_chart(view_mode):
    """根据选择的视图模式更新图表"""
    # 根据视图模式处理数据
    if view_mode == "normalized":
        # 归一化：所有货币除以各自第一天的值
        df_plot = df.set_index('date')
        # 处理 NaN：用前向填充后，再除以各自第一天的非空值
        df_plot = df_plot.ffill()
        # 计算每个货币的第一个有效值
        first_values = df_plot.apply(lambda col: col.dropna().iloc[0] if not col.dropna().empty else 1)
        df_plot = df_plot / first_values
        df_plot = df_plot.reset_index()
        yaxis_type = 'linear'
        yaxis_title = '归一化值 (起点=1)'
        title = '虚拟货币收益率比较 (归一化)'
    elif view_mode == "log":
        df_plot = df
        yaxis_type = 'log'
        yaxis_title = 'USD(美元) - 对数坐标'
        title = '虚拟货币价格走势 (对数坐标)'
    else:  # linear
        df_plot = df
        yaxis_type = 'linear'
        yaxis_title = 'USD(美元) - 线性坐标'
        title = '虚拟货币价格走势 (线性坐标)'

    # 创建图表
    fig = px.line(
        df_plot,
        x="date",
        y=[col for col in df_plot.columns if col != 'date'],
        hover_data={"date": "|%B %d, %Y"},
        title=title,
    )

    fig.update_layout(
        height=1000,
        yaxis_title=yaxis_title,
        yaxis_type=yaxis_type,
    )

    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(count=3, label="3Y", step="year", stepmode="backward"),
                dict(count=5, label="5Y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )

    return fig
