## Why

运行 `utils/update_datas.py` 时程序经常卡在网络请求调用上（如 `ak.macro_cons_gold()`），无法继续执行。这是因为网络请求函数没有内置的超时机制，当数据源网站响应慢或不可用时，会无限期等待。

## What Changes

- **新增依赖**: 添加 `func-timeout` 包，提供跨平台的函数超时保护
- **新增通用工具函数**: 在 `utils/update_datas.py` 中添加 `safe_call()` 函数，封装超时逻辑
- **修改所有网络请求调用**: 为 akshare、efinance、yfinance 的网络请求添加 10 秒超时保护
- **改进日志**: 超时时记录函数名到日志文件，便于排查问题
- **优雅降级**: 超时或失败时跳过该数据源，继续执行其他数据获取

## Capabilities

### New Capabilities
- `network-timeout`: 网络请求超时保护机制，为数据获取函数提供超时控制和错误日志记录

### Modified Capabilities
- (none - this is an implementation improvement, no spec-level behavior changes)

## Impact

- **修改文件**: `utils/update_datas.py` - 添加 `safe_call()` 函数，修改约 15 个网络请求调用
- **新增依赖**: `func-timeout` (添加到 `pyproject.toml`)
- **日志文件**: `logs/update_datas.log` - 将增加超时/失败的警告日志
- **无 API 变更**: 外部调用接口不变，仅内部实现增强
