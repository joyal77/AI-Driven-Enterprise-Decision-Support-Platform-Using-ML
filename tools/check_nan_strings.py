import sqlite3

conn = sqlite3.connect("backend/ecommerce_churn.db")
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = [r[0] for r in c.fetchall()]

nan_count = 0
for t in tables:
    c.execute(f'PRAGMA table_info("{t}")')
    cols = [col[1] for col in c.fetchall()]
    for col in cols:
        c.execute(f'SELECT COUNT(*) FROM "{t}" WHERE "{col}" = "NaN" OR "{col}" = "nan" OR "{col}" = "None"')
        cnt = c.fetchone()[0]
        if cnt > 0:
            print(f"Table {t}, column {col} has {cnt} literal 'NaN'/'None' strings!")
            nan_count += cnt

if nan_count == 0:
    print("No literal 'NaN'/'None' string corruptions found in source database.")
conn.close()

