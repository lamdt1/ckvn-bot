"""
Run Backtest
Collect 50-100 simulated trades for clean data
"""

import sys
sys.path.insert(0, '/Volumes/Data/projects/ckbot')

from backtesting import BacktestEngine
from bot.data_fetcher import DataFetcher
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Run backtest to collect clean training data"""
    
    print("\n" + "="*80)
    print("🔬 BACKTEST - COLLECT CLEAN DATA (50-100 TRADES)")
    print("="*80)
    
    # Configuration
    SYMBOLS = ['VNM', 'VCB', 'HPG', 'VIC', 'VHM', 'MSN', 'MWG', 'FPT', 'VPB', 'GAS']
    START_DATE = '2024-01-01'  # 1 year of data
    END_DATE = '2025-12-31'
    INITIAL_CAPITAL = 100_000_000  # 100M VND
    
    print(f"\n⚙️ Configuration:")
    print(f"   Symbols: {', '.join(SYMBOLS)}")
    print(f"   Period: {START_DATE} → {END_DATE}")
    print(f"   Capital: {INITIAL_CAPITAL:,.0f} VND")
    
    # Step 1: Fetch historical data
    print(f"\n📊 Step 1: Fetching historical data...")
    fetcher = DataFetcher(source='vnstock')
    
    data_dict = {}
    for symbol in SYMBOLS:
        logger.info(f"Fetching {symbol}...")
        df = fetcher.fetch_historical_data(
            symbol=symbol,
            start_date=START_DATE,
            end_date=END_DATE,
            limit=500
        )
        
        if df is not None and not df.empty:
            data_dict[symbol] = df
            logger.info(f"  ✅ {symbol}: {len(df)} candles")
        else:
            logger.warning(f"  ❌ {symbol}: No data")
    
    if not data_dict:
        print("\n❌ No data fetched. Please check:")
        print("  1. Internet connection")
        print("  2. vnstock installation: pip install vnstock")
        print("  3. Symbol names are correct")
        return
    
    print(f"\n✅ Fetched data for {len(data_dict)} symbols")
    
    # Step 2: Run backtest
    print(f"\n🔬 Step 2: Running backtest...")
    engine = BacktestEngine(initial_capital=INITIAL_CAPITAL)
    
    results = engine.run_backtest(
        data_dict=data_dict,
        start_date=START_DATE,
        end_date=END_DATE
    )
    
    # Step 3: Save results
    print(f"\n💾 Step 3: Saving results...")
    
    # Save to database
    engine.save_trades_to_db()
    
    # Export to CSV
    engine.export_trades_to_csv('backtest_trades.csv')
    
    # Step 4: Analysis
    print(f"\n📊 Step 4: Analysis...")
    
    if results['total_trades'] < 50:
        print(f"\n⚠️ WARNING: Only {results['total_trades']} trades generated")
        print("   Recommendations:")
        print("   - Extend date range (try 2023-01-01 to 2025-12-31)")
        print("   - Add more symbols")
        print("   - Lower min_confidence from 60% to 50%")
    elif results['total_trades'] > 100:
        print(f"\n✅ Great! {results['total_trades']} trades generated")
        print("   You have enough data for analysis")
    else:
        print(f"\n✅ Perfect! {results['total_trades']} trades in target range (50-100)")
    
    # Validation checks
    print(f"\n🔍 Validation Checks:")
    
    # Check 1: Win rate reasonable?
    if 40 <= results['win_rate'] <= 70:
        print(f"   ✅ Win rate {results['win_rate']:.1f}% is reasonable")
    else:
        print(f"   ⚠️ Win rate {results['win_rate']:.1f}% seems unusual")
        print("      - Too high (>70%): May be overfitting or unrealistic")
        print("      - Too low (<40%): Strategy may need adjustment")
    
    # Check 2: Return reasonable?
    if -20 <= results['total_return_pct'] <= 50:
        print(f"   ✅ Return {results['total_return_pct']:+.2f}% is reasonable")
    else:
        print(f"   ⚠️ Return {results['total_return_pct']:+.2f}% seems unusual")
    
    # Check 3: Average holding period
    if 3 <= results['avg_holding_days'] <= 30:
        print(f"   ✅ Avg holding {results['avg_holding_days']:.1f} days is reasonable")
    else:
        print(f"   ⚠️ Avg holding {results['avg_holding_days']:.1f} days seems unusual")
    
    print(f"\n✅ Backtest complete!")
    print(f"\n📁 Output files:")
    print(f"   - database/trading.db (SQLite database)")
    print(f"   - backtest_trades.csv (CSV export)")
    
    print(f"\n🎯 Next steps:")
    print(f"   1. Review trades in backtest_trades.csv")
    print(f"   2. Analyze patterns (winning vs losing trades)")
    print(f"   3. Validate indicator logic")
    print(f"   4. Proceed to Phase 2: Telegram Alerts")


if __name__ == "__main__":
    main()
