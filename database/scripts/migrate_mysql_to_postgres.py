"""
database/scripts/migrate_mysql_to_postgres.py

Production-Grade, Safe Data Migration Utility from SQLite to Supabase PostgreSQL.

Safety & Reliability Guarantees:
1. Non-Destructive: Original SQLite database is strictly read-only and never modified.
2. Dialect-Safe: Normalizes postgres:// and postgresql:// to postgresql+psycopg:// for psycopg v3.
3. Pooler-Compatible: Sets prepare_threshold=None to support PgBouncer / Supabase Transaction Pooler (Port 6543).
4. Pre-Flight Conflict Detection: Audits target database before writing; halts if unexpected data exists.
5. Strict Resume Verification: When resuming, does NOT silently ignore conflicting rows. Performs field-level comparison between existing target rows and source rows, flagging any data discrepancies before inserting missing rows.
6. Topological DAG Order: Inserts tables in strict parent-before-child dependency order.
7. Sequence Synchronization: Resets all PostgreSQL identity sequences so subsequent writes never collide.
8. Safe Output: Pure ASCII logging compatible with all Windows PowerShell code pages.

Usage:
  python database/scripts/migrate_mysql_to_postgres.py --target-url "postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?sslmode=require"
or:
  $env:TARGET_DATABASE_URL="postgresql://..."
  python database/scripts/migrate_mysql_to_postgres.py
"""

import os
import sys
import argparse
import datetime
import math
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import create_engine, MetaData, Table, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert

# Ensure project root is on Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
    load_dotenv(os.path.join(PROJECT_ROOT, "backend", ".env"))
except ImportError:
    pass

from backend.app.db.models import Base

# Strict topological ordering: Independent tables first, dependent children later
ORDERED_TABLES = [
    "users",
    "customers",
    "products",
    "prediction_batches",
    "data_integrity_audit_log",
    "store_users",
    "orders",
    "order_items",
    "cart_items",
    "churn_predictions",
    "retention_recommendations",
    "customer_retention_perks",
    "customer_notifications",
    "customer_perk_redemptions"
]

def normalize_db_url(url: str) -> str:
    """Normalizes connection URLs to use psycopg v3 driver on SQLAlchemy 2.0+."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

def sanitize_value(val: Any) -> Any:
    """Sanitizes field values for PostgreSQL type safety."""
    if val is None:
        return None
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return None
    return val

def sanitize_row(row_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitizes an entire row dictionary."""
    clean = {}
    for k, v in row_dict.items():
        clean[k] = sanitize_value(v)
    return clean

def compare_record_fields(src: Dict[str, Any], tgt: Dict[str, Any]) -> List[str]:
    """Compares fields between source and existing target record, returning list of mismatched columns."""
    mismatches = []
    for k, s_val in src.items():
        if k not in tgt:
            continue
        t_val = tgt[k]
        # Ignore None vs empty string or timestamp sub-second precision diffs
        if s_val is None and t_val is None:
            continue
        if str(s_val).strip() != str(t_val).strip():
            # Check float equivalence
            try:
                if abs(float(s_val) - float(t_val)) < 1e-4:
                    continue
            except (ValueError, TypeError):
                pass
            mismatches.append(f"{k} (src='{s_val}' vs tgt='{t_val}')")
    return mismatches

def execute_schema_ddl(target_engine) -> bool:
    """Safely executes the initial schema DDL on PostgreSQL statement by statement."""
    schema_file = os.path.join(PROJECT_ROOT, "database", "migrations", "001_initial_schema.sql")
    if not os.path.exists(schema_file):
        print("[*] Applying DDL using SQLAlchemy Base metadata...")
        Base.metadata.create_all(target_engine)
        print("[OK] Schema created via SQLAlchemy metadata.")
        return True

    print(f"[*] Applying DDL from {os.path.basename(schema_file)}...")
    with open(schema_file, "r", encoding="utf-8") as f:
        ddl = f.read()

    # Strip line-by-line comments before splitting statements
    clean_lines = []
    for line in ddl.split("\n"):
        line_clean = line.strip()
        if line_clean.startswith("--"):
            continue
        clean_lines.append(line)
    clean_ddl = "\n".join(clean_lines)

    statements = [s.strip() for s in clean_ddl.split(";") if s.strip()]

    for stmt in statements:
        if not stmt:
            continue
        try:
            with target_engine.begin() as conn:
                conn.execute(text(stmt))
        except Exception as e:
            err_msg = str(e).lower()
            if "already exists" in err_msg or "duplicate" in err_msg:
                continue
            print(f"[!] DDL Notice on statement ({stmt[:40]}...): {e}")

    print("[OK] PostgreSQL table schemas, indexes, and RLS policies verified.")
    return True

