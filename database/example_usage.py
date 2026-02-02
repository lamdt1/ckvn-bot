"""
Example Usage: Trading Database with Pro Trader Strategy
Demonstrates how to use the database for storing and analyzing trading signals
"""

from database.db_manager import TradingDatabase, initialize_database
from datetime import datetime, timedelta
import random


def example_1_insert_price_data(db: TradingDatabase):
    """Example: Insert historical price data"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Inserting Price Data")
    print("="*60)
    
    # Simulate 30 days of price data for VNM stock
    symbol = "VNM"
    base_price = 85000
    base_timestamp = int((datetime.now() - timedelta(days=30)).timestamp())
    
    for i in range(30):
        # Daily data (1D timeframe)
        timestamp_1d = base_timestamp + (i * 86400)  # 1 day = 86400 seconds
        
        # Simulate price movement
        price_change = random.uniform(-2, 2) / 100
        open_price = base_price
        close_price = base_price * (1 + price_change)
        high = max(open_price, close_price) * 1.01
        low = min(open_price, close_price) * 0.99
        volume = random.randint(1000000, 5000000)
        
        db.insert_price_data(
            symbol=symbol,
            timeframe="1D",
            timestamp=timestamp_1d,
            open_price=open_price,
            high=high,
            low=low,
            close=close_price,
            volume=volume
        )
        
        base_price = close_price
        
        # Also insert 4H data (6 candles per day)
        for h in range(6):
            timestamp_4h = timestamp_1d + (h * 14400)  # 4 hours = 14400 seconds
            db.insert_price_data(
                symbol=symbol,
                timeframe="4H",
                timestamp=timestamp_4h,
                open_price=open_price * random.uniform(0.995, 1.005),
                high=high * random.uniform(0.995, 1.005),
                low=low * random.uniform(0.995, 1.005),
                close=close_price * random.uniform(0.995, 1.005),
                volume=volume // 6
            )
    
    print(f"✅ Inserted 30 days of 1D data and 180 candles of 4H data for {symbol}")


def example_2_insert_indicators(db: TradingDatabase):
    """Example: Calculate and insert indicators"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Inserting Technical Indicators")
    print("="*60)
    
    # Get recent price data
    prices = db.execute_query("""
        SELECT * FROM stock_prices 
        WHERE symbol = 'VNM' AND timeframe = '1D'
        ORDER BY timestamp DESC LIMIT 5
    """)
    
    for price in prices:
        # Simulate indicator calculations
        indicators = {
            'ma_200': price['close'] * 0.95,  # Simulated MA 200
            'ema_20': price['close'] * 0.98,  # Simulated EMA 20
            'trend_direction': 'UP' if price['close'] > price['open'] else 'DOWN',
            'trend_strength': random.uniform(60, 90),
            
            'rsi_14': random.uniform(30, 70),
            'rsi_signal': 'NEUTRAL',
            'macd_line': random.uniform(-100, 100),
            'macd_signal': random.uniform(-100, 100),
            'macd_histogram': random.uniform(-50, 50),
            'macd_trend': 'BULLISH',
            
            'bb_upper': price['close'] * 1.05,
            'bb_middle': price['close'],
            'bb_lower': price['close'] * 0.95,
            'bb_width': price['close'] * 0.10,
            'bb_position': 0.5,
            
            'volume_ma_20': price['volume'] * 0.9,
            'volume_ratio': 1.2,
            'volume_signal': 'HIGH',
            
            'support_level': price['close'] * 0.97,
            'resistance_level': price['close'] * 1.03,
            'distance_to_support_pct': 3.0,
            'distance_to_resistance_pct': 3.0
        }
        
        db.insert_indicators(
            symbol=price['symbol'],
            timeframe=price['timeframe'],
            timestamp=price['timestamp'],
            indicators=indicators
        )
    
    print(f"✅ Inserted indicators for 5 recent candles")


