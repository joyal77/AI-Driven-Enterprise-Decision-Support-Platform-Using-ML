import sqlite3
import json

conn = sqlite3.connect("backend/ecommerce_churn.db")
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = sorted([r[0] for r in c.fetchall()])

print(f"Total tables found: {len(tables)}")
total_rows = 0
detailed_info = {}

for tbl in tables:
    c.execute(f'SELECT COUNT(*) FROM "{tbl}"')
    cnt = c.fetchone()[0]
    total_rows += cnt

    c.execute(f'PRAGMA table_info("{tbl}")')
    cols = c.fetchall()

    c.execute(f'PRAGMA foreign_key_list("{tbl}")')
    fks = c.fetchall()

    c.execute(f'PRAGMA index_list("{tbl}")')
    idxs = c.fetchall()

    detailed_info[tbl] = {
        "rows": cnt,
        "columns": [{"cid": col[0], "name": col[1], "type": col[2], "notnull": col[3], "dflt_value": col[4], "pk": col[5]} for col in cols],
        "foreign_keys": [{"id": fk[0], "seq": fk[1], "table": fk[2], "from": fk[3], "to": fk[4], "on_update": fk[5], "on_delete": fk[6]} for fk in fks],
        "indexes": [{"name": idx[1], "unique": idx[2]} for idx in idxs]
    }

    print(f"{tbl:<32}: {cnt:>5} rows | {len(cols):>2} cols | {len(fks):>2} FKs")

print("-" * 65)
print(f"TOTAL ROWS ACROSS ALL TABLES: {total_rows}")
conn.close()

with open("tools/source_db_audit.json", "w", encoding="utf-8") as f:
    json.dump(detailed_info, f, indent=2)

print("[✓] Saved detailed schema inspection to tools/source_db_audit.json")

