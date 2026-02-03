import sqlite3
import os

db_path = 'database/trading.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Columns to add
cols = [
    ('bb_position_label', 'TEXT'),
    ('trend_strength', 'REAL')
]

for col_name, col_type in cols:
    try:
        cursor.execute(f"ALTER TABLE indicators ADD COLUMN {col_name} {col_type}")
        print(f"✅ Added column {col_name}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"ℹ️ Column {col_name} already exists")
        else:
            print(f"❌ Error adding {col_name}: {e}")

# Update version
try:
    cursor.execute("INSERT OR IGNORE INTO schema_version (version, description) VALUES (3, 'Added new indicator columns')")
except Exception:
    pass

conn.commit()
conn.close()
print("Migration 003 applied manually.")
