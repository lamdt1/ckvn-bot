"""
Example: Integration of Indicator Calculator with Database
Demonstrates complete workflow from price data to indicators storage
"""

import sys
import pandas as pd
from datetime import datetime, timedelta
import random

# Add project root to path
sys.path.insert(0, '/Volumes/Data/projects/ckbot')

from database.db_manager import TradingDatabase
from indicators.calculator import IndicatorCalculator


def generate_sample_data(symbol: str = "VNM", days: int = 250) -> pd.DataFrame:
    """
    Generate sample OHLCV data for testing
    
    Args:
        symbol: Stock symbol
        days: Number of days of data
        
    Returns:
        DataFrame with OHLCV data
    """
    print(f"\n📊 Generating {days} days of sample data for {symbol}...")
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    base_price = 85000
    base_volume = 2000000
    
    data = []
    for i in range(days):
        change = random.uniform(-0.025, 0.025)
        close = base_price * (1 + change)
        volatility = random.uniform(0.005, 0.015)
        
        # Simulate volume spike occasionally
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


def example_1_basic_calculation():
    """Example 1: Basic indicator calculation"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Indicator Calculation")
    print("="*70)
    
    # Generate sample data
    df = generate_sample_data("VNM", days=250)
    
    # Initialize calculator
    calculator = IndicatorCalculator()
    
    # Calculate indicators
    print("\n🔬 Calculating indicators...")
    indicators = calculator.calculate_for_signal(df)
    
    # Display results
    print("\n✅ Results:")
    print(f"\n  Trend: {indicators['trend_direction']}")
    print(f"  MA 200: {indicators['ma_200']:,.0f}")
    print(f"  EMA 20: {indicators['ema_20']:,.0f}")
    print(f"  RSI: {indicators['rsi_14']} ({indicators['rsi_signal']})")
    print(f"  MACD: {indicators['macd_trend']}")
    print(f"  Volume: {indicators['volume_signal']}")
    print(f"  BB Position: {indicators['bb_position']} ({indicators['bb_position_label']})")
    
    return indicators


def example_2_database_integration():
    """Example 2: Calculate and save to database"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Database Integration")
    print("="*70)
    
    # Initialize database
    db = TradingDatabase()
    db.connect()
    
    # Generate sample data
    df = generate_sample_data("VNM", days=250)
    
    # Save price data to database
    print("\n💾 Saving price data to database...")
    for _, row in df.tail(30).iterrows():  # Save last 30 days
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
    print("  ✅ Saved 30 days of price data")
    
    # Calculate indicators
    print("\n🔬 Calculating indicators...")
    calculator = IndicatorCalculator()
    indicators = calculator.calculate_for_signal(df)
    
    # Save indicators to database
    print("\n💾 Saving indicators to database...")
    latest_timestamp = df['timestamp'].iloc[-1]
    
    db.insert_indicators(
        symbol='VNM',
        timeframe='1D',
        timestamp=latest_timestamp,
        indicators=indicators
    )
    print("  ✅ Saved indicators")
    
    # Verify data
    print("\n🔍 Verifying saved data...")
    saved_indicators = db.execute_query("""
        SELECT * FROM indicators 
        WHERE symbol = 'VNM' AND timeframe = '1D'
        ORDER BY timestamp DESC LIMIT 1
    """)
    
    if saved_indicators:
        ind = dict(saved_indicators[0])
        print(f"\n  Trend: {ind['trend_direction']}")
        print(f"  RSI: {ind['rsi_14']}")
        print(f"  MACD Trend: {ind['macd_trend']}")
        print(f"  Volume Signal: {ind['volume_signal']}")
    
    db.disconnect()


