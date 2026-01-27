from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import dash

from loguru import logger
from utils.chart_utils import transform_for_view


dash.register_page(__name__)



# 分析REITs数据
def analyze_reits_data(df):
    """分析REITs数据，返回统计信息"""
    if df.empty:
        return {
            'total_reits': 0,
            'rising_reits': 0,
            'falling_reits': 0,
            'flat_reits': 0,
            'avg_change': 0,
            'max_rise': 0,
            'max_fall': 0,
            'total_volume': 0,
            'avg_volume': 0
        }
    
    # 确保数据类型正确
    df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
    df['成交量'] = pd.to_numeric(df['成交量'], errors='coerce')
    
    # 基本统计
    total_reits = len(df)
    rising_reits = len(df[df['涨跌幅'] > 0])
    falling_reits = len(df[df['涨跌幅'] < 0])
    flat_reits = len(df[df['涨跌幅'] == 0])
    
    # 涨跌幅统计
    avg_change = df['涨跌幅'].mean()
    max_rise = df['涨跌幅'].max()
    max_fall = df['涨跌幅'].min()
    
    # 成交量统计
    total_volume = df['成交量'].sum()
    avg_volume = df['成交量'].mean()
    
    analysis = {
        'total_reits': total_reits,
        'rising_reits': rising_reits,
        'falling_reits': falling_reits,
        'flat_reits': flat_reits,
        'avg_change': avg_change,
        'max_rise': max_rise,
        'max_fall': max_fall,
        'total_volume': total_volume,
        'avg_volume': avg_volume
    }
    
    return analysis

# 获取REITs分类
def get_reits_categories(df):
    """根据REITs名称分类"""
    categories = {
        '物流仓储': ['物流', '仓储'],
        '产业园区': ['产业园', '科创', '智造', '产园'],
        '商业地产': ['商业', '奥莱', '消费', '商场'],
        '基础设施': ['高速', '公路', '水利', '能源', '光伏', '清洁能源', '数据中心'],
        '租赁住房': ['租赁', '住房', '安居', '保租房'],
        '其他': []
    }
    
    category_counts = {category: 0 for category in categories.keys()}
    
    for name in df['名称']:
        matched = False
        for category, keywords in categories.items():
            if any(keyword in name for keyword in keywords):
                category_counts[category] += 1
                matched = True
                break
        if not matched:
            category_counts['其他'] += 1
    
    return category_counts


# 处理实时整体数据, 前两个块
df_reits = pd.read_csv('datas/raw/reits/reits_realtime_em.csv')
analysis = analyze_reits_data(df_reits)
category_counts = get_reits_categories(df_reits)

# 绘制整体的历史数据图, 用merged的历史数据
df = pd.read_csv('datas/processed/reits/reits_merged.csv', parse_dates=['日期'])


