from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import pandas as pd
import dash
from utils.chart_utils import transform_for_view

dash.register_page(__name__)

# 加载数据
df_gold = pd.read_csv("datas/raw/metals/macro_cons_gold.csv")
df_silver = pd.read_csv("datas/raw/metals/macro_cons_silver.csv")

# 合并数据为一个 DataFrame
df = pd.DataFrame({
    'date': df_gold['日期'],
    'Gold': df_gold['单价'],
    'Silver': df_silver['单价']
}).dropna()


# Layout 必须在回调函数之前定义
layout = html.Div([
    html.H4("贵金属价格走势"),
    # 视图模式选择器
    html.Div([
        html.Label("视图模式：", className='fw-bold me-2'),
        dcc.RadioItems(
            id="metals-view-mode",
            options=[
                {"label": "归一化 (收益率比较)", "value": "normalized"},
                {"label": "对数坐标", "value": "log"},
                {"label": "线性坐标", "value": "linear"},
            ],
            value="log",  # 默认对数
            inline=True,
        )
    ], className='d-flex align-items-center my-3'),
    dcc.Graph(id="metals-chart")
])


@callback(
    Output("metals-chart", "figure"),
    Input("metals-view-mode", "value"),
)
def update_metals_chart(view_mode):
    """根据视图模式更新图表"""
    # 使用工具函数转换数据
    df_plot, yaxis_type, yaxis_suffix = transform_for_view(df, view_mode, date_col='date')

    # 创建图表
    fig = go.Figure()
    for col in [c for c in df_plot.columns if c != 'date']:
        fig.add_trace(go.Scatter(
            x=df_plot['date'],
            y=df_plot[col],
            mode='lines+markers',
            name=col
        ))

    # 设置 Y 轴标题
    if view_mode == "normalized":
        yaxis_title = '归一化值 (起点=1)'
    else:
        yaxis_title = 'Price (USD per Ounce)'

    fig.update_layout(
        title='Gold and Silver Prices Over Time',
        xaxis_title='Date',
        yaxis_title=yaxis_title,
        legend_title='Metals',
        height=1000,
        yaxis_type=yaxis_type,
    )
    fig.update_xaxes(
        rangeslider_visible=True,
        minor=dict(ticks="inside", showgrid=True),
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
