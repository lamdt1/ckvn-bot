# 🎯 Tích hợp Database vào Trading Bot - Hướng dẫn Implementation

## 📋 Tổng quan

Bạn đã có đầy đủ schema database cho chiến lược **Pro Trader Rule-Based Decision Tree**. Bây giờ cần tích hợp vào bot hiện tại.

---

## 🗂️ Files đã tạo

```
database/
├── migrations/
│   └── 001_create_trading_schema.sql  # ✅ Schema SQL (5 tables + 6 views)
├── db_manager.py                       # ✅ Database manager class
├── strategy_analyzer.py                # ✅ Advanced analysis tools
├── example_usage.py                    # ✅ Examples & tests
├── README.md                           # ✅ Documentation
└── trading.db                          # ✅ SQLite database (auto-created)
```

---

## 🚀 Roadmap Triển khai

### Phase 1: Setup Database (✅ HOÀN THÀNH)

- [x] Thiết kế schema
- [x] Tạo migration script
- [x] Tạo database manager
- [x] Tạo views phân tích
- [x] Test với dữ liệu mẫu

### Phase 2: Tích hợp Indicator Calculator (TIẾP THEO)

**Mục tiêu:** Tính toán các chỉ số kỹ thuật từ dữ liệu giá

**Files cần tạo:**
```
indicators/
├── __init__.py
├── trend_indicators.py      # MA 200, EMA 20, trend detection
├── momentum_indicators.py   # RSI, MACD
├── volatility_indicators.py # Bollinger Bands
├── volume_indicators.py     # Volume analysis
└── calculator.py            # Main calculator orchestrator
```

**Thư viện đề xuất:**
- `pandas-ta` (recommended) - Dễ dùng, nhiều indicator
- `ta-lib` (advanced) - Nhanh hơn nhưng khó cài đặt
- Tự viết (custom) - Kiểm soát hoàn toàn

**Example code:**
```python
import pandas as pd
import pandas_ta as ta

def calculate_indicators(df: pd.DataFrame) -> dict:
    """
    Calculate all indicators for Pro Trader strategy
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        Dictionary of indicator values
    """
    # Trend
    df['MA_200'] = ta.sma(df['close'], length=200)
    df['EMA_20'] = ta.ema(df['close'], length=20)
    
    # Momentum
    df['RSI_14'] = ta.rsi(df['close'], length=14)
    macd = ta.macd(df['close'])
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_signal'] = macd['MACDs_12_26_9']
    df['MACD_hist'] = macd['MACDh_12_26_9']
    
    # Volatility
    bbands = ta.bbands(df['close'], length=20)
    df['BB_upper'] = bbands['BBU_20_2.0']
    df['BB_middle'] = bbands['BBM_20_2.0']
    df['BB_lower'] = bbands['BBL_20_2.0']
    
    # Volume
    df['Volume_MA_20'] = ta.sma(df['volume'], length=20)
    
    # Get latest values
    latest = df.iloc[-1]
    
    return {
        'ma_200': latest['MA_200'],
        'ema_20': latest['EMA_20'],
        'trend_direction': 'UP' if latest['close'] > latest['MA_200'] else 'DOWN',
        'rsi_14': latest['RSI_14'],
        'rsi_signal': 'OVERSOLD' if latest['RSI_14'] < 30 else 'OVERBOUGHT' if latest['RSI_14'] > 70 else 'NEUTRAL',
        'macd_line': latest['MACD'],
        'macd_signal': latest['MACD_signal'],
        'macd_histogram': latest['MACD_hist'],
        'macd_trend': 'BULLISH' if latest['MACD_hist'] > 0 else 'BEARISH',
        'bb_upper': latest['BB_upper'],
        'bb_middle': latest['BB_middle'],
        'bb_lower': latest['BB_lower'],
        'volume_ma_20': latest['Volume_MA_20'],
        'volume_ratio': latest['volume'] / latest['Volume_MA_20'],
        'volume_signal': 'HIGH' if latest['volume'] > latest['Volume_MA_20'] * 1.5 else 'NORMAL'
    }
```

### Phase 3: Decision Tree Engine (SAU ĐÓ)

**Mục tiêu:** Implement logic quyết định theo Pro Trader strategy

**File cần tạo:**
```
strategies/
├── __init__.py
├── decision_tree.py         # Main decision tree logic
├── pro_trader_strategy.py   # Pro Trader implementation
└── risk_manager.py          # Risk management rules
```

