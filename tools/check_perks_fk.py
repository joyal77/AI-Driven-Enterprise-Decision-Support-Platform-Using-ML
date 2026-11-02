import sqlite3

conn = sqlite3.connect("backend/ecommerce_churn.db")
c = conn.cursor()

print("=== Checking customer_perk_redemptions Foreign Keys ===")

# 1. Check perk_id in customer_retention_perks
c.execute("SELECT id, perk_id FROM customer_perk_redemptions WHERE perk_id IS NOT NULL")
redemptions = c.fetchall()
print(f"Total redemption records: {len(redemptions)}")

for r_id, p_id in redemptions:
    c.execute("SELECT id, customer_id, title FROM customer_retention_perks WHERE id = ?", (p_id,))
    perk = c.fetchone()
    print(f"Redemption #{r_id} perk_id={p_id} -> customer_retention_perks: {perk}")

# 2. Check order_id in orders
for r_id, p_id in redemptions:
    c.execute("SELECT order_id FROM customer_perk_redemptions WHERE id = ?", (r_id,))
    o_id = c.fetchone()[0]
    c.execute("SELECT id, order_number, customer_id FROM orders WHERE id = ?", (o_id,))
    order = c.fetchone()
    print(f"Redemption #{r_id} order_id={o_id} -> orders: {order}")

# 3. Check customer_id in customers
for r_id, p_id in redemptions:
    c.execute("SELECT customer_id FROM customer_perk_redemptions WHERE id = ?", (r_id,))
    cust_id = c.fetchone()[0]
    c.execute("SELECT id, source_customer_id FROM customers WHERE id = ?", (cust_id,))
    cust = c.fetchone()
    print(f"Redemption #{r_id} customer_id={cust_id} -> customers: {cust}")

# List all IDs in customer_retention_perks
c.execute("SELECT id, customer_id, title, used_order_id FROM customer_retention_perks")
print("\nAll records in customer_retention_perks:")
for p in c.fetchall():
    print(p)

conn.close()

