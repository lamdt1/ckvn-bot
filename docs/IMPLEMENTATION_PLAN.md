# 📋 Implementation Plan: Hybrid Strategy + Learning System

## 🎯 Objectives

1. ✅ **Clean Data Collection:** 50-100 backtest trades
2. ✅ **Telegram Alerts:** 100% market scan + manual review
3. ✅ **Conservative Mode:** Strict stop-loss, no auto-trade
4. ✅ **Raspberry Pi Optimization:** Lightweight DB operations

---

## 📅 Timeline: 3-4 Weeks

### **Week 1: Backtesting & Data Collection** ✅

**Goal:** Collect 50-100 simulated trades to validate strategy logic

**Tasks:**
- [x] Create backtesting framework
- [x] Implement trade simulation engine
- [x] Add performance tracking
- [x] Create backtest runner script
- [ ] Run backtest on 1-2 years of historical data
- [ ] Validate indicator logic (RSI, EMA, MACD)
- [ ] Export trades to CSV for analysis

**Deliverables:**
- `backtesting/__init__.py` - Backtest engine
- `backtesting/run_backtest.py` - Runner script
- `backtest_trades.csv` - Clean training data
- Database with 50-100 simulated trades

**Commands:**
```bash
# Install dependencies
pip install pandas numpy vnstock

# Run backtest
python3 backtesting/run_backtest.py

# Analyze results
sqlite3 database/trading.db
SELECT * FROM signal_performance;
```

---

### **Week 2: Telegram Alerts & Manual Review** 🔄

**Goal:** Bot scans 100% market, sends alerts, manual review before trading

**Tasks:**
- [x] Create Telegram notification module
- [x] Implement signal alert formatting
- [x] Add position close alerts
- [x] Add daily summary reports
- [ ] Integrate with main bot
- [ ] Test Telegram bot setup
- [ ] Create alert templates
- [ ] Test notification flow

**Deliverables:**
- `bot/notification.py` - Telegram notifier
- Telegram bot configured
- Alert templates tested

**Setup:**
```bash
# 1. Create Telegram bot
# Talk to @BotFather, send /newbot

# 2. Get chat ID
# Talk to @userinfobot

# 3. Configure .env
BOT_TELEGRAM_ENABLED=true
BOT_TELEGRAM_TOKEN=your_token_here
BOT_TELEGRAM_CHAT_ID=your_chat_id_here

# 4. Test notification
python3 bot/notification.py
```

---

### **Week 3: Performance-Based Learning** 🔄

**Goal:** Bot learns from trading history, adjusts strategy

**Tasks:**
- [ ] Create `SymbolPerformanceFilter` class
- [ ] Implement win rate tracking per symbol
- [ ] Add confidence adjustment based on history
- [ ] Create cooldown mechanism for poor performers
- [ ] Integrate with signal generator
- [ ] Test with backtest data
- [ ] Validate filtering logic

**Deliverables:**
- `strategies/performance_filter.py` - Performance-based filtering
- `strategies/hybrid_strategy.py` - Hybrid strategy (Pro Trader + Learning)
- Updated signal generator with learning

**Implementation:**
```python
# strategies/performance_filter.py
class SymbolPerformanceFilter:
    def get_symbol_stats(self, symbol):
        # Query from signal_performance view
        pass
    
    def should_skip_symbol(self, symbol):
        # Skip if win rate < 40% (after min 5 trades)
        pass
    
    def adjust_confidence(self, symbol, base_confidence):
        # Boost/reduce based on history
        pass

# strategies/hybrid_strategy.py
class HybridStrategy(ProTraderStrategy):
    def generate_signal(self, ...):
        # 1. Check performance filter
        # 2. Generate base signal
        # 3. Adjust confidence
        # 4. Return adjusted signal
        pass
```

---

### **Week 4: Raspberry Pi Optimization** 🔄

**Goal:** Optimize for Pi 3+ (limited RAM, SD card storage)

**Tasks:**
- [ ] Optimize database queries (use indexes)
- [ ] Implement data retention policy (keep last 6 months)
- [ ] Add database vacuum/cleanup script
- [ ] Optimize memory usage (process symbols in batches)
- [ ] Test on Raspberry Pi
- [ ] Monitor resource usage
- [ ] Add error recovery (network disconnects)

**Optimizations:**

```python
# 1. Database Indexes
CREATE INDEX idx_signals_symbol ON signals(symbol);
CREATE INDEX idx_signals_timestamp ON signals(timestamp);
CREATE INDEX idx_prices_symbol_time ON stock_prices(symbol, timestamp);

# 2. Data Retention
DELETE FROM stock_prices 
WHERE timestamp < unixepoch('now', '-6 months');

# 3. Batch Processing
for batch in chunks(symbols, batch_size=5):
    process_batch(batch)
    time.sleep(1)  # Avoid overload

# 4. Memory Management
import gc
gc.collect()  # Force garbage collection after heavy operations
```

**Raspberry Pi Setup:**
```bash
# 1. Install on Pi
sudo apt-get update
sudo apt-get install python3-pip sqlite3

# 2. Install dependencies
pip3 install pandas numpy vnstock python-telegram-bot schedule

# 3. Configure for low memory
export PYTHONOPTIMIZE=1  # Enable optimizations
export MALLOC_TRIM_THRESHOLD_=100000  # Reduce memory fragmentation

# 4. Run bot
python3 bot/main.py --mode scheduled --time 15:30

# 5. Monitor resources
htop  # Check CPU/RAM usage
df -h  # Check disk space
```