# 创建布局
layout = dbc.Container([
    # 页面标题
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1(
                    '🏢 REITs市场分析',
                    className='text-center mb-3',
                    style={'color': '#2E86AB', 'fontWeight': 'bold'}
                ),
                html.P(
                    '房地产投资信托基金(REITs)实时数据与分析',
                    className='text-center text-muted lead mb-4'
                )
            ], className='py-4', style={'backgroundColor': '#f8f9fa'})
        ], width=12)
    ]),
    
    # 数据概览卡片
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader('📊 REITs市场概览'),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H5('市场统计', className='text-primary'),
                                html.Div([
                                    html.Span('总数量: ', className='fw-bold'),
                                    html.Span(f"{analysis.get('total_reits', 0)}", className='text-info')
                                ], className='mb-1'),
                                html.Div([
                                    html.Span('上涨: ', className='fw-bold'),
                                    html.Span(f"{analysis.get('rising_reits', 0)}", className='text-success')
                                ], className='mb-1'),
                                html.Div([
                                    html.Span('下跌: ', className='fw-bold'),
                                    html.Span(f"{analysis.get('falling_reits', 0)}", className='text-danger')
                                ], className='mb-1'),
                                html.Div([
                                    html.Span('平盘: ', className='fw-bold'),
                                    html.Span(f"{analysis.get('flat_reits', 0)}", className='text-warning')
                                ])
                            ])
                        ], md=4),
                        dbc.Col([
                            html.Div([
                                html.H5('涨跌幅统计', className='text-info'),
                                html.Div([
                                    html.Span('平均涨跌: ', className='fw-bold'),
                                    html.Span(f"{analysis.get('avg_change', 0):.2f}%", 
                                             className='text-success' if analysis.get('avg_change', 0) > 0 else 'text-danger')
                                ], className='mb-1'),
                                html.Div([
                                    html.Span('最大涨幅: ', className='fw-bold'),
                                    html.Span(f"{analysis.get('max_rise', 0):.2f}%", className='text-success')
                                ], className='mb-1'),
                                html.Div([
                                    html.Span('最大跌幅: ', className='fw-bold'),
                                    html.Span(f"{analysis.get('max_fall', 0):.2f}%", className='text-danger')
                                ])
                            ])
                        ], md=4),
                        dbc.Col([
                            html.Div([
                                html.H5('成交量统计', className='text-warning'),
                                html.Div([
                                    html.Span('总成交量: ', className='fw-bold'),
                                    html.Span(f"{analysis.get('total_volume', 0):,.0f}", className='text-info')
                                ], className='mb-1'),
                                html.Div([
                                    html.Span('平均成交量: ', className='fw-bold'),
                                    html.Span(f"{analysis.get('avg_volume', 0):,.0f}", className='text-info')
                                ])
                            ])
                        ], md=4)
                    ])
                ])
            ], className='border-0 shadow-sm mb-4')
        ], width=12)
    ]),
    
    # REITs分类统计
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader('📈 REITs分类统计'),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H6(category, className='text-center'),
                                html.H4(count, className='text-center text-primary mb-0'),
                                html.Small(f'{count/analysis.get("total_reits", 1)*100:.1f}%', 
                                         className='text-muted d-block text-center')
                            ])
                        ], md=2) for category, count in category_counts.items()
                    ])
                ])
            ], className='border-0 shadow-sm mb-4')
        ], width=12)
    ]),
    
    # 视图模式选择器
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Label("视图模式：", className='fw-bold me-2'),
                dcc.RadioItems(
                    id="reits-view-mode",
                    options=[
                        {"label": "归一化 (收益率比较)", "value": "normalized"},
                        {"label": "对数坐标", "value": "log"},
                        {"label": "线性坐标", "value": "linear"},
                    ],
                    value="log",  # 默认对数
                    inline=True,
                )
            ], className='d-flex align-items-center my-3'),
        ], width=12)
    ]),

    # REITs图表
    dcc.Graph(id="reits-chart"),
    
    
], fluid=True, className='py-4', style={'backgroundColor': '#f8f9fa'})


@callback(
    Output("reits-chart", "figure"),
    Input("reits-view-mode", "value"),
)
def update_reits_chart(view_mode):
    """根据视图模式更新图表"""
    # 使用工具函数转换数据
    df_plot, yaxis_type, yaxis_suffix = transform_for_view(df, view_mode, date_col='日期')

    # 设置 Y 轴标题
    if view_mode == "normalized":
        yaxis_title = '归一化值 (起点=1)'
    else:
        yaxis_title = '开盘价'

    # 创建图表
    fig = px.line(
        df_plot,
        x='日期',
        y=[col for col in df_plot.columns if col != '日期'],
        title='REITs历史价格走势',
        color_discrete_sequence=px.colors.qualitative.Dark24,
    )

    fig.update_layout(
        title='REITs历史价格走势',
        xaxis_title='日期',
        yaxis_title=yaxis_title,
        legend_title='REITs名称',
        height=1000,
        template='plotly_white',
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
