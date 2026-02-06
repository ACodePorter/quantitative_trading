import os
from datetime import datetime

from loguru import logger
from dotenv import load_dotenv
from pathlib import Path
import akshare as ak
import efinance as ef  # 国内
import yfinance as yf  # 国际
import easyquotation as eq  # 国内
import pandas as pd
from func_timeout import func_timeout, FunctionTimedOut

load_dotenv()


def safe_call(func, *args, timeout_seconds=10, **kwargs):
    """通用安全调用函数，带超时保护（跨平台）

    超时时打印函数名到日志，返回 None，继续执行后续代码

    Args:
        func: 要调用的函数
        *args: 函数位置参数
        timeout_seconds: 超时时间（秒），默认 10
        **kwargs: 函数关键字参数

    Returns:
        函数返回值，超时或失败返回 None
    """
    try:
        return func_timeout(timeout_seconds, func, args=args, kwargs=kwargs)
    except FunctionTimedOut:
        logger.warning(f"【超时】{func.__name__} 调用超时 ({timeout_seconds}秒)，已跳过")
        return None
    except Exception as e:
        logger.error(f"【失败】{func.__name__} 调用失败: {str(e)}")
        return None


def data_handler(func):
    """数据获取函数的统一异常处理装饰器

    自动捕获异常并记录详细的调试信息：
    - 函数名
    - 异常类型
    - 异常消息
    - 发生位置
    - 局部变量

    使用:
        @data_handler
        def get_ak_news_data():
            # 不需要 try-except
            df = safe_call(ak.stock_info_global_ths)
            ...
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 获取异常位置信息
            tb = e.__traceback__

            # 找到异常发生的实际位置
            # 跳过 wrapper 帧，找到实际执行函数的帧
            frame = None
            filename = ""
            lineno = 0
            func_name = ""

            if tb:
                # 首先尝试使用 traceback 的第一帧（异常发生位置）
                first_tb = tb
                first_frame = first_tb.tb_frame
                first_filename = first_frame.f_code.co_filename
                first_lineno = first_tb.tb_lineno
                first_func_name = first_frame.f_code.co_name

                # 检查第一帧是否在 update_datas.py 中（wrapper 帧）
                if "update_datas.py" not in first_filename:
                    # 第一帧不在 update_datas.py，直接使用
                    frame = first_frame
                    filename = first_filename
                    lineno = first_lineno
                    func_name = first_func_name
                else:
                    # 第一帧在 update_datas.py 中，查看下一帧
                    next_tb = first_tb.tb_next
                    if next_tb is not None:
                        frame = next_tb.tb_frame
                        filename = frame.f_code.co_filename
                        lineno = next_tb.tb_lineno
                        func_name = frame.f_code.co_name
                    else:
                        # 没有下一帧，使用第一帧
                        frame = first_frame
                        filename = first_filename
                        lineno = first_lineno
                        func_name = first_func_name

            logger.error(f"【异常】{func.__name__} 执行失败")
            logger.error(f"  位置: {filename}:{lineno} in {func_name}")
            logger.error(f"  类型: {type(e).__name__}")
            logger.error(f"  消息: {str(e)}")

            # 获取局部变量（截断长值）
            if frame:
                local_vars = {}
                for k, v in frame.f_locals.items():
                    v_str = str(v)[:100]  # 限制长度
                    local_vars[k] = v_str
                if local_vars:
                    logger.error(f"  变量: {local_vars}")

            return None

    return wrapper


# TODO: 目录改为日期

def ensure_dir(file_path):
    """确保目录存在"""
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


@data_handler
def get_ak_news_data():
    """获取 akshare 新闻数据"""
    date_str = datetime.now().strftime('%Y%m%d')

    # 全球财经直播
    df1 = safe_call(ak.stock_info_global_ths, timeout_seconds=10)
    if df1 is not None:
        filename = f"datas/raw/news/ak_stock_info_global_ths.csv"
        ensure_dir(filename)
        df1.to_csv(filename, index=False)
        logger.info(f"全球财经直播数据: {filename} 已更新")

    # 同花顺财经-电报
    df2 = safe_call(ak.stock_info_global_cls, timeout_seconds=10)
    if df2 is not None:
        filename = f"datas/raw/news/ak_stock_info_global_cls.csv"
        ensure_dir(filename)
        df2.to_csv(filename, index=False)
        logger.info(f"同花顺财经-电报数据: {filename} 已更新")

    # 东方财富-财经早餐
    df3 = safe_call(ak.stock_info_cjzc_em, timeout_seconds=10)
    if df3 is not None:
        filename = f"datas/raw/news/ak_stock_info_cjzc_em.csv"
        ensure_dir(filename)
        df3.to_csv(filename, index=False)
        logger.info(f"东方财富-财经早餐数据: {filename} 已更新")

    # stock_info_global_sina
    df4 = safe_call(ak.stock_info_global_sina, timeout_seconds=10)
    if df4 is not None:
        filename = f"datas/raw/news/ak_stock_info_global_sina.csv"
        ensure_dir(filename)
        df4.to_csv(filename, index=False)
        logger.info(f"新浪财经-全球财经新闻数据: {filename} 已更新")

    # stock_info_global_em
    df5 = safe_call(ak.stock_info_global_em, timeout_seconds=10)
    if df5 is not None:
        filename = f"datas/raw/news/ak_stock_info_global_em.csv"
        ensure_dir(filename)
        df5.to_csv(filename, index=False)
        logger.info(f"东方财富-全球财经新闻数据: {filename} 已更新")
    
    
@data_handler
def get_ak_reits_data():

    """
    获取 akshare reits 数据
    """
    # date_str = datetime.now().strftime('%Y%m%d')
    # reits列表
    reits_list = safe_call(ak.reits_realtime_em, timeout_seconds=10)
    if reits_list is not None:
        filename = f"datas/raw/reits/reits_realtime_em.csv"
        ensure_dir(filename)
        reits_list.to_csv(filename, index=False)
        logger.info(f"REITs列表数据: {filename} 已更新")

        # reits_hist_em

        for symbol, name in zip(reits_list['代码'], reits_list['名称']):
            df = safe_call(ak.reits_hist_em, symbol=symbol, timeout_seconds=10)
            if df is not None:
                filename = f"datas/raw/reits/reits_hist_em_{symbol}_{name}.csv"
                ensure_dir(filename)
                df.to_csv(filename, index=False)
                logger.info(f"REITs {symbol} 数据: {filename} 已更新")
        
    # merge_ak_reits()
        

def merge_ak_reits():
    """
    读取多个 akshare REITs 数据, pd.merge 合并后保存为一个csv文件, 方便绘图
    """
    reits_dir = Path("datas/raw/reits")
    output_dir = Path("datas/processed/reits")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for csv_file in sorted(reits_dir.glob("reits_hist_em_*.csv")):
        try:
            df_tmp = pd.read_csv(csv_file)
            if "日期" in df_tmp.columns and "今开" in df_tmp.columns:
                # 解析日期
                dates = pd.to_datetime(df_tmp["日期"], errors="coerce")
                vals = pd.to_numeric(df_tmp["今开"], errors="coerce")

                name = csv_file.stem.replace("reits_hist_em_", "")
                
                # 合并数据
                if 'merged_df' in locals():
                    merged_df = pd.merge(merged_df, pd.DataFrame({
                        '日期': dates,
                        name: vals
                    }), on='日期', how='outer')
                else:
                    merged_df = pd.DataFrame({
                        '日期': dates,
                        name: vals
                    })

        except Exception as e:
            logger.warning(f"读取文件 {csv_file} 失败: {e}")
            
    # 保存合并后的数据
    if 'merged_df' in locals():
        merged_df.sort_values('日期', inplace=True)
        merge_file = output_dir / "reits_merged.csv"
        merged_df.to_csv(merge_file, index=False)
        logger.info(f"REITs合并数据已保存: {merge_file}")
        
    else:
        logger.warning("没有可合并的REITs数据")

    
    
@data_handler
def get_ak_metals_data():
    """获取 akshare 贵金属数据"""
    # date_str = datetime.now().strftime('%Y%m%d')
    # 黄金持仓数据
    gold_data = safe_call(ak.macro_cons_gold, timeout_seconds=10)

    if gold_data is not None:
        gold_data['单价'] = gold_data['总价值']/gold_data['总库存']
        gold_data['单价'] = gold_data['单价'].round(2)

        filename = f"datas/raw/metals/macro_cons_gold.csv"
        ensure_dir(filename)
        gold_data.to_csv(filename, index=False)
        logger.info(f"黄金持仓数据: {filename} 已更新")

    # 白银持仓数据
    silver_data = safe_call(ak.macro_cons_silver, timeout_seconds=10)

    if silver_data is not None:
        silver_data['单价'] = silver_data['总价值']/silver_data['总库存']
        silver_data['单价'] = silver_data['单价'].round(2)

        filename = f"datas/raw/metals/macro_cons_silver.csv"
        ensure_dir(filename)
        silver_data.to_csv(filename, index=False)
        logger.info(f"白银持仓数据: {filename} 已更新")
        
    
@data_handler
def get_ak_industry_data():
    """获取 akshare 行业数据"""
    date_str = datetime.now().strftime('%Y%m%d')

    # 行业分类数据

    industry_list = safe_call(ak.stock_sector_spot, timeout_seconds=10)
    if industry_list is not None:
        filename = f"datas/raw/n_indexes/ak_industry_list_{date_str}.csv"
        ensure_dir(filename)
        industry_list.to_csv(filename, index=False)
        logger.info(f"行业分类数据: {filename} 已更新")

    # industry_list_dfcf = ak.stock_board_industry_name_em()  # 行业板块-名称， 推荐
    # industry_list_ths = ak.stock_board_industry_summary_ths()  # 同花顺行业一览表
    # ak.stock_fund_flow_industry()
    # industry_list_xl = ak.stock_sector_spot()
    # logger.info("行业分类数据已更新")
        

@data_handler
def get_ak_bond_data():
    """获取 akshare 债券数据"""
    date_str = datetime.now().strftime('%Y%m%d')

    # 可转债数据
    conv_bond = safe_call(ak.bond_zh_cov, timeout_seconds=10)
    if conv_bond is not None:
        filename = f"datas/raw/bonds/ak_bond_zh_cov.csv"
        ensure_dir(filename)
        conv_bond.to_csv(filename, index=False)
        logger.info(f"可转债数据: {filename} 已更新")

    # 国债收益率数据
    bond_rate = safe_call(ak.bond_zh_us_rate, timeout_seconds=10)
    if bond_rate is not None:
        filename = f"datas/raw/bonds/ak_cn_us_rate.csv"
        ensure_dir(filename)
        bond_rate.to_csv(filename, index=False)
        logger.info(f"中美债券收益率数据: {filename} 已更新")
        
        
@data_handler
def get_ak_index_global_data():
    """
    获取 akshare 全球指数数据
    """
    # date_str = datetime.now().strftime('%Y%m%d')
    # 全球指数列表
    index_global = safe_call(ak.index_global_spot_em, timeout_seconds=10)
    if index_global is not None:
        filename = f"datas/raw/indexes/ak_index_global_spot_em.csv"
        ensure_dir(filename)
        index_global.to_csv(filename, index=False)
        logger.info(f"全球指数列表数据: {filename} 已更新")

        for symbol in index_global['名称'].unique():
            df = safe_call(ak.index_global_hist_em, symbol=symbol, timeout_seconds=10)
            if df is not None:
                filename = f"datas/raw/indexes/ak_index_global_hist_em_{symbol.replace('/', '')}.csv"
                ensure_dir(filename)
                df.to_csv(filename, index=False)
                logger.info(f"全球指数 {symbol} 数据: {filename} 已更新")
        
    # merge_ak_index()
    
    
def merge_ak_index():
    """
    读取多个 akshare 全球指数数据, pd.merge 合并后保存为一个csv文件, 方便绘图
    数据的columns: 日期, 名称1, 名称2, 名称3, ...
    
    数据为归一化值
    min-max 会扭曲涨跌幅，只能表示区间位置，所以不能用。只有 x/start 才能表达真实涨跌率，是金融标准做法
    
    基准归一化（x / start）
    
    归一化后保留两位小数
    归一化后保存为新的csv文件
    方便后续绘图使用
    
    """

    index_dir = Path("datas/raw/indexes")
    output_dir = Path("datas/processed/indexes")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 获取制定的csv
    target_csv = [
        '道琼斯', '标普500', '纳斯达克', '加拿大S&PTSX',
        '巴西BOVESPA',
        '富时100', '德国DAX', '法国CAC', 
        '日经225', '韩国KOSPI',
        '上证指数', '深证成指', '恒生指数', '沪深300',
        '澳大利亚标普200', 
        '印度孟买SENSEX',
        '越南',
    ]
    csvs = []
    for csv_file in index_dir.glob("ak_index_global_hist_em_*.csv"):
        if any(tc in csv_file.stem.replace("ak_index_global_hist_em_", "") for tc in target_csv):
            csvs.append(csv_file)
    
    # 获取 start date
    start_date = get_start_date(csvs)
    
    for csv_file in csvs:
        try:
            
            df_tmp = pd.read_csv(csv_file)
            
            if "日期" in df_tmp.columns and "今开" in df_tmp.columns:
                # 解析日期并归一化今开列
                # dates = pd.to_datetime(df_tmp["日期"], errors="coerce")
                dates = df_tmp["日期"]
                vals = pd.to_numeric(df_tmp["今开"], errors="coerce")
                if vals.dropna().empty:
                    continue

                # 计算norm
                start_val = vals[dates == start_date].values[0]
                norm = vals / start_val    
                # norm(Series) 保留两位小数
                norm = norm.round(2)

                name = csv_file.stem.replace("ak_index_global_hist_em_", "")
                
                # 合并数据
                if 'merged_df' in locals():
                    merged_df = pd.merge(merged_df, pd.DataFrame({
                        '日期': dates,
                        name: norm
                    }), on='日期', how='outer')
                else:
                    merged_df = pd.DataFrame({
                        '日期': dates,
                        name: norm
                    })

        except Exception as e:
            logger.error(f"读取文件 {csv_file} 失败: {e}")
            
    # 保存合并后的数据
    if 'merged_df' in locals():
        merged_df.sort_values('日期', inplace=True)
        merge_file = output_dir / f"ak_index_global_merged_{start_date}.csv"
        merged_df.to_csv(merge_file, index=False)
        logger.info(f"全球指数合并数据已保存: {merge_file}")
    else:
        logger.error("没有可合并的全球指数数据")
    

def get_start_date(csvs: list) -> str:
    """
    获取多个csv文件的共同起始日期, 非连续
    """
    k = '日期'
    common_dates = set(pd.read_csv(csvs[0])[k])
    for f in csvs[1:]:
        common_dates &= set(pd.read_csv(f)[k])
    common_dates = sorted(list(common_dates))
        
    if common_dates:
        return min(common_dates)


@data_handler
def get_ak_fund_data():
    """获取 akshare 基金数据"""
    date_str = datetime.now().strftime('%Y%m%d')

    # ETF基金列表
    etf_list = safe_call(ak.fund_etf_category_sina, timeout_seconds=10)
    if etf_list is not None:
        filename = f"datas/raw/funds/ak_etf_list_{date_str}.csv"
        ensure_dir(filename)
        etf_list.to_csv(filename, index=False)
        logger.info(f"ETF基金列表: {filename} 已更新")

    # # 基金公司数据
    # fund_aum = safe_call(ak.fund_aum_em, timeout_seconds=10)
    # if fund_aum is not None:
    #     filename = f"datas/raw/funds/ak_fund_aum_{date_str}.csv"
    #     ensure_dir(filename)
    #     fund_aum.to_csv(filename, index=False)
    #     logger.info(f"基金公司数据: {filename} 已更新")

    # ak.fund_portfolio_industry_allocation_em()  # 基金行业配置
    
    
@data_handler
def get_ak_macro_data():
    """获取 akshare 宏观经济数据"""
    # CPI数据
    get_ak_cpi_data()

    # GDP数据
    get_ak_gdp_data()

    # date_str = datetime.now().strftime('%Y%m%d')

    # # 中国PMI数据
    # pmi_data = ak.macro_china_pmi_yearly()
    # filename = f"datas/raw/macro/ak_china_pmi_{date_str}.csv"
    # ensure_dir(filename)
    # pmi_data.to_csv(filename, index=False)
    # logger.info("中国PMI数据已更新")

    # # 中国货币供应量
    # money_supply = ak.macro_china_money_supply()
    # filename = f"datas/raw/macro/ak_china_money_supply_{date_str}.csv"
    # ensure_dir(filename)
    # money_supply.to_csv(filename, index=False)
    # logger.info("中国货币供应量数据已更新")


def get_ak_cpi_data():

    # date_str = datetime.now().strftime('%Y%m%d')

    # cpi消费者物价指数
    cpi_cn_data = safe_call(ak.macro_china_cpi_yearly, timeout_seconds=10)
    if cpi_cn_data is not None:
        filename = f"datas/raw/cpis/macro_china_cpi_yearly.csv"
        ensure_dir(filename)
        cpi_cn_data.to_csv(filename, index=False)
        logger.info(f"中国CPI数据: {filename} 已更新")

    # cpi 美国
    cpi_usa = safe_call(ak.macro_usa_cpi_yoy, timeout_seconds=10)
    if cpi_usa is not None:
        filename = f"datas/raw/cpis/macro_usa_cpi_yoy.csv"
        ensure_dir(filename)
        cpi_usa.to_csv(filename, index=False)
        logger.info(f"美国CPI数据: {filename} 已更新")
    # cpi 欧元区
    cpi_enro = safe_call(ak.macro_euro_cpi_yoy, timeout_seconds=10)
    if cpi_enro is not None:
        filename = f"datas/raw/cpis/macro_euro_cpi_yoy.csv"
        ensure_dir(filename)
        cpi_enro.to_csv(filename, index=False)
        logger.info(f"欧元区CPI数据: {filename} 已更新")

    # cpi 澳大利亚
    cpi_australia = safe_call(ak.macro_australia_cpi_yearly, timeout_seconds=10)
    if cpi_australia is not None:
        filename = f"datas/raw/cpis/macro_australia_cpi_yearly.csv"
        ensure_dir(filename)
        cpi_australia.to_csv(filename, index=False)
        logger.info(f"澳大利亚CPI数据: {filename} 已更新")

    # cpi 加拿大
    cpi_canada = safe_call(ak.macro_canada_cpi_yearly, timeout_seconds=10)
    if cpi_canada is not None:
        filename = f"datas/raw/cpis/macro_canada_cpi_yearly.csv"
        ensure_dir(filename)
        cpi_canada.to_csv(filename, index=False)
        logger.info(f"加拿大CPI数据: {filename} 已更新")

    # cpi 日本
    cpi_japan = safe_call(ak.macro_japan_cpi_yearly, timeout_seconds=10)
    if cpi_japan is not None:
        filename = f"datas/raw/cpis/macro_japan_cpi_yearly.csv"
        ensure_dir(filename)
        cpi_japan.to_csv(filename, index=False)
        logger.info(f"日本CPI数据: {filename} 已更新")
    
    
def get_ak_gdp_data():

    # date_str = datetime.now().strftime('%Y%m%d')
    # china gdp
    china_gdp = safe_call(ak.macro_china_gdp_yearly, timeout_seconds=10)
    if china_gdp is not None:
        filename = f"datas/raw/gdps/ak_china_gdp.csv"
        ensure_dir(filename)
        china_gdp.to_csv(filename, index=False)
        logger.info(f"中国GDP数据: {filename} 已更新")

    # usa gdp
    usa_gdp = safe_call(ak.macro_usa_gdp_monthly, timeout_seconds=10)
    if usa_gdp is not None:
        filename = f"datas/raw/gdps/ak_usa_gdp.csv"
        ensure_dir(filename)
        usa_gdp.to_csv(filename, index=False)
        logger.info(f"美国GDP数据: {filename} 已更新")

    # euro gdp
    enro_gdp = safe_call(ak.macro_euro_gdp_yoy, timeout_seconds=10)
    if enro_gdp is not None:
        filename = f"datas/raw/gdps/ak_euro_gdp.csv"
        ensure_dir(filename)
        enro_gdp.to_csv(filename, index=False)
        logger.info(f"欧元区GDP数据: {filename} 已更新")

    # canada gdp
    canada_gdp = safe_call(ak.macro_canada_gdp_monthly, timeout_seconds=10)
    if canada_gdp is not None:
        filename = f"datas/raw/gdps/ak_canada_gdp.csv"
        ensure_dir(filename)
        canada_gdp.to_csv(filename, index=False)
        logger.info(f"加拿大GDP数据: {filename} 已更新")

@data_handler
def get_yf_market_data():
    """获取 yfinance 市场数据"""
    date_str = datetime.now().strftime('%Y%m%d')

    # 主要市场指数
    tickers = {
        '^GSPC': 'SP500',
        '^DJI': 'DowJones',
        '^IXIC': 'NASDAQ',
        '^N225': 'Nikkei225',
        '^FTSE': 'FTSE100',
        '^GDAXI': 'DAX',
        '000001.SS': 'SSE',
        '399001.SZ': 'SZSE'
    }

    # TODO: 获取SP500数据失败: Too Many Requests. Rate limited. Try after a while.

    # for symbol, name in tickers.items():
    #     try:
    #         ticker = yf.Ticker(symbol)
    #         # 获取历史数据
    #         hist = ticker.history(period="1y")
    #         filename = f"datas/raw/indexes/yf_{name}_{date_str}.csv"
    #         ensure_dir(filename)
    #         hist.to_csv(filename)
    #         logger.info(f"{name}指数数据已更新")
    #
    #         # 获取基本信息
    #         info = pd.Series(ticker.info)
    #         filename = f"datas/raw/indexes/yf_{name}_info_{date_str}.csv"
    #         ensure_dir(filename)
    #         info.to_csv(filename)
    #         logger.info(f"{name}指数信息已更新")
    #
    #     except Exception as e:
    #         logger.error(f"获取{name}数据失败: {str(e)}")


@data_handler
def get_ef_stock_data():
    """获取股票相关数据"""
    # 获取所有A股列表
    # date_str = datetime.now().strftime('%Y%m%d')

    for k in [
        '沪深A股',
        '美股',
        '港股',
        '行业板块',
        '概念板块',
        '可转债',
        'ETF',
    ]:
        # PE in data
        df = safe_call(ef.stock.get_realtime_quotes, k, timeout_seconds=10)
        if df is not None:
            filename = f"datas/raw/stocks/ef_{k}.csv"
            df.to_csv(filename, index=False)
            logger.info(f"ef {k} 数据: {filename} 已更新")


@data_handler
def get_ef_bond_data():
    """获取债券相关数据"""
    # date_str = datetime.now().strftime('%Y%m%d')
    # 获取可转债数据
    # bond_list = safe_call(ef.bond.get_realtime_quotes, timeout_seconds=10)
    # if bond_list is not None:
    #     filename = f"datas/raw/bonds/ef_bond_list_{date_str}.csv"
    #     bond_list.to_csv(filename, index=False)

    bond_base_info = safe_call(ef.bond.get_all_base_info, timeout_seconds=10)
    if bond_base_info is not None:
        filename = f"datas/raw/bonds/ef_get_all_base_info.csv"
        bond_base_info.to_csv(filename, index=False)
        logger.info(f"债券数据: {filename} 已更新")


@data_handler
def get_ef_futures_data():
    """获取期货相关数据"""
    # 获取期货合约列表
    date_str = datetime.now().strftime('%Y%m%d')
    futures_list = safe_call(ef.futures.get_realtime_quotes, timeout_seconds=10)
    if futures_list is not None:
        filename = f"datas/raw/futures/ef_futures_list_{date_str}.csv"
        ensure_dir(filename)
        futures_list.to_csv(filename, index=False)
        logger.info(f"期货合约列表数据: {filename} 已更新")


@data_handler
def get_ak_jsl_bond():
    cookies = os.getenv('JISILU_COOKIES')
    df = safe_call(ak.bond_cb_jsl, cookie=cookies, timeout_seconds=10)
    if df is not None:
        if len(df) < 200:
            logger.error(f'jsl df get fail, need to login: https://www.jisilu.cn/data/cbnew/#cb')
            return
        # breakpoint()
        filename = f"datas/raw/bonds/conv_{datetime.now().strftime("%Y%m%d")}.csv"
        df.to_csv(filename, index=False)
        logger.info(f"jsl债券数据: {filename} 已更新")
    

def get_eq_stock_data():
    """
    eq stock, 没有有效数据
    """
    date_str = datetime.now().strftime('%Y%m%d')
    
    obj = eq.use("sina")
    res = obj.market_snapshot(prefix=True)
    df = pd.DataFrame(res).T.reset_index().rename(columns={"index": "code"})
    filename = f"datas/raw/stocks/eq_stocks_{date_str}.csv"
    df.to_csv(filename, index=False)
    logger.info(f"eq股票数据: {filename} 已更新")


def ana_ak_bonds(bond_id2names: dict):
    """
    对特定债券进行分析
    """
    for bond_id, bond_name in bond_id2names.items():
        df_detail = ak.bond_zh_cov_value_analysis(bond_id)
        breakpoint()
        df_detail.to_csv(f'datas/raw/bonds/details/{bond_name}.csv', index=False)
        

@data_handler
def ana_ef_fund(codes: list):
    """获取基金相关数据"""
    date_str = datetime.now().strftime('%Y%m%d')

    for code in codes:
        ef.fund.get_pdf_reports(code)      # 基金公告, 非常老旧10年前的pdf
        logger.info(f"{code}基金pdf, 已更新")

        df0 = ef.fund.get_base_info(code)        # 基金基本信息
        filename = f"datas/raw/funds/ef_get_base_info_{date_str}.csv"
        df0.to_csv(filename, index=False)
        logger.info(f"{code} 基金基本信息: {filename} 已更新")

        df = ef.fund.get_types_percentage(code)  # 基金类型占比
        filename = f"datas/raw/funds/ef_get_types_percentage_{date_str}.csv"
        df.to_csv(filename, index=False)
        logger.info(f"{code} 基金类型占比: {filename} 已更新")
        # df2 = ef.stock.get_members(code)         # 获取指数的成分股, FIXME: notwork


"""===============================stage================================="""
    
    
def update_ef():
    # 更新 efinance 数据
    get_ef_stock_data()
    get_ef_bond_data()
    

def update_ak0():
    get_ak_jsl_bond()
    get_ak_news_data()
    

def update_ak1():
    
    get_ak_metals_data()
    get_ak_bond_data()
    get_ak_fund_data()
    get_ak_macro_data()
    
    
def update_ak2():
    # 更新 akshare 数据
    get_ak_reits_data()
    get_ak_index_global_data()
    
    
def update_ak3():
    merge_ak_index()
    merge_ak_reits()


@data_handler
def get_yf_virtual_data():
    """获取 yfinance 虚拟货币历史数据

    支持的虚拟货币：
    - BTC-USD: Bitcoin (BTC)
    - ETH-USD: Ethereum (ETH)
    - XRP-USD: XRP (XRP)
    - BNB-USD: BNB (BNB)
    - SOL-USD: Solana (SOL)
    - USDT-USD: Tether (USDT)
    """
    # 虚拟货币映射: yfinance代码 -> 英文全名+缩写
    virtual_currencies = {
        'BTC-USD': 'Bitcoin (BTC)',
        'ETH-USD': 'Ethereum (ETH)',
        'XRP-USD': 'XRP (XRP)',
        'BNB-USD': 'BNB (BNB)',
        'SOL-USD': 'Solana (SOL)',
        'USDT-USD': 'Tether (USDT)',
    }

    for symbol, name in virtual_currencies.items():
        # 创建 Ticker 并获取历史数据的包装函数
        def fetch_virtual_data():
            ticker = yf.Ticker(symbol)
            return ticker.history(period='max')

        hist = safe_call(fetch_virtual_data, timeout_seconds=10)

        if hist is None:
            continue

        if hist.empty:
            logger.warning(f"{name}({symbol}) 数据为空，跳过")
            continue

        # 格式转换
        hist = hist.reset_index()
        hist['日期'] = hist['Date'].dt.strftime('%Y-%m-%d')
        hist = hist.rename(columns={
            'Close': '收盘',
            'Open': '开盘',
            'High': '高',
            'Low': '低',
            'Volume': '交易量'
        })

        # 保存文件
        filename = f"datas/raw/virtual/{name}历史数据.csv"
        ensure_dir(filename)
        hist[['日期', '收盘', '开盘', '高', '低', '交易量']].to_csv(filename, index=False)
        logger.info(f"{name}数据: {filename} 已更新，共 {len(hist)} 条记录")


if __name__ == "__main__":
    from utils.set_log import set_log
    set_log('update_datas.log')
    
    # update_ef()
    # update_ak0()
    update_ak1()
    # update_ak2()
    # update_ak3()
    # get_yf_virtual_data()
    