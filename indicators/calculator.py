"""
Main Indicator Calculator
Orchestrates all indicator calculations for Pro Trader strategy
"""

import pandas as pd
from typing import Dict, Optional
from .trend_indicators import TrendIndicators
from .momentum_indicators import MomentumIndicators
from .volatility_indicators import VolatilityIndicators
from .volume_indicators import VolumeIndicators


class IndicatorCalculator:
    """
    Main calculator that orchestrates all indicator calculations
    for the Pro Trader Rule-Based Decision Tree strategy
    """
    
    def __init__(self, 
                 ma_period: int = 200,
                 ema_period: int = 20,
                 rsi_period: int = 14,
                 macd_fast: int = 12,
                 macd_slow: int = 26,
                 macd_signal: int = 9,
                 bb_period: int = 20,
                 bb_std: float = 2.0,
                 volume_ma_period: int = 20):
        """
        Initialize indicator calculator with custom parameters
        
        Args:
            ma_period: Moving Average period (default: 200)
            ema_period: Exponential MA period (default: 20)
            rsi_period: RSI period (default: 14)
            macd_fast: MACD fast period (default: 12)
            macd_slow: MACD slow period (default: 26)
            macd_signal: MACD signal period (default: 9)
            bb_period: Bollinger Bands period (default: 20)
            bb_std: Bollinger Bands standard deviation (default: 2.0)
            volume_ma_period: Volume MA period (default: 20)
        """
        self.ma_period = ma_period
        self.ema_period = ema_period
        self.rsi_period = rsi_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.volume_ma_period = volume_ma_period
        
    def calculate_all(self, df: pd.DataFrame, 
                     include_optional: bool = False) -> Dict[str, any]:
        """
        Calculate all indicators for Pro Trader strategy
        
        Args:
            df: DataFrame with OHLCV data
                Required columns: timestamp, open, high, low, close, volume
            include_optional: Include optional indicators (OBV, VWAP, ATR)
            
        Returns:
            Dictionary with all indicator values
        """
        # Validate input
        required_cols = ['close', 'volume']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"DataFrame must have columns: {required_cols}")
        
        # Check minimum data length
        min_length = max(self.ma_period, self.macd_slow + self.macd_signal)
        if len(df) < min_length:
            raise ValueError(f"Need at least {min_length} data points, got {len(df)}")
        
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Layer 1: Trend Indicators
        trend_indicators = TrendIndicators.calculate_all(
            df, 
            ma_period=self.ma_period,
            ema_period=self.ema_period
        )
        
        # Layer 2: Momentum Indicators
        momentum_indicators = MomentumIndicators.calculate_all(
            df,
            rsi_period=self.rsi_period,
            macd_fast=self.macd_fast,
            macd_slow=self.macd_slow,
            macd_signal=self.macd_signal
        )
        
        # Layer 4: Volatility Indicators (for entry timing)
        volatility_indicators = VolatilityIndicators.calculate_all(
            df,
            bb_period=self.bb_period,
            bb_std=self.bb_std,
            include_atr=include_optional
        )
        
        # Layer 3: Volume Indicators (confirmation)
        volume_indicators = VolumeIndicators.calculate_all(
            df,
            volume_ma_period=self.volume_ma_period,
            include_obv=include_optional,
            include_vwap=include_optional
        )
        
        # Combine all indicators
        all_indicators = {
            **trend_indicators,
            **momentum_indicators,
            **volatility_indicators,
            **volume_indicators
        }
        
        return all_indicators
    
    def calculate_for_signal(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Calculate indicators specifically for signal generation
        (excludes optional indicators to save computation)
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary with core indicators only
        """
        return self.calculate_all(df, include_optional=False)
    
    def calculate_with_history(self, df: pd.DataFrame, 
                               lookback: int = 50) -> pd.DataFrame:
        """
        Calculate indicators for historical data (for backtesting)
        
        Args:
            df: DataFrame with OHLCV data
            lookback: Number of recent periods to return (default: 50)
            
        Returns:
            DataFrame with indicators added as columns
        """
        # Make a copy
        df = df.copy()
        
        # Calculate trend indicators
        df['MA_200'] = TrendIndicators.calculate_sma(df['close'], self.ma_period)
        df['EMA_20'] = TrendIndicators.calculate_ema(df['close'], self.ema_period)
        
        # Calculate momentum indicators
        df['RSI_14'] = MomentumIndicators.calculate_rsi(df['close'], self.rsi_period)
        macd_data = MomentumIndicators.calculate_macd(
            df['close'], self.macd_fast, self.macd_slow, self.macd_signal
        )
        df['MACD'] = macd_data['macd_line']
        df['MACD_signal'] = macd_data['macd_signal']
        df['MACD_hist'] = macd_data['macd_histogram']
        
        # Calculate volatility indicators
        bb_data = VolatilityIndicators.calculate_bollinger_bands(
            df['close'], self.bb_period, self.bb_std
        )
        df['BB_upper'] = bb_data['bb_upper']
        df['BB_middle'] = bb_data['bb_middle']
        df['BB_lower'] = bb_data['bb_lower']
        
        # Calculate volume indicators
        df['Volume_MA_20'] = VolumeIndicators.calculate_volume_ma(
            df['volume'], self.volume_ma_period
        )
        
        # Return recent data
        return df.tail(lookback) if lookback else df
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> bool:
        """
        Validate if DataFrame has required structure
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        if len(df) == 0:
            raise ValueError("DataFrame is empty")
        
        return True


# Convenience function for quick calculations
def calculate_indicators(df: pd.DataFrame, 
                        include_optional: bool = False,
                        **kwargs) -> Dict[str, any]:
    """
    Convenience function to calculate all indicators with default parameters
    
    Args:
        df: DataFrame with OHLCV data
        include_optional: Include optional indicators
        **kwargs: Custom parameters for IndicatorCalculator
        
    Returns:
        Dictionary with all indicator values
    """
    calculator = IndicatorCalculator(**kwargs)
    return calculator.calculate_all(df, include_optional=include_optional)


if __name__ == "__main__":
    # Test with sample data
    import random
    from datetime import datetime, timedelta
    
    print("="*70)
    print("INDICATOR CALCULATOR - COMPREHENSIVE TEST")
    print("="*70)
    
    # Generate sample OHLCV data
    dates = pd.date_range(end=datetime.now(), periods=250, freq='D')
    base_price = 85000
    base_volume = 2000000
    
    data = []
    for i in range(250):
        change = random.uniform(-0.02, 0.02)
        close = base_price * (1 + change)
        volatility = random.uniform(0.005, 0.015)
        
        # Simulate volume spike occasionally
        if random.random() < 0.1:
            volume = base_volume * random.uniform(2.0, 3.0)
        else:
            volume = base_volume * random.uniform(0.7, 1.3)
        
        data.append({
            'timestamp': int(dates[i].timestamp()),
            'open': base_price,
            'high': close * (1 + volatility),
            'low': close * (1 - volatility),
            'close': close,
            'volume': int(volume)
        })
        base_price = close
    
    df = pd.DataFrame(data)
    
    # Test 1: Calculate all indicators (core only)
    print("\n" + "="*70)
    print("TEST 1: Core Indicators (for Signal Generation)")
    print("="*70)
    
    calculator = IndicatorCalculator()
    indicators = calculator.calculate_for_signal(df)
    
    print("\n📊 LAYER 1: TREND INDICATORS")
    print(f"  MA 200: {indicators['ma_200']:,.0f}")
    print(f"  EMA 20: {indicators['ema_20']:,.0f}")
    print(f"  Trend Direction: {indicators['trend_direction']}")
    print(f"  Trend Strength: {indicators['trend_strength']}")
    print(f"  Support: {indicators['support_level']:,.0f}")
    print(f"  Resistance: {indicators['resistance_level']:,.0f}")
    
    print("\n📈 LAYER 2: MOMENTUM INDICATORS")
    print(f"  RSI 14: {indicators['rsi_14']}")
    print(f"  RSI Signal: {indicators['rsi_signal']}")
    print(f"  MACD Line: {indicators['macd_line']}")
    print(f"  MACD Signal: {indicators['macd_signal']}")
    print(f"  MACD Histogram: {indicators['macd_histogram']}")
    print(f"  MACD Trend: {indicators['macd_trend']}")
    
    print("\n🎪 LAYER 4: VOLATILITY INDICATORS")
    print(f"  BB Upper: {indicators['bb_upper']:,.0f}")
    print(f"  BB Middle: {indicators['bb_middle']:,.0f}")
    print(f"  BB Lower: {indicators['bb_lower']:,.0f}")
    print(f"  BB Width: {indicators['bb_width']}%")
    print(f"  BB Position: {indicators['bb_position']} ({indicators['bb_position_label']})")
    
    print("\n💰 LAYER 3: VOLUME INDICATORS")
    print(f"  Volume MA 20: {indicators['volume_ma_20']:,.0f}")
    print(f"  Volume Ratio: {indicators['volume_ratio']}")
    print(f"  Volume Signal: {indicators['volume_signal']}")
    print(f"  Volume Spike: {indicators['volume_spike']}")
    
    # Test 2: Calculate with optional indicators
    print("\n" + "="*70)
    print("TEST 2: All Indicators (including optional)")
    print("="*70)
    
    indicators_full = calculator.calculate_all(df, include_optional=True)
    
    print("\n🔬 OPTIONAL INDICATORS:")
    if 'atr' in indicators_full:
        print(f"  ATR: {indicators_full['atr']}")
    if 'obv' in indicators_full:
        print(f"  OBV: {indicators_full['obv']:,.0f}")
        print(f"  OBV Trend: {indicators_full.get('obv_trend', 'N/A')}")
    if 'vwap' in indicators_full:
        print(f"  VWAP: {indicators_full['vwap']:,.0f}")
        print(f"  Price vs VWAP: {indicators_full.get('price_vs_vwap', 'N/A')}")
    
    # Test 3: Historical calculation (for backtesting)
    print("\n" + "="*70)
    print("TEST 3: Historical Calculation (last 10 periods)")
    print("="*70)
    
    df_with_indicators = calculator.calculate_with_history(df, lookback=10)
    print(f"\nDataFrame shape: {df_with_indicators.shape}")
    print(f"Columns: {list(df_with_indicators.columns)}")
    print("\nLast 3 rows:")
    print(df_with_indicators[['close', 'MA_200', 'EMA_20', 'RSI_14', 'MACD']].tail(3))
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)
