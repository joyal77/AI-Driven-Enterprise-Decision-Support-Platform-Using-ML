import sqlite3
import re
import json

conn = sqlite3.connect("backend/ecommerce_churn.db")
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = sorted([r[0] for r in c.fetchall()])

sqlite_cols = {}
for t in tables:
    c.execute(f'PRAGMA table_info("{t}")')
    cols = c.fetchall()
    sqlite_cols[t] = {col[1]: col[2] for col in cols}

conn.close()

with open("database/migrations/001_initial_schema.sql", "r", encoding="utf-8") as f:
    sql_text = f.read()

# Parse CREATE TABLE blocks from 001_initial_schema.sql
table_blocks = re.findall(r'CREATE TABLE IF NOT EXISTS\s+([a-zA-Z0-9_]+)\s*\((.*?)\);', sql_text, re.DOTALL | re.IGNORECASE)

sql_tables = {}
for tbl_name, block in table_blocks:
    cols = {}
    for line in block.split('\n'):
        line = line.strip().rstrip(',')
        if not line or line.startswith('--') or line.startswith('CONSTRAINT') or line.startswith('PRIMARY KEY'):
            continue
        parts = line.split()
        if len(parts) >= 2:
            col_name = parts[0]
            col_type = parts[1]
            cols[col_name] = col_type
    sql_tables[tbl_name] = cols

print("=== Column Comparison: SQLite Source vs 001_initial_schema.sql ===")
mismatches = 0
for t in tables:
    if t not in sql_tables:
        print(f"[MISSING TABLE] {t} not found in SQL file!")
        mismatches += 1
        continue
    
    src_c = set(sqlite_cols[t].keys())
    tgt_c = set(sql_tables[t].keys())
    
    missing_in_sql = src_c - tgt_c
    extra_in_sql = tgt_c - src_c
    
    if missing_in_sql:
        print(f"[{t}] MISSING columns in SQL: {missing_in_sql}")
        mismatches += 1
    if extra_in_sql:
        print(f"[{t}] EXTRA columns in SQL: {extra_in_sql}")
        mismatches += 1
    if not missing_in_sql and not extra_in_sql:
        print(f"[OK] {t:<30}: all {len(src_c)} columns match exactly.")

print(f"\nTotal column mismatches: {mismatches}")
