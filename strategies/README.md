# Pro Trader Strategy Module

## 📋 Tổng quan

Module Decision Tree Engine cho chiến lược **Pro Trader Rule-Based Trading**.

### Kiến trúc

```
ProTraderStrategy (Concrete Implementation)
├─ DecisionTree (Abstract Base)
├─ RiskManager (Risk Management)
└─ Signal (Data Class)
```

---

## 🎯 Components

### 1. Signal (Data Class)
Represents a trading signal with complete metadata.

**Fields:**
- `symbol`, `timeframe`, `timestamp`, `price`
- `signal_type`: STRONG_BUY, WEAK_BUY, WATCH, NO_ACTION, SELL
- `confidence_score`: 0-100
- `reasoning`: Decision tree reasoning (JSON)
- `conditions_met`: List of passed conditions
- `stop_loss`, `take_profit`, `position_size_pct`, `risk_reward_ratio`

### 2. RiskManager
Calculates risk management parameters.

**Features:**
- Stop-loss calculation (fixed % or ATR-based)
- Take-profit calculation (fixed % or R/R based)
- Position sizing (confidence-adjusted)
- Signal validation (R/R ratio, stop-loss range)

**Default Parameters:**
- Stop-loss: 5%
- Take-profit: 10%
- Position size: 5% of capital
- Min R/R ratio: 1.5

### 3. DecisionTree (Abstract Base)
Base class for decision tree strategies.

**4-Layer Framework:**
1. `evaluate_trend()` - Layer 1: Trend filter
2. `evaluate_momentum()` - Layer 2: Momentum check
3. `evaluate_volume()` - Layer 3: Volume confirmation
4. `evaluate_entry()` - Layer 4: Entry timing

**Weights (configurable):**
- Trend: 30%
- Momentum: 30%
- Volume: 20%
- Entry: 20%

### 4. ProTraderStrategy (Implementation)
Concrete implementation of Pro Trader logic.

**Signal Thresholds:**
- STRONG_BUY: Confidence >= 80%
- WEAK_BUY: Confidence >= 60%
- WATCH: Confidence >= 40%
- NO_ACTION: Confidence < 40%

---

## 🚀 Quick Start

### Basic Usage

```python
from strategies.pro_trader_strategy import ProTraderStrategy

# Initialize strategy
strategy = ProTraderStrategy()

# Prepare indicators (from Indicator Calculator)
indicators = {
    'trend_direction': 'UP',
    'ma_200': 84000,
    'ema_20': 85000,
    'rsi_14': 55.0,
    'rsi_signal': 'NEUTRAL',
    'macd_trend': 'BULLISH',
    'volume_signal': 'HIGH',
    'volume_ratio': 1.8,
    'bb_position': 0.25,
    'bb_position_label': 'NEAR_LOWER',
    # ... other indicators
}

# Generate signal
signal = strategy.generate_signal(
    symbol='VNM',
    timeframe='1D',
    timestamp=current_timestamp,
    price=86000,
    indicators=indicators,
    total_capital=100_000_000
)

# Check result
print(f"Signal: {signal.signal_type.value}")
print(f"Confidence: {signal.confidence_score}%")
print(f"Stop-Loss: {signal.stop_loss:,.0f}")
print(f"Take-Profit: {signal.take_profit:,.0f}")
```

### Custom Configuration

```python
from strategies.pro_trader_strategy import ProTraderStrategy
from strategies.risk_manager import RiskManager

# Custom risk manager
risk_manager = RiskManager(
    stop_loss_pct=4.0,
    take_profit_pct=12.0,
    min_risk_reward=2.0,
    use_atr_stop_loss=True  # Use ATR instead of fixed %
)

# Initialize with custom risk manager
strategy = ProTraderStrategy(risk_manager=risk_manager)

# Set custom thresholds
strategy.set_thresholds(
    strong_buy=85.0,  # More conservative
    weak_buy=70.0,
    watch=50.0
)

# Set custom weights
strategy.set_weights(
    trend=0.40,      # Increase trend importance
    momentum=0.30,
    volume=0.15,
    entry=0.15
)
```

---

## 🔬 Decision Logic

### Layer 1: Trend Evaluation

**Conditions:**
- Trend direction is UP
- Price above MA 200
- Price above EMA 20

**Scoring:**
- Strong uptrend: 100
- Weak uptrend: 60
- Sideways: 50
- Downtrend: 0

**Pass Criteria:** Trend direction == 'UP'

---

### Layer 2: Momentum Evaluation

**Conditions:**
- RSI not overbought (< 70)
- MACD trend is BULLISH

**Scoring:**
- RSI sweet spot (40-60) + MACD bullish: 100
- RSI neutral + MACD bullish: 80
- RSI oversold + MACD bullish: 60
- RSI overbought: 20
- MACD bearish: 0

**Pass Criteria:** MACD bullish AND RSI not overbought

---

### Layer 3: Volume Evaluation

**Conditions:**
- Volume signal is HIGH or NORMAL
- Volume ratio >= 1.0

**Scoring:**
- Volume HIGH (> 1.5x avg): 100
- Volume NORMAL (0.7-1.5x avg): 70
- Volume LOW (< 0.7x avg): 30

**Pass Criteria:** Volume signal != 'LOW'

---

### Layer 4: Entry Timing Evaluation

**Conditions:**
- BB position < 0.5 (below middle band)
- Preferably near lower band (< 0.3)

**Scoring:**
- Near lower band (< 0.3): 100
- Below middle (0.3-0.5): 80
- Around middle (0.5-0.7): 50
- Above middle (0.7-0.9): 30
- Near upper band (> 0.9): 10

**Pass Criteria:** BB position < 0.5

---

## 📊 Confidence Calculation

