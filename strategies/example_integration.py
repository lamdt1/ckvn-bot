"""
Complete Integration Example
Demonstrates full workflow: Price Data → Indicators → Strategy → Signal → Database
"""

import sys
sys.path.insert(0, '/Volumes/Data/projects/ckbot')

import pandas as pd
import random
from datetime import datetime, timedelta

# Import all modules
from indicators.calculator import IndicatorCalculator
from strategies.pro_trader_strategy import ProTraderStrategy
from strategies.risk_manager import RiskManager
from database.db_manager import TradingDatabase


def generate_realistic_data(symbol: str, days: int = 250) -> pd.DataFrame:
    """Generate realistic OHLCV data with trends"""
    print(f"\n📊 Generating {days} days of data for {symbol}...")
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    base_price = 85000
    base_volume = 2000000
    
    data = []
    trend_direction = 1  # 1 for up, -1 for down
    
    for i in range(days):
        # Change trend occasionally
        if random.random() < 0.05:  # 5% chance
            trend_direction *= -1
        
        # Price movement with trend bias
        if trend_direction > 0:
            change = random.uniform(-0.01, 0.025)  # Uptrend bias
        else:
            change = random.uniform(-0.025, 0.01)  # Downtrend bias
        
        close = base_price * (1 + change)
        volatility = random.uniform(0.005, 0.015)
        
        # Volume spike occasionally
        if random.random() < 0.1:
            volume = base_volume * random.uniform(2.0, 3.0)
        else:
            volume = base_volume * random.uniform(0.7, 1.3)
        
        data.append({
            'symbol': symbol,
            'timestamp': int(dates[i].timestamp()),
            'open': base_price,
            'high': close * (1 + volatility),
            'low': close * (1 - volatility),
            'close': close,
            'volume': int(volume)
        })
        base_price = close
    
    return pd.DataFrame(data)


def example_1_basic_workflow():
    """Example 1: Basic workflow from data to signal"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Workflow (Data → Indicators → Signal)")
    print("="*70)
    
    # Step 1: Generate price data
    df = generate_realistic_data('VNM', days=250)
    print(f"✅ Generated {len(df)} candles")
    print(f"   Price range: {df['close'].min():,.0f} - {df['close'].max():,.0f}")
    
    # Step 2: Calculate indicators
    print("\n🔬 Calculating indicators...")
    calculator = IndicatorCalculator()
    indicators = calculator.calculate_for_signal(df)
    
    print(f"✅ Indicators calculated:")
    print(f"   Trend: {indicators['trend_direction']}")
    print(f"   RSI: {indicators['rsi_14']} ({indicators['rsi_signal']})")
    print(f"   MACD: {indicators['macd_trend']}")
    print(f"   Volume: {indicators['volume_signal']}")
    
    # Step 3: Generate signal
    print("\n🎯 Generating signal...")
    strategy = ProTraderStrategy()
    signal = strategy.generate_signal(
        symbol='VNM',
        timeframe='1D',
        timestamp=df['timestamp'].iloc[-1],
        price=df['close'].iloc[-1],
        indicators=indicators,
        total_capital=100_000_000
    )
    
    print(f"✅ Signal generated:")
    print(f"   Type: {signal.signal_type.value}")
    print(f"   Confidence: {signal.confidence_score}%")
    print(f"   Price: {signal.price:,.0f} VND")
    print(f"   Stop-Loss: {signal.stop_loss:,.0f} VND")
    print(f"   Take-Profit: {signal.take_profit:,.0f} VND")
    print(f"   Position Size: {signal.position_size_pct}%")
    
    return signal


def example_2_database_integration():
    """Example 2: Complete workflow with database"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Complete Workflow with Database")
    print("="*70)
    
    # Initialize database
    db = TradingDatabase()
    db.connect()
    
    # Generate data
    df = generate_realistic_data('VCB', days=250)
    
    # Save last 30 days of price data
    print("\n💾 Saving price data to database...")
    for _, row in df.tail(30).iterrows():
        db.insert_price_data(
            symbol=row['symbol'],
            timeframe='1D',
            timestamp=row['timestamp'],
            open_price=row['open'],
            high=row['high'],
            low=row['low'],
            close=row['close'],
            volume=row['volume']
        )
    print("✅ Saved 30 days of price data")
    
    # Calculate indicators
    print("\n🔬 Calculating indicators...")
    calculator = IndicatorCalculator()
    indicators = calculator.calculate_for_signal(df)
    
    # Save indicators
    print("\n💾 Saving indicators to database...")
    db.insert_indicators(
        symbol='VCB',
        timeframe='1D',
        timestamp=df['timestamp'].iloc[-1],
        indicators=indicators
    )
    print("✅ Saved indicators")
    
    # Generate signal
    print("\n🎯 Generating signal...")
    strategy = ProTraderStrategy()
    signal = strategy.generate_signal(
        symbol='VCB',
        timeframe='1D',
        timestamp=df['timestamp'].iloc[-1],
        price=df['close'].iloc[-1],
        indicators=indicators
    )
    
    # Save signal if actionable
    if signal.is_actionable():
        print("\n💾 Saving signal to database...")
        db.create_signal(signal.to_dict())
        print(f"✅ Saved {signal.signal_type.value} signal")
    else:
        print(f"\n⏭️ Signal is {signal.signal_type.value}, not saving")
    
    # Verify
    print("\n🔍 Verifying saved data...")
    saved_signals = db.execute_query("""
        SELECT * FROM signals 
        WHERE symbol = 'VCB'
        ORDER BY timestamp DESC LIMIT 1
    """)
    
    if saved_signals:
        sig = dict(saved_signals[0])
        print(f"✅ Found signal: {sig['signal_type']} (confidence: {sig['confidence_score']}%)")
    
    db.disconnect()


