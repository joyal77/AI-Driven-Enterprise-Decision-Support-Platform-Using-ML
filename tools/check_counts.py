import sqlite3

conn = sqlite3.connect("backend/ecommerce_churn.db")
c = conn.cursor()

tables = [
    "cart_items", "churn_predictions", "customer_notifications", "customer_perk_redemptions",
    "customer_retention_perks", "customers", "data_integrity_audit_log", "order_items",
    "orders", "prediction_batches", "products", "retention_recommendations", "store_users", "users"
]

counts = {}
for t in tables:
    c.execute(f'SELECT COUNT(*) FROM "{t}"')
    counts[t] = c.fetchone()[0]

for t, cnt in counts.items():
    print(f"{t}: {cnt}")

print("Sum of all 14 tables:", sum(counts.values()))

# Check subset combinations that might equal 1896
# For example, if data_integrity_audit_log was 468 rows before or if cart_items was 79 rows?
# Or 2096 - 200?
conn.close()

