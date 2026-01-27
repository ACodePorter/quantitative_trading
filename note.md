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
- [ ] Linear Scale 和 Log Scale




- [ ] 按钮刷新数据的日志问题
- [ ] 统一异常处理
