# Trading Database - Pro Trader Strategy

## 📋 Tổng quan

Database SQLite được thiết kế để lưu trữ và phân tích dữ liệu giao dịch theo chiến lược **Pro Trader Rule-Based Decision Tree**.

### Kiến trúc

```
┌─────────────────┐
│  stock_prices   │  ← Dữ liệu giá OHLCV (1D + 4H)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   indicators    │  ← MA, EMA, RSI, MACD, Bollinger, Volume
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     signals     │  ← Tín hiệu MUA/BÁN + Risk Management
└────────┬────────┘
         │
         ├──────────────────┐
         ▼                  ▼
┌──────────────────┐  ┌──────────────────┐
│signal_performance│  │ portfolio_state  │
└──────────────────┘  └──────────────────┘
```

---

## 🚀 Quick Start

### 1. Khởi tạo Database

```python
from database.db_manager import initialize_database

# Tạo database và chạy migration
db = initialize_database()
```

### 2. Insert Dữ liệu Giá

```python
# Insert giá 1D (Daily)
db.insert_price_data(
    symbol="VNM",
    timeframe="1D",
    timestamp=1738540800,  # Unix timestamp
    open_price=85000,
    high=86500,
    low=84500,
    close=86000,
    volume=2500000
)

# Insert giá 4H (4-Hour)
db.insert_price_data(
    symbol="VNM",
    timeframe="4H",
    timestamp=1738540800,
    open_price=85000,
    high=85800,
    low=84800,
    close=85500,
    volume=600000
)
```

### 3. Insert Indicators

```python
indicators = {
    # Trend (Layer 1)
    'ma_200': 82000,
    'ema_20': 84500,
    'trend_direction': 'UP',
    'trend_strength': 75.5,
    
    # Momentum (Layer 2)
    'rsi_14': 55.3,
    'rsi_signal': 'NEUTRAL',
    'macd_line': 120.5,
    'macd_signal': 100.2,
    'macd_histogram': 20.3,
    'macd_trend': 'BULLISH',
    
    # Volatility (Layer 4)
    'bb_upper': 88000,
    'bb_middle': 85000,
    'bb_lower': 82000,
    'bb_width': 6000,
    'bb_position': 0.6,
    
    # Volume (Layer 3)
    'volume_ma_20': 2000000,
    'volume_ratio': 1.25,
    'volume_signal': 'HIGH',
    
    # Support/Resistance
    'support_level': 83000,
    'resistance_level': 87000,
    'distance_to_support_pct': 3.6,
    'distance_to_resistance_pct': 1.2
}

db.insert_indicators(
    symbol="VNM",
    timeframe="1D",
    timestamp=1738540800,
    indicators=indicators
)
```

### 4. Tạo Signal

```python
# Reasoning từ Decision Tree
reasoning = {
    'trend_direction': 'UP',
    'ma_200_vs_price': 'ABOVE',
    'ema_20_vs_price': 'ABOVE',
    'rsi_signal': 'NEUTRAL',
    'rsi_value': 55.3,
    'macd_trend': 'BULLISH',
    'volume_signal': 'HIGH',
    'bb_position': 0.6
}

signal_id = db.create_signal(
    symbol="VNM",
    timeframe="1D",
    timestamp=1738540800,
    signal_type="STRONG_BUY",
    price=86000,
    reasoning=reasoning,
    confidence_score=85,
    strategy_name="Pro Trader - Trend Following",
    suggested_stop_loss=81700,  # 5% stop loss
    suggested_take_profit=94600,  # 10% take profit
    position_size_pct=5.0,
    risk_reward_ratio=2.0
)
```

### 5. Execute Signal

```python
# Khi thực hiện lệnh mua
db.execute_signal(
    signal_id=signal_id,
    execution_price=86100  # Giá thực tế mua
)
```

### 6. Close Position

```python
# Khi đóng vị thế
db.close_signal(
    signal_id=signal_id,
    close_price=92000,
    close_reason="TAKE_PROFIT"  # hoặc 'STOP_LOSS', 'MANUAL', 'TIMEOUT'
)
```

---

## 📊 Views - Phân tích Hiệu suất

### 1. Strategy Performance Summary

```python
# Tổng hợp hiệu suất theo chiến lược
performance = db.get_strategy_performance()

for strat in performance:
    print(f"{strat['strategy_name']}: Win Rate {strat['win_rate_pct']}%")
```

**SQL trực tiếp:**
```sql
SELECT * FROM v_strategy_performance
ORDER BY win_rate_pct DESC, total_pnl_pct DESC;
```

