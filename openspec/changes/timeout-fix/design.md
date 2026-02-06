## Context

当前 `utils/update_datas.py` 调用多个外部数据源（akshare、efinance、yfinance）获取金融数据。这些网络请求没有超时机制，当数据源服务响应慢或不可用时，程序会无限期挂起。

受影响的函数包括：
- **akshare**: `get_ak_news_data()`, `get_ak_reits_data()`, `get_ak_metals_data()`, `get_ak_industry_data()`, `get_ak_bond_data()`, `get_ak_index_global_data()`, `get_ak_fund_data()`, `get_ak_cpi_data()`, `get_ak_gdp_data()`, `get_ak_jsl_bond()`
- **efinance**: `get_ef_stock_data()`, `get_ef_bond_data()`, `get_ef_futures_data()`
- **yfinance**: `get_yf_market_data()`, `get_yf_virtual_data()`

## Goals / Non-Goals

**Goals:**
- 为所有网络请求调用添加 10 秒超时保护
- 超时时记录日志，包含函数名便于排查
- 超时或失败时优雅降级，跳过该数据源继续执行
- 保持外部接口不变，向后兼容

**Non-Goals:**
- 不修改数据源 API 或数据格式
- 不改变业务逻辑（数据获取后的处理流程）
- 不添加重试机制（可在后续需求中添加）

## Decisions

### 超时实现方案: `func-timeout`

**选择**: 使用 `func-timeout` 包

**理由**:
- 跨平台兼容（Windows/Linux/macOS）
- API 简洁，易于集成
- 不需要修改现有函数签名
- 相比 `signal` 模块，在 Windows 上也能正常工作

**替代方案考虑**:
- `signal.alarm()`: 不支持 Windows
- `requests` timeout 参数: 需要深入修改每个库的调用，不可行
- 多线程方案: 增加复杂度，可能引入竞态条件

### `safe_call()` 函数设计

```python
def safe_call(func, *args, timeout_seconds=10, **kwargs):
    """通用安全调用函数，带超时保护

    Args:
        func: 要调用的函数
        *args: 函数参数
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
```

**设计要点**:
- 10 秒默认超时（可配置）
- 捕获 `FunctionTimedOut` 和通用异常
- 返回 `None` 表示失败，调用方需检查返回值
- 使用 `func.__name__` 记录函数名

### 调用模式

原代码：
```python
gold_data = ak.macro_cons_gold()
```

修改后：
```python
gold_data = safe_call(ak.macro_cons_gold, timeout_seconds=10)
if gold_data is not None:
    # 处理数据
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| 超时时间设置过短，正常请求被截断 | 10 秒足够大多数请求完成，失败可手动重试 |
| 某些数据源持续超时导致数据缺失 | 日志记录可定位问题数据源，后续可针对性优化 |
| `func-timeout` 在某些环境下兼容性问题 | 该包已广泛使用，支持主流 Python 版本 |

### Trade-offs

- **简单性 vs 重试**: 选择不添加重试机制，保持实现简单。如果数据获取失败，用户可重新运行脚本。
- **超时时间 vs 等待时间**: 10 秒是平衡点，既能捕获卡死的请求，又不会过快中断慢速但正常的请求。

## Migration Plan

### 部署步骤

1. 添加依赖：`uv add func-timeout`
2. 修改 `utils/update_datas.py`：
   - 在文件顶部添加 `safe_call()` 函数
   - 为每个网络请求调用添加 `safe_call()` 包装
   - 添加 `None` 检查逻辑
3. 运行验证：`uv run python -m utils/update_datas`
4. 检查日志确认超时被正确记录

### 回滚策略

直接回滚 Git commit 即可，无需数据库迁移或配置变更。

## Open Questions

- 是否需要为不同数据源设置不同的超时时间？（当前统一为 10 秒）
- 是否需要添加重试机制？（当前不重试）
- 是否需要添加超时统计/监控？（当前仅日志记录）
