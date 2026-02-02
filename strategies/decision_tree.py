"""
Decision Tree Base Class
Abstract base for implementing trading decision trees
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from .signal import Signal, SignalType
from .risk_manager import RiskManager


class DecisionTree(ABC):
    """
    Abstract base class for decision tree strategies
    
    Subclasses must implement:
    - evaluate_trend()
    - evaluate_momentum()
    - evaluate_volume()
    - evaluate_entry()
    - calculate_confidence()
    - determine_signal_type()
    """
    
    def __init__(self,
                 strategy_name: str,
                 risk_manager: Optional[RiskManager] = None):
        """
        Initialize decision tree
        
        Args:
            strategy_name: Name of the strategy
            risk_manager: Risk manager instance (creates default if None)
        """
        self.strategy_name = strategy_name
        self.risk_manager = risk_manager or RiskManager()
        
        # Weights for confidence calculation (must sum to 1.0)
        self.weights = {
            'trend': 0.30,
            'momentum': 0.30,
            'volume': 0.20,
            'entry': 0.20
        }
    
    @abstractmethod
    def evaluate_trend(self, indicators: Dict[str, any]) -> Dict[str, any]:
        """
        Evaluate trend layer (Layer 1)
        
        Args:
            indicators: Dictionary with indicator values
            
        Returns:
            Dictionary with:
            - score: 0-100
            - passed: bool
            - reason: str
        """
        pass
    
    @abstractmethod
    def evaluate_momentum(self, indicators: Dict[str, any]) -> Dict[str, any]:
        """
        Evaluate momentum layer (Layer 2)
        
        Args:
            indicators: Dictionary with indicator values
            
        Returns:
            Dictionary with:
            - score: 0-100
            - passed: bool
            - reason: str
        """
        pass
    
    @abstractmethod
    def evaluate_volume(self, indicators: Dict[str, any]) -> Dict[str, any]:
        """
        Evaluate volume layer (Layer 3)
        
        Args:
            indicators: Dictionary with indicator values
            
        Returns:
            Dictionary with:
            - score: 0-100
            - passed: bool
            - reason: str
        """
        pass
    
    @abstractmethod
    def evaluate_entry(self, indicators: Dict[str, any]) -> Dict[str, any]:
        """
        Evaluate entry timing layer (Layer 4)
        
        Args:
            indicators: Dictionary with indicator values
            
        Returns:
            Dictionary with:
            - score: 0-100
            - passed: bool
            - reason: str
        """
        pass
    
    def calculate_confidence(self, 
                            trend_score: float,
                            momentum_score: float,
                            volume_score: float,
                            entry_score: float) -> float:
        """
        Calculate overall confidence score
        
        Args:
            trend_score: Trend layer score (0-100)
            momentum_score: Momentum layer score (0-100)
            volume_score: Volume layer score (0-100)
            entry_score: Entry layer score (0-100)
            
        Returns:
            Weighted confidence score (0-100)
        """
        confidence = (
            trend_score * self.weights['trend'] +
            momentum_score * self.weights['momentum'] +
            volume_score * self.weights['volume'] +
            entry_score * self.weights['entry']
        )
        
        return round(confidence, 2)
    
    @abstractmethod
    def determine_signal_type(self, confidence: float) -> SignalType:
        """
        Determine signal type based on confidence score
        
        Args:
            confidence: Confidence score (0-100)
            
        Returns:
            SignalType
        """
        pass
    
    def generate_signal(self,
                       symbol: str,
                       timeframe: str,
                       timestamp: int,
                       price: float,
                       indicators: Dict[str, any],
                       total_capital: float = 100_000_000) -> Signal:
        """
        Generate trading signal using decision tree
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe ('1D', '4H')
            timestamp: Current timestamp
            price: Current price
            indicators: Dictionary with all indicator values
            total_capital: Total capital for position sizing
            
        Returns:
            Signal object
        """
        # Evaluate all layers
        trend_eval = self.evaluate_trend(indicators)
        momentum_eval = self.evaluate_momentum(indicators)
        volume_eval = self.evaluate_volume(indicators)
        entry_eval = self.evaluate_entry(indicators)
        
        # Calculate confidence
        confidence = self.calculate_confidence(
            trend_eval['score'],
            momentum_eval['score'],
            volume_eval['score'],
            entry_eval['score']
        )
        
        # Determine signal type
        signal_type = self.determine_signal_type(confidence)
        
        # Build reasoning
        reasoning = {
            'trend_direction': indicators.get('trend_direction'),
            'trend_score': trend_eval['score'],
            'trend_reason': trend_eval['reason'],
            
            'rsi_signal': indicators.get('rsi_signal'),
            'rsi_value': indicators.get('rsi_14'),
            'macd_trend': indicators.get('macd_trend'),
            'momentum_score': momentum_eval['score'],
            'momentum_reason': momentum_eval['reason'],
            
            'volume_signal': indicators.get('volume_signal'),
            'volume_ratio': indicators.get('volume_ratio'),
            'volume_score': volume_eval['score'],
            'volume_reason': volume_eval['reason'],
            
            'bb_position': indicators.get('bb_position'),
            'bb_position_label': indicators.get('bb_position_label'),
            'entry_score': entry_eval['score'],
            'entry_reason': entry_eval['reason']
        }
        
        # Conditions met
        conditions_met = []
        if trend_eval['passed']:
            conditions_met.append('trend_favorable')
        if momentum_eval['passed']:
            conditions_met.append('momentum_strong')
        if volume_eval['passed']:
            conditions_met.append('volume_confirmed')
        if entry_eval['passed']:
            conditions_met.append('entry_timing_good')
        
        # Calculate risk management parameters
        risk_params = self.risk_manager.calculate_all(
            price, indicators, total_capital, confidence
        )
        
        # Create signal
        signal = Signal(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=timestamp,
            signal_type=signal_type,
            price=price,
            confidence_score=confidence,
            strategy_name=self.strategy_name,
            reasoning=reasoning,
            conditions_met=conditions_met,
            stop_loss=risk_params['stop_loss'],
            take_profit=risk_params['take_profit'],
            position_size_pct=risk_params['position_size_pct'],
            risk_reward_ratio=risk_params['risk_reward_ratio']
        )
        
        return signal
    
    def set_weights(self, 
                   trend: float = 0.30,
                   momentum: float = 0.30,
                   volume: float = 0.20,
                   entry: float = 0.20):
        """
        Set custom weights for confidence calculation
        
        Args:
            trend: Trend weight (default: 0.30)
            momentum: Momentum weight (default: 0.30)
            volume: Volume weight (default: 0.20)
            entry: Entry weight (default: 0.20)
        """
        total = trend + momentum + volume + entry
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        
        self.weights = {
            'trend': trend,
            'momentum': momentum,
            'volume': volume,
            'entry': entry
        }
