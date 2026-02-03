-- ============================================================================
-- Transaction History Schema
-- Version: 2.0
-- Description: Stores actual buy/sell transactions to track history and pnl
-- ============================================================================

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    type TEXT NOT NULL,                -- 'BUY' or 'SELL'
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    fees REAL DEFAULT 0,
    timestamp INTEGER NOT NULL,        -- Unix timestamp
    notes TEXT,
    
    -- Metadata
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Index for fast retrieval by symbol
CREATE INDEX IF NOT EXISTS idx_transactions_symbol 
    ON transactions(symbol, timestamp DESC);

INSERT INTO schema_version (version, description) 
VALUES (2, 'Added transactions table for history tracking');
