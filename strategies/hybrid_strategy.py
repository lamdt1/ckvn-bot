"""
Hybrid Strategy
Combines Pro Trader rule-based logic with performance-based learning
"""

import logging
from typing import Optional
import pandas as pd

from strategies.pro_trader_strategy import ProTraderStrategy
from strategies.performance_filter import SymbolPerformanceFilter
from strategies.signal import Signal

logger = logging.getLogger(__name__)


class HybridStrategy(ProTraderStrategy):
    """
    Hybrid trading strategy
    
    Combines:
    1. Pro Trader rule-based decision tree (base logic)
    2. Performance-based learning (historical adjustment)
    
    Features:
    - Skip poor-performing symbols (< 40% win rate after 5+ trades)
    - Adjust confidence based on historical performance
    - Implement cooldown after consecutive losses
    - Maintain conservative risk management
    """
    
    def __init__(self,
                 db_path: str,
                 min_trades_for_filter: int = 5,
                 min_win_rate: float = 40.0,
                 cooldown_days: int = 7,
                 enable_learning: bool = True,
                 **kwargs):
        """
        Initialize hybrid strategy
        
        Args:
            db_path: Path to trading database
            min_trades_for_filter: Minimum trades before filtering
            min_win_rate: Minimum win rate % to continue trading
            cooldown_days: Days to skip symbol after consecutive losses
            enable_learning: Enable performance-based learning
            **kwargs: Additional args for ProTraderStrategy
        """
        # Initialize base strategy
        super().__init__(**kwargs)
        
        self.db_path = db_path
        self.enable_learning = enable_learning
        
        # Initialize performance filter
        if self.enable_learning:
            self.performance_filter = SymbolPerformanceFilter(
                db_path=db_path,
                min_trades_for_filter=min_trades_for_filter,
                min_win_rate=min_win_rate,
                cooldown_days=cooldown_days
            )
            logger.info("✅ Hybrid strategy initialized (Learning ENABLED)")
        else:
            self.performance_filter = None
            logger.info("✅ Hybrid strategy initialized (Learning DISABLED)")
    
    def generate_signal(self,
                       df: pd.DataFrame,
                       symbol: str,
                       timeframe: str = '1D',
                       indicators: dict = None) -> Optional[Signal]:
        """
        Generate trading signal with performance-based adjustment
        
        Workflow:
        1. Check performance filter (skip if poor performer)
        2. Generate base signal using Pro Trader logic
        3. Adjust confidence based on historical performance
        4. Return adjusted signal
        
        Args:
            df: Price data with indicators
            symbol: Stock symbol
            timeframe: Timeframe (e.g., '1D')
            indicators: Pre-calculated indicators (optional)
            
        Returns:
            Signal object or None
        """
        # Step 1: Check performance filter
        if self.enable_learning and self.performance_filter:
            should_skip, skip_reason = self.performance_filter.should_skip_symbol(symbol)
            
            if should_skip:
                logger.info(f"⏭️ Skipping {symbol}: {skip_reason}")
                return None
        
        # Step 2: Generate base signal using Pro Trader logic
        base_signal = super().generate_signal(df, symbol, timeframe, indicators)
        
        if not base_signal:
            return None
        
        # Step 3: Adjust confidence based on historical performance
        if self.enable_learning and self.performance_filter:
            original_confidence = base_signal.confidence_score
            
            adjusted_confidence, adjustment_reason = self.performance_filter.adjust_confidence(
                symbol,
                original_confidence
            )
            
            # Update signal confidence
            base_signal.confidence_score = adjusted_confidence
            
            # Add adjustment reason to signal metadata
            if not hasattr(base_signal, 'metadata'):
                base_signal.metadata = {}
            
            base_signal.metadata['original_confidence'] = original_confidence
            base_signal.metadata['confidence_adjustment'] = adjustment_reason
            base_signal.metadata['learning_enabled'] = True
            
            logger.info(f"🎯 {symbol}: Confidence adjusted {original_confidence:.1f}% → {adjusted_confidence:.1f}%")
        else:
            # No learning - use base confidence
            if not hasattr(base_signal, 'metadata'):
                base_signal.metadata = {}
            base_signal.metadata['learning_enabled'] = False
        
        return base_signal
    
    def get_symbol_performance_summary(self, symbol: str) -> Optional[dict]:
        """
        Get performance summary for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Performance stats dictionary or None
        """
        if not self.enable_learning or not self.performance_filter:
            return None
        
        return self.performance_filter.get_symbol_stats(symbol)
    
    def print_performance_rankings(self):
        """Print performance rankings for all symbols"""
        if not self.enable_learning or not self.performance_filter:
            print("\n⚠️ Learning disabled - no performance data")
            return
        
        self.performance_filter.print_performance_summary()
    
    def get_strategy_info(self) -> dict:
        """Get strategy information"""
        base_info = super().get_strategy_info()
        
        base_info.update({
            'strategy_type': 'Hybrid (Pro Trader + Learning)',
            'learning_enabled': self.enable_learning,
            'performance_filter': self.performance_filter is not None
        })
        
        if self.enable_learning and self.performance_filter:
            base_info.update({
                'min_trades_for_filter': self.performance_filter.min_trades_for_filter,
                'min_win_rate': self.performance_filter.min_win_rate,
                'cooldown_days': self.performance_filter.cooldown_days
            })
        
        return base_info


if __name__ == "__main__":
    # Test hybrid strategy
    import sys
    sys.path.insert(0, '/Volumes/Data/projects/ckbot')
    
    from indicators.calculator import IndicatorCalculator
    from bot.data_fetcher import DataFetcher
    
    print("="*70)
    print("HYBRID STRATEGY TEST")
    print("="*70)
    
    # Initialize strategy
    strategy = HybridStrategy(
        db_path="database/trading.db",
        min_trades_for_filter=5,
        min_win_rate=40.0,
        cooldown_days=7,
        enable_learning=True
    )
    
    # Print strategy info
    info = strategy.get_strategy_info()
    print("\n📊 Strategy Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test with sample data
    print("\n🧪 Testing signal generation...")
    
    try:
        # Fetch data
        fetcher = DataFetcher(source='vnstock')
        df = fetcher.fetch_data('VNM', timeframe='1D', limit=250)
        
        if df is not None and not df.empty:
            # Calculate indicators
            calculator = IndicatorCalculator()
            indicators = calculator.calculate_all(df)
            
            # Generate signal
            signal = strategy.generate_signal(df, 'VNM', '1D', indicators)
            
            if signal:
                print(f"\n✅ Signal generated:")
                print(f"  Symbol: {signal.symbol}")
                print(f"  Type: {signal.signal_type.value}")
                print(f"  Confidence: {signal.confidence_score:.1f}%")
                
                if hasattr(signal, 'metadata'):
                    if 'original_confidence' in signal.metadata:
                        print(f"  Original Confidence: {signal.metadata['original_confidence']:.1f}%")
                    if 'confidence_adjustment' in signal.metadata:
                        print(f"  Adjustment: {signal.metadata['confidence_adjustment']}")
            else:
                print("\n⚠️ No signal generated")
        else:
            print("\n❌ Failed to fetch data")
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Print performance rankings
    print("\n" + "="*70)
    strategy.print_performance_rankings()
