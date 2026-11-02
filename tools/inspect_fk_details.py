import sqlite3

conn = sqlite3.connect("backend/ecommerce_churn.db")
c = conn.cursor()

c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='customer_perk_redemptions'")
print("SQLite DDL for customer_perk_redemptions:\n", c.fetchone()[0])

print("\nPRAGMA foreign_key_list for customer_perk_redemptions:")
c.execute("PRAGMA foreign_key_list(customer_perk_redemptions)")
for fk in c.fetchall():
    print(fk)

print("\nRecords in customer_perk_redemptions:")
c.execute("SELECT * FROM customer_perk_redemptions")
cols = [d[0] for d in c.description]
print(cols)
for r in c.fetchall():
    print(r)

conn.close()

