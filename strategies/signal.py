"""
Signal Data Class
Represents a trading signal with all metadata
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional, List
from datetime import datetime


class SignalType(Enum):
    """Signal type enumeration"""
    STRONG_BUY = "STRONG_BUY"
    WEAK_BUY = "WEAK_BUY"
    WATCH = "WATCH"
    NO_ACTION = "NO_ACTION"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


@dataclass
class Signal:
    """
    Trading signal with complete metadata
    
    Attributes:
        symbol: Stock symbol
        timeframe: Timeframe used for signal ('1D', '4H')
        timestamp: Signal generation timestamp
        signal_type: Type of signal (STRONG_BUY, WEAK_BUY, etc.)
        price: Price at signal generation
        confidence_score: Confidence score (0-100)
        strategy_name: Name of strategy used
        
        # Reasoning
        reasoning: Dictionary with decision tree reasoning
        conditions_met: List of conditions that were met
        
        # Risk Management
        stop_loss: Suggested stop-loss price
        take_profit: Suggested take-profit price
        position_size_pct: Suggested position size (% of capital)
        risk_reward_ratio: Risk/Reward ratio
        
        # Metadata
        created_at: Creation timestamp
    """
    symbol: str
    timeframe: str
    timestamp: int
    signal_type: SignalType
    price: float
    confidence_score: float
    strategy_name: str
    
    # Reasoning
    reasoning: Dict[str, any]
    conditions_met: List[str]
    
    # Risk Management
    stop_loss: float
    take_profit: float
    position_size_pct: float
    risk_reward_ratio: float
    
    # Metadata
    created_at: Optional[int] = None
    
    def __post_init__(self):
        """Set created_at if not provided"""
        if self.created_at is None:
            self.created_at = int(datetime.now().timestamp())
    
    def to_dict(self) -> Dict[str, any]:
        """Convert signal to dictionary for database storage"""
        return {
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'timestamp': self.timestamp,
            'signal_type': self.signal_type.value,
            'price_at_signal': self.price,
            'confidence_score': self.confidence_score,
            'strategy_name': self.strategy_name,
            'reasoning': self.reasoning,
            'conditions_met': self.conditions_met,
            'suggested_stop_loss': self.stop_loss,
            'suggested_take_profit': self.take_profit,
            'position_size_pct': self.position_size_pct,
            'risk_reward_ratio': self.risk_reward_ratio
        }
    
    def is_buy_signal(self) -> bool:
        """Check if this is a buy signal"""
        return self.signal_type in [SignalType.STRONG_BUY, SignalType.WEAK_BUY]
    
    def is_sell_signal(self) -> bool:
        """Check if this is a sell signal"""
        return self.signal_type in [SignalType.SELL, SignalType.STRONG_SELL]
    
    def is_actionable(self) -> bool:
        """Check if this signal requires action"""
        return self.signal_type != SignalType.NO_ACTION
    
    def get_potential_profit_pct(self) -> float:
        """Calculate potential profit percentage"""
        return ((self.take_profit - self.price) / self.price) * 100
    
    def get_potential_loss_pct(self) -> float:
        """Calculate potential loss percentage"""
        return ((self.price - self.stop_loss) / self.price) * 100
    
    def __str__(self) -> str:
        """String representation"""
        return (f"Signal({self.symbol}, {self.signal_type.value}, "
                f"confidence={self.confidence_score:.1f}%, "
                f"price={self.price:,.0f})")
    
    def __repr__(self) -> str:
        """Detailed representation"""
        return self.__str__()


if __name__ == "__main__":
    # Test Signal class
    signal = Signal(
        symbol="VNM",
        timeframe="1D",
        timestamp=int(datetime.now().timestamp()),
        signal_type=SignalType.STRONG_BUY,
        price=86000,
        confidence_score=85.5,
        strategy_name="Pro Trader - Trend Following",
        reasoning={
            'trend_direction': 'UP',
            'rsi_signal': 'NEUTRAL',
            'macd_trend': 'BULLISH',
            'volume_signal': 'HIGH'
        },
        conditions_met=['trend_up', 'momentum_strong', 'volume_confirmed'],
        stop_loss=81700,
        take_profit=94600,
        position_size_pct=5.0,
        risk_reward_ratio=2.0
    )
    
    print("Signal Test:")
    print(f"  {signal}")
    print(f"  Is Buy: {signal.is_buy_signal()}")
    print(f"  Is Actionable: {signal.is_actionable()}")
    print(f"  Potential Profit: {signal.get_potential_profit_pct():.2f}%")
    print(f"  Potential Loss: {signal.get_potential_loss_pct():.2f}%")
    print(f"\n  Dict format:")
    for key, value in signal.to_dict().items():
        print(f"    {key}: {value}")
