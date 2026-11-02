import sqlite3

conn = sqlite3.connect("backend/ecommerce_churn.db")
c = conn.cursor()

# Get all tables and their foreign keys
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
tables = [r[0] for r in c.fetchall()]

print("=== Complete SQLite Source Orphan FK Audit ===")
total_orphans = 0

for tbl in tables:
    c.execute(f'PRAGMA foreign_key_list("{tbl}")')
    fks = c.fetchall()
    for fk in fks:
        target_tbl = fk[2]
        from_col = fk[3]
        to_col = fk[4]
        
        # Count non-null values
        c.execute(f'SELECT COUNT(*) FROM "{tbl}" WHERE "{from_col}" IS NOT NULL')
        non_null_cnt = c.fetchone()[0]
        
        # Check for orphans
        orphan_query = f"""
            SELECT c."id", c."{from_col}" FROM "{tbl}" c
            LEFT JOIN "{target_tbl}" p ON c."{from_col}" = p."{to_col}"
            WHERE c."{from_col}" IS NOT NULL AND p."{to_col}" IS NULL
        """
        c.execute(orphan_query)
        orphans = c.fetchall()
        
        status = "CLEAN (0 orphans)" if len(orphans) == 0 else f"ORPHANS DETECTED: {len(orphans)}"
        print(f"{tbl}.{from_col} -> {target_tbl}.{to_col} ({non_null_cnt} values): {status}")
        
        if len(orphans) > 0:
            total_orphans += len(orphans)
            for o_id, bad_val in orphans:
                print(f"   [!] Row ID={o_id} has invalid {from_col}={bad_val} (not in {target_tbl})")

print("-" * 75)
print(f"Total Orphan Foreign Keys in Source SQLite: {total_orphans}")
conn.close()

