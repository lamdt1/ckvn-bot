"""
Bot Package
Main trading bot integration - orchestrates all components
"""

from .data_fetcher import DataFetcher
from .signal_generator import SignalGenerator
from .position_manager import PositionManager
from .notification import NotificationManager
from .config import BotConfig

__all__ = [
    'DataFetcher',
    'SignalGenerator',
    'PositionManager',
    'NotificationManager',
    'BotConfig'
]

__version__ = '1.0.0'
