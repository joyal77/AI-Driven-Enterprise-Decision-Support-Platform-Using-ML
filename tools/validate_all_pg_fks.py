import json
import re

with open("database/migrations/001_initial_schema.sql", "r", encoding="utf-8") as f:
    sql = f.read()

# 1. Extract tables in order of creation in SQL file
table_order = re.findall(r'CREATE TABLE IF NOT EXISTS\s+([a-zA-Z0-9_]+)', sql, re.IGNORECASE)
table_positions = {tbl: i for i, tbl in enumerate(table_order)}

# 2. Extract all foreign key constraints from the SQL file
# Match inline: col_name TYPE ... REFERENCES target_table(target_col)
# Match table-level: FOREIGN KEY (from_col) REFERENCES target_table(target_col)
inline_fks = re.findall(r'([a-zA-Z0-9_]+)\s+([a-zA-Z0-9_]+).*?REFERENCES\s+([a-zA-Z0-9_]+)\s*\(([a-zA-Z0-9_]+)\)', sql, re.IGNORECASE)

# Also parse table blocks to know which table owns each FK
create_blocks = re.findall(r'CREATE TABLE IF NOT EXISTS\s+([a-zA-Z0-9_]+)\s*\((.*?)\);', sql, re.DOTALL | re.IGNORECASE)

all_fks = []
table_columns = {}
table_pks = {}

for tbl_name, body in create_blocks:
    cols = {}
    pks = []
    lines = [line.strip().rstrip(',') for line in body.split('\n') if line.strip()]
    for line in lines:
        if line.startswith('--'):
            continue
        parts = line.split()
        if len(parts) >= 2 and not line.upper().startswith('CONSTRAINT'):
            col_name = parts[0]
            col_type = parts[1]
            cols[col_name] = col_type
            if "PRIMARY KEY" in line.upper():
                pks.append(col_name)
            if "REFERENCES" in line.upper():
                ref_m = re.search(r'REFERENCES\s+([a-zA-Z0-9_]+)\s*\(([a-zA-Z0-9_]+)\)', line, re.IGNORECASE)
                del_m = re.search(r'ON DELETE\s+([A-Za-z ]+)', line, re.IGNORECASE)
                del_rule = del_m.group(1).strip() if del_m else "NO ACTION"
                if ref_m:
                    all_fks.append({
                        "child_table": tbl_name,
                        "child_col": col_name,
                        "child_type": col_type,
                        "parent_table": ref_m.group(1),
                        "parent_col": ref_m.group(2),
                        "on_delete": del_rule
                    })
    table_columns[tbl_name] = cols
    table_pks[tbl_name] = pks

print(f"Total Foreign Keys identified in PostgreSQL DDL: {len(all_fks)}\n")
fk_validation_table = []

for fk in all_fks:
    c_tbl = fk["child_table"]
    c_col = fk["child_col"]
    c_type = fk["child_type"]
    p_tbl = fk["parent_table"]
    p_col = fk["parent_col"]
    
    # 1. Parent table exists
    parent_exists = p_tbl in table_positions
    
    # 2. Parent column exists
    parent_col_exists = parent_exists and (p_col in table_columns.get(p_tbl, {}))
    p_type = table_columns.get(p_tbl, {}).get(p_col, "MISSING")
    
    # 3. Type compatibility
    # BIGINT vs BIGINT GENERATED AS IDENTITY or INTEGER
    type_compatible = ("BIGINT" in c_type.upper() and "BIGINT" in p_type.upper()) or (c_type.upper() == p_type.upper())
    
    # 4. Parent table created before child table (DAG order)
    dag_order_valid = parent_exists and (table_positions[p_tbl] < table_positions[c_tbl])
    
    # 5. Parent column is Primary Key / Unique
    is_parent_pk = p_col in table_pks.get(p_tbl, [])
    
    valid = parent_exists and parent_col_exists and dag_order_valid and is_parent_pk
    
    fk_validation_table.append({
        "child": f"{c_tbl}.{c_col}",
        "parent": f"{p_tbl}.{p_col}",
        "child_type": c_type,
        "parent_type": p_type,
        "on_delete": fk["on_delete"],
        "parent_created_first": dag_order_valid,
        "parent_is_pk": is_parent_pk,
        "valid": valid
    })

print(f"{'#':<3} | {'CHILD (FROM)':<38} | {'PARENT (TO)':<32} | {'DAG ORDER':<10} | {'PARENT PK':<10} | {'STATUS':<6}")
print("-" * 110)
for i, fkv in enumerate(fk_validation_table, 1):
    print(f"{i:<3} | {fkv['child']:<38} | {fkv['parent']:<32} | {str(fkv['parent_created_first']):<10} | {str(fkv['parent_is_pk']):<10} | {'VALID' if fkv['valid'] else 'INVALID':<6}")

with open("tools/fk_validation_table.json", "w", encoding="utf-8") as f:
    json.dump(fk_validation_table, f, indent=2)

print("\nSaved FK validation report to tools/fk_validation_table.json")

