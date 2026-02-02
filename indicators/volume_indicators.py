"""
Volume Indicators Calculator
Implements volume analysis for Pro Trader strategy
"""

import pandas as pd
import numpy as np
from typing import Dict


class VolumeIndicators:
    """Calculate volume-based indicators"""
    
    @staticmethod
    def calculate_volume_ma(data: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate Volume Moving Average
        
        Args:
            data: Volume series
            period: MA period (default: 20)
            
        Returns:
            Volume MA series
        """
        return data.rolling(window=period, min_periods=period).mean()
    
    @staticmethod
    def calculate_volume_ratio(current_volume: float, volume_ma: float) -> float:
        """
        Calculate volume ratio (current volume / average volume)
        
        Args:
            current_volume: Current volume
            volume_ma: Volume moving average
            
        Returns:
            Volume ratio
        """
        if pd.isna(volume_ma) or volume_ma == 0:
            return 1.0
        
        ratio = current_volume / volume_ma
        return round(ratio, 2)
    
    @staticmethod
    def classify_volume_signal(volume_ratio: float, 
                               high_threshold: float = 1.5,
                               low_threshold: float = 0.7) -> str:
        """
        Classify volume signal
        
        Args:
            volume_ratio: Volume ratio value
            high_threshold: High volume threshold (default: 1.5x average)
            low_threshold: Low volume threshold (default: 0.7x average)
            
        Returns:
            'HIGH', 'NORMAL', or 'LOW'
        """
        if volume_ratio >= high_threshold:
            return 'HIGH'
        elif volume_ratio <= low_threshold:
            return 'LOW'
        else:
            return 'NORMAL'
    
    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.Series:
        """
        Calculate On-Balance Volume (OBV)
        
        Args:
            df: DataFrame with close and volume columns
            
        Returns:
            OBV series
        """
        # Price direction
        price_change = df['close'].diff()
        
        # Volume direction
        volume_direction = pd.Series(index=df.index, dtype=float)
        volume_direction[price_change > 0] = df['volume']
        volume_direction[price_change < 0] = -df['volume']
        volume_direction[price_change == 0] = 0
        
        # Cumulative OBV
        obv = volume_direction.cumsum()
        
        return obv
    
    @staticmethod
    def calculate_vwap(df: pd.DataFrame) -> float:
        """
        Calculate Volume Weighted Average Price (VWAP) for current period
        
        Args:
            df: DataFrame with high, low, close, volume columns
            
        Returns:
            VWAP value
        """
        if not all(col in df.columns for col in ['high', 'low', 'close', 'volume']):
            return None
        
        # Typical price
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        
        # VWAP
        vwap = (typical_price * df['volume']).sum() / df['volume'].sum()
        
        return round(vwap, 2)
    
    @staticmethod
    def detect_volume_spike(df: pd.DataFrame, lookback: int = 20, threshold: float = 2.0) -> bool:
        """
        Detect if there's a volume spike
        
        Args:
            df: DataFrame with volume column
            lookback: Number of periods to look back
            threshold: Spike threshold (default: 2x average)
            
        Returns:
            True if volume spike detected
        """
        if len(df) < lookback + 1:
            return False
        
        recent_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].iloc[-lookback-1:-1].mean()
        
        return recent_volume >= (avg_volume * threshold)
    
    @classmethod
    def calculate_all(cls, df: pd.DataFrame, 
                     volume_ma_period: int = 20,
                     include_obv: bool = False,
                     include_vwap: bool = False) -> Dict[str, any]:
        """
        Calculate all volume indicators
        
        Args:
            df: DataFrame with OHLCV data
            volume_ma_period: Volume MA period (default: 20)
            include_obv: Include OBV calculation (default: False)
            include_vwap: Include VWAP calculation (default: False)
            
        Returns:
            Dictionary with all volume indicators
        """
        if 'volume' not in df.columns:
            raise ValueError("DataFrame must have 'volume' column")
        
        # Calculate Volume MA
        df['Volume_MA_20'] = cls.calculate_volume_ma(df['volume'], volume_ma_period)
        
        # Get latest values
        latest = df.iloc[-1]
        current_volume = latest['volume']
        volume_ma = latest['Volume_MA_20']
        
        # Calculate volume ratio and signal
        volume_ratio = cls.calculate_volume_ratio(current_volume, volume_ma)
        volume_signal = cls.classify_volume_signal(volume_ratio)
        
        # Detect volume spike
        volume_spike = cls.detect_volume_spike(df, lookback=volume_ma_period)
        
        result = {
            'volume_ma_20': round(volume_ma, 0) if not pd.isna(volume_ma) else None,
            'volume_ratio': volume_ratio,
            'volume_signal': volume_signal,
            'volume_spike': volume_spike
        }
        
        # Optional: Include OBV
        if include_obv and 'close' in df.columns:
            df['OBV'] = cls.calculate_obv(df)
            obv_value = df['OBV'].iloc[-1]
            result['obv'] = round(obv_value, 0) if not pd.isna(obv_value) else None
            
            # OBV trend (compare with 20-period MA)
            obv_ma = df['OBV'].rolling(window=20, min_periods=20).mean().iloc[-1]
            if not pd.isna(obv_ma):
                result['obv_trend'] = 'UP' if obv_value > obv_ma else 'DOWN'
        
        # Optional: Include VWAP
        if include_vwap and all(col in df.columns for col in ['high', 'low', 'close']):
            # Calculate VWAP for last 20 periods
            vwap_df = df.tail(volume_ma_period)
            vwap_value = cls.calculate_vwap(vwap_df)
            result['vwap'] = vwap_value
            
            # Price vs VWAP
            if vwap_value:
                current_price = latest['close']
                result['price_vs_vwap'] = 'ABOVE' if current_price > vwap_value else 'BELOW'
        
        return result


if __name__ == "__main__":
    # Test with sample data
    import random
    from datetime import datetime, timedelta
    
    # Generate sample OHLCV data
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    base_price = 85000
    base_volume = 2000000
    
    data = []
    for i in range(100):
        change = random.uniform(-0.02, 0.02)
        close = base_price * (1 + change)
        
        # Simulate volume spike at random intervals
        if random.random() < 0.1:  # 10% chance of spike
            volume = base_volume * random.uniform(2.0, 3.0)
        else:
            volume = base_volume * random.uniform(0.7, 1.3)
        
        data.append({
            'timestamp': int(dates[i].timestamp()),
            'open': base_price,
            'high': max(base_price, close) * 1.01,
            'low': min(base_price, close) * 0.99,
            'close': close,
            'volume': int(volume)
        })
        base_price = close
    
    df = pd.DataFrame(data)
    
    # Calculate indicators
    indicators = VolumeIndicators.calculate_all(df, include_obv=True, include_vwap=True)
    
    print("Volume Indicators Test:")
    print(f"  Volume MA 20: {indicators['volume_ma_20']:,.0f}")
    print(f"  Volume Ratio: {indicators['volume_ratio']}")
    print(f"  Volume Signal: {indicators['volume_signal']}")
    print(f"  Volume Spike: {indicators['volume_spike']}")
    print(f"  OBV: {indicators.get('obv', 'N/A'):,.0f}" if indicators.get('obv') else "  OBV: N/A")
    print(f"  OBV Trend: {indicators.get('obv_trend', 'N/A')}")
    print(f"  VWAP: {indicators.get('vwap', 'N/A'):,.0f}" if indicators.get('vwap') else "  VWAP: N/A")
    print(f"  Price vs VWAP: {indicators.get('price_vs_vwap', 'N/A')}")
