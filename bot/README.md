# Trading Bot - Main Integration

## 📋 Tổng quan

Module chính để chạy bot giao dịch tự động, kết nối tất cả components:
- Data Fetcher (vnstock/SSI)
- Indicator Calculator
- Pro Trader Strategy
- Position Manager
- Database
- Notifications (Telegram/Email)

---

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
cd /Volumes/Data/projects/ckbot
pip install -r bot/requirements.txt

# Or with virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r bot/requirements.txt
```

### 2. Configuration

```bash
# Create .env file
python3 bot/config.py

# Edit .env file
nano .env
```

**Minimum configuration:**
```env
BOT_DATA_SOURCE=vnstock
BOT_SYMBOLS=VNM,VCB,HPG,VIC,VHM
BOT_CAPITAL=100000000
BOT_MIN_CONFIDENCE=60.0
```

### 3. Run Bot

```bash
# Run once (manual)
python3 bot/main.py --mode once

# Run continuously (every 60 minutes)
python3 bot/main.py --mode continuous --interval 60

# Run scheduled (daily at 15:30)
python3 bot/main.py --mode scheduled --time 15:30
```

---

## 📁 File Structure

```
bot/
├── __init__.py              # Package exports
├── config.py                # Configuration management
├── data_fetcher.py          # Fetch price data (vnstock/SSI)
├── signal_generator.py      # Generate trading signals
├── position_manager.py      # Manage open positions
├── notification.py          # Send alerts (Telegram/Email)
├── main.py                  # Main bot orchestrator
├── requirements.txt         # Dependencies
└── README.md               # This file
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BOT_DATA_SOURCE` | `vnstock` | Data source ('vnstock', 'ssi') |
| `BOT_SYMBOLS` | Top 10 VN30 | Comma-separated symbols |
| `BOT_CAPITAL` | 100000000 | Total capital (VND) |
| `BOT_MAX_POSITIONS` | 5 | Max open positions |
| `BOT_MIN_CONFIDENCE` | 60.0 | Min confidence score |
| `BOT_RUN_TIME` | 15:30 | Daily run time |
| `BOT_INTERVAL` | 60 | Interval (minutes) |
| `BOT_STOP_LOSS_PCT` | 5.0 | Stop-loss % |
| `BOT_TAKE_PROFIT_PCT` | 10.0 | Take-profit % |
| `BOT_MIN_RR` | 1.5 | Min risk/reward ratio |

### Telegram Notifications (Optional)

```env
BOT_TELEGRAM_ENABLED=true
BOT_TELEGRAM_TOKEN=your_bot_token
BOT_TELEGRAM_CHAT_ID=your_chat_id
```

**How to get Telegram token:**
1. Talk to [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Follow instructions
4. Copy token

**How to get chat ID:**
1. Talk to [@userinfobot](https://t.me/userinfobot)
2. Copy your ID

---

## 🔄 Bot Workflow

```
1. FETCH DATA
   ├─ Fetch OHLCV for all symbols
   └─ Store in database

2. UPDATE POSITIONS
   ├─ Load open positions
   ├─ Update with current prices
   ├─ Check stop-loss / take-profit
   └─ Close triggered positions

3. GENERATE SIGNALS
   ├─ Calculate indicators
   ├─ Run Pro Trader strategy
   ├─ Filter by confidence
   └─ Save to database

4. SEND NOTIFICATIONS
   ├─ Telegram alerts
   └─ Email reports

5. WAIT
   └─ Until next scheduled run
```

---

## 📊 Components

### 1. Data Fetcher

Fetches stock price data from multiple sources.

**Supported sources:**
- **vnstock** (recommended): Free, easy to use
- **SSI API**: Real-time, requires account
- **CSV**: For backtesting

**Usage:**
```python
from bot.data_fetcher import DataFetcher

fetcher = DataFetcher(source='vnstock')
df = fetcher.fetch_historical_data('VNM', limit=250)
```

---

### 2. Signal Generator

Orchestrates indicator calculation and signal generation.

**Features:**
- Batch processing (multiple symbols)
- Signal filtering (by confidence, R/R)
- Signal ranking
- Database integration

**Usage:**
```python
from bot.signal_generator import SignalGenerator

generator = SignalGenerator(
    total_capital=100_000_000,
    min_confidence=60.0
)

signals = generator.generate_signals_batch(data_dict)
top_signals = generator.get_top_signals(signals, top_n=5)
```

---

### 3. Position Manager

Manages open trading positions.

**Features:**
- Track open positions
- Update prices and P&L
- Check stop-loss / take-profit
- Close positions automatically
- Generate position reports

**Usage:**
```python
from bot.position_manager import PositionManager

manager = PositionManager()
manager.load_open_positions()
manager.update_positions(current_prices)

# Check triggers
to_close = manager.check_positions()
for item in to_close:
    manager.close_position(item['position'].symbol, ...)
```

---

### 4. Main Bot

Orchestrates all components.

**Run modes:**
- **Once**: Run manually (for testing)
- **Continuous**: Run every N minutes
- **Scheduled**: Run daily at specific time

**Usage:**
```python
from bot.main import TradingBot

