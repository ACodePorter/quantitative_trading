from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import pandas as pd
import dash

dash.register_page(__name__)

layout = html.Div([
    html.H4("股票K线图"),
    # 视图模式选择器
    html.Div([
        html.Label("视图模式：", className='fw-bold me-2'),
        dcc.RadioItems(
            id="view-mode",
            options=[
                {"label": "对数坐标", "value": "log"},
                {"label": "线性坐标", "value": "linear"},
            ],
            value="log",  # 默认对数
            inline=True,
        ),
        html.Div(style={'width': '20px'}),  # 间隔
        dcc.Checklist(
            id="toggle-rangeslider",
            options=[{"label": "显示范围滑块", "value": "slider"}],
            value=["slider"],
            inline=True,
        ),
    ], className='d-flex align-items-center my-3'),
    dcc.Graph(id="graph"),
])


@callback(
    Output("graph", "figure"),
    Input("view-mode", "value"),
    Input("toggle-rangeslider", "value"),
)
def display_candlestick(view_mode, slider_value):
    """根据视图模式和滑块设置更新K线图"""
    df = pd.read_excel("datas/raw/stocks/gegu_stock_ak.xlsx")

    fig = go.Figure(
        go.Candlestick(
            x=df["date"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
        )
    )

    fig.update_layout(
        xaxis_rangeslider_visible="slider" in slider_value,
        height=1000,
        yaxis_type=view_mode,  # 使用选择的视图模式
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