def example_3_batch_analysis():
    """Example 3: Analyze multiple symbols"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Batch Analysis (Multiple Symbols)")
    print("="*70)
    
    symbols = ['VNM', 'VCB', 'HPG', 'VIC', 'VHM']
    calculator = IndicatorCalculator()
    strategy = ProTraderStrategy()
    
    results = []
    
    for symbol in symbols:
        print(f"\n📊 Analyzing {symbol}...")
        
        # Generate data
        df = generate_realistic_data(symbol, days=250)
        
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
        
        results.append({
            'symbol': symbol,
            'signal': signal.signal_type.value,
            'confidence': signal.confidence_score,
            'price': signal.price,
            'trend': indicators['trend_direction'],
            'rsi': indicators['rsi_14'],
            'volume': indicators['volume_signal']
        })
    
    # Display summary
    print("\n" + "="*70)
    print("📊 ANALYSIS SUMMARY")
    print("="*70)
    print(f"\n{'Symbol':<8} {'Signal':<15} {'Conf':<6} {'Price':<12} {'Trend':<10} {'RSI':<6}")
    print("-" * 70)
    
    for r in results:
        print(f"{r['symbol']:<8} {r['signal']:<15} {r['confidence']:<6.1f} "
              f"{r['price']:>10,.0f}  {r['trend']:<10} {r['rsi']:<6.1f}")
    
    # Count signals
    buy_signals = sum(1 for r in results if 'BUY' in r['signal'])
    print(f"\n📈 Buy signals: {buy_signals}/{len(results)}")


def example_4_custom_strategy():
    """Example 4: Custom strategy configuration"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Custom Strategy Configuration")
    print("="*70)
    
    # Custom risk manager
    risk_manager = RiskManager(
        stop_loss_pct=4.0,
        take_profit_pct=12.0,
        min_risk_reward=2.5,
        max_position_size_pct=8.0
    )
    
    # Custom strategy
    strategy = ProTraderStrategy(risk_manager=risk_manager)
    
    # Set conservative thresholds
    strategy.set_thresholds(
        strong_buy=85.0,
        weak_buy=70.0,
        watch=55.0
    )
    
    # Adjust weights (more emphasis on trend)
    strategy.set_weights(
        trend=0.40,
        momentum=0.30,
        volume=0.15,
        entry=0.15
    )
    
    print("\n⚙️ Custom Configuration:")
    print(f"  Stop-Loss: {risk_manager.stop_loss_pct}%")
    print(f"  Take-Profit: {risk_manager.take_profit_pct}%")
    print(f"  Min R/R: {risk_manager.min_risk_reward}")
    print(f"  STRONG_BUY threshold: {strategy.thresholds['strong_buy']}%")
    print(f"  Trend weight: {strategy.weights['trend']*100}%")
    
    # Generate data and signal
    df = generate_realistic_data('VNM', days=250)
    calculator = IndicatorCalculator()
    indicators = calculator.calculate_for_signal(df)
    
    signal = strategy.generate_signal(
        symbol='VNM',
        timeframe='1D',
        timestamp=df['timestamp'].iloc[-1],
        price=df['close'].iloc[-1],
        indicators=indicators
    )
    
    print(f"\n📊 Signal with custom config:")
    print(f"  Type: {signal.signal_type.value}")
    print(f"  Confidence: {signal.confidence_score}%")
    print(f"  R/R Ratio: {signal.risk_reward_ratio}")
    print(f"  Position Size: {signal.position_size_pct}%")


