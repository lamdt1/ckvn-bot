"""
Signal Generator
Orchestrates indicator calculation and signal generation
"""

import sys
sys.path.insert(0, '/Volumes/Data/projects/ckbot')

import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
import logging

from indicators.calculator import IndicatorCalculator
from strategies.pro_trader_strategy import ProTraderStrategy
from strategies.hybrid_strategy import HybridStrategy
from strategies.risk_manager import RiskManager
from strategies.signal import Signal, SignalType
from database.db_manager import TradingDatabase

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalGenerator:
    """
    Generates trading signals by orchestrating:
    1. Indicator calculation
    2. Strategy evaluation (with optional performance learning)
    3. Signal creation
    4. Database storage
    """
    
    def __init__(self,
                 strategy_name: str = 'Pro Trader - Trend Following',
                 total_capital: float = 100_000_000,
                 min_confidence: float = 60.0,
                 db_path: str = 'database/trading.db',
                 enable_learning: bool = True,
                 min_trades_for_filter: int = 5,
                 min_win_rate: float = 40.0,
                 cooldown_days: int = 7):
        """
        Initialize signal generator
        
        Args:
            strategy_name: Name of strategy to use
            total_capital: Total capital for position sizing
            min_confidence: Minimum confidence score to generate signal
            db_path: Path to database
            enable_learning: Enable performance-based learning
            min_trades_for_filter: Minimum trades before filtering
            min_win_rate: Minimum win rate % to continue trading
            cooldown_days: Days to skip symbol after consecutive losses
        """
        self.strategy_name = strategy_name
        self.total_capital = total_capital
        self.min_confidence = min_confidence
        self.enable_learning = enable_learning
        
        # Initialize components
        self.indicator_calculator = IndicatorCalculator()
        
        # Use Hybrid Strategy if learning enabled, otherwise Pro Trader
        if enable_learning:
            self.strategy = HybridStrategy(
                db_path=db_path,
                min_trades_for_filter=min_trades_for_filter,
                min_win_rate=min_win_rate,
                cooldown_days=cooldown_days,
                enable_learning=True
            )
            strategy_type = "Hybrid (Pro Trader + Learning)"
        else:
            self.strategy = ProTraderStrategy()
            strategy_type = "Pro Trader (Rule-Based)"
        
        self.db = TradingDatabase(db_path=db_path)
        
        logger.info(f"✅ SignalGenerator initialized")
        logger.info(f"   Strategy: {strategy_type}")
        logger.info(f"   Capital: {total_capital:,.0f} VND")
        logger.info(f"   Min Confidence: {min_confidence}%")
        if enable_learning:
            logger.info(f"   Learning: ✅ Enabled (min_trades={min_trades_for_filter}, min_win_rate={min_win_rate}%)")
    
    def generate_signal(self,
                       symbol: str,
                       timeframe: str,
                       df: pd.DataFrame,
                       save_to_db: bool = True) -> Optional[Signal]:
        """
        Generate trading signal for a symbol
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe ('1D', '4H')
            df: DataFrame with OHLCV data
            save_to_db: Save signal to database
            
        Returns:
            Signal object or None if no actionable signal
        """
        try:
            # Validate data
            if df is None or df.empty:
                logger.warning(f"No data for {symbol}")
                return None
            
            if len(df) < 250:
                logger.warning(f"Insufficient data for {symbol} ({len(df)} candles, need 250)")
                return None
            
            # Calculate indicators
            logger.debug(f"Calculating indicators for {symbol}...")
            indicators = self.indicator_calculator.calculate_all(df)
            
            # Generate signal using strategy
            logger.debug(f"Generating signal for {symbol}...")
            signal = self.strategy.generate_signal(
                df=df,
                symbol=symbol,
                timeframe=timeframe,
                indicators=indicators
            )
            
            # Check if signal was generated
            if signal is None:
                logger.debug(f"{symbol}: No signal generated (filtered or no opportunity)")
                return None
            
            # Filter by minimum confidence
            if signal.confidence_score < self.min_confidence:
                logger.debug(f"{symbol}: Confidence {signal.confidence_score}% < {self.min_confidence}% (skipped)")
                return None
            
            # Save to database
            if save_to_db and signal.is_actionable():
                self._save_signal(signal, indicators, df)
            
            # Log signal with learning info if available
            log_msg = f"✅ {symbol}: {signal.signal_type.value} (confidence: {signal.confidence_score:.1f}%)"
            if hasattr(signal, 'metadata') and signal.metadata.get('learning_enabled'):
                if 'original_confidence' in signal.metadata:
                    log_msg += f" [adjusted from {signal.metadata['original_confidence']:.1f}%]"
            logger.info(log_msg)
            
            return signal
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _save_signal(self, signal: Signal, indicators: Dict, df: pd.DataFrame):
        """Save signal and related data to database"""
        try:
            self.db.connect()
            
            # Save indicators
            self.db.insert_indicators(
                symbol=signal.symbol,
                timeframe=signal.timeframe,
                timestamp=signal.timestamp,
                indicators=indicators
            )
            
            # Save price data (last 30 days)
            for _, row in df.tail(30).iterrows():
                self.db.insert_price_data(
                    symbol=signal.symbol,
                    timeframe=signal.timeframe,
                    timestamp=int(row['timestamp']),
                    open_price=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=int(row['volume'])
                )
            
            # Save signal
            self.db.create_signal(signal.to_dict())
            
            self.db.disconnect()
            logger.debug(f"💾 Saved signal and data for {signal.symbol}")
            
        except Exception as e:
            logger.error(f"Error saving signal to database: {e}")
    
    def generate_signals_batch(self,
                              data_dict: Dict[str, pd.DataFrame],
                              timeframe: str = '1D',
                              save_to_db: bool = True) -> List[Signal]:
        """
        Generate signals for multiple symbols
        
        Args:
            data_dict: Dictionary mapping symbol to DataFrame
            timeframe: Timeframe
            save_to_db: Save signals to database
            
        Returns:
            List of generated signals
        """
        signals = []
        
        logger.info(f"\n🎯 Generating signals for {len(data_dict)} symbols...")
        
        for symbol, df in data_dict.items():
            signal = self.generate_signal(symbol, timeframe, df, save_to_db)
            
            if signal is not None:
                signals.append(signal)
        
        logger.info(f"\n✅ Generated {len(signals)} actionable signals")
        return signals
    
    def filter_signals(self,
                      signals: List[Signal],
                      signal_types: Optional[List[SignalType]] = None,
                      min_confidence: Optional[float] = None,
                      min_risk_reward: Optional[float] = None) -> List[Signal]:
        """
        Filter signals by criteria
        
        Args:
            signals: List of signals
            signal_types: Filter by signal types
            min_confidence: Minimum confidence score
            min_risk_reward: Minimum risk/reward ratio
            
        Returns:
            Filtered list of signals
        """
        filtered = signals
        
        # Filter by signal type
        if signal_types:
            filtered = [s for s in filtered if s.signal_type in signal_types]
        
        # Filter by confidence
        if min_confidence is not None:
            filtered = [s for s in filtered if s.confidence_score >= min_confidence]
        
        # Filter by risk/reward
        if min_risk_reward is not None:
            filtered = [s for s in filtered if s.risk_reward_ratio >= min_risk_reward]
        
        return filtered
    
    def rank_signals(self,
                    signals: List[Signal],
                    by: str = 'confidence') -> List[Signal]:
        """
        Rank signals by criteria
        
        Args:
            signals: List of signals
            by: Ranking criteria ('confidence', 'risk_reward', 'potential_profit')
            
        Returns:
            Sorted list of signals
        """
        if by == 'confidence':
            return sorted(signals, key=lambda s: s.confidence_score, reverse=True)
        elif by == 'risk_reward':
            return sorted(signals, key=lambda s: s.risk_reward_ratio, reverse=True)
        elif by == 'potential_profit':
            return sorted(signals, key=lambda s: s.get_potential_profit_pct(), reverse=True)
        else:
            logger.warning(f"Unknown ranking criteria: {by}")
            return signals
    
    def get_top_signals(self,
                       signals: List[Signal],
                       top_n: int = 5,
                       by: str = 'confidence') -> List[Signal]:
        """
        Get top N signals
        
        Args:
            signals: List of signals
            top_n: Number of top signals to return
            by: Ranking criteria
            
        Returns:
            Top N signals
        """
        ranked = self.rank_signals(signals, by=by)
        return ranked[:top_n]
    
    def print_signal_summary(self, signals: List[Signal]):
        """Print summary of signals"""
        if not signals:
            print("\n📊 No signals generated")
            return
        
        print("\n" + "="*80)
        print(f"📊 SIGNAL SUMMARY ({len(signals)} signals)")
        print("="*80)
        
        # Group by signal type
        by_type = {}
        for signal in signals:
            signal_type = signal.signal_type.value
            if signal_type not in by_type:
                by_type[signal_type] = []
            by_type[signal_type].append(signal)
        
        # Print summary
        for signal_type, sigs in by_type.items():
            print(f"\n{signal_type}: {len(sigs)} signals")
        
        # Print top signals
        print("\n" + "-"*80)
        print("🏆 TOP SIGNALS (by confidence):")
        print("-"*80)
        print(f"\n{'Rank':<6} {'Symbol':<8} {'Signal':<15} {'Conf':<7} {'Price':<12} {'R/R':<6} {'Pos%':<6}")
        print("-"*80)
        
        top_signals = self.get_top_signals(signals, top_n=10)
        for i, sig in enumerate(top_signals, 1):
            print(f"{i:<6} {sig.symbol:<8} {sig.signal_type.value:<15} "
                  f"{sig.confidence_score:<7.1f} {sig.price:>10,.0f}  "
                  f"{sig.risk_reward_ratio:<6.2f} {sig.position_size_pct:<6.1f}")
        
        print("\n" + "="*80)


