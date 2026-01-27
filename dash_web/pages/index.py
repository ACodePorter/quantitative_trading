from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import pandas as pd
import dash
import plotly.express as px
from loguru import logger
from pathlib import Path
from functools import reduce
from utils.chart_utils import transform_for_view


dash.register_page(__name__)


# 加载原始指数数据
index_dir = Path("datas/raw/indexes")
csv_files = sorted(index_dir.glob("ak_index_global_hist_em_*.csv"))

dfs = []
for csv_file in csv_files:
    try:
        # 从文件名提取指数名称
        name = csv_file.stem.replace("ak_index_global_hist_em_", "")
        df_temp = pd.read_csv(csv_file)
        if "日期" in df_temp.columns and "今开" in df_temp.columns:
            df_temp = df_temp.rename(columns={'日期': 'date', '今开': name})
            dfs.append(df_temp[['date', name]])
    except Exception as e:
        logger.warning(f"读取文件 {csv_file} 失败: {e}")

# 合并所有指数数据
if dfs:
    df = reduce(lambda left, right: pd.merge(left, right, on='date', how='outer'), dfs)
    df = df.sort_values('date')
else:
    # 如果原始数据加载失败，使用归一化数据
    data_dir = Path("datas/processed/indexes")
    file_pattern = "ak_index_global_merged_*.csv"
    matching_files = list(data_dir.glob(file_pattern))
    if matching_files:
        matching_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        df = pd.read_csv(matching_files[0])
        df = df.rename(columns={'日期': 'date'})


# index_dir = Path("datas/raw/indexes")

# fig = go.Figure()
# for csv_file in sorted(index_dir.glob("ak_index_global_hist_em_*.csv")):
#     try:
#         df_tmp = pd.read_csv(csv_file)
#         if "日期" in df_tmp.columns and "今开" in df_tmp.columns:
#             # 解析日期并归一化今开列
#             dates = pd.to_datetime(df_tmp["日期"], errors="coerce")
#             vals = pd.to_numeric(df_tmp["今开"], errors="coerce")
#             if vals.dropna().empty:
#                 continue
#             vmin = vals.min()
#             vmax = vals.max()
#             if vmax > vmin:
#                 norm = (vals - vmin) / (vmax - vmin)
#             else:
#                 norm = pd.Series(0.5, index=vals.index)

#             name = csv_file.stem.replace("ak_index_global_hist_em_", "")
#             fig.add_trace(go.Scatter(
#                 x=dates,
#                 y=norm,
#                 mode="lines",
#                 name=name,
#                 hovertemplate=(
#                     "Index: " + name +
#                     "<br>日期: %{x}<br>归一化值: %{y:.3f}<extra></extra>"
#                 )
#             ))
#     except Exception as e:
#         logger.warning(f"读取文件 {csv_file} 失败: {e}")

# fig.update_layout(
#     title="全球指数归一化走势图",
#     xaxis_title="日期",
#     yaxis_title="归一化值 (0-1)",
#     height=1000,
#     template="plotly_white",
# )

# fig.update_xaxes(
#     rangeslider_visible=True,
#     minor=dict(ticks="inside", showgrid=True),
#     rangeselector=dict(
#         buttons=list([
#             dict(count=1, label="1month", step="month", stepmode="backward"),
#             dict(count=6, label="6month", step="month", stepmode="backward"),
#             dict(count=1, label="1year", step="year", stepmode="backward"),
#             dict(count=3, label="3year", step="year", stepmode="backward"),
#             dict(count=5, label="5year", step="year", stepmode="backward"),
#             dict(count=10, label="10year", step="year", stepmode="backward"),
#             dict(count=20, label="20year", step="year", stepmode="backward"),
#             dict(step="all")
#         ])
#     )
# )

