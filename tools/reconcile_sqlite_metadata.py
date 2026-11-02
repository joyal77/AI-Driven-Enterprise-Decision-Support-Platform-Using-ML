import sqlite3
import json

conn = sqlite3.connect("backend/ecommerce_churn.db")
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
tables = [r[0] for r in c.fetchall()]

table_stats = []
total_cols = 0
total_fks = 0
total_rows = 0

detailed_metadata = {}

for tbl in tables:
    c.execute(f'PRAGMA table_info("{tbl}")')
    cols = c.fetchall()
    
    c.execute(f'PRAGMA foreign_key_list("{tbl}")')
    fks = c.fetchall()
    
    c.execute(f'PRAGMA index_list("{tbl}")')
    idxs = c.fetchall()
    
    c.execute(f'SELECT COUNT(*) FROM "{tbl}"')
    cnt = c.fetchone()[0]
    
    num_cols = len(cols)
    num_fks = len(fks)
    
    total_cols += num_cols
    total_fks += num_fks
    total_rows += cnt
    
    stats_entry = {
        "table": tbl,
        "rows": cnt,
        "columns_count": num_cols,
        "columns": [
            {
                "cid": col[0],
                "name": col[1],
                "type": col[2],
                "notnull": bool(col[3]),
                "default": col[4],
                "pk": col[5]
            }
            for col in cols
        ],
        "foreign_keys_count": num_fks,
        "foreign_keys": [
            {
                "id": fk[0],
                "seq": fk[1],
                "target_table": fk[2],
                "from_col": fk[3],
                "to_col": fk[4],
                "on_update": fk[5],
                "on_delete": fk[6]
            }
            for fk in fks
        ],
        "indexes_count": len(idxs),
        "indexes": [
            {
                "name": idx[1],
                "unique": bool(idx[2]),
                "origin": idx[3],
                "partial": bool(idx[4])
            }
            for idx in idxs
        ]
    }
    
    detailed_metadata[tbl] = stats_entry
    table_stats.append((tbl, cnt, num_cols, num_fks, len(idxs)))

conn.close()

print(f"{'TABLE NAME':<32} | {'ROWS':<8} | {'COLS':<6} | {'FKS':<5} | {'INDEXES':<7}")
print("-" * 68)
for tbl, cnt, num_cols, num_fks, num_idxs in table_stats:
    print(f"{tbl:<32} | {cnt:<8} | {num_cols:<6} | {num_fks:<5} | {num_idxs:<7}")
print("-" * 68)
print(f"{'TOTALS (' + str(len(tables)) + ' tables)':<32} | {total_rows:<8} | {total_cols:<6} | {total_fks:<5} |")

summary = {
    "total_tables": len(tables),
    "total_records": total_rows,
    "total_columns": total_cols,
    "total_foreign_keys": total_fks,
    "tables": detailed_metadata
}

with open("tools/reconciled_sqlite_metadata.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

print("\nSaved detailed metadata to tools/reconciled_sqlite_metadata.json")