def example_3_batch_processing():
    """Example 3: Process multiple symbols"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Batch Processing Multiple Symbols")
    print("="*70)
    
    symbols = ['VNM', 'VCB', 'HPG', 'VIC', 'VHM']
    calculator = IndicatorCalculator()
    
    results = {}
    
    for symbol in symbols:
        print(f"\n📊 Processing {symbol}...")
        
        # Generate data
        df = generate_sample_data(symbol, days=250)
        
        # Calculate indicators
        indicators = calculator.calculate_for_signal(df)
        
        results[symbol] = {
            'trend': indicators['trend_direction'],
            'rsi': indicators['rsi_14'],
            'rsi_signal': indicators['rsi_signal'],
            'macd_trend': indicators['macd_trend'],
            'volume_signal': indicators['volume_signal'],
            'bb_position': indicators['bb_position_label']
        }
    
    # Display summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"\n{'Symbol':<8} {'Trend':<10} {'RSI':<8} {'MACD':<10} {'Volume':<8} {'BB Pos':<15}")
    print("-" * 70)
    
    for symbol, data in results.items():
        print(f"{symbol:<8} {data['trend']:<10} {data['rsi']:<8.1f} "
              f"{data['macd_trend']:<10} {data['volume_signal']:<8} {data['bb_position']:<15}")


def example_4_custom_parameters():
    """Example 4: Custom indicator parameters"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Custom Indicator Parameters")
    print("="*70)
    
    # Generate data
    df = generate_sample_data("VNM", days=250)
    
    # Standard parameters
    print("\n📊 Standard Parameters (MA 200, EMA 20, RSI 14):")
    calculator_standard = IndicatorCalculator()
    indicators_standard = calculator_standard.calculate_for_signal(df)
    
    print(f"  MA 200: {indicators_standard['ma_200']:,.0f}")
    print(f"  EMA 20: {indicators_standard['ema_20']:,.0f}")
    print(f"  RSI 14: {indicators_standard['rsi_14']}")
    
    # Custom parameters
    print("\n📊 Custom Parameters (MA 100, EMA 50, RSI 21):")
    calculator_custom = IndicatorCalculator(
        ma_period=100,
        ema_period=50,
        rsi_period=21,
        bb_period=30,
        bb_std=2.5
    )
    indicators_custom = calculator_custom.calculate_for_signal(df)
    
    print(f"  MA 100: {indicators_custom['ma_200']:,.0f}")  # Note: key is still 'ma_200'
    print(f"  EMA 50: {indicators_custom['ema_20']:,.0f}")  # Note: key is still 'ema_20'
    print(f"  RSI 21: {indicators_custom['rsi_14']}")  # Note: key is still 'rsi_14'
    print(f"  BB Width: {indicators_custom['bb_width']}%")


def example_5_historical_analysis():
    """Example 5: Historical indicator analysis (for backtesting)"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Historical Indicator Analysis")
    print("="*70)
    
    # Generate data
    df = generate_sample_data("VNM", days=250)
    
    # Calculate indicators for all historical data
    print("\n🔬 Calculating indicators for historical data...")
    calculator = IndicatorCalculator()
    df_with_indicators = calculator.calculate_with_history(df, lookback=50)
    
    print(f"\n✅ Calculated indicators for {len(df_with_indicators)} periods")
    print(f"   Columns: {list(df_with_indicators.columns)}")
    
    # Find signals in historical data
    print("\n🔍 Scanning for STRONG_BUY conditions...")
    
    strong_buy_conditions = (
        (df_with_indicators['close'] > df_with_indicators['MA_200']) &
        (df_with_indicators['close'] > df_with_indicators['EMA_20']) &
        (df_with_indicators['RSI_14'] > 30) &
        (df_with_indicators['RSI_14'] < 70) &
        (df_with_indicators['MACD_hist'] > 0)
    )
    
    signals = df_with_indicators[strong_buy_conditions]
    
    print(f"\n  Found {len(signals)} potential STRONG_BUY signals")
    
    if len(signals) > 0:
        print("\n  Last 3 signals:")
        for _, row in signals.tail(3).iterrows():
            date = datetime.fromtimestamp(row['timestamp']).strftime('%Y-%m-%d')
            print(f"    {date}: Price {row['close']:,.0f} | "
                  f"RSI {row['RSI_14']:.1f} | MACD Hist {row['MACD_hist']:.2f}")


def run_all_examples():
    """Run all examples"""
    print("\n" + "="*70)
    print("INDICATOR CALCULATOR - INTEGRATION EXAMPLES")
    print("="*70)
    
    try:
        # Example 1
        example_1_basic_calculation()
        
        # Example 2
        example_2_database_integration()
        
        # Example 3
        example_3_batch_processing()
        
        # Example 4
        example_4_custom_parameters()
        
        # Example 5
        example_5_historical_analysis()
        
        print("\n" + "="*70)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*70)
        
        print("\n📚 Next Steps:")
        print("  1. Install dependencies: pip install pandas numpy")
        print("  2. Integrate with your data source (vnstock, API, etc.)")
        print("  3. Move to Phase 3: Decision Tree Engine")
        
    except ImportError as e:
        print(f"\n❌ Missing dependency: {e}")
        print("\n📦 Please install dependencies:")
        print("   pip install pandas numpy")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