bot = TradingBot()

# Run once
bot.run_once()

# Run continuously (every 60 minutes)
bot.run_continuous(interval_minutes=60)

# Run scheduled (daily at 15:30)
bot.run_scheduled(run_time='15:30')
```

---

## 🧪 Testing

### Test Individual Components

```bash
# Test configuration
python3 bot/config.py

# Test data fetcher
python3 bot/data_fetcher.py

# Test signal generator
python3 bot/signal_generator.py

# Test position manager
python3 bot/position_manager.py
```

### Test Full Bot

```bash
# Dry run (no database writes)
python3 bot/main.py --mode once
```

---

## 📈 Usage Examples

### Example 1: Manual Run

```bash
# Run bot once
python3 bot/main.py --mode once
```

**Output:**
```
🤖 TRADING BOT RUN - 2026-02-03 15:30:00
================================================================================

📊 Fetching data for 10 symbols...
✅ Successfully fetched 10/10 symbols

💼 Updating open positions...
  No open positions

🎯 Generating signals...
✅ VNM: STRONG_BUY (confidence: 85.5%)
✅ VCB: WEAK_BUY (confidence: 65.2%)
...

📊 SIGNAL SUMMARY (5 signals)
================================================================================
STRONG_BUY: 2 signals
WEAK_BUY: 3 signals

🏆 TOP SIGNALS (by confidence):
--------------------------------------------------------------------------------
Rank   Symbol   Signal          Conf    Price        R/R    Pos%
--------------------------------------------------------------------------------
1      VNM      STRONG_BUY      85.5    86,000       2.00   5.0
2      VCB      STRONG_BUY      82.3    92,000       2.10   4.8
...

✅ Bot run completed successfully
```

---

### Example 2: Continuous Mode

```bash
# Run every 60 minutes
python3 bot/main.py --mode continuous --interval 60
```

---

### Example 3: Scheduled Mode

```bash
# Run daily at 15:30 (after market close)
python3 bot/main.py --mode scheduled --time 15:30
```

**Run as background service:**
```bash
# Using nohup
nohup python3 bot/main.py --mode scheduled --time 15:30 > bot.log 2>&1 &

# Or using screen
screen -S trading-bot
python3 bot/main.py --mode scheduled --time 15:30
# Press Ctrl+A, then D to detach
```

---

## 🔔 Notifications

### Telegram Setup

1. Create bot with @BotFather
2. Get bot token
3. Get your chat ID from @userinfobot
4. Update .env:

```env
BOT_TELEGRAM_ENABLED=true
BOT_TELEGRAM_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
BOT_TELEGRAM_CHAT_ID=123456789
```

### Email Setup

```env
BOT_EMAIL_ENABLED=true
BOT_EMAIL_FROM=your_email@gmail.com
BOT_EMAIL_TO=recipient@gmail.com
BOT_EMAIL_PASSWORD=your_app_password
```

**Note:** For Gmail, use [App Password](https://support.google.com/accounts/answer/185833)

---

## 🛡️ Safety Features

### 1. Position Limits
- Max open positions: 5 (configurable)
- Max position size: 10% of capital
- Max risk per trade: 2% of capital

### 2. Signal Filters
- Minimum confidence: 60%
- Minimum R/R ratio: 1.5
- Trend filter (no buy in downtrend)

### 3. Auto Stop-Loss/Take-Profit
- Automatic position closing
- Database tracking
- P&L calculation

---

## 🐛 Troubleshooting

### Issue: "vnstock not installed"

```bash
pip install vnstock
```

### Issue: "No data fetched"

Check:
1. Internet connection
2. Symbol names (must be valid VN stock codes)
3. vnstock version: `pip show vnstock`

### Issue: "Database not found"

```bash
# Initialize database
python3 database/db_manager.py
```

### Issue: "Configuration errors"

```bash
# Validate configuration
python3 bot/config.py
```

---

## 📊 Performance Monitoring

### View Signals

```bash
# Check database
sqlite3 database/trading.db

# Query signals
SELECT symbol, signal_type, confidence_score, price_at_signal 
FROM signals 
WHERE created_at > datetime('now', '-7 days')
ORDER BY confidence_score DESC;
```

### View Positions

```bash
# Open positions
SELECT * FROM signals WHERE is_executed = 1 AND is_closed = 0;

# Closed positions (last 30 days)
SELECT symbol, profit_loss_pct, holding_days 
FROM signals 
WHERE is_closed = 1 
AND close_timestamp > unixepoch('now', '-30 days');
```

---

## 🚀 Next Steps

1. **Test with real data**: Run bot in dry-run mode
2. **Backtest**: Test strategy on historical data
3. **Paper trading**: Track signals without real money
4. **Live trading**: Start with small capital
5. **Optimize**: Fine-tune parameters based on results

---

## ⚠️ Disclaimer

**This bot is for educational purposes only.**

- Not financial advice
- Past performance ≠ future results
- Always do your own research
- Start with paper trading
- Use at your own risk

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-03  
**Dependencies:** pandas, vnstock, schedule
