## 1. Setup

- [x] 1.1 Add `func-timeout` dependency using `uv add func-timeout`
- [x] 1.2 Create backup branch `feature/timeout-fix` (if not already created)

## 2. Core Implementation

- [x] 2.1 Add `safe_call()` function to `utils/update_datas.py`
  - Import `func_timeout` and `FunctionTimedOut` from `func_timeout`
  - Implement `safe_call()` with 10-second default timeout
  - Add logging for timeout and exception cases

## 3. Apply Timeout Protection - akshare Functions

- [x] 3.1 Update `get_ak_metals_data()` - Wrap `ak.macro_cons_gold()` and `ak.macro_cons_silver()` with `safe_call()`
- [x] 3.2 Update `get_ak_news_data()` - Wrap akshare news API calls with `safe_call()`
- [x] 3.3 Update `get_ak_reits_data()` - Wrap akshare REITs API calls with `safe_call()`
- [x] 3.4 Update `get_ak_industry_data()` - Wrap akshare industry API calls with `safe_call()`
- [x] 3.5 Update `get_ak_bond_data()` - Wrap akshare bond API calls with `safe_call()`
- [x] 3.6 Update `get_ak_index_global_data()` - Wrap akshare global index API calls with `safe_call()`
- [x] 3.7 Update `get_ak_fund_data()` - Wrap akshare fund API calls with `safe_call()`
- [x] 3.8 Update `get_ak_cpi_data()` - Wrap `ak.macro_china_cpi()` with `safe_call()`
- [x] 3.9 Update `get_ak_gdp_data()` - Wrap akshare GDP API calls with `safe_call()`
- [x] 3.10 Update `get_ak_jsl_bond()` - Wrap akshare JSL bond API calls with `safe_call()`

## 4. Apply Timeout Protection - efinance Functions

- [x] 4.1 Update `get_ef_stock_data()` - Wrap efinance stock API calls with `safe_call()`
- [x] 4.2 Update `get_ef_bond_data()` - Wrap efinance bond API calls with `safe_call()`
- [x] 4.3 Update `get_ef_futures_data()` - Wrap efinance futures API calls with `safe_call()`

## 5. Apply Timeout Protection - yfinance Functions

- [x] 5.1 Update `get_yf_market_data()` - Wrap yfinance market API calls with `safe_call()`
- [x] 5.2 Update `get_yf_virtual_data()` - Wrap yfinance virtual/cryptocurrency API calls with `safe_call()`

## 6. Verification

- [x] 6.1 Run `uv run python -m utils/update_datas` and verify no hanging occurs
- [x] 6.2 Check `logs/update_datas.log` for timeout/failure log messages
- [x] 6.3 Verify data files are still created for successful requests
- [x] 6.4 Verify graceful degradation - script continues after timeout
