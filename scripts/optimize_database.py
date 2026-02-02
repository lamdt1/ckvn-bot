"""
Database Optimization Script
Optimize database for Raspberry Pi (limited resources)
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """
    Database optimization for Raspberry Pi
    
    Features:
    - Create indexes for faster queries
    - Implement data retention (keep last 6 months)
    - Vacuum database to reclaim space
    - Analyze query performance
    """
    
    def __init__(self, db_path: str):
        """
        Initialize database optimizer
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        logger.info(f"✅ Database optimizer initialized: {db_path}")
    
    def create_indexes(self):
        """Create indexes for frequently queried columns"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            indexes = [
                # Signals table
                ("idx_signals_symbol", "CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol)"),
                ("idx_signals_timestamp", "CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp)"),
                ("idx_signals_is_closed", "CREATE INDEX IF NOT EXISTS idx_signals_is_closed ON signals(is_closed)"),
                ("idx_signals_symbol_closed", "CREATE INDEX IF NOT EXISTS idx_signals_symbol_closed ON signals(symbol, is_closed)"),
                
                # Stock prices table
                ("idx_prices_symbol", "CREATE INDEX IF NOT EXISTS idx_prices_symbol ON stock_prices(symbol)"),
                ("idx_prices_timestamp", "CREATE INDEX IF NOT EXISTS idx_prices_timestamp ON stock_prices(timestamp)"),
                ("idx_prices_symbol_time", "CREATE INDEX IF NOT EXISTS idx_prices_symbol_time ON stock_prices(symbol, timestamp)"),
                
                # Indicators table
                ("idx_indicators_symbol", "CREATE INDEX IF NOT EXISTS idx_indicators_symbol ON indicators(symbol)"),
                ("idx_indicators_timestamp", "CREATE INDEX IF NOT EXISTS idx_indicators_timestamp ON indicators(timestamp)"),
                ("idx_indicators_symbol_time", "CREATE INDEX IF NOT EXISTS idx_indicators_symbol_time ON indicators(symbol, timestamp)"),
            ]
            
            print("\n📊 Creating database indexes...")
            print("-" * 70)
            
            for idx_name, sql in indexes:
                try:
                    cursor.execute(sql)
                    print(f"✅ Created: {idx_name}")
                except Exception as e:
                    print(f"⚠️ {idx_name}: {e}")
            
            conn.commit()
            conn.close()
            
            print("-" * 70)
            print("✅ Indexes created successfully\n")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise
    
    def cleanup_old_data(self, retention_days: int = 180):
        """
        Delete data older than retention period
        
        Args:
            retention_days: Number of days to keep (default: 180 = 6 months)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate cutoff timestamp
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            cutoff_timestamp = int(cutoff_date.timestamp())
            
            print(f"\n🗑️ Cleaning up data older than {retention_days} days...")
            print(f"   Cutoff date: {cutoff_date.strftime('%Y-%m-%d')}")
            print("-" * 70)
            
            # Delete old stock prices
            cursor.execute("SELECT COUNT(*) FROM stock_prices WHERE timestamp < ?", (cutoff_timestamp,))
            old_prices = cursor.fetchone()[0]
            
            if old_prices > 0:
                cursor.execute("DELETE FROM stock_prices WHERE timestamp < ?", (cutoff_timestamp,))
                print(f"✅ Deleted {old_prices:,} old price records")
            else:
                print("✅ No old price records to delete")
            
            # Delete old indicators (keep if associated with open signals)
            cursor.execute("""
                SELECT COUNT(*) FROM indicators 
                WHERE timestamp < ? 
                AND NOT EXISTS (
                    SELECT 1 FROM signals 
                    WHERE signals.symbol = indicators.symbol 
                    AND signals.timestamp = indicators.timestamp 
                    AND signals.is_closed = 0
                )
            """, (cutoff_timestamp,))
            old_indicators = cursor.fetchone()[0]
            
            if old_indicators > 0:
                cursor.execute("""
                    DELETE FROM indicators 
                    WHERE timestamp < ? 
                    AND NOT EXISTS (
                        SELECT 1 FROM signals 
                        WHERE signals.symbol = indicators.symbol 
                        AND signals.timestamp = indicators.timestamp 
                        AND signals.is_closed = 0
                    )
                """, (cutoff_timestamp,))
                print(f"✅ Deleted {old_indicators:,} old indicator records")
            else:
                print("✅ No old indicator records to delete")
            
            # Note: Keep all signals (closed and open) for performance tracking
            print("✅ Keeping all signal records for performance tracking")
            
            conn.commit()
            conn.close()
            
            print("-" * 70)
            print("✅ Cleanup completed\n")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            raise
    
    def vacuum_database(self):
        """Vacuum database to reclaim space and optimize"""
        try:
            print("\n🔧 Vacuuming database...")
            print("-" * 70)
            
            # Get size before
            size_before = Path(self.db_path).stat().st_size / (1024 * 1024)  # MB
            print(f"Size before: {size_before:.2f} MB")
            
            conn = sqlite3.connect(self.db_path)
            conn.execute("VACUUM")
            conn.close()
            
            # Get size after
            size_after = Path(self.db_path).stat().st_size / (1024 * 1024)  # MB
            saved = size_before - size_after
            
            print(f"Size after:  {size_after:.2f} MB")
            print(f"Space saved: {saved:.2f} MB ({(saved/size_before*100):.1f}%)")
            print("-" * 70)
            print("✅ Vacuum completed\n")
            
        except Exception as e:
            logger.error(f"Failed to vacuum database: {e}")
            raise
    
    def analyze_database(self):
        """Analyze database to update query optimizer statistics"""
        try:
            print("\n📈 Analyzing database...")
            print("-" * 70)
            
            conn = sqlite3.connect(self.db_path)
            conn.execute("ANALYZE")
            conn.close()
            
            print("✅ Analysis completed")
            print("-" * 70)
            print()
            
        except Exception as e:
            logger.error(f"Failed to analyze database: {e}")
            raise
    
    def get_database_stats(self):
        """Get database statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            print("\n📊 DATABASE STATISTICS")
            print("=" * 70)
            
            # File size
            size_mb = Path(self.db_path).stat().st_size / (1024 * 1024)
            print(f"\n💾 File Size: {size_mb:.2f} MB")
            
            # Table counts
            tables = ['signals', 'stock_prices', 'indicators']
            print(f"\n📋 Record Counts:")
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table:<20} {count:>10,}")
            
            # Signal stats
            cursor.execute("SELECT COUNT(*) FROM signals WHERE is_closed = 0")
            open_signals = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM signals WHERE is_closed = 1")
            closed_signals = cursor.fetchone()[0]
            
            print(f"\n📊 Signal Breakdown:")
            print(f"  Open signals:        {open_signals:>10,}")
            print(f"  Closed signals:      {closed_signals:>10,}")
            
            # Date range
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM stock_prices")
            min_ts, max_ts = cursor.fetchone()
            
            if min_ts and max_ts:
                min_date = datetime.fromtimestamp(min_ts).strftime('%Y-%m-%d')
                max_date = datetime.fromtimestamp(max_ts).strftime('%Y-%m-%d')
                days = (max_ts - min_ts) / (24 * 60 * 60)
                
                print(f"\n📅 Data Range:")
                print(f"  From:                {min_date}")
                print(f"  To:                  {max_date}")
                print(f"  Days:                {days:.0f}")
            
            # Index info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
            indexes = cursor.fetchall()
            
            print(f"\n🔍 Indexes: {len(indexes)}")
            for idx in indexes:
                print(f"  - {idx[0]}")
            
            print("\n" + "=" * 70 + "\n")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            raise
    
    def optimize_all(self, retention_days: int = 180):
        """
        Run full optimization
        
        Args:
            retention_days: Number of days to keep data
        """
        print("\n" + "=" * 70)
        print("🚀 RASPBERRY PI DATABASE OPTIMIZATION")
        print("=" * 70)
        
        # Show stats before
        print("\n📊 BEFORE OPTIMIZATION:")
        self.get_database_stats()
        
        # Run optimizations
        self.create_indexes()
        self.cleanup_old_data(retention_days)
        self.vacuum_database()
        self.analyze_database()
        
        # Show stats after
        print("📊 AFTER OPTIMIZATION:")
        self.get_database_stats()
        
        print("=" * 70)
        print("✅ OPTIMIZATION COMPLETE!")
        print("=" * 70)


if __name__ == "__main__":
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Get database path from args or use default
    db_path = sys.argv[1] if len(sys.argv) > 1 else "database/trading.db"
    
    # Get retention days from args or use default (180 days = 6 months)
    retention_days = int(sys.argv[2]) if len(sys.argv) > 2 else 180
    
    # Run optimization
    optimizer = DatabaseOptimizer(db_path)
    optimizer.optimize_all(retention_days)
    
    print(f"\n💡 TIP: Run this script monthly to keep database optimized")
    print(f"   python3 scripts/optimize_database.py {db_path} {retention_days}\n")
