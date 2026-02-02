# Indicator Calculator Module

## 📋 Tổng quan

Module tính toán các chỉ số kỹ thuật cho chiến lược **Pro Trader Rule-Based Decision Tree**.

### Kiến trúc 4 Layers

```
Layer 1: TREND (Xu hướng)
├─ MA 200
├─ EMA 20
├─ Trend Direction
└─ Support/Resistance

Layer 2: MOMENTUM (Động lượng)
├─ RSI 14
└─ MACD (Line, Signal, Histogram)

Layer 3: VOLUME (Dòng tiền)
├─ Volume MA 20
├─ Volume Ratio
└─ Volume Spike Detection

Layer 4: VOLATILITY (Biến động - Điểm vào)
├─ Bollinger Bands (Upper, Middle, Lower)
├─ BB Width
└─ BB Position
```

---

## 🚀 Installation

### Option 1: Virtual Environment (Recommended)

```bash
# Tạo virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
# hoặc
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r indicators/requirements.txt
```

### Option 2: System-wide (với --user flag)

```bash
pip3 install --user pandas numpy matplotlib
```

### Option 3: Sử dụng pipx (nếu có)

```bash
brew install pipx
pipx install pandas numpy
```

---

## 📦 Dependencies

- **pandas** >= 2.0.0 - Data manipulation
- **numpy** >= 1.24.0 - Numerical calculations
- **matplotlib** >= 3.7.0 (optional) - Visualization

**Note:** Module này **KHÔNG** yêu cầu `pandas-ta` hay `TA-Lib`. Tất cả indicators được implement bằng pure pandas/numpy để dễ cài đặt và maintain.

---

## 🎯 Quick Start

### 1. Basic Usage

```python
from indicators.calculator import IndicatorCalculator
import pandas as pd

# Prepare OHLCV data
df = pd.DataFrame({
    'timestamp': [...],
    'open': [...],
    'high': [...],
    'low': [...],
    'close': [...],
    'volume': [...]
})

# Calculate all indicators
calculator = IndicatorCalculator()
indicators = calculator.calculate_for_signal(df)

print(f"Trend: {indicators['trend_direction']}")
print(f"RSI: {indicators['rsi_14']}")
print(f"MACD Trend: {indicators['macd_trend']}")
print(f"Volume Signal: {indicators['volume_signal']}")
```

### 2. Custom Parameters

```python
# Customize indicator parameters
calculator = IndicatorCalculator(
    ma_period=200,      # MA period
    ema_period=20,      # EMA period
    rsi_period=14,      # RSI period
    bb_period=20,       # Bollinger Bands period
    bb_std=2.0          # BB standard deviation
)

indicators = calculator.calculate_all(df, include_optional=True)
```

### 3. Integration với Database

```python
from database.db_manager import TradingDatabase
from indicators.calculator import IndicatorCalculator

db = TradingDatabase()
db.connect()

# Fetch price data
prices = db.execute_query("""
    SELECT * FROM stock_prices 
    WHERE symbol = 'VNM' AND timeframe = '1D'
    ORDER BY timestamp DESC LIMIT 250
""")

df = pd.DataFrame([dict(p) for p in prices])

# Calculate indicators
calculator = IndicatorCalculator()
indicators = calculator.calculate_for_signal(df)

# Save to database
db.insert_indicators(
    symbol='VNM',
    timeframe='1D',
    timestamp=df['timestamp'].iloc[-1],
    indicators=indicators
)
```

---

## 📚 Module Structure

```
indicators/
├── __init__.py                 # Package exports
├── requirements.txt            # Dependencies
├── calculator.py               # Main orchestrator
├── trend_indicators.py         # MA, EMA, Support/Resistance
├── momentum_indicators.py      # RSI, MACD
├── volatility_indicators.py    # Bollinger Bands, ATR
├── volume_indicators.py        # Volume analysis, OBV, VWAP
└── README.md                   # This file
```

---

## 🔬 Indicator Details

### Layer 1: Trend Indicators

**MA 200 (Simple Moving Average)**
- Xác định xu hướng dài hạn
- Giá > MA 200 = Uptrend
- Giá < MA 200 = Downtrend