def example_5_signal_filtering():
    """Example 5: Filter and rank signals"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Signal Filtering & Ranking")
    print("="*70)
    
    symbols = ['VNM', 'VCB', 'HPG', 'VIC', 'VHM', 'MSN', 'MWG', 'FPT']
    calculator = IndicatorCalculator()
    strategy = ProTraderStrategy()
    
    buy_signals = []
    
    for symbol in symbols:
        df = generate_realistic_data(symbol, days=250)
        indicators = calculator.calculate_for_signal(df)
        signal = strategy.generate_signal(
            symbol=symbol,
            timeframe='1D',
            timestamp=df['timestamp'].iloc[-1],
            price=df['close'].iloc[-1],
            indicators=indicators
        )
        
        # Filter: Only buy signals with confidence >= 60%
        if signal.is_buy_signal() and signal.confidence_score >= 60:
            buy_signals.append(signal)
    
    # Sort by confidence (descending)
    buy_signals.sort(key=lambda x: x.confidence_score, reverse=True)
    
    print(f"\n✅ Found {len(buy_signals)} buy signals (confidence >= 60%)")
    
    if buy_signals:
        print("\n🏆 TOP SIGNALS:")
        print(f"\n{'Rank':<6} {'Symbol':<8} {'Signal':<15} {'Conf':<6} {'R/R':<6} {'Pos%':<6}")
        print("-" * 60)
        
        for i, sig in enumerate(buy_signals[:5], 1):  # Top 5
            print(f"{i:<6} {sig.symbol:<8} {sig.signal_type.value:<15} "
                  f"{sig.confidence_score:<6.1f} {sig.risk_reward_ratio:<6.2f} {sig.position_size_pct:<6.1f}")


def run_all_examples():
    """Run all integration examples"""
    print("\n" + "="*70)
    print("COMPLETE INTEGRATION EXAMPLES")
    print("="*70)
    
    try:
        example_1_basic_workflow()
        example_2_database_integration()
        example_3_batch_analysis()
        example_4_custom_strategy()
        example_5_signal_filtering()
        
        print("\n" + "="*70)
        print("✅ ALL EXAMPLES COMPLETED!")
        print("="*70)
        
        print("\n📚 You can now:")
        print("  1. Integrate with real data source (vnstock, API)")
        print("  2. Run backtests on historical data")
        print("  3. Deploy for live signal generation")
        print("  4. Build notification system")
        
    except ImportError as e:
        print(f"\n❌ Missing dependency: {e}")
        print("\n📦 Please install: pip install pandas")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
