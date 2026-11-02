import sqlite3

conn = sqlite3.connect("backend/ecommerce_churn.db")
c = conn.cursor()

c.execute("SELECT id, customer_id, title, used_order_id FROM customer_retention_perks")
perks = c.fetchall()

print(f"Total rows in customer_retention_perks: {len(perks)}")
non_null_count = 0
matching_orders = 0
orphan_count = 0

for p_id, cust_id, title, used_order_id in perks:
    if used_order_id is not None:
        non_null_count += 1
        c.execute("SELECT id, order_number FROM orders WHERE id = ?", (used_order_id,))
        order = c.fetchone()
        if order:
            matching_orders += 1
            print(f"Perk ID={p_id}: used_order_id={used_order_id} -> MATCHES Order {order[1]}")
        else:
            orphan_count += 1
            print(f"Perk ID={p_id}: used_order_id={used_order_id} -> ORPHAN (Order does not exist!)")
    else:
        print(f"Perk ID={p_id}: used_order_id is NULL")

print("\n=== SUMMARY FOR customer_retention_perks.used_order_id ===")
print(f"Total rows in customer_retention_perks: {len(perks)}")
print(f"Total non-null used_order_id values   : {non_null_count}")
print(f"Number of matching orders             : {matching_orders}")
print(f"Number of orphan references           : {orphan_count}")
print(f"Is additional foreign key constraint safe? : {'YES' if orphan_count == 0 else 'NO'}")

conn.close()