**Example Decision Tree:**
```python
class ProTraderStrategy:
    def generate_signal(self, indicators: dict, price: float) -> dict:
        """
        Pro Trader Decision Tree
        
        Layer 1: Trend → Layer 2: Momentum → Layer 3: Volume → Layer 4: Entry
        """
        reasoning = {}
        
        # Layer 1: Xác định xu hướng
        if indicators['trend_direction'] == 'UP' and price > indicators['ema_20']:
            reasoning['trend'] = 'STRONG_UPTREND'
            trend_score = 100
        elif indicators['trend_direction'] == 'UP':
            reasoning['trend'] = 'WEAK_UPTREND'
            trend_score = 60
        else:
            reasoning['trend'] = 'DOWNTREND'
            return self._create_signal('NO_ACTION', 0, reasoning, price)
        
        # Layer 2: Kiểm tra động lượng
        if indicators['rsi_signal'] == 'OVERBOUGHT':
            reasoning['momentum'] = 'OVERBOUGHT_RISKY'
            return self._create_signal('WATCH', 30, reasoning, price)
        elif indicators['macd_trend'] == 'BULLISH' and indicators['rsi_14'] < 70:
            reasoning['momentum'] = 'STRONG_MOMENTUM'
            momentum_score = 100
        else:
            reasoning['momentum'] = 'WEAK_MOMENTUM'
            momentum_score = 50
        
        # Layer 3: Xác nhận dòng tiền
        if indicators['volume_signal'] == 'HIGH':
            reasoning['volume'] = 'CONFIRMED'
            volume_score = 100
        else:
            reasoning['volume'] = 'WEAK_CONFIRMATION'
            volume_score = 50
        
        # Layer 4: Tìm điểm vào
        bb_position = (price - indicators['bb_lower']) / (indicators['bb_upper'] - indicators['bb_lower'])
        
        if bb_position < 0.3:  # Gần Lower Band
            reasoning['entry'] = 'NEAR_SUPPORT'
            entry_score = 100
        elif bb_position < 0.5:
            reasoning['entry'] = 'BELOW_MIDDLE'
            entry_score = 80
        else:
            reasoning['entry'] = 'ABOVE_MIDDLE'
            entry_score = 40
        
        # Calculate final score
        confidence = (trend_score * 0.3 + momentum_score * 0.3 + 
                     volume_score * 0.2 + entry_score * 0.2)
        
        # Determine signal type
        if confidence >= 80:
            signal_type = 'STRONG_BUY'
        elif confidence >= 60:
            signal_type = 'WEAK_BUY'
        else:
            signal_type = 'WATCH'
        
        return self._create_signal(signal_type, confidence, reasoning, price)
    
    def _create_signal(self, signal_type: str, confidence: float, 
                      reasoning: dict, price: float) -> dict:
        """Create signal with risk management"""
        stop_loss = price * 0.95  # 5% stop loss
        take_profit = price * 1.10  # 10% take profit
        
        return {
            'signal_type': signal_type,
            'confidence_score': confidence,
            'reasoning': reasoning,
            'price': price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_reward_ratio': (take_profit - price) / (price - stop_loss),
            'position_size_pct': 5.0  # 5% of capital
        }
```

### Phase 4: Main Bot Integration (CUỐI CÙNG)

**Mục tiêu:** Tích hợp tất cả vào bot chính

