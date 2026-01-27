# quantitative_trading

## pip-tools

```cmd
.venv\Scripts\activate
```


```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.in .
RUN pip install pip-tools \
    && pip-compile requirements.in \
    && pip-sync requirements.txt

COPY . .

CMD ["python", "main.py"]

```



```bash
pip install pip-tools

pip-compile requirements.in
pip-compile --upgrade

# 会删除多余包, 包严格一致
pip-sync requirements.txt


```

## pipdeptree

```bash
pip install pipdeptree
pipdeptree
```



## st
```bash
streamlit run your_app.py

```

TODO:

- [x] bond
  - [x] 数据
  - [x] 绘图
  - [x] 策略(指标, 买卖)
  - [x] 国债
- [x] reits
  - [x] 数据
  - [x] 绘图
  - [ ] 策略(指标, 买卖)
- [x] gold
  - [x] 数据
  - [x] 绘图
  - [ ] 策略(指标, 买卖)
- [x] news
  - [x] 数据
  - [x] 绘图
- [x] index
  - [x] 数据
  - [x] 绘图
  - [ ] 策略(指标, 买卖)
- [x] virtual
  - [x] 数据
  - [x] 绘图
  - [ ] 策略(指标, 买卖)

行业

交易
回测



TA-Lib: 提供 200+ 技术指标（如 SMA、RSI、MACD）。
pandas_ta: 轻量、易用，集成 Pandas。



性能优化:

- [x] metals: 计算单价
- [x] reits, index: 多个csv读取,很慢, 改用保存结果
- [x] Linear Scale 和 Log Scale：已实现视图模式切换功能

## 图表视图模式配置

| 页面 | 图表 | 视图模式支持 | 默认模式 | 数据类型 |
|------|------|------------|---------|---------|
| virtual | 加密货币价格走势 | 归一化/对数/线性 ✅ | 归一化 | 价格(USD) |
| metals | 贵金属价格走势 | 归一化/对数/线性 ✅ | 对数 | 价格(USD/盎司) |
| reits | REITs价格走势 | 归一化/对数/线性 ✅ | 对数 | 开盘价 |
| company | 股票K线图 | 对数/线性 ✅ | 对数 | 价格 |
| index | 全球指数走势 | 归一化/对数/线性 ✅ | 归一化 | 指数点数 |
| industry | 行业板块气泡图 | 无（固定对数） | - | 涨跌幅%,市值 |
| bond | 国债收益率曲线 | 无（固定线性） | - | 收益率(%) |
| period | GDP/CPI散点图 | 无（固定线性） | - | 百分比 |
| allocation | 资产配置饼图 | 无（饼图不适用） | - | 比例 |

### 视图模式说明
- **归一化**：所有资产起点为1，直接比较收益率
- **对数**：相同百分比变化显示为相同垂直距离，适合长期趋势
- **线性**：显示原始绝对价格




- [ ] 按钮刷新数据的日志问题
- [ ] 统一异常处理
$市值 = 单价 \times 流通供应量$