def get_fig(csv_path: str, x_key: str, y_title: str) -> go.Figure:
    df = pd.read_csv(csv_path)
    # breakpoint()
    fig = px.line(
    # fig = px.area(
    # fig = px.scatter(
        df,
        x=x_key,
        y=df.columns,
        hover_data={x_key: "|%B %d, %Y"},
        title='indexes chart',
        color_discrete_sequence=px.colors.qualitative.Dark24,  # Alphabet, Light24, Dark24

    )
    fig.update_layout(
        height=1000,
        # xaxis_title='花萼宽度（cm）',
        yaxis_title=y_title,

    )
    
    fig.update_xaxes(
        # dtick="M1",
        # tickformat="%b\n%Y",
        # tickformat="%Y",
        rangeslider_visible=True,  # 添加滑动块
        minor=dict(ticks="inside", showgrid=True),  # 辅助刻度
        # 范围选择器按钮
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1month", step="month", stepmode="backward"),
                dict(count=6, label="6month", step="month", stepmode="backward"),
                # dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1year", step="year", stepmode="backward"),
                dict(count=3, label="3year", step="year", stepmode="backward"),
                dict(count=5, label="5year", step="year", stepmode="backward"),
                dict(count=10, label="10year", step="year", stepmode="backward"),
                dict(count=20, label="20year", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
        # ticklabelmode="period"
    )
    return fig

# 归一化指数图 - 删除静态图创建，使用回调动态生成


# 美元计价指数图, out 了
# fig2 = get_fig("datas/processed/indexes/all_indexes_data_usd2.csv", "date", "USD(美元)")


layout = html.Div([
    html.H4("全球经济走势，关注变化，而不是价格"),
    html.P(
        "不同国家的股票市场指数"
        "（如上证指数、标普500、日经225、沪深300等）"
        "的单位（数值大小）并不相同，而且它们的计算方法、"
        "基期、基点也各不相同，因此直接比较指数的点数"
        "是没有意义的"
    ),
    # 视图模式选择器
    html.Div([
        html.Label("视图模式：", className='fw-bold me-2'),
        dcc.RadioItems(
            id="index-view-mode",
            options=[
                {"label": "归一化 (收益率比较)", "value": "normalized"},
                {"label": "对数坐标", "value": "log"},
                {"label": "线性坐标", "value": "linear"},
            ],
            value="normalized",  # 默认归一化
            inline=True,
        )
    ], className='d-flex align-items-center my-3'),
    dcc.Graph(id="index-chart"),
])


@callback(
    Output("index-chart", "figure"),
    Input("index-view-mode", "value"),
)
def update_index_chart(view_mode):
    """根据视图模式更新全球指数图表"""
    # 使用工具函数转换数据
    df_plot, yaxis_type, yaxis_suffix = transform_for_view(df, view_mode, date_col='date')

    # 设置 Y 轴标题
    if view_mode == "normalized":
        yaxis_title = '归一化值 (起点=1)'
    else:
        yaxis_title = '指数点数'

    # 创建图表
    fig = px.line(
        df_plot,
        x='date',
        y=[col for col in df_plot.columns if col != 'date'],
        hover_data={'date': "|%B %d, %Y"},
        title='全球指数走势',
        color_discrete_sequence=px.colors.qualitative.Dark24,
    )

    fig.update_layout(
        height=1000,
        xaxis_title='日期',
        yaxis_title=yaxis_title,
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


# @callback(
#     Output("graph3", "figure"),
#     Input("toggle-rangeslider", "value"),
# )
# def display_candlestick2(value):
#     df = pd.read_csv("datas/indexes/all_indexes_data.csv")
#
#     fig = px.line(df, x="date", y=df.columns,
#                   hover_data={"date": "|%B %d, %Y"},
#                   title='custom tick labels')
#     fig.update_xaxes(
#         dtick="M1",
#         tickformat="%b\n%Y",
#         ticklabelmode="period")
#     fig.update_layout(xaxis_rangeslider_visible="slider" in value)
#     return fig


# # if __name__ == "__main__":
# #     app.run_server(debug=True)