```
Confidence = (Trend_Score × 0.30) + 
             (Momentum_Score × 0.30) + 
             (Volume_Score × 0.20) + 
             (Entry_Score × 0.20)
```

**Example:**
- Trend: 100 (strong uptrend)
- Momentum: 80 (RSI neutral, MACD bullish)
- Volume: 100 (high volume)
- Entry: 100 (near lower BB)

Confidence = (100×0.3) + (80×0.3) + (100×0.2) + (100×0.2) = **84%** → **STRONG_BUY**

---

## 🛡️ Risk Management

### Stop-Loss Calculation

**Method 1: Fixed Percentage** (default)
```
Stop-Loss = Price × (1 - stop_loss_pct/100)
```

**Method 2: ATR-Based**
```
Stop-Loss = Price - (ATR × atr_multiplier)
```

**Optimization:**
- Use support level if within 2-8% below price
- Ensure stop-loss is not too tight (< 1%) or too wide (> 15%)

### Take-Profit Calculation

**Method 1: Risk/Reward Based**
```
Risk = Price - Stop-Loss
Take-Profit = Price + (Risk × target_rr)
```

**Method 2: Fixed Percentage**
```
Take-Profit = Price × (1 + take_profit_pct/100)
```

**Optimization:**
- Use the more conservative (lower) target
- Use resistance level if within 5-15% above price

### Position Sizing

**Formula:**
```
Risk_Per_Share = Price - Stop-Loss
Max_Risk_Capital = Total_Capital × (max_risk_per_trade_pct/100)
Quantity = Max_Risk_Capital / Risk_Per_Share

# Adjust by confidence
Position_Size = Quantity × (Confidence/100)

# Cap at max position size
Final_Position = min(Position_Size, max_position_size_pct)
```

**Default:**
- Max risk per trade: 2% of capital
- Max position size: 10% of capital

---

## 🔗 Integration Examples

### Example 1: Complete Workflow

```python
from indicators.calculator import IndicatorCalculator
from strategies.pro_trader_strategy import ProTraderStrategy
from database.db_manager import TradingDatabase
import pandas as pd

# 1. Fetch price data
db = TradingDatabase()
db.connect()

prices = db.execute_query("""
    SELECT * FROM stock_prices 
    WHERE symbol = 'VNM' AND timeframe = '1D'
    ORDER BY timestamp DESC LIMIT 250
""")

df = pd.DataFrame([dict(p) for p in prices])

# 2. Calculate indicators
calculator = IndicatorCalculator()
indicators = calculator.calculate_for_signal(df)

# 3. Generate signal
strategy = ProTraderStrategy()
signal = strategy.generate_signal(
    symbol='VNM',
    timeframe='1D',
    timestamp=df['timestamp'].iloc[-1],
    price=df['close'].iloc[-1],
    indicators=indicators,
    total_capital=100_000_000
)

# 4. Save signal to database
if signal.is_buy_signal():
    signal_id = db.create_signal(
        symbol=signal.symbol,
        timeframe=signal.timeframe,
        timestamp=signal.timestamp,
        signal_type=signal.signal_type.value,
        price=signal.price,
        reasoning=signal.reasoning,
        **signal.to_dict()
    )
    
    print(f"✅ Signal saved: {signal.signal_type.value} at {signal.price:,.0f}")
```

### Example 2: Batch Processing

```python
symbols = ['VNM', 'VCB', 'HPG', 'VIC', 'VHM']
strategy = ProTraderStrategy()

for symbol in symbols:
    # Fetch data
    df = fetch_price_data(symbol, timeframe='1D', limit=250)
    
    # Calculate indicators
    indicators = calculator.calculate_for_signal(df)
    
    # Generate signal
    signal = strategy.generate_signal(
        symbol=symbol,
        timeframe='1D',
        timestamp=df['timestamp'].iloc[-1],
        price=df['close'].iloc[-1],
        indicators=indicators
    )
    
    # Process signal
    if signal.signal_type.value in ['STRONG_BUY', 'WEAK_BUY']:
        print(f"{symbol}: {signal.signal_type.value} ({signal.confidence_score}%)")
```

---

## 🧪 Testing

```bash
# Run test suite
python3 strategies/test_strategy.py
```

**Test Scenarios:**
1. STRONG_BUY (confidence >= 80%)
2. WEAK_BUY (confidence 60-80%)
3. NO_ACTION (downtrend)
4. Overbought rejection
5. Custom thresholds
6. Risk management

---

## 📁 File Structure

```
strategies/
├── __init__.py                  # Package exports
├── signal.py                    # Signal data class
├── risk_manager.py              # Risk management
├── decision_tree.py             # Abstract base class
├── pro_trader_strategy.py       # Pro Trader implementation
├── test_strategy.py             # Test suite
└── README.md                    # This file
```

---

## 🎯 Next Steps

1. ✅ **Phase 3: Decision Tree Engine** - HOÀN THÀNH
2. 🔲 **Phase 4: Main Bot Integration**
   - Integrate with price data source
   - Real-time signal generation
   - Position monitoring
   - Notification system

---

## 🔧 Customization

### Add New Strategy

```python
from strategies.decision_tree import DecisionTree
from strategies.signal import SignalType

class MyCustomStrategy(DecisionTree):
    def __init__(self):
        super().__init__(strategy_name="My Custom Strategy")
    
    def evaluate_trend(self, indicators):
        # Your custom trend logic
        return {'score': 100, 'passed': True, 'reason': 'Custom logic'}
    
    # Implement other methods...
```

### Modify Scoring Logic

```python
# In ProTraderStrategy
def evaluate_momentum(self, indicators):
    # Modify scoring logic
    if indicators['rsi_14'] < 40:
        score = 90  # More aggressive on oversold
    # ...
```

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-03  
**Dependencies:** None (pure Python)
