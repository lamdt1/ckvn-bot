import sqlite3
import pandas as pd
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.config import BotConfig

def view_signals():
    db_path = "database/trading.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        
        print(f"\n📊 SIGNAL HISTORY (Last 20)")
        print("="*100)
        
        # Query signals
        query = """
            SELECT 
                datetime(timestamp, 'unixepoch') as date,
                symbol,
                signal_type,
                ROUND(confidence_score, 1) as score,
                price_at_signal as price,
                suggested_stop_loss as sl,
                suggested_take_profit as tp
            FROM signals
            ORDER BY timestamp DESC
            LIMIT 20
        """
        
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            print("📭 No signals found in database.")
        else:
            # Format columns
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', 1000)
            print(df.to_string(index=False))
            
        conn.close()
        print("\n" + "="*100)
        
    except Exception as e:
        print(f"❌ Error reading history: {e}")

if __name__ == "__main__":
    view_signals()