---

## 🔧 Configuration

### **Conservative Mode Settings**

```env
# .env configuration for conservative mode

# Risk Management (Strict)
BOT_STOP_LOSS_PCT=5.0          # Strict 5% stop-loss
BOT_TAKE_PROFIT_PCT=10.0       # Conservative 10% target
BOT_MIN_RR=2.0                 # Min 2:1 risk/reward
BOT_MAX_POSITION_SIZE=5.0      # Max 5% per position
BOT_MAX_RISK_PER_TRADE=1.0     # Max 1% risk per trade

# Signal Filtering (Conservative)
BOT_MIN_CONFIDENCE=70.0        # Only high confidence (70%+)
BOT_MAX_POSITIONS=3            # Max 3 open positions

# Auto-Trading (DISABLED)
BOT_AUTO_TRADING=false         # Manual review required

# Notifications (ENABLED)
BOT_TELEGRAM_ENABLED=true
BOT_TELEGRAM_TOKEN=your_token
BOT_TELEGRAM_CHAT_ID=your_chat_id

# Performance Learning
BOT_MIN_TRADES_FOR_FILTER=5    # Min trades before filtering
BOT_MIN_WIN_RATE=40.0          # Skip if win rate < 40%
BOT_COOLDOWN_DAYS=7            # Cooldown after 3 losses
```

---

## 📊 Performance Tracking

### **Metrics to Monitor**

```sql
-- 1. Overall Performance
SELECT 
    COUNT(*) as total_trades,
    SUM(CASE WHEN profit_loss_pct > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate,
    AVG(profit_loss_pct) as avg_return,
    MAX(profit_loss_pct) as max_win,
    MIN(profit_loss_pct) as max_loss
FROM signals
WHERE is_closed = 1;

-- 2. Per-Symbol Performance
SELECT * FROM signal_performance
ORDER BY win_rate DESC;

-- 3. Recent Performance (Last 30 days)
SELECT 
    symbol,
    COUNT(*) as trades,
    AVG(profit_loss_pct) as avg_return
FROM signals
WHERE is_closed = 1
AND close_timestamp > unixepoch('now', '-30 days')
GROUP BY symbol
ORDER BY avg_return DESC;

-- 4. Indicator Effectiveness
SELECT * FROM indicator_performance
ORDER BY avg_profit_pct DESC;
```

---

## 🚀 Deployment Workflow

### **Daily Workflow**

```
15:00 - Market closes
15:30 - Bot runs (scheduled)
  ├─ Fetch latest data (vnstock)
  ├─ Update open positions
  ├─ Check stop-loss / take-profit
  ├─ Generate new signals
  └─ Send Telegram alerts

15:35 - Manual review
  ├─ Check Telegram alerts
  ├─ Review news/macro factors
  ├─ Decide: Execute or Skip
  └─ Place orders manually (if approved)

16:00 - Update database
  └─ Mark signals as executed (if traded)

Daily Summary
  └─ Bot sends daily report via Telegram
```

---

## ✅ Validation Checklist

### **Before Live Trading**

- [ ] Backtest shows 50-100 trades
- [ ] Win rate 45-65% (reasonable range)
- [ ] Average R/R ratio >= 1.5
- [ ] Max drawdown < 20%
- [ ] Telegram alerts working
- [ ] Stop-loss triggers correctly
- [ ] Database optimized for Pi
- [ ] Error recovery tested
- [ ] Manual review process defined
- [ ] Risk limits configured

---

## 🎯 Success Criteria

### **Week 1 Success:**
- ✅ 50-100 backtest trades collected
- ✅ Indicator logic validated
- ✅ Win rate 45-65%
- ✅ Clean data exported to CSV

### **Week 2 Success:**
- ✅ Telegram bot configured
- ✅ Alerts sent successfully
- ✅ Manual review workflow tested
- ✅ Daily summaries working

### **Week 3 Success:**
- ✅ Performance filter working
- ✅ Confidence adjustment validated
- ✅ Poor performers filtered out
- ✅ Win rate improved by 5-10%

### **Week 4 Success:**
- ✅ Bot runs smoothly on Pi 3+
- ✅ Memory usage < 500MB
- ✅ Database size < 100MB
- ✅ Network errors handled gracefully
- ✅ Ready for paper trading

---

## 📚 Documentation

### **User Guides**
- `backtesting/README.md` - Backtesting guide
- `bot/notification.md` - Telegram setup guide
- `strategies/hybrid_strategy.md` - Learning system guide
- `docs/raspberry_pi_setup.md` - Pi deployment guide

### **Developer Guides**
- `docs/database_optimization.md` - DB optimization
- `docs/performance_tuning.md` - Performance tuning
- `docs/error_handling.md` - Error recovery

---

## 🔄 Next Steps After Week 4

1. **Paper Trading (1 month)**
   - Run bot with real data
   - No real money
   - Track all signals
   - Validate performance

2. **Performance Analysis**
   - Compare backtest vs paper trading
   - Identify discrepancies
   - Adjust thresholds

3. **Live Trading (Small Capital)**
   - Start with 10M VND (10% of capital)
   - Max 1-2 positions
   - Monitor closely

4. **Scale Up**
   - Gradually increase capital
   - Add more symbols
   - Optimize parameters

---

**Status:** Week 1 in progress (Backtesting framework ready)  
**Next:** Run backtest to collect 50-100 trades  
**Timeline:** 3-4 weeks to production-ready system