**Workflow:**
```python
from database.db_manager import TradingDatabase
from indicators.calculator import calculate_indicators
from strategies.pro_trader_strategy import ProTraderStrategy

class TradingBot:
    def __init__(self):
        self.db = TradingDatabase()
        self.db.connect()
        self.strategy = ProTraderStrategy()
    
    def process_new_candle(self, symbol: str, timeframe: str, candle: dict):
        """Process new price candle"""
        
        # 1. Save price data
        self.db.insert_price_data(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=candle['timestamp'],
            open_price=candle['open'],
            high=candle['high'],
            low=candle['low'],
            close=candle['close'],
            volume=candle['volume']
        )
        
        # 2. Get historical data for indicator calculation
        prices = self.db.execute_query("""
            SELECT * FROM stock_prices 
            WHERE symbol = ? AND timeframe = ?
            ORDER BY timestamp DESC LIMIT 200
        """, (symbol, timeframe))
        
        df = pd.DataFrame([dict(p) for p in prices])
        
        # 3. Calculate indicators
        indicators = calculate_indicators(df)
        
        # 4. Save indicators
        self.db.insert_indicators(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=candle['timestamp'],
            indicators=indicators
        )
        
        # 5. Generate signal (only on 1D for trend, 4H for entry)
        if timeframe == '1D':
            # Check trend on 1D
            self.check_trend(symbol, indicators, candle['close'])
        elif timeframe == '4H':
            # Find entry on 4H
            signal = self.strategy.generate_signal(indicators, candle['close'])
            
            if signal['signal_type'] in ['STRONG_BUY', 'WEAK_BUY']:
                # Save signal
                signal_id = self.db.create_signal(
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=candle['timestamp'],
                    signal_type=signal['signal_type'],
                    price=signal['price'],
                    reasoning=signal['reasoning'],
                    confidence_score=signal['confidence_score'],
                    strategy_name='Pro Trader - Trend Following',
                    suggested_stop_loss=signal['stop_loss'],
                    suggested_take_profit=signal['take_profit'],
                    position_size_pct=signal['position_size_pct'],
                    risk_reward_ratio=signal['risk_reward_ratio']
                )
                
                # Send notification
                self.send_notification(symbol, signal)
                
                # Execute if auto-trading enabled
                if self.auto_trading_enabled:
                    self.execute_trade(signal_id, signal)
    
    def monitor_positions(self):
        """Monitor open positions for stop-loss/take-profit"""
        positions = self.db.get_open_positions()
        
        for pos in positions:
            current_price = self.get_current_price(pos['symbol'])
            
            # Check stop-loss
            if current_price <= pos['suggested_stop_loss']:
                self.close_position(pos['id'], current_price, 'STOP_LOSS')
            
            # Check take-profit
            elif current_price >= pos['suggested_take_profit']:
                self.close_position(pos['id'], current_price, 'TAKE_PROFIT')
    
    def daily_analysis(self):
        """Run daily performance analysis"""
        from database.strategy_analyzer import StrategyAnalyzer
        
        analyzer = StrategyAnalyzer(self.db)
        report = analyzer.generate_optimization_report()
        
        # Send report to user
        self.send_daily_report(report)
```

---

## 📊 Cách sử dụng Views để tối ưu chiến lược

### 1. Tìm chiến lược tốt nhất

```python
# Sau 1 tháng giao dịch
performance = db.get_strategy_performance()

best_strategy = max(performance, key=lambda x: x['total_pnl_pct'])
print(f"Best: {best_strategy['strategy_name']} - {best_strategy['total_pnl_pct']}%")
```

### 2. Điều chỉnh Decision Tree dựa trên dữ liệu

```python
from database.strategy_analyzer import StrategyAnalyzer

analyzer = StrategyAnalyzer(db)

# Phân tích indicator nào quan trọng nhất
importance = analyzer.analyze_indicator_importance()

# Nếu volume_signal = 'HIGH' có win rate thấp → Giảm trọng số volume
# Nếu rsi_signal = 'OVERSOLD' có win rate cao → Tăng trọng số RSI
```

### 3. Tối ưu Stop-Loss và Take-Profit

```python
# Phân tích holding period tối ưu
holding = analyzer.find_optimal_holding_period()

# Nếu "4-7 days" có avg_pnl cao nhất → Set timeout 7 days
# Nếu "0-1 days" có win rate thấp → Tránh day trading
```

---

## 🎯 Next Steps

### Ngay lập tức:
1. **Cài đặt pandas-ta**: `pip install pandas-ta`
2. **Tạo indicator calculator** (Phase 2)
3. **Test với dữ liệu thật** từ vnstock

### Tuần tới:
4. **Implement Decision Tree** (Phase 3)
5. **Backtest trên dữ liệu lịch sử** (1-2 năm)
6. **Điều chỉnh threshold** dựa trên kết quả backtest

### Tháng tới:
7. **Tích hợp vào bot chính** (Phase 4)
8. **Paper trading** (giao dịch ảo) 1 tháng
9. **Live trading** với vốn nhỏ

---

## ❓ Câu hỏi cho bạn

Để tôi tiếp tục hỗ trợ, bạn muốn:

1. **Tôi tạo Indicator Calculator ngay?** (Phase 2)
   - Sử dụng pandas-ta hay ta-lib?
   - Có cần thêm indicator nào không? (ATR, Stochastic, etc.)

2. **Tôi tạo Decision Tree Engine?** (Phase 3)
   - Bạn có muốn điều chỉnh threshold không? (VD: RSI < 30 thay vì < 35?)
   - Có cần thêm rule nào? (VD: không mua nếu đang nắm > 3 mã?)

3. **Tôi giúp tích hợp vào bot hiện tại?** (Phase 4)
   - Bot hiện tại đang chạy như thế nào? (Cron job? Real-time?)
   - Bạn muốn auto-trading hay chỉ gửi notification?

Cho tôi biết hướng nào bạn muốn đi tiếp! 🚀
