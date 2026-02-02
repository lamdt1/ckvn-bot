"""
Position Manager
Manages open positions, tracks P&L, checks stop-loss and take-profit
"""

import sys
sys.path.insert(0, '/Volumes/Data/projects/ckbot')

from typing import List, Dict, Optional
from datetime import datetime
import logging

from database.db_manager import TradingDatabase

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Position:
    """Represents an open trading position"""
    
    def __init__(self, signal_id: int, symbol: str, entry_price: float,
                 quantity: int, stop_loss: float, take_profit: float,
                 entry_timestamp: int):
        self.signal_id = signal_id
        self.symbol = symbol
        self.entry_price = entry_price
        self.quantity = quantity
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.entry_timestamp = entry_timestamp
        
        self.current_price = entry_price
        self.unrealized_pnl = 0.0
        self.unrealized_pnl_pct = 0.0
    
    def update_price(self, current_price: float):
        """Update current price and calculate P&L"""
        self.current_price = current_price
        self.unrealized_pnl = (current_price - self.entry_price) * self.quantity
        self.unrealized_pnl_pct = ((current_price - self.entry_price) / self.entry_price) * 100
    
    def should_close(self) -> tuple[bool, str]:
        """
        Check if position should be closed
        
        Returns:
            (should_close, reason)
        """
        # Check stop-loss
        if self.current_price <= self.stop_loss:
            return True, f"STOP_LOSS (price {self.current_price:,.0f} <= SL {self.stop_loss:,.0f})"
        
        # Check take-profit
        if self.current_price >= self.take_profit:
            return True, f"TAKE_PROFIT (price {self.current_price:,.0f} >= TP {self.take_profit:,.0f})"
        
        return False, ""
    
    def get_holding_days(self) -> int:
        """Calculate holding days"""
        current_timestamp = int(datetime.now().timestamp())
        days = (current_timestamp - self.entry_timestamp) / (24 * 3600)
        return int(days)
    
    def __str__(self) -> str:
        return (f"Position({self.symbol}, entry={self.entry_price:,.0f}, "
                f"current={self.current_price:,.0f}, "
                f"P&L={self.unrealized_pnl_pct:+.2f}%)")


