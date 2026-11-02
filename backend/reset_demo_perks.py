import sqlite3

conn = sqlite3.connect('backend/ecommerce_churn.db')
c = conn.cursor()
c.execute('DELETE FROM customer_perk_redemptions')
c.execute("""
    UPDATE customer_retention_perks
    SET status = 'Accepted', coupon_used = 0, shipping_used = 0, used_order_id = NULL, used_at = NULL, is_single_use = 1
    WHERE customer_id = 1 AND coupon_code = 'RECOVER10'
""")
c.execute("""
    UPDATE customer_retention_perks
    SET status = 'Approved', coupon_used = 0, shipping_used = 0, used_order_id = NULL, used_at = NULL, is_single_use = 1
    WHERE customer_id = 3 AND coupon_code IN ('CARE10', 'SPEED5')
""")
c.execute("""
    UPDATE customer_retention_perks
    SET status = 'Accepted', coupon_used = 0, shipping_used = 0, used_order_id = NULL, used_at = NULL, is_single_use = 1
    WHERE customer_id = 3 AND coupon_code = 'RECOVER10'
""")
c.execute("""
    UPDATE customer_retention_perks
    SET status = 'Accepted', coupon_used = 0, shipping_used = 0, used_order_id = NULL, used_at = NULL, is_single_use = 1
    WHERE customer_id = 9 AND coupon_code IN ('VIP15', 'SPEED5')
""")
conn.commit()
print("Reset result:", c.execute('SELECT customer_id, coupon_code, status, coupon_used, shipping_used FROM customer_retention_perks').fetchall())
conn.close()