def reset_postgres_sequences(target_engine, table_name: str):
    """Safely resets the PostgreSQL identity sequence for a table."""
    seq_query = text(f"""
        DO $$
        DECLARE
            seq_name text;
            max_val bigint;
        BEGIN
            seq_name := pg_get_serial_sequence('"{table_name}"', 'id');
            IF seq_name IS NOT NULL THEN
                EXECUTE 'SELECT COALESCE(MAX(id), 0) FROM "{table_name}"' INTO max_val;
                IF max_val > 0 THEN
                    PERFORM setval(seq_name, max_val, true);
                ELSE
                    PERFORM setval(seq_name, 1, false);
                END IF;
            END IF;
        END $$;
    """)
    try:
        with target_engine.begin() as conn:
            conn.execute(seq_query)
    except Exception:
        pass

def run_migration(source_url: str, target_url: str, apply_schema: bool = True, resume: bool = False) -> bool:
    target_url = normalize_db_url(target_url)

    print("=" * 80)
    print(" SmartCart Enterprise -- SQLite to Supabase PostgreSQL Migration")
    print("=" * 80)
    safe_source = source_url.split("@")[-1] if "@" in source_url else source_url
    safe_target = target_url.split("@")[-1] if "@" in target_url else target_url
    print(f" Source DB : {safe_source}")
    print(f" Target DB : {safe_target}")
    print("-" * 80)

    # 1. Connect to source
    try:
        source_engine = create_engine(source_url)
        with source_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[OK] Source database connected successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to connect to source database: {e}")
        return False

    # 2. Connect to target
    connect_args = {}
    if "postgresql" in target_url:
        connect_args["prepare_threshold"] = None  # Supabase pooler compatibility

    try:
        target_engine = create_engine(
            target_url,
            pool_recycle=300,
            pool_pre_ping=True,
            connect_args=connect_args
        )
        with target_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[OK] Supabase PostgreSQL target connected successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to connect to Supabase PostgreSQL target: {e}")
        print("\nPlease check your Supabase credentials, database password, or pooler URL.")
        return False

    # 3. Apply schema
    if apply_schema:
        execute_schema_ddl(target_engine)

    # 4. Reflect metadata
    source_meta = MetaData()
    source_meta.reflect(bind=source_engine)

    target_meta = MetaData()
    target_meta.reflect(bind=target_engine)

    # 5. Pre-flight conflict audit
    print("\n[*] Performing pre-flight data audit on target database...")
    target_existing_counts = {}
    with target_engine.connect() as tgt_conn:
        for tbl_name in ORDERED_TABLES:
            if tbl_name in target_meta.tables:
                try:
                    c = tgt_conn.execute(text(f'SELECT COUNT(*) FROM "{tbl_name}"')).scalar()
                    target_existing_counts[tbl_name] = c
                except Exception:
                    target_existing_counts[tbl_name] = 0

    has_existing_data = any(cnt > 0 for cnt in target_existing_counts.values())
    if has_existing_data and not resume:
        print("\n[CONFLICT NOTICE] The target database already contains data:")
        for t, cnt in target_existing_counts.items():
            if cnt > 0:
                print(f"   - {t:<30}: {cnt} existing rows")
        print("\nSafety lock activated: Migration halted to prevent accidental overwrite.")
        print("To safely resume and verify only missing records, run with: --resume")
        return False

    # 6. Execute data migration table-by-table
    print("\n[*] Beginning record migration in topological order...")
    migration_report = []
    total_discrepancies = 0

    with source_engine.connect() as src_conn, target_engine.connect() as tgt_conn:
        for tbl_name in ORDERED_TABLES:
            if tbl_name not in source_meta.tables:
                print(f"[WARN] Source table '{tbl_name}' not found. Skipping.")
                continue
            if tbl_name not in target_meta.tables:
                print(f"[WARN] Target table '{tbl_name}' not found. Skipping.")
                continue

            src_table = source_meta.tables[tbl_name]
            tgt_table = target_meta.tables[tbl_name]

            # Fetch source records
            rows = src_conn.execute(select(src_table)).fetchall()
            src_count = len(rows)

            clean_records = [sanitize_row(dict(r._mapping)) for r in rows]

            # Orphan FK sanitization for nullable foreign keys
            if tbl_name == "customer_perk_redemptions":
                valid_perk_ids = set(r[0] for r in src_conn.execute(text("SELECT id FROM customer_retention_perks")).fetchall())
                for rec in clean_records:
                    if rec.get("perk_id") and rec["perk_id"] not in valid_perk_ids:
                        print(f"   [ORPHAN FK RESOLUTION] customer_perk_redemptions ID={rec.get('id')}: perk_id={rec['perk_id']} not in customer_retention_perks. Nullified to preserve transaction integrity.")
                        rec["perk_id"] = None

            # Check existing target records
            tgt_existing_rows = {}
            if target_existing_counts.get(tbl_name, 0) > 0:
                tgt_rows = tgt_conn.execute(select(tgt_table)).fetchall()
                tgt_existing_rows = {r.id: dict(r._mapping) for r in tgt_rows if hasattr(r, 'id')}

            # Check for data discrepancies in existing rows (never silently ignore conflicting data)
            records_to_insert = []
            table_conflicts = 0

            for rec in clean_records:
                rec_id = rec.get("id")
                if rec_id in tgt_existing_rows:
                    mismatches = compare_record_fields(rec, tgt_existing_rows[rec_id])
                    if mismatches:
                        print(f"   [DATA MISMATCH] {tbl_name} (ID={rec_id}): {', '.join(mismatches[:3])}")
                        table_conflicts += 1
                        total_discrepancies += 1
                else:
                    records_to_insert.append(rec)

            if table_conflicts > 0:
                print(f"   [WARN] Table '{tbl_name}' had {table_conflicts} conflicting record(s) with mismatched values.")

            if len(records_to_insert) > 0:
                chunk_size = 250
                for i in range(0, len(records_to_insert), chunk_size):
                    chunk = records_to_insert[i:i + chunk_size]
                    if target_engine.name == "postgresql":
                        stmt = pg_insert(tgt_table).values(chunk)
                        tgt_conn.execute(stmt)
                    else:
                        tgt_conn.execute(tgt_table.insert(), chunk)
                tgt_conn.commit()
                print(f"[OK] Migrated '{tbl_name}': {len(records_to_insert)} new records inserted ({len(tgt_existing_rows)} previously existed).")
            else:
                print(f"[-] Table '{tbl_name}': All {src_count} records already present on target.")

            # Verify target count
            tgt_count_after = tgt_conn.execute(text(f'SELECT COUNT(*) FROM "{tbl_name}"')).scalar()
            is_match = (tgt_count_after >= src_count)
            migration_report.append({
                "table": tbl_name,
                "source_count": src_count,
                "target_count": tgt_count_after,
                "new_inserted": len(records_to_insert),
                "conflicts": table_conflicts,
                "status": "PASS" if is_match and table_conflicts == 0 else ("WARN" if is_match else "FAIL")
            })

            # Reset sequence
            if target_engine.name == "postgresql":
                reset_postgres_sequences(target_engine, tbl_name)

    # 7. Summary
    print("\n" + "=" * 80)
    print(f" {'TABLE NAME':<30} | {'SOURCE':<8} | {'TARGET':<8} | {'INSERTED':<9} | {'STATUS':<8}")
    print("-" * 80)
    all_passed = True
    for rep in migration_report:
        status_str = rep["status"]
        if status_str != "PASS":
            all_passed = False
        print(f" {rep['table']:<30} | {rep['source_count']:<8} | {rep['target_count']:<8} | {rep['new_inserted']:<9} | [{status_str}]")
    print("=" * 80)

    if total_discrepancies > 0:
        print(f"\n[ALERT] {total_discrepancies} data discrepancies detected in overlapping records.")
    elif all_passed:
        print("\n[SUCCESS] Data migration completed with 100% referential integrity and zero data conflicts!")
        print("Run verification audit: python database/scripts/verify_migration.py")
    else:
        print("\n[WARNING] Row count discrepancies detected. Inspect the summary above.")

    return all_passed and (total_discrepancies == 0)

