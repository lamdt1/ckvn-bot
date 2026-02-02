"""
Database Manager for Trading Bot
Handles SQLite database initialization, migrations, and common operations
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingDatabase:
    """Main database manager for trading bot"""
    
    def __init__(self, db_path: str = "database/trading.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
        
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False
        )
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        logger.info(f"Connected to database: {self.db_path}")
        
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
            
    def run_migration(self, migration_file: str = "database/migrations/001_create_trading_schema.sql"):
        """
        Run migration script to create/update schema
        
        Args:
            migration_file: Path to SQL migration file
        """
        if not self.conn:
            self.connect()
            
        migration_path = Path(migration_file)
        if not migration_path.exists():
            raise FileNotFoundError(f"Migration file not found: {migration_file}")
            
        with open(migration_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            
        try:
            self.conn.executescript(sql_script)
            self.conn.commit()
            logger.info(f"Migration completed successfully: {migration_file}")
        except sqlite3.Error as e:
            logger.error(f"Migration failed: {e}")
            raise
            
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """
        Execute SELECT query and return results
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of rows
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
        
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Execute INSERT/UPDATE/DELETE query
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor.rowcount
        
    def insert_price_data(self, symbol: str, timeframe: str, timestamp: int,
                         open_price: float, high: float, low: float, 
                         close: float, volume: int) -> int:
        """
        Insert stock price data
        
        Args:
            symbol: Stock symbol
            timeframe: '1D' or '4H'
            timestamp: Unix timestamp
            open_price, high, low, close: OHLC prices
            volume: Trading volume
            
        Returns:
            Inserted row ID
        """
        query = """
        INSERT OR REPLACE INTO stock_prices 
        (symbol, timeframe, timestamp, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (symbol, timeframe, timestamp, open_price, high, low, close, volume))
        self.conn.commit()
        return cursor.lastrowid
        
    def insert_indicators(self, symbol: str, timeframe: str, timestamp: int,
                         indicators: Dict[str, Any]) -> int:
        """
        Insert calculated indicators
        
        Args:
            symbol: Stock symbol
            timeframe: '1D' or '4H'
            timestamp: Unix timestamp
            indicators: Dictionary of indicator values
            
        Returns:
            Inserted row ID
        """
        # Build dynamic query based on provided indicators
        columns = ['symbol', 'timeframe', 'timestamp'] + list(indicators.keys())
        placeholders = ', '.join(['?'] * len(columns))
        values = [symbol, timeframe, timestamp] + list(indicators.values())
        
        query = f"""
        INSERT OR REPLACE INTO indicators 
        ({', '.join(columns)})
        VALUES ({placeholders})
        """
        
        cursor = self.conn.cursor()
        cursor.execute(query, values)
        self.conn.commit()
        return cursor.lastrowid
        
    def create_signal(self, symbol: str, timeframe: str, timestamp: int,
                     signal_type: str, price: float, 
                     reasoning: Dict[str, Any],
                     **kwargs) -> int:
        """
        Create a new trading signal
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe used for signal
            timestamp: Signal generation timestamp
            signal_type: 'STRONG_BUY', 'WEAK_BUY', 'WATCH', 'SELL', 'NO_ACTION'
            price: Price at signal generation
            reasoning: Dictionary with decision tree reasoning
            **kwargs: Additional signal parameters (confidence_score, stop_loss, etc.)
            
        Returns:
            Signal ID
        """
        query = """
        INSERT INTO signals 
        (symbol, timeframe, timestamp, signal_type, price_at_signal, reasoning,
         confidence_score, strategy_name, suggested_stop_loss, suggested_take_profit,
         position_size_pct, risk_reward_ratio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor = self.conn.cursor()
        cursor.execute(query, (
            symbol, timeframe, timestamp, signal_type, price,
            json.dumps(reasoning),
            kwargs.get('confidence_score'),
            kwargs.get('strategy_name'),
            kwargs.get('suggested_stop_loss'),
            kwargs.get('suggested_take_profit'),
            kwargs.get('position_size_pct'),
            kwargs.get('risk_reward_ratio')
        ))
        self.conn.commit()
        return cursor.lastrowid
        
    def execute_signal(self, signal_id: int, execution_price: float, 
                      execution_timestamp: Optional[int] = None) -> bool:
        """
        Mark signal as executed
        
        Args:
            signal_id: Signal ID
            execution_price: Actual execution price
            execution_timestamp: Execution time (default: now)
            
        Returns:
            Success status
        """
        if execution_timestamp is None:
            execution_timestamp = int(datetime.now().timestamp())
            
        query = """
        UPDATE signals 
        SET is_executed = 1, executed_at = ?, execution_price = ?
        WHERE id = ?
        """
        
        rows = self.execute_update(query, (execution_timestamp, execution_price, signal_id))
        return rows > 0
        
    def close_signal(self, signal_id: int, close_price: float, 
                    close_reason: str, close_timestamp: Optional[int] = None) -> bool:
        """
        Close a signal/position
        
        Args:
            signal_id: Signal ID
            close_price: Close price
            close_reason: 'TAKE_PROFIT', 'STOP_LOSS', 'MANUAL', 'TIMEOUT'
            close_timestamp: Close time (default: now)
            
        Returns:
            Success status
        """
        if close_timestamp is None:
            close_timestamp = int(datetime.now().timestamp())
            
        # Get execution price to calculate P&L
        signal = self.execute_query(
            "SELECT execution_price FROM signals WHERE id = ?", 
            (signal_id,)
        )
        
        if not signal:
            return False
            
        execution_price = signal[0]['execution_price']
        profit_loss_pct = ((close_price - execution_price) / execution_price) * 100
        
        query = """
        UPDATE signals 
        SET is_closed = 1, closed_at = ?, close_price = ?, 
            close_reason = ?, profit_loss_pct = ?
        WHERE id = ?
        """
        
        rows = self.execute_update(
            query, 
            (close_timestamp, close_price, close_reason, profit_loss_pct, signal_id)
        )
        return rows > 0
        
    def get_open_positions(self) -> List[Dict[str, Any]]:
        """
        Get all open positions
        
        Returns:
            List of open position dictionaries
        """
        rows = self.execute_query("SELECT * FROM v_open_positions")
        return [dict(row) for row in rows]
        
    def get_strategy_performance(self) -> List[Dict[str, Any]]:
        """
        Get performance summary by strategy
        
        Returns:
            List of strategy performance dictionaries
        """
        rows = self.execute_query("SELECT * FROM v_strategy_performance")
        return [dict(row) for row in rows]
        
    def get_symbol_performance(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get performance by symbol
        
        Args:
            symbol: Specific symbol (optional, returns all if None)
            
        Returns:
            List of symbol performance dictionaries
        """
        if symbol:
            query = "SELECT * FROM v_symbol_performance WHERE symbol = ?"
            rows = self.execute_query(query, (symbol,))
        else:
            rows = self.execute_query("SELECT * FROM v_symbol_performance")
            
        return [dict(row) for row in rows]
        
    def get_indicator_combination_performance(self, min_trades: int = 5) -> List[Dict[str, Any]]:
        """
        Get performance by indicator combinations
        
        Args:
            min_trades: Minimum number of trades to include
            
        Returns:
            List of indicator combination performance
        """
        query = """
        SELECT * FROM v_indicator_combination_performance 
        WHERE closed_positions >= ?
        ORDER BY win_rate_pct DESC, avg_pnl_pct DESC
        """
        rows = self.execute_query(query, (min_trades,))
        return [dict(row) for row in rows]
        
    def update_portfolio_state(self, total_capital: float, available_cash: float,
                              invested_value: float, position_details: List[Dict],
                              **kwargs) -> int:
        """
        Update portfolio state snapshot
        
        Args:
            total_capital: Total capital
            available_cash: Available cash
            invested_value: Current invested value
            position_details: List of position dictionaries
            **kwargs: Additional metrics
            
        Returns:
            Inserted row ID
        """
        query = """
        INSERT INTO portfolio_state 
        (timestamp, total_capital, available_cash, invested_value, 
         total_positions, position_details, portfolio_exposure_pct,
         total_realized_pnl, total_realized_pnl_pct, win_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        timestamp = int(datetime.now().timestamp())
        exposure_pct = (invested_value / total_capital * 100) if total_capital > 0 else 0
        
        cursor = self.conn.cursor()
        cursor.execute(query, (
            timestamp, total_capital, available_cash, invested_value,
            len(position_details), json.dumps(position_details), exposure_pct,
            kwargs.get('total_realized_pnl', 0),
            kwargs.get('total_realized_pnl_pct', 0),
            kwargs.get('win_rate', 0)
        ))
        self.conn.commit()
        return cursor.lastrowid


def initialize_database(db_path: str = "database/trading.db") -> TradingDatabase:
    """
    Initialize database and run migrations
    
    Args:
        db_path: Path to database file
        
    Returns:
        TradingDatabase instance
    """
    db = TradingDatabase(db_path)
    db.connect()
    
    try:
        db.run_migration()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
        
    return db


if __name__ == "__main__":
    # Example usage
    print("Initializing trading database...")
    db = initialize_database()
    
    print("\nDatabase schema created successfully!")
    print(f"Database location: {db.db_path.absolute()}")
    
    # Test views
    print("\n=== Testing Views ===")
    
    print("\n1. Strategy Performance (empty - no data yet):")
    performance = db.get_strategy_performance()
    print(f"   Found {len(performance)} strategies")
    
    print("\n2. Open Positions (empty - no data yet):")
    positions = db.get_open_positions()
    print(f"   Found {len(positions)} open positions")
    
    print("\nDatabase ready for use! ✅")
    
    db.disconnect()