**Output:**
- `strategy_name`: Tên chiến lược
- `signal_type`: Loại tín hiệu (STRONG_BUY, WEAK_BUY, etc.)
- `total_signals`: Tổng số tín hiệu
- `closed_positions`: Số vị thế đã đóng
- `win_rate_pct`: Tỷ lệ thắng (%)
- `avg_pnl_pct`: Lãi/lỗ trung bình (%)
- `total_pnl_pct`: Tổng lãi/lỗ (%)
- `avg_max_drawdown_pct`: Drawdown trung bình
- `avg_holding_days`: Số ngày nắm giữ trung bình

---

### 2. Indicator Combination Performance

```python
# Phân tích tổ hợp chỉ số nào hiệu quả nhất
combinations = db.get_indicator_combination_performance(min_trades=5)

for combo in combinations:
    print(f"Trend: {combo['trend']} | RSI: {combo['rsi_signal']} | "
          f"MACD: {combo['macd_trend']} | Volume: {combo['volume_signal']}")
    print(f"  Win Rate: {combo['win_rate_pct']}%")
```

**SQL trực tiếp:**
```sql
SELECT * FROM v_indicator_combination_performance
WHERE closed_positions >= 5
ORDER BY win_rate_pct DESC;
```

**Use Case:**
- Tìm tổ hợp chỉ số có win rate cao nhất
- Loại bỏ tổ hợp không hiệu quả
- Tối ưu hóa Decision Tree

---

### 3. Symbol Performance

```python
# Hiệu suất theo từng mã cổ phiếu
symbols = db.get_symbol_performance()

for sym in symbols:
    print(f"{sym['symbol']}: {sym['win_rate_pct']}% win rate, "
          f"{sym['total_pnl_pct']}% total P&L")
```

**SQL trực tiếp:**
```sql
SELECT * FROM v_symbol_performance
ORDER BY total_pnl_pct DESC;
```

---

### 4. Time-Based Performance

```sql
-- Hiệu suất theo tháng
SELECT * FROM v_time_performance
ORDER BY month DESC;
```

**Use Case:**
- Phát hiện tháng nào chiến lược hoạt động tốt/kém
- Điều chỉnh chiến lược theo mùa vụ

---

### 5. Risk-Reward Analysis

```sql
-- Phân tích theo tỷ lệ Risk/Reward
SELECT * FROM v_risk_reward_analysis
ORDER BY avg_pnl_pct DESC;
```

**Use Case:**
- Kiểm tra xem tín hiệu có R:R cao có thực sự tốt hơn không
- Tối ưu hóa stop-loss và take-profit levels

---

### 6. Open Positions Dashboard

```python
# Xem tất cả vị thế đang mở
positions = db.get_open_positions()

for pos in positions:
    print(f"{pos['symbol']}: {pos['current_pnl_pct']:+.2f}% | "
          f"Status: {pos['position_status']}")
```

**SQL trực tiếp:**
```sql
SELECT * FROM v_open_positions
ORDER BY current_pnl_pct DESC;
```

**Output:**
- `position_status`: 'ACTIVE', 'STOP_LOSS_HIT', 'TAKE_PROFIT_HIT'
- `current_pnl_pct`: Lãi/lỗ hiện tại (%)
- `days_held`: Số ngày đã nắm giữ

---

## 🔍 Useful Queries

### Tìm chiến lược tốt nhất

```sql
SELECT 
    strategy_name,
    signal_type,
    win_rate_pct,
    avg_pnl_pct,
    total_signals
FROM v_strategy_performance
WHERE closed_positions >= 10  -- Ít nhất 10 giao dịch
ORDER BY win_rate_pct DESC, avg_pnl_pct DESC
LIMIT 5;
```

### Tìm tổ hợp chỉ số tốt nhất

```sql
SELECT 
    json_extract(reasoning, '$.trend_direction') as trend,
    json_extract(reasoning, '$.rsi_signal') as rsi,
    json_extract(reasoning, '$.volume_signal') as volume,
    COUNT(*) as trades,
    ROUND(AVG(profit_loss_pct), 2) as avg_pnl,
    ROUND(
        100.0 * SUM(CASE WHEN profit_loss_pct > 0 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) as win_rate
FROM signals
WHERE is_closed = 1
GROUP BY trend, rsi, volume
HAVING trades >= 5
ORDER BY win_rate DESC, avg_pnl DESC;
```

### Phân tích theo giờ trong ngày (4H timeframe)

