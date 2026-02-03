import sqlite3
import os

db_path = 'database/trading.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    type TEXT NOT NULL,                -- 'BUY' or 'SELL'
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    fees REAL DEFAULT 0,
    timestamp INTEGER NOT NULL,        -- Unix timestamp
    notes TEXT,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);
""")

# Create index
cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_transactions_symbol 
    ON transactions(symbol, timestamp DESC);
""")

# Insert version if not exists
try:
    cursor.execute("INSERT OR IGNORE INTO schema_version (version, description) VALUES (2, 'Added transactions table')")
except Exception as e:
    print(f"Version update skipped: {e}")

conn.commit()
conn.close()
print("Migration 002 applied manually.")