**EMA 20 (Exponential Moving Average)**
- Xu hướng ngắn hạn, phản ứng nhanh hơn SMA
- Dùng để xác nhận trend và tìm điểm vào

**Trend Direction**
- `UP`: Giá trên cả MA 200 và EMA 20
- `DOWN`: Giá dưới cả MA 200 và EMA 20
- `SIDEWAYS`: Tín hiệu hỗn hợp

**Support/Resistance**
- Dynamic levels dựa trên recent high/low
- Distance to support/resistance (%)

---

### Layer 2: Momentum Indicators

**RSI 14 (Relative Strength Index)**
- Đo lường tốc độ và độ lớn của price changes
- `OVERSOLD`: RSI < 30 (có thể tăng)
- `OVERBOUGHT`: RSI > 70 (có thể giảm)
- `NEUTRAL`: 30 <= RSI <= 70

**MACD (Moving Average Convergence Divergence)**
- MACD Line: EMA(12) - EMA(26)
- Signal Line: EMA(9) of MACD Line
- Histogram: MACD Line - Signal Line
- `BULLISH`: Histogram > 0
- `BEARISH`: Histogram < 0

---

### Layer 3: Volume Indicators

**Volume MA 20**
- Average volume over 20 periods
- Baseline để so sánh volume hiện tại

**Volume Ratio**
- Current Volume / Volume MA
- Ratio > 1.5 = HIGH volume
- Ratio < 0.7 = LOW volume

**Volume Spike**
- Phát hiện volume bất thường (> 2x average)
- Xác nhận breakout hoặc reversal

**Optional: OBV, VWAP**
- On-Balance Volume: Cumulative volume direction
- VWAP: Volume-weighted average price

---

### Layer 4: Volatility Indicators

**Bollinger Bands**
- Upper Band: SMA(20) + 2 * STD
- Middle Band: SMA(20)
- Lower Band: SMA(20) - 2 * STD

**BB Width**
- (Upper - Lower) / Middle * 100
- Đo lường volatility

**BB Position**
- (Price - Lower) / (Upper - Lower)
- 0 = At lower band (oversold)
- 1 = At upper band (overbought)
- 0.5 = At middle

**Position Labels:**
- `NEAR_LOWER`: < 0.2 (good entry for long)
- `BELOW_MIDDLE`: 0.2 - 0.4
- `AROUND_MIDDLE`: 0.4 - 0.6
- `ABOVE_MIDDLE`: 0.6 - 0.8
- `NEAR_UPPER`: > 0.8 (overbought)

---

## 🧪 Testing

### Test Individual Modules

```bash
# Test trend indicators
python3 indicators/trend_indicators.py

# Test momentum indicators
python3 indicators/momentum_indicators.py

# Test volatility indicators
python3 indicators/volatility_indicators.py

# Test volume indicators
python3 indicators/volume_indicators.py
```

### Test Complete Calculator

```bash
python3 indicators/calculator.py
```

**Expected Output:**
```
======================================================================
INDICATOR CALCULATOR - COMPREHENSIVE TEST
======================================================================

TEST 1: Core Indicators (for Signal Generation)
======================================================================

📊 LAYER 1: TREND INDICATORS
  MA 200: 84,523
  EMA 20: 85,234
  Trend Direction: UP
  Trend Strength: 75.5
  Support: 83,000
  Resistance: 87,000

📈 LAYER 2: MOMENTUM INDICATORS
  RSI 14: 55.3
  RSI Signal: NEUTRAL
  MACD Line: 120.5
  MACD Signal: 100.2
  MACD Histogram: 20.3
  MACD Trend: BULLISH

...
```

---

## 🔗 Integration Examples

### Example 1: Real-time Signal Generation

```python
def process_new_candle(symbol, timeframe, candle_data):
    """Process new price candle and calculate indicators"""
    
    # Fetch historical data (need 250 candles for MA 200)
    df = fetch_historical_data(symbol, timeframe, limit=250)
    
    # Add new candle
    df = df.append(candle_data, ignore_index=True)
    
    # Calculate indicators
    calculator = IndicatorCalculator()
    indicators = calculator.calculate_for_signal(df)
    
    # Save to database
    db.insert_indicators(symbol, timeframe, candle_data['timestamp'], indicators)
    
    return indicators
```

