# Backtesting Module

## 📋 Overview

Module backtesting để mô phỏng giao dịch trên dữ liệu lịch sử, thu thập clean data, và validate strategy logic.

---

## 🎯 Objectives

1. **Collect Clean Data:** 50-100 simulated trades
2. **Validate Strategy:** Test Pro Trader logic on historical data
3. **Measure Performance:** Win rate, returns, drawdown
4. **Identify Patterns:** Winning vs losing trades

---

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install pandas numpy vnstock
```

### 2. Run Backtest

```bash
# Run backtest (1 year of data, 10 symbols)
python3 backtesting/run_backtest.py
```

### 3. Review Results

```bash
# Check CSV export
cat backtest_trades.csv

# Query database
sqlite3 database/trading.db
SELECT * FROM signal_performance;
```

---

## 📊 How It Works

### Workflow

```
1. FETCH HISTORICAL DATA
   └─ vnstock → 1-2 years of OHLCV data

2. SIMULATE TRADING
   ├─ Day 1: Calculate indicators → Generate signals
   ├─ Day 2: Check positions → Execute new signals
   ├─ Day 3: Check stop-loss/take-profit → Close if triggered
   └─ ...

3. TRACK PERFORMANCE
   ├─ Entry price, exit price
   ├─ Profit/loss %
   ├─ Holding days
   └─ Close reason (STOP_LOSS, TAKE_PROFIT, etc.)

4. SAVE RESULTS
   ├─ Database (signals table)
   └─ CSV export (backtest_trades.csv)
```

---

## 🔬 Backtest Engine

### Features

- **Realistic Simulation:** Respects stop-loss and take-profit
- **Position Management:** Tracks open positions
- **Capital Management:** Tracks available capital
- **Performance Metrics:** Win rate, returns, drawdown
- **Data Export:** CSV and database

### Example Usage

```python
from backtesting import BacktestEngine
from bot.data_fetcher import DataFetcher

# Fetch historical data
fetcher = DataFetcher(source='vnstock')
data_dict = fetcher.fetch_multiple_symbols(
    symbols=['VNM', 'VCB', 'HPG'],
    limit=500
)

# Run backtest
engine = BacktestEngine(initial_capital=100_000_000)
results = engine.run_backtest(
    data_dict=data_dict,
    start_date='2024-01-01',
    end_date='2025-12-31'
)

# Save results
engine.save_trades_to_db()
engine.export_trades_to_csv('backtest_trades.csv')

# Print summary
print(f"Total Trades: {results['total_trades']}")
print(f"Win Rate: {results['win_rate']:.1f}%")
print(f"Total Return: {results['total_return_pct']:+.2f}%")
```

---

## 📈 Performance Metrics

### Calculated Metrics

| Metric | Description |
|--------|-------------|
| **Total Trades** | Number of completed trades |
| **Win Rate** | % of profitable trades |
| **Total Return** | Overall profit/loss (%) |
| **Avg Profit** | Average profit per winning trade (%) |
| **Avg Loss** | Average loss per losing trade (%) |
| **Avg Holding** | Average holding period (days) |
| **Max Loss** | Largest single loss (%) |
| **Final Capital** | Ending capital (VND) |

### Example Output

```
📊 BACKTEST RESULTS
================================================================================

💰 CAPITAL:
   Initial: 100,000,000 VND
   Final: 112,500,000 VND
   Return: +12,500,000 VND (+12.50%)

📈 TRADES:
   Total: 75
   Wins: 45 (60.0%)
   Losses: 30

📊 PERFORMANCE:
   Avg Profit: +8.50%
   Avg Loss: -4.20%
   Avg Holding: 12.5 days
   Max Loss: -5.00%

================================================================================
```

---

## 🔍 Validation Checks

### Automatic Validation

The backtest runner performs automatic validation:

```python
# Check 1: Win rate reasonable?
if 40 <= win_rate <= 70:
    ✅ Win rate is reasonable
else:
    ⚠️ Win rate seems unusual

# Check 2: Return reasonable?
if -20 <= total_return_pct <= 50:
    ✅ Return is reasonable
else:
    ⚠️ Return seems unusual

# Check 3: Holding period reasonable?
if 3 <= avg_holding_days <= 30:
    ✅ Avg holding is reasonable
else:
    ⚠️ Avg holding seems unusual
```

---

## 📁 Output Files

### 1. Database (trading.db)

All trades saved to `signals` table:

```sql
SELECT 
    symbol,
    signal_type,
    confidence_score,
    price_at_signal,
    profit_loss_pct,
    holding_days
FROM signals
WHERE is_closed = 1
ORDER BY close_timestamp DESC;
```

### 2. CSV Export (backtest_trades.csv)

```csv
symbol,entry_date,entry_price,exit_date,exit_price,profit_loss_pct,holding_days,reason,confidence
VNM,2024-03-15,86000,2024-03-28,94600,10.00,13,TAKE_PROFIT,85.5
VCB,2024-03-16,92000,2024-03-20,87400,-5.00,4,STOP_LOSS,65.2
...
```

---

## 🎯 Configuration

### Backtest Parameters

```python
# In run_backtest.py

