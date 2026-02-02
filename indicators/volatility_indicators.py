"""
Volatility Indicators Calculator
Implements Bollinger Bands for Pro Trader strategy
"""

import pandas as pd
import numpy as np
from typing import Dict


class VolatilityIndicators:
    """Calculate volatility-based indicators"""
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, 
                                  period: int = 20, 
                                  num_std: float = 2.0) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Args:
            data: Price series
            period: MA period (default: 20)
            num_std: Number of standard deviations (default: 2.0)
            
        Returns:
            Dictionary with upper, middle, and lower bands
        """
        # Middle band (SMA)
        middle_band = data.rolling(window=period, min_periods=period).mean()
        
        # Standard deviation
        std = data.rolling(window=period, min_periods=period).std()
        
        # Upper and lower bands
        upper_band = middle_band + (std * num_std)
        lower_band = middle_band - (std * num_std)
        
        return {
            'bb_upper': upper_band,
            'bb_middle': middle_band,
            'bb_lower': lower_band
        }
    
    @staticmethod
    def calculate_bb_width(upper: float, lower: float, middle: float) -> float:
        """
        Calculate Bollinger Band width (volatility measure)
        
        Args:
            upper: Upper band value
            lower: Lower band value
            middle: Middle band value
            
        Returns:
            BB width as percentage
        """
        if pd.isna(upper) or pd.isna(lower) or pd.isna(middle) or middle == 0:
            return 0.0
        
        width = ((upper - lower) / middle) * 100
        return round(width, 2)
    
    @staticmethod
    def calculate_bb_position(price: float, upper: float, lower: float) -> float:
        """
        Calculate price position within Bollinger Bands (0-1)
        
        Args:
            price: Current price
            upper: Upper band value
            lower: Lower band value
            
        Returns:
            Position (0 = at lower band, 1 = at upper band, 0.5 = middle)
        """
        if pd.isna(upper) or pd.isna(lower) or upper == lower:
            return 0.5
        
        position = (price - lower) / (upper - lower)
        
        # Clamp to 0-1 range
        position = max(0.0, min(1.0, position))
        
        return round(position, 3)
    
    @staticmethod
    def classify_bb_position(bb_position: float) -> str:
        """
        Classify price position in Bollinger Bands
        
        Args:
            bb_position: Position value (0-1)
            
        Returns:
            'NEAR_LOWER', 'BELOW_MIDDLE', 'AROUND_MIDDLE', 'ABOVE_MIDDLE', 'NEAR_UPPER'
        """
        if bb_position < 0.2:
            return 'NEAR_LOWER'
        elif bb_position < 0.4:
            return 'BELOW_MIDDLE'
        elif bb_position < 0.6:
            return 'AROUND_MIDDLE'
        elif bb_position < 0.8:
            return 'ABOVE_MIDDLE'
        else:
            return 'NEAR_UPPER'
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range (ATR) - Optional volatility measure
        
        Args:
            df: DataFrame with high, low, close columns
            period: ATR period (default: 14)
            
        Returns:
            ATR series
        """
        # True Range calculation
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        
        # ATR is EMA of True Range
        atr = true_range.ewm(span=period, adjust=False, min_periods=period).mean()
        
        return atr
    
    @classmethod
    def calculate_all(cls, df: pd.DataFrame, 
                     bb_period: int = 20,
                     bb_std: float = 2.0,
                     atr_period: int = 14,
                     include_atr: bool = False) -> Dict[str, any]:
        """
        Calculate all volatility indicators
        
        Args:
            df: DataFrame with OHLC data
            bb_period: Bollinger Bands period (default: 20)
            bb_std: Bollinger Bands standard deviation (default: 2.0)
            atr_period: ATR period (default: 14)
            include_atr: Include ATR calculation (default: False)
            
        Returns:
            Dictionary with all volatility indicators
        """
        if 'close' not in df.columns:
            raise ValueError("DataFrame must have 'close' column")
        
        # Calculate Bollinger Bands
        bb_data = cls.calculate_bollinger_bands(df['close'], bb_period, bb_std)
        df['BB_upper'] = bb_data['bb_upper']
        df['BB_middle'] = bb_data['bb_middle']
        df['BB_lower'] = bb_data['bb_lower']
        
        # Get latest values
        latest = df.iloc[-1]
        current_price = latest['close']
        bb_upper = latest['BB_upper']
        bb_middle = latest['BB_middle']
        bb_lower = latest['BB_lower']
        
        # Calculate BB metrics
        bb_width = cls.calculate_bb_width(bb_upper, bb_lower, bb_middle)
        bb_position = cls.calculate_bb_position(current_price, bb_upper, bb_lower)
        bb_position_label = cls.classify_bb_position(bb_position)
        
        result = {
            'bb_upper': round(bb_upper, 2) if not pd.isna(bb_upper) else None,
            'bb_middle': round(bb_middle, 2) if not pd.isna(bb_middle) else None,
            'bb_lower': round(bb_lower, 2) if not pd.isna(bb_lower) else None,
            'bb_width': bb_width,
            'bb_position': bb_position,
            'bb_position_label': bb_position_label
        }
        
        # Optional: Include ATR
        if include_atr and all(col in df.columns for col in ['high', 'low']):
            df['ATR'] = cls.calculate_atr(df, atr_period)
            atr_value = df['ATR'].iloc[-1]
            result['atr'] = round(atr_value, 2) if not pd.isna(atr_value) else None
        
        return result


if __name__ == "__main__":
    # Test with sample data
    import random
    from datetime import datetime, timedelta
    
    # Generate sample OHLC data
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    base_price = 85000
    
    data = []
    for i in range(100):
        change = random.uniform(-0.02, 0.02)
        close = base_price * (1 + change)
        volatility = random.uniform(0.005, 0.015)
        
        data.append({
            'timestamp': int(dates[i].timestamp()),
            'open': base_price,
            'high': close * (1 + volatility),
            'low': close * (1 - volatility),
            'close': close,
            'volume': random.randint(1000000, 5000000)
        })
        base_price = close
    
    df = pd.DataFrame(data)
    
    # Calculate indicators
    indicators = VolatilityIndicators.calculate_all(df, include_atr=True)
    
    print("Volatility Indicators Test:")
    print(f"  BB Upper: {indicators['bb_upper']:,.0f}")
    print(f"  BB Middle: {indicators['bb_middle']:,.0f}")
    print(f"  BB Lower: {indicators['bb_lower']:,.0f}")
    print(f"  BB Width: {indicators['bb_width']}%")
    print(f"  BB Position: {indicators['bb_position']} ({indicators['bb_position_label']})")
    print(f"  ATR: {indicators.get('atr', 'N/A')}")