### Example 2: Backtesting

```python
def backtest_strategy(symbol, start_date, end_date):
    """Backtest strategy on historical data"""
    
    # Fetch historical data
    df = fetch_historical_data(symbol, '1D', start_date, end_date)
    
    # Calculate indicators for all periods
    calculator = IndicatorCalculator()
    df_with_indicators = calculator.calculate_with_history(df, lookback=None)
    
    # Iterate and generate signals
    for i in range(200, len(df_with_indicators)):
        row = df_with_indicators.iloc[i]
        
        # Check Pro Trader conditions
        if (row['trend_direction'] == 'UP' and 
            row['rsi_signal'] == 'NEUTRAL' and
            row['macd_trend'] == 'BULLISH' and
            row['volume_signal'] == 'HIGH' and
            row['bb_position'] < 0.4):
            
            print(f"STRONG_BUY signal at {row['timestamp']}")
```

### Example 3: Batch Processing

```python
def calculate_indicators_for_all_symbols(symbols, timeframe='1D'):
    """Calculate indicators for multiple symbols"""
    
    calculator = IndicatorCalculator()
    results = {}
    
    for symbol in symbols:
        df = fetch_historical_data(symbol, timeframe, limit=250)
        indicators = calculator.calculate_for_signal(df)
        results[symbol] = indicators
    
    return results
```

---

## 🎓 Best Practices

### 1. Data Requirements

- **Minimum 250 candles** for MA 200
- **Minimum 50 candles** for reliable MACD
- **Clean data** (no missing values, sorted by timestamp)

### 2. Performance Optimization

```python
# Cache calculator instance
calculator = IndicatorCalculator()  # Create once

# Reuse for multiple calculations
for symbol in symbols:
    indicators = calculator.calculate_for_signal(df)
```

### 3. Error Handling

```python
try:
    indicators = calculator.calculate_for_signal(df)
except ValueError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Calculation error: {e}")
```

---

## 🐛 Troubleshooting

### Issue: "Need at least 250 data points"

**Solution:** Fetch more historical data
```python
df = fetch_historical_data(symbol, timeframe, limit=300)  # Extra buffer
```

### Issue: "DataFrame must have 'close' column"

**Solution:** Check column names
```python
print(df.columns)  # Verify column names
df = df.rename(columns={'Close': 'close'})  # Rename if needed
```

### Issue: NaN values in indicators

**Solution:** Check data quality
```python
print(df.isnull().sum())  # Check for missing values
df = df.dropna()  # Remove rows with NaN
```

---

## 📊 Output Format

All `calculate_*` methods return a dictionary:

```python
{
    # Trend
    'ma_200': 84523.45,
    'ema_20': 85234.12,
    'trend_direction': 'UP',
    'trend_strength': 75.5,
    'support_level': 83000.0,
    'resistance_level': 87000.0,
    'distance_to_support_pct': 3.6,
    'distance_to_resistance_pct': 1.2,
    
    # Momentum
    'rsi_14': 55.3,
    'rsi_signal': 'NEUTRAL',
    'macd_line': 120.5,
    'macd_signal': 100.2,
    'macd_histogram': 20.3,
    'macd_trend': 'BULLISH',
    
    # Volatility
    'bb_upper': 88000.0,
    'bb_middle': 85000.0,
    'bb_lower': 82000.0,
    'bb_width': 7.06,
    'bb_position': 0.6,
    'bb_position_label': 'ABOVE_MIDDLE',
    
    # Volume
    'volume_ma_20': 2000000.0,
    'volume_ratio': 1.25,
    'volume_signal': 'HIGH',
    'volume_spike': False
}
```

---

## 🔄 Next Steps

1. ✅ **Indicators Module** - HOÀN THÀNH
2. 🔲 **Decision Tree Engine** - Tiếp theo (Phase 3)
3. 🔲 **Backtesting Framework**
4. 🔲 **Integration với Bot chính**

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-03  
**Dependencies:** pandas, numpy
