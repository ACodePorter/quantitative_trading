"""
图表数据转换工具函数
用于支持对数/线性/归一化三种视图模式
"""
import pandas as pd


def transform_for_view(df, view_mode, date_col='date'):
    """
    根据视图模式转换数据

    Args:
        df: 原始数据 DataFrame
        view_mode: 视图模式
            - 'normalized': 归一化，所有资产起点为1
            - 'log': 对数坐标（返回原始数据，由图表设置 yaxis_type='log'）
            - 'linear': 线性坐标（返回原始数据）
        date_col: 日期列名

    Returns:
        tuple: (处理后的 df, yaxis_type, yaxis_title)

    Examples:
        >>> df_plot, y_type, y_title = transform_for_view(df, 'normalized', '日期')
        >>> fig.update_layout(yaxis_type=y_type, yaxis_title=y_title)
    """
    if view_mode == "normalized":
        # 归一化：所有资产除以各自第一天的值
        df_plot = df.set_index(date_col)
        # 前向填充 NaN
        df_plot = df_plot.ffill()
        # 计算每个资产第一个有效值
        first_values = df_plot.apply(
            lambda col: col.dropna().iloc[0] if not col.dropna().empty else 1
        )
        df_plot = df_plot / first_values
        df_plot = df_plot.reset_index()
        return df_plot, 'linear', '归一化值 (起点=1)'

    elif view_mode == "log":
        # 对数坐标：返回原始数据，图表设置 yaxis_type='log'
        return df, 'log', ''

    else:  # linear
        # 线性坐标：返回原始数据
        return df, 'linear', ''