```sql
SELECT 
    strftime('%H', datetime(timestamp, 'unixepoch')) as hour,
    COUNT(*) as total_signals,
    ROUND(AVG(profit_loss_pct), 2) as avg_pnl,
    ROUND(
        100.0 * SUM(CASE WHEN profit_loss_pct > 0 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) as win_rate
FROM signals
WHERE timeframe = '4H' AND is_closed = 1
GROUP BY hour
ORDER BY win_rate DESC;
```

### Tìm tín hiệu có confidence cao nhưng kết quả kém

```sql
SELECT 
    symbol,
    signal_type,
    confidence_score,
    profit_loss_pct,
    reasoning
FROM signals
WHERE is_closed = 1
  AND confidence_score >= 80
  AND profit_loss_pct < 0
ORDER BY confidence_score DESC;
```

**Use Case:** Debug tại sao tín hiệu "tự tin" lại thua lỗ

---

### Phân tích Drawdown

```sql
SELECT 
    symbol,
    AVG(max_drawdown_pct) as avg_drawdown,
    MAX(max_drawdown_pct) as worst_drawdown,
    COUNT(*) as trades
FROM signals
WHERE is_closed = 1
GROUP BY symbol
ORDER BY worst_drawdown DESC;
```

---

### Tìm mã có win rate cao nhất với ít nhất 10 giao dịch

```sql
SELECT 
    symbol,
    COUNT(*) as total_trades,
    ROUND(
        100.0 * SUM(CASE WHEN profit_loss_pct > 0 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) as win_rate,
    ROUND(AVG(profit_loss_pct), 2) as avg_pnl,
    ROUND(SUM(profit_loss_pct), 2) as total_pnl
FROM signals
WHERE is_closed = 1
GROUP BY symbol
HAVING total_trades >= 10
ORDER BY win_rate DESC, total_pnl DESC;
```

---

## 🎯 Integration với Bot

### Workflow chuẩn

```python
from database.db_manager import TradingDatabase

db = TradingDatabase()
db.connect()

# 1. Fetch giá mới từ API
# 2. Insert vào database
db.insert_price_data(...)

# 3. Tính toán indicators
# 4. Insert indicators
db.insert_indicators(...)

# 5. Chạy Decision Tree
# 6. Nếu có tín hiệu → Create signal
signal_id = db.create_signal(...)

# 7. Nếu execute → Update
db.execute_signal(signal_id, execution_price)

# 8. Theo dõi vị thế
positions = db.get_open_positions()

# 9. Khi đóng vị thế → Update
db.close_signal(signal_id, close_price, close_reason)

# 10. Phân tích định kỳ
performance = db.get_strategy_performance()
```

---

## 📁 File Structure

```
database/
├── migrations/
│   └── 001_create_trading_schema.sql  # Schema definition
├── db_manager.py                       # Database manager class
├── example_usage.py                    # Examples & tests
├── README.md                           # This file
└── trading.db                          # SQLite database (auto-created)
```

---

## 🔧 Maintenance

### Backup Database

```bash
# Backup
cp database/trading.db database/backups/trading_$(date +%Y%m%d).db

# Restore
cp database/backups/trading_20260203.db database/trading.db
```

### Vacuum Database (Optimize)

```python
db.conn.execute("VACUUM")
```

### Check Database Size

```bash
ls -lh database/trading.db
```

---

## 📈 Performance Tips

1. **Indexes đã được tạo sẵn** cho các query phổ biến
2. **Sử dụng Views** thay vì viết query phức tạp
3. **Batch insert** khi có nhiều dữ liệu:
   ```python
   db.conn.executemany(query, data_list)
   db.conn.commit()
   ```
4. **Cleanup dữ liệu cũ** định kỳ (nếu cần):
   ```sql
   DELETE FROM stock_prices 
   WHERE timestamp < strftime('%s', 'now', '-365 days');
   ```

---

## 🐛 Troubleshooting

### Database locked

```python
# Tăng timeout
db.conn.execute("PRAGMA busy_timeout = 5000")
```

### Foreign key constraint failed

```python
# Kiểm tra foreign key
db.conn.execute("PRAGMA foreign_keys = ON")
```

### View không cập nhật

```python
# Drop và recreate view
db.conn.execute("DROP VIEW IF EXISTS v_strategy_performance")
db.run_migration()  # Recreate
```

---

## 📞 Support

Nếu có vấn đề, kiểm tra:
1. File `example_usage.py` để xem cách sử dụng đúng
2. Logs trong console
3. SQLite browser để kiểm tra dữ liệu trực tiếp

---

**Version:** 1.0  
**Last Updated:** 2026-02-03  
**Database Schema Version:** 1
