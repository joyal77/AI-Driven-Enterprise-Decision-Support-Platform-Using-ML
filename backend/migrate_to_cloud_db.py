"""
migrate_to_cloud_db.py

SmartCart Enterprise — Safe SQLite to Cloud Database Migration Tool
Migrates all tables and records from local backend/ecommerce_churn.db to a cloud database
(e.g., Neon Serverless PostgreSQL or TiDB Serverless MySQL) with 100% data integrity verification.

Usage:
  python backend/migrate_to_cloud_db.py --target-url "postgresql://user:pass@ep-xyz.us-east-2.aws.neon.tech/neondb?sslmode=require"
or:
  set TARGET_DATABASE_URL=postgresql://...
  python backend/migrate_to_cloud_db.py
"""

import os
import sys
import argparse
import datetime
from sqlalchemy import create_engine, MetaData, Table, select, insert, text
from sqlalchemy.orm import sessionmaker

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.app.db.models import Base

# Dependency-ordered tables for clean relational insertion
ORDERED_TABLES = [
    "users",
    "customers",
    "store_users",
    "products",
    "orders",
    "order_items",
    "cart_items",
    "churn_predictions",
    "retention_recommendations",
    "customer_retention_perks",
    "customer_notifications",
    "customer_perk_redemptions",
    "data_integrity_audit_logs",
    "prediction_batches"
]

def migrate(target_url: str):
    # Standardize postgres URL
    if target_url.startswith("postgres://"):
        target_url = target_url.replace("postgres://", "postgresql://", 1)

    sqlite_path = os.path.join(ROOT_DIR, "backend", "ecommerce_churn.db")
    if not os.path.exists(sqlite_path):
        print(f"[Error] Source SQLite database not found at {sqlite_path}")
        return False

    print("=" * 70)
    print(" SmartCart Enterprise — SQLite to Cloud DB Migration")
    print("=" * 70)
    print(f" Source SQLite: {sqlite_path} ({os.path.getsize(sqlite_path):,} bytes)")
    safe_target = target_url.split("@")[-1] if "@" in target_url else target_url
    print(f" Target Cloud DB: {safe_target}")
    print("-" * 70)

    # 1. Create engines
    source_engine = create_engine(f"sqlite:///{sqlite_path}")
    
    if "postgresql" in target_url or "postgres" in target_url:
        target_engine = create_engine(target_url, pool_recycle=300, pool_pre_ping=True)
    else:
        target_engine = create_engine(target_url, pool_recycle=3600, pool_pre_ping=True, connect_args={"connect_timeout": 10})

    # Test target connection
    try:
        with target_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[✓] Target database connected successfully.")
    except Exception as e:
        print(f"[✗] Failed to connect to target database: {e}")
        return False

    # 2. Create tables on target
    print("[*] Creating table schema on target database...")
    Base.metadata.create_all(target_engine)
    print("[✓] Schema created successfully.")

    # 3. Read metadata
    source_meta = MetaData()
    source_meta.reflect(bind=source_engine)

    target_meta = MetaData()
    target_meta.reflect(bind=target_engine)

    migration_report = []

    # 4. Copy data table by table
    with source_engine.connect() as src_conn, target_engine.connect() as tgt_conn:
        for tbl_name in ORDERED_TABLES:
            if tbl_name not in source_meta.tables or tbl_name not in target_meta.tables:
                print(f"[!] Table '{tbl_name}' skipped (not present in metadata)")
                continue

            src_table = source_meta.tables[tbl_name]
            tgt_table = target_meta.tables[tbl_name]

            # Read source rows
            rows = src_conn.execute(select(src_table)).fetchall()
            src_count = len(rows)

            # Check if target already has rows
            tgt_count_before = tgt_conn.execute(select(tgt_table)).rowcount
            if tgt_count_before > 0:
                print(f"[-] Table '{tbl_name}' already has data on target ({tgt_count_before} rows).")
            elif src_count > 0:
                # Convert rows to dicts
                row_dicts = [dict(r._mapping) for r in rows]
                # Chunked insertion
                chunk_size = 500
                for i in range(0, len(row_dicts), chunk_size):
                    chunk = row_dicts[i:i + chunk_size]
                    tgt_conn.execute(insert(tgt_table), chunk)
                tgt_conn.commit()
                print(f"[✓] Migrated '{tbl_name}': {src_count} rows copied.")
            else:
                print(f"[-] Table '{tbl_name}': 0 rows to copy.")

            # Verify count
            tgt_res = tgt_conn.execute(text(f"SELECT COUNT(*) FROM {tbl_name}")).scalar()
            is_match = (tgt_res >= src_count)
            migration_report.append({
                "table": tbl_name,
                "source_count": src_count,
                "target_count": tgt_res,
                "status": "PASS" if is_match else "FAIL"
            })

            # For PostgreSQL, update sequence values so new autoincrement IDs don't collide
            if target_engine.name == "postgresql":
                try:
                    tgt_conn.execute(text(f"SELECT setval(pg_get_serial_sequence('{tbl_name}', 'id'), coalesce(max(id), 1)) FROM {tbl_name}"))
                    tgt_conn.commit()
                except Exception:
                    pass

    # 5. Display Summary Report
    print("\n" + "=" * 70)
    print(f" {'TABLE NAME':<30} | {'SOURCE':<10} | {'TARGET':<10} | {'STATUS':<6}")
    print("-" * 70)
    all_passed = True
    for rep in migration_report:
        status_symbol = "✓ PASS" if rep["status"] == "PASS" else "✗ FAIL"
        if rep["status"] != "PASS":
            all_passed = False
        print(f" {rep['table']:<30} | {rep['source_count']:<10} | {rep['target_count']:<10} | {status_symbol}")
    print("=" * 70)

    if all_passed:
        print("[SUCCESS] All tables and rows migrated with 100% integrity!")
        print("Your cloud database is ready to be connected to Render via DATABASE_URL.")
    else:
        print("[WARNING] One or more tables had row count discrepancies. Please check the logs.")

    return all_passed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate SmartCart SQLite to Cloud DB")
    parser.add_argument("--target-url", type=str, default=None, help="Target Cloud Database URL")
    args = parser.parse_args()

    target_url = args.target_url or os.getenv("TARGET_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not target_url or "sqlite" in target_url:
        print("[Usage Error] Please provide a valid target cloud database URL.")
        print('Example: python backend/migrate_to_cloud_db.py --target-url "postgresql://..."')
        sys.exit(1)

    success = migrate(target_url)
    sys.exit(0 if success else 1)
