import sqlite3
import math

conn = sqlite3.connect("backend/ecommerce_churn.db")
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = [r[0] for r in c.fetchall()]

issues = 0
for t in tables:
    c.execute(f'PRAGMA table_info("{t}")')
    cols = [col[1] for col in c.fetchall() if 'FLOAT' in col[2].upper() or 'DOUBLE' in col[2].upper() or 'REAL' in col[2].upper()]
    for col in cols:
        c.execute(f'SELECT "{col}" FROM "{t}" WHERE "{col}" IS NOT NULL')
        for r in c.fetchall():
            val = r[0]
            if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
                print(f"Warning: {t}.{col} has NaN/Inf value")
                issues += 1

print(f"Total NaN/Inf float issues found: {issues}")
conn.close()