if __name__ == "__main__":
    # Test signal generator
    import random
    from datetime import timedelta
    
    print("="*70)
    print("SIGNAL GENERATOR TEST")
    print("="*70)
    
    # Generate sample data
    def generate_sample_data(symbol, days=250):
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        base_price = 85000
        data = []
        
        for i in range(days):
            change = random.uniform(-0.02, 0.02)
            close = base_price * (1 + change)
            
            data.append({
                'symbol': symbol,
                'timestamp': int(dates[i].timestamp()),
                'open': base_price,
                'high': close * 1.01,
                'low': close * 0.99,
                'close': close,
                'volume': random.randint(1000000, 5000000)
            })
            base_price = close
        
        return pd.DataFrame(data)
    
    # Initialize generator
    generator = SignalGenerator(
        total_capital=100_000_000,
        min_confidence=60.0
    )
    
    # Test single symbol
    print("\nTest 1: Generate signal for single symbol")
    df = generate_sample_data('VNM')
    signal = generator.generate_signal('VNM', '1D', df, save_to_db=False)
    
    if signal:
        print(f"\n✅ Signal: {signal.signal_type.value}")
        print(f"   Confidence: {signal.confidence_score}%")
        print(f"   Price: {signal.price:,.0f}")
    
    # Test batch generation
    print("\n" + "="*70)
    print("Test 2: Generate signals for multiple symbols")
    
    symbols = ['VNM', 'VCB', 'HPG', 'VIC', 'VHM']
    data_dict = {symbol: generate_sample_data(symbol) for symbol in symbols}
    
    signals = generator.generate_signals_batch(data_dict, save_to_db=False)
    
    # Print summary
    generator.print_signal_summary(signals)
    
    print("\n✅ Test completed!")