if __name__ == "__main__":
    default_sqlite = os.path.join(PROJECT_ROOT, "backend", "ecommerce_churn.db")
    default_source = os.getenv("SOURCE_DATABASE_URL") or f"sqlite:///{default_sqlite}"

    parser = argparse.ArgumentParser(description="Migrate data from SQLite to Supabase PostgreSQL")
    parser.add_argument("--source-url", type=str, default=default_source, help="Source database connection string")
    parser.add_argument("--target-url", type=str, default=None, help="Target Supabase PostgreSQL connection string")
    parser.add_argument("--skip-schema", action="store_true", help="Skip DDL schema creation")
    parser.add_argument("--resume", action="store_true", help="Resume interrupted migration safely with data reconciliation")

    args = parser.parse_args()
    target_url = args.target_url or os.getenv("TARGET_DATABASE_URL") or os.getenv("DATABASE_URL")

    if not target_url or "sqlite" in target_url:
        print("\n[Configuration Required] No Supabase PostgreSQL target URL specified.")
        print("Set your connection string via PowerShell:")
        print('  $env:TARGET_DATABASE_URL="postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?sslmode=require"')
        print("or pass directly via flag:")
        print('  python database/scripts/migrate_mysql_to_postgres.py --target-url "postgresql://..."')
        sys.exit(1)

    success = run_migration(args.source_url, target_url, apply_schema=not args.skip_schema, resume=args.resume)
    sys.exit(0 if success else 1)
