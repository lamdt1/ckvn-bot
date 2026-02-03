-- ============================================================================
-- Add missing columns to indicators table
-- Version: 3.0
-- ============================================================================

-- Add bb_position_label if not exists
-- Note: SQLite doesn't support IF NOT EXISTS in ADD COLUMN, so we might need a script wrapper or just try/catch in python manual migration. 
-- However, we can use the manual runner to handle safety.

ALTER TABLE indicators ADD COLUMN bb_position_label TEXT;
ALTER TABLE indicators ADD COLUMN trend_strength REAL;

INSERT INTO schema_version (version, description) 
VALUES (3, 'Added new indicator columns');