def example_3_create_signals(db: TradingDatabase):
    """Example: Generate trading signals using Pro Trader strategy"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Creating Trading Signals")
    print("="*60)
    
    # Get latest indicators
    indicators = db.execute_query("""
        SELECT i.*, p.close as current_price
        FROM indicators i
        JOIN stock_prices p ON 
            i.symbol = p.symbol AND 
            i.timeframe = p.timeframe AND 
            i.timestamp = p.timestamp
        WHERE i.symbol = 'VNM' AND i.timeframe = '1D'
        ORDER BY i.timestamp DESC LIMIT 3
    """)
    
    strategies = [
        {
            'name': 'Pro Trader - Trend Following',
            'type': 'STRONG_BUY',
            'confidence': 85
        },
        {
            'name': 'Pro Trader - Mean Reversion',
            'type': 'WEAK_BUY',
            'confidence': 65
        },
        {
            'name': 'Pro Trader - Breakout',
            'type': 'WATCH',
            'confidence': 50
        }
    ]
    
    for idx, ind in enumerate(indicators):
        if idx >= len(strategies):
            break
            
        strategy = strategies[idx]
        current_price = ind['current_price']
        
        # Build reasoning JSON
        reasoning = {
            'trend_direction': ind['trend_direction'],
            'ma_200_vs_price': 'ABOVE' if current_price > ind['ma_200'] else 'BELOW',
            'ema_20_vs_price': 'ABOVE' if current_price > ind['ema_20'] else 'BELOW',
            'rsi_signal': ind['rsi_signal'],
            'rsi_value': ind['rsi_14'],
            'macd_trend': ind['macd_trend'],
            'volume_signal': ind['volume_signal'],
            'bb_position': ind['bb_position']
        }
        
        # Calculate risk management levels
        stop_loss = current_price * 0.95  # 5% stop loss
        take_profit = current_price * 1.10  # 10% take profit
        risk_reward = (take_profit - current_price) / (current_price - stop_loss)
        
        signal_id = db.create_signal(
            symbol=ind['symbol'],
            timeframe=ind['timeframe'],
            timestamp=ind['timestamp'],
            signal_type=strategy['type'],
            price=current_price,
            reasoning=reasoning,
            confidence_score=strategy['confidence'],
            strategy_name=strategy['name'],
            suggested_stop_loss=stop_loss,
            suggested_take_profit=take_profit,
            position_size_pct=5.0,  # 5% of capital
            risk_reward_ratio=risk_reward
        )
        
        print(f"✅ Created signal #{signal_id}: {strategy['type']} for VNM at {current_price:,.0f}")
        
        # Simulate execution for first signal
        if idx == 0:
            execution_price = current_price * 1.001  # Slight slippage
            db.execute_signal(signal_id, execution_price)
            print(f"   → Executed at {execution_price:,.0f}")
            
            # Simulate closing the position after 7 days with profit
            close_price = execution_price * 1.08  # 8% profit
            close_timestamp = ind['timestamp'] + (7 * 86400)
            db.close_signal(signal_id, close_price, 'TAKE_PROFIT', close_timestamp)
            print(f"   → Closed at {close_price:,.0f} (+8% profit)")


def example_4_query_performance(db: TradingDatabase):
    """Example: Query strategy performance using views"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Querying Strategy Performance")
    print("="*60)
    
    # 1. Strategy Performance Summary
    print("\n📊 Strategy Performance Summary:")
    print("-" * 60)
    performance = db.get_strategy_performance()
    
    if performance:
        for strat in performance:
            print(f"\nStrategy: {strat['strategy_name']}")
            print(f"  Signal Type: {strat['signal_type']}")
            print(f"  Total Signals: {strat['total_signals']}")
            print(f"  Closed: {strat['closed_positions']} | Open: {strat['open_positions']}")
            print(f"  Win Rate: {strat['win_rate_pct']}%")
            print(f"  Avg P&L: {strat['avg_pnl_pct']}%")
            print(f"  Total P&L: {strat['total_pnl_pct']}%")
            print(f"  Avg Confidence: {strat['avg_confidence']}")
    else:
        print("  No closed positions yet")
    
    # 2. Symbol Performance
    print("\n📈 Symbol Performance:")
    print("-" * 60)
    symbols = db.get_symbol_performance()
    
    for sym in symbols:
        print(f"\n{sym['symbol']}:")
        print(f"  Total Signals: {sym['total_signals']}")
        print(f"  Win Rate: {sym['win_rate_pct']}%")
        print(f"  Avg P&L: {sym['avg_pnl_pct']}%")
        print(f"  Best Trade: +{sym['best_trade_pct']}%")
        print(f"  Worst Trade: {sym['worst_trade_pct']}%")
    
    # 3. Open Positions
    print("\n💼 Open Positions:")
    print("-" * 60)
    positions = db.get_open_positions()
    
    if positions:
        for pos in positions:
            print(f"\n{pos['symbol']} - {pos['signal_type']}")
            print(f"  Strategy: {pos['strategy_name']}")
            print(f"  Entry: {pos['execution_price']:,.0f}")
            print(f"  Current: {pos['current_price']:,.0f} ({pos['current_pnl_pct']:+.2f}%)")
            print(f"  Stop Loss: {pos['suggested_stop_loss']:,.0f}")
            print(f"  Take Profit: {pos['suggested_take_profit']:,.0f}")
            print(f"  Days Held: {pos['days_held']}")
            print(f"  Status: {pos['position_status']}")
    else:
        print("  No open positions")
    
    # 4. Indicator Combination Performance
    print("\n🔬 Indicator Combination Analysis:")
    print("-" * 60)
    combinations = db.get_indicator_combination_performance(min_trades=1)
    
    if combinations:
        for combo in combinations[:5]:  # Top 5
            print(f"\nTrend: {combo['trend']} | RSI: {combo['rsi_signal']} | "
                  f"MACD: {combo['macd_trend']} | Volume: {combo['volume_signal']}")
            print(f"  Trades: {combo['closed_positions']}")
            print(f"  Win Rate: {combo['win_rate_pct']}%")
            print(f"  Avg P&L: {combo['avg_pnl_pct']}%")
    else:
        print("  Not enough data for analysis (need at least 1 closed trade)")


