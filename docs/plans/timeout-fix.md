# 修复数据获取超时问题

## 问题描述

运行 `uv run python -m utils.update_datas` 时，程序卡在网络请求调用上（如 `ak.macro_cons_gold()`），无法继续执行。

## 根本原因

网络请求函数没有内置的超时机制，当数据源网站响应慢或不可用时，会无限期等待。

## 解决方案

创建新分支 `feature/timeout-fix`，添加通用超时保护机制：
1. **超时机制** - 10秒超时
2. **日志记录** - 超时时打印函数名到日志，便于后续排查
3. **优雅降级** - 跳过失败的函数，继续执行其他数据获取

## 实现步骤

### 0. 创建新分支
```bash
git checkout master
git pull origin master
git checkout -b feature/timeout-fix
```

### 1. 添加依赖
```bash
uv add func-timeout
```

### 2. 添加通用超时工具函数

在 `utils/update_datas.py` 文件顶部添加通用的 `safe_call()` 函数。

### 3. 为所有网络请求调用添加超时保护

覆盖所有可能超时的网络请求：
- **akshare**: `get_ak_news_data()`, `get_ak_reits_data()`, `get_ak_metals_data()`, `get_ak_industry_data()`, `get_ak_bond_data()`, `get_ak_index_global_data()`, `get_ak_fund_data()`, `get_ak_cpi_data()`, `get_ak_gdp_data()`, `get_ak_jsl_bond()`
- **efinance**: `get_ef_stock_data()`, `get_ef_bond_data()`, `get_ef_futures_data()`
- **yfinance**: `get_yf_market_data()`, `get_yf_virtual_data()`

## 关键文件

- `utils/update_datas.py` - 需要添加 `safe_call()` 函数，并修改所有网络请求调用
- `pyproject.toml` - 添加 func-timeout 依赖

## 实现代码示例

```python
from func_timeout import func_timeout, FunctionTimedOut

def safe_call(func, *args, timeout_seconds=10, **kwargs):
    """通用安全调用函数，带超时保护（跨平台）

    超时时打印函数名到日志，返回 None，继续执行后续代码
    """
    try:
        return func_timeout(timeout_seconds, func, args=args, kwargs=kwargs)
    except FunctionTimedOut:
        logger.warning(f"【超时】{func.__name__} 调用超时 ({timeout_seconds}秒)，已跳过")
        return None
    except Exception as e:
        logger.error(f"【失败】{func.__name__} 调用失败: {str(e)}")
        return None

# 使用示例：
def get_ak_metals_data():
    """获取 akshare 贵金属数据"""
    try:
        # 黄金持仓数据（带10秒超时）
        gold_data = safe_call(ak.macro_cons_gold, timeout_seconds=10)

        if gold_data is not None:
            gold_data['单价'] = gold_data['总价值']/gold_data['总库存']
            gold_data['单价'] = gold_data['单价'].round(2)
            filename = f"datas/raw/metals/macro_cons_gold.csv"
            ensure_dir(filename)
            gold_data.to_csv(filename, index=False)
            logger.info(f"黄金持仓数据: {filename} 已更新")

        # 白银持仓数据（带10秒超时）
        silver_data = safe_call(ak.macro_cons_silver, timeout_seconds=10)
        # ... 同样处理

# 同样方式处理其他网络请求：
# - akshare 函数
# - efinance 函数
# - yfinance 函数
```

## 验证步骤

1. 切换到新分支 `feature/timeout-fix`
2. 安装依赖：`uv add func-timeout`
3. 运行：`uv run python -m utils/update_datas`
4. 确认程序不再卡住
5. 检查日志文件 `logs/update_datas.log`，确认超时或错误被正确记录
6. 确认其他数据源仍能正常更新