class PositionManager:
    """
    Manages open trading positions
    
    Features:
    - Track open positions
    - Update prices and P&L
    - Check stop-loss and take-profit
    - Close positions
    - Generate position reports
    """
    
    def __init__(self, db_path: str = 'database/trading.db'):
        """
        Initialize position manager
        
        Args:
            db_path: Path to database
        """
        self.db = TradingDatabase(db_path=db_path)
        self.positions: Dict[str, Position] = {}
        
        logger.info("✅ PositionManager initialized")
    
    def load_open_positions(self):
        """Load open positions from database"""
        try:
            self.db.connect()
            
            # Query open signals
            open_signals = self.db.execute_query("""
                SELECT 
                    id,
                    symbol,
                    price_at_signal,
                    suggested_stop_loss,
                    suggested_take_profit,
                    timestamp,
                    execution_price,
                    position_size_pct
                FROM signals
                WHERE is_executed = 1 AND is_closed = 0
                ORDER BY timestamp DESC
            """)
            
            self.positions = {}
            
            for sig in open_signals:
                signal_id = sig['id']
                symbol = sig['symbol']
                entry_price = sig['execution_price'] or sig['price_at_signal']
                stop_loss = sig['suggested_stop_loss']
                take_profit = sig['suggested_take_profit']
                timestamp = sig['timestamp']
                
                # Estimate quantity (simplified - in real app, get from execution)
                quantity = 100  # Placeholder
                
                position = Position(
                    signal_id=signal_id,
                    symbol=symbol,
                    entry_price=entry_price,
                    quantity=quantity,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    entry_timestamp=timestamp
                )
                
                self.positions[symbol] = position
            
            self.db.disconnect()
            
            logger.info(f"📊 Loaded {len(self.positions)} open positions")
            return self.positions
            
        except Exception as e:
            logger.error(f"Error loading open positions: {e}")
            return {}
    
    def update_positions(self, price_data: Dict[str, float]):
        """
        Update positions with current prices
        
        Args:
            price_data: Dictionary mapping symbol to current price
        """
        for symbol, position in self.positions.items():
            if symbol in price_data:
                position.update_price(price_data[symbol])
                logger.debug(f"Updated {symbol}: {position.current_price:,.0f} ({position.unrealized_pnl_pct:+.2f}%)")
    
    def check_positions(self) -> List[Dict]:
        """
        Check all positions for stop-loss or take-profit triggers
        
        Returns:
            List of positions to close with reasons
        """
        to_close = []
        
        for symbol, position in self.positions.items():
            should_close, reason = position.should_close()
            
            if should_close:
                to_close.append({
                    'position': position,
                    'reason': reason
                })
                logger.info(f"🔔 {symbol}: {reason}")
        
        return to_close
    
    def close_position(self, symbol: str, close_price: float, reason: str):
        """
        Close a position
        
        Args:
            symbol: Stock symbol
            close_price: Closing price
            reason: Reason for closing
        """
        if symbol not in self.positions:
            logger.warning(f"Position {symbol} not found")
            return
        
        position = self.positions[symbol]
        
        try:
            self.db.connect()
            
            # Calculate final P&L
            profit_loss = (close_price - position.entry_price) * position.quantity
            profit_loss_pct = ((close_price - position.entry_price) / position.entry_price) * 100
            holding_days = position.get_holding_days()
            
            # Update signal in database
            self.db.execute_update("""
                UPDATE signals
                SET 
                    is_closed = 1,
                    close_price = ?,
                    close_timestamp = ?,
                    profit_loss_pct = ?,
                    holding_days = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                close_price,
                int(datetime.now().timestamp()),
                profit_loss_pct,
                holding_days,
                int(datetime.now().timestamp()),
                position.signal_id
            ))
            
            self.db.disconnect()
            
            # Remove from open positions
            del self.positions[symbol]
            
            logger.info(f"✅ Closed {symbol}: {profit_loss_pct:+.2f}% ({reason})")
            
        except Exception as e:
            logger.error(f"Error closing position {symbol}: {e}")
    
    def close_all_positions(self, price_data: Dict[str, float], reason: str = "Manual close"):
        """
        Close all open positions
        
        Args:
            price_data: Dictionary mapping symbol to current price
            reason: Reason for closing
        """
        symbols_to_close = list(self.positions.keys())
        
        for symbol in symbols_to_close:
            if symbol in price_data:
                self.close_position(symbol, price_data[symbol], reason)
    
    def get_total_pnl(self) -> tuple[float, float]:
        """
        Calculate total unrealized P&L
        
        Returns:
            (total_pnl_amount, total_pnl_pct)
        """
        total_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
        
        # Calculate weighted average P&L %
        if self.positions:
            total_value = sum(pos.entry_price * pos.quantity for pos in self.positions.values())
            total_pnl_pct = (total_pnl / total_value * 100) if total_value > 0 else 0.0
        else:
            total_pnl_pct = 0.0
        
        return total_pnl, total_pnl_pct
    
    def print_positions(self):
        """Print current positions"""
        if not self.positions:
            print("\n📊 No open positions")
            return
        
        print("\n" + "="*80)
        print(f"📊 OPEN POSITIONS ({len(self.positions)})")
        print("="*80)
        
        print(f"\n{'Symbol':<8} {'Entry':<12} {'Current':<12} {'SL':<12} {'TP':<12} {'P&L%':<10} {'Days':<6}")
        print("-"*80)
        
        for symbol, pos in self.positions.items():
            print(f"{symbol:<8} {pos.entry_price:>10,.0f}  {pos.current_price:>10,.0f}  "
                  f"{pos.stop_loss:>10,.0f}  {pos.take_profit:>10,.0f}  "
                  f"{pos.unrealized_pnl_pct:>8.2f}%  {pos.get_holding_days():<6}")
        
        # Total P&L
        total_pnl, total_pnl_pct = self.get_total_pnl()
        print("-"*80)
        print(f"{'TOTAL':<8} {'':<12} {'':<12} {'':<12} {'':<12} {total_pnl_pct:>8.2f}%")
        
        print("\n" + "="*80)


if __name__ == "__main__":
    # Test position manager
    print("="*70)
    print("POSITION MANAGER TEST")
    print("="*70)
    
    # Initialize manager
    manager = PositionManager()
    
    # Create sample positions (in real app, these come from database)
    print("\nCreating sample positions...")
    
    # Manually add positions for testing
    manager.positions = {
        'VNM': Position(
            signal_id=1,
            symbol='VNM',
            entry_price=86000,
            quantity=100,
            stop_loss=81700,
            take_profit=94600,
            entry_timestamp=int(datetime.now().timestamp()) - 86400  # 1 day ago
        ),
        'VCB': Position(
            signal_id=2,
            symbol='VCB',
            entry_price=92000,
            quantity=50,
            stop_loss=87400,
            take_profit=101200,
            entry_timestamp=int(datetime.now().timestamp()) - 172800  # 2 days ago
        )
    }
    
    # Update with current prices
    print("\nUpdating positions with current prices...")
    current_prices = {
        'VNM': 88000,  # +2.3%
        'VCB': 90000   # -2.2%
    }
    
    manager.update_positions(current_prices)
    
    # Print positions
    manager.print_positions()
    
    # Check for triggers
    print("\n" + "="*70)
    print("Checking for stop-loss / take-profit triggers...")
    
    to_close = manager.check_positions()
    
    if to_close:
        print(f"\n⚠️ {len(to_close)} positions to close:")
        for item in to_close:
            print(f"  - {item['position'].symbol}: {item['reason']}")
    else:
        print("\n✅ No positions to close")
    
    print("\n✅ Test completed!")
