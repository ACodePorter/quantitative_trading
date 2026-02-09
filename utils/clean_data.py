from pathlib import Path

import pandas as pd
from loguru import logger

# from .constants import *


def merge_res(
    csv_paths: list, target_columns: list, new_columns: list, output_csv: str
):
    """
    按照时间, 合并多种类型的csv为一个csv
    Args:
        csv_paths:
        target_columns: first must be time , will convert to datetime, sorted
        new_columns:
        output_csv:

    Returns:

    """

    df_list = [pd.read_csv(csv_path) for csv_path in csv_paths]
    df_list_target = []  # target df
    for df in df_list:
        # if '日期' in df.columns:
        #     df.rename(columns={'日期': 'date', '收盘': 'close'}, inplace=True)
        # breakpoint()
        df = convert_time(df, target_columns[0])
        df_list_target.append(df[target_columns])
    # breakpoint()
    df_m = pd.merge(
        df_list_target[0], df_list_target[1], how="outer", on=target_columns[0]
    )
    for i, df in enumerate(df_list_target[2:]):
        df_m = df_m.merge(
            df, how="outer", on=target_columns[0], suffixes=(f"_{i}", f"_{i + 1}")
        )

    df_m.columns = new_columns

    df_m.sort_values("date", inplace=True)

    logger.debug(df_m.dtypes)
    breakpoint()
    # df_m['比特币'] = df_m['比特币'].str.replace(',', '')
    # df_m['比特币'] = df_m['比特币'].astype(float)
    # df_m['以太坊'] = df_m['以太坊'].str.replace(',', '')
    # df_m['以太坊'] = df_m['以太坊'].astype(float)
    # pd.to_numeric()
    df_m.to_csv(output_csv, index=False)
    logger.info(f"{output_csv}已更新")
    return output_csv