def example_5_portfolio_tracking(db: TradingDatabase):
    """Example: Track portfolio state"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Portfolio State Tracking")
    print("="*60)
    
    # Simulate portfolio state
    total_capital = 100_000_000  # 100M VND
    available_cash = 85_000_000  # 85M VND
    invested_value = 15_000_000  # 15M VND
    
    position_details = [
        {
            'symbol': 'VNM',
            'quantity': 100,
            'avg_price': 85000,
            'current_price': 91800,
            'pnl_pct': 8.0
        }
    ]
    
    portfolio_id = db.update_portfolio_state(
        total_capital=total_capital,
        available_cash=available_cash,
        invested_value=invested_value,
        position_details=position_details,
        total_realized_pnl=1_200_000,  # 1.2M profit
        total_realized_pnl_pct=1.2,
        win_rate=100.0  # 1/1 winning trade
    )
    
    print(f"✅ Portfolio state snapshot #{portfolio_id} saved")
    print(f"   Total Capital: {total_capital:,.0f} VND")
    print(f"   Available Cash: {available_cash:,.0f} VND")
    print(f"   Invested: {invested_value:,.0f} VND ({invested_value/total_capital*100:.1f}%)")
    print(f"   Realized P&L: +{1_200_000:,.0f} VND (+1.2%)")


def run_all_examples():
    """Run all examples in sequence"""
    print("\n" + "="*60)
    print("TRADING DATABASE - COMPLETE EXAMPLE")
    print("="*60)
    
    # Initialize database
    print("\n🔧 Initializing database...")
    db = initialize_database()
    
    try:
        # Run examples
        example_1_insert_price_data(db)
        example_2_insert_indicators(db)
        example_3_create_signals(db)
        example_4_query_performance(db)
        example_5_portfolio_tracking(db)
        
        print("\n" + "="*60)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"\nDatabase location: {db.db_path.absolute()}")
        print("\nYou can now:")
        print("  1. Open the database with any SQLite browser")
        print("  2. Query the views for analysis")
        print("  3. Integrate with your trading bot")
        
    finally:
        db.disconnect()


if __name__ == "__main__":
    run_all_examples()