SYMBOLS = ['VNM', 'VCB', 'HPG', 'VIC', 'VHM']  # Symbols to test
START_DATE = '2024-01-01'                       # Start date
END_DATE = '2025-12-31'                         # End date
INITIAL_CAPITAL = 100_000_000                   # Starting capital (VND)
```

### Strategy Parameters

Uses Pro Trader strategy with default settings:
- Min confidence: 60%
- Stop-loss: 5%
- Take-profit: 10%
- Min R/R: 1.5

To customize:

```python
from strategies.pro_trader_strategy import ProTraderStrategy
from strategies.risk_manager import RiskManager

# Custom risk manager
risk_manager = RiskManager(
    stop_loss_pct=4.0,
    take_profit_pct=12.0,
    min_risk_reward=2.0
)

# Custom strategy
strategy = ProTraderStrategy(risk_manager=risk_manager)
strategy.set_thresholds(strong_buy=85.0, weak_buy=70.0)

# Use in backtest
engine = BacktestEngine(initial_capital=100_000_000)
engine.strategy = strategy  # Override default
```

---

## 📊 Analysis Examples

### 1. Winning vs Losing Trades

```python
import pandas as pd

# Load trades
df = pd.read_csv('backtest_trades.csv')

# Separate wins and losses
wins = df[df['profit_loss_pct'] > 0]
losses = df[df['profit_loss_pct'] <= 0]

# Compare
print(f"Wins: Avg confidence = {wins['confidence'].mean():.1f}%")
print(f"Losses: Avg confidence = {losses['confidence'].mean():.1f}%")

print(f"Wins: Avg holding = {wins['holding_days'].mean():.1f} days")
print(f"Losses: Avg holding = {losses['holding_days'].mean():.1f} days")
```

### 2. Per-Symbol Performance

```python
# Group by symbol
by_symbol = df.groupby('symbol').agg({
    'profit_loss_pct': ['count', 'mean', lambda x: (x > 0).sum() / len(x) * 100]
})

print(by_symbol)
```

### 3. Monthly Performance

```python
df['month'] = pd.to_datetime(df['entry_date']).dt.to_period('M')

monthly = df.groupby('month').agg({
    'profit_loss_pct': ['count', 'mean', 'sum']
})

print(monthly)
```

---

## ⚠️ Important Notes

### Limitations

1. **Slippage Not Modeled:** Assumes exact entry/exit at signal price
2. **Commissions Not Included:** No trading fees
3. **Liquidity Not Considered:** Assumes can always buy/sell
4. **No News Events:** Doesn't account for macro factors
5. **Look-Ahead Bias:** Ensure indicators don't use future data

### Best Practices

1. **Use Enough Data:** Minimum 1 year, preferably 2-3 years
2. **Multiple Symbols:** Test on 10+ symbols for diversity
3. **Walk-Forward Testing:** Test on different time periods
4. **Parameter Sensitivity:** Test with different thresholds
5. **Compare to Benchmark:** Compare to buy-and-hold VN-Index

---

## 🚀 Next Steps

After collecting 50-100 trades:

1. **Analyze Patterns**
   ```bash
   # Review trades
   cat backtest_trades.csv
   
   # Identify winning patterns
   # - Which indicators work best?
   # - Optimal holding period?
   # - Best entry timing?
   ```

2. **Validate Indicators**
   ```sql
   -- Check indicator effectiveness
   SELECT * FROM indicator_performance;
   ```

3. **Optimize Thresholds**
   ```python
   # Test different confidence thresholds
   for min_conf in [50, 60, 70, 80]:
       # Run backtest
       # Compare results
   ```

4. **Proceed to Paper Trading**
   ```bash
   # Start bot in alert-only mode
   python3 bot/main.py --mode scheduled --time 15:30
   ```

---

## 🐛 Troubleshooting

### Issue: "No data fetched"

```bash
# Check internet connection
ping google.com

# Check vnstock installation
pip show vnstock

# Try manual fetch
python3 -c "from vnstock import stock_historical_data; print(stock_historical_data('VNM', '2024-01-01', '2024-12-31'))"
```

### Issue: "Not enough trades"

Solutions:
1. Extend date range (2023-2025)
2. Add more symbols (20+ symbols)
3. Lower min_confidence (50% instead of 60%)

### Issue: "Win rate too high (>80%)"

Possible causes:
1. Look-ahead bias (indicators using future data)
2. Overfitting (strategy too specific)
3. Unrealistic assumptions (no slippage/fees)

Review indicator calculations!

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-03  
**Dependencies:** pandas, numpy, vnstock
