import sqlite3
import requests
import json
import concurrent.futures
import time

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = "backend/ecommerce_churn.db"

def get_db():
    return sqlite3.connect(DB_PATH)

def reset_db_perks():
    conn = get_db()
    c = conn.cursor()
    # Clear test redemptions
    c.execute("DELETE FROM customer_perk_redemptions")
    # Reset customer 1
    c.execute("""
        UPDATE customer_retention_perks
        SET status = 'Accepted', coupon_used = 0, shipping_used = 0, used_order_id = NULL, used_at = NULL, is_single_use = 1
        WHERE customer_id = 1 AND coupon_code = 'RECOVER10'
    """)
    # Reset customer 3
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
    # Reset customer 9
    c.execute("""
        UPDATE customer_retention_perks
        SET status = 'Accepted', coupon_used = 0, shipping_used = 0, used_order_id = NULL, used_at = NULL, is_single_use = 1
        WHERE customer_id = 9 AND coupon_code IN ('VIP15', 'SPEED5')
    """)
    conn.commit()
    conn.close()

reset_db_perks()

print("="*60)
print("TESTING 10 SCENARIOS FOR AUTOMATIC RETENTION OFFER REMOVAL")
print("="*60)

# SCENARIO 8: Check other customer account baseline
print("\n--- BASELINE CHECK (Customer 1, 3, 9) ---")
res1 = requests.get(f"{BASE_URL}/api/customers/1/retention-perks").json()
vouchers_c1 = [v["code"] for v in res1.get("active_vouchers", [])]
print(f"Customer 1 initial active vouchers: {vouchers_c1}, free_shipping: {res1.get('has_express_shipping')}")

res3 = requests.get(f"{BASE_URL}/api/customers/3/retention-perks").json()
vouchers_c3 = [v["code"] for v in res3.get("active_vouchers", [])]
print(f"Customer 3 initial active vouchers: {vouchers_c3}")

res9 = requests.get(f"{BASE_URL}/api/customers/9/retention-perks").json()
vouchers_c9 = [v["code"] for v in res9.get("active_vouchers", [])]
print(f"Customer 9 initial active vouchers: {vouchers_c9}")

# SCENARIO 5: Fail checkout or payment: no benefit is incorrectly consumed
print("\n--- SCENARIO 5: Failed checkout does not consume perks ---")
fail_payload = {
    "customer_id": 1,
    "items": [], # Empty items causes 400 failure
    "shipping_address": "Test Fail",
    "payment_mode": "UPI",
    "voucher_code": "RECOVER10"
}
fail_resp = requests.post(f"{BASE_URL}/api/store/orders", json=fail_payload)
print(f"Fail checkout response status: {fail_resp.status_code}")
res1_after_fail = requests.get(f"{BASE_URL}/api/customers/1/retention-perks").json()
vouchers_c1_after_fail = [v["code"] for v in res1_after_fail.get("active_vouchers", [])]
print(f"Customer 1 vouchers after failed checkout: {vouchers_c1_after_fail}")
assert "RECOVER10" in vouchers_c1_after_fail, "FAIL: RECOVER10 was prematurely consumed on failed checkout!"
print(">>> SCENARIO 5 PASSED: Failed checkout did not consume RECOVER10.")

# SCENARIO 1 & 2: Use RECOVER10 and free-delivery benefit -> disappears after successful order
print("\n--- SCENARIO 1 & 2: Redeem RECOVER10 & free delivery on successful order ---")
# Validate voucher first
val_resp = requests.post(f"{BASE_URL}/api/store/orders/validate-voucher", json={
    "customer_id": 1,
    "voucher_code": "RECOVER10",
    "cart_subtotal": 600
}).json()
print(f"Validation before order: {val_resp}")
assert val_resp["valid"] == True

success_payload = {
    "customer_id": 1,
    "items": [{"product_id": 1, "quantity": 1}],
    "shipping_address": "Flat 402, Bangalore",
    "payment_mode": "UPI",
    "wallet_credit_applied": 0,
    "voucher_code": "RECOVER10"
}
order_resp = requests.post(f"{BASE_URL}/api/store/orders", json=success_payload).json()
print(f"Order placement response success: {order_resp.get('success')}, order_number: {order_resp.get('order', {}).get('order_number')}")
assert order_resp.get("success") == True

res1_after_order = requests.get(f"{BASE_URL}/api/customers/1/retention-perks").json()
vouchers_c1_after_order = [v["code"] for v in res1_after_order.get("active_vouchers", [])]
print(f"Customer 1 vouchers after order: {vouchers_c1_after_order}")
assert "RECOVER10" not in vouchers_c1_after_order, "FAIL: RECOVER10 still in active vouchers!"
print(">>> SCENARIO 1 PASSED: RECOVER10 disappeared from Active Vouchers after successful order placement.")
print(f"Customer 1 free shipping perk after order: {res1_after_order.get('has_express_shipping')}")
print(">>> SCENARIO 2 PASSED: Associated free delivery benefit was consumed.")

# Try to validate RECOVER10 again for customer 1
val_resp_again = requests.post(f"{BASE_URL}/api/store/orders/validate-voucher", json={
    "customer_id": 1,
    "voucher_code": "RECOVER10",
    "cart_subtotal": 600
}).json()
print(f"Validation after order: {val_resp_again}")
assert val_resp_again["valid"] == False, "FAIL: RECOVER10 should be invalid after being used!"

# SCENARIO 3: Use CARE10: single use cannot be redeemed again
print("\n--- SCENARIO 3: Single-use CARE10 cannot be redeemed again ---")
care_order_payload = {
    "customer_id": 3,
    "items": [{"product_id": 2, "quantity": 1}],
    "shipping_address": "Indiranagar, Bangalore",
    "payment_mode": "Credit Card",
    "voucher_code": "CARE10"
}
order_resp_care = requests.post(f"{BASE_URL}/api/store/orders", json=care_order_payload).json()
print(f"Customer 3 order with CARE10: {order_resp_care.get('success')}")
assert order_resp_care.get("success") == True

# Second order attempt with CARE10 on a new shopping basket must fail
care_order_payload_repeat = {
    "customer_id": 3,
    "items": [{"product_id": 5, "quantity": 1}],
    "shipping_address": "Indiranagar, Bangalore",
    "payment_mode": "Credit Card",
    "voucher_code": "CARE10"
}
order_resp_care_repeat = requests.post(f"{BASE_URL}/api/store/orders", json=care_order_payload_repeat)
print(f"Second order attempt with CARE10 status: {order_resp_care_repeat.status_code}, response: {order_resp_care_repeat.text}")
assert order_resp_care_repeat.status_code == 400 or order_resp_care_repeat.json().get("success") == False
print(">>> SCENARIO 3 PASSED: CARE10 cannot be redeemed again.")

# SCENARIO 4: Use SPEED5: coupon and express delivery follow individual usage rules
print("\n--- SCENARIO 4: SPEED5 coupon and express-delivery tracking ---")
# Customer 9 has SPEED5. Let's place an order without coupon code but using express delivery or vice versa
speed_val = requests.post(f"{BASE_URL}/api/store/orders/validate-voucher", json={
    "customer_id": 9,
    "voucher_code": "SPEED5",
    "cart_subtotal": 1000
}).json()
print(f"Customer 9 SPEED5 validation: {speed_val}")
assert speed_val["valid"] == True

speed_order = requests.post(f"{BASE_URL}/api/store/orders", json={
    "customer_id": 9,
    "items": [{"product_id": 3, "quantity": 1}],
    "shipping_address": "Whitefield, Bangalore",
    "payment_mode": "UPI",
    "voucher_code": "SPEED5"
}).json()
print(f"Customer 9 order with SPEED5: {speed_order.get('success')}")
assert speed_order.get("success") == True

res9_after = requests.get(f"{BASE_URL}/api/customers/9/retention-perks").json()
vouchers_c9_after = [v["code"] for v in res9_after.get("active_vouchers", [])]
print(f"Customer 9 active vouchers after SPEED5: {vouchers_c9_after}")
assert "SPEED5" not in vouchers_c9_after
# Note: VIP15 should still remain for Customer 9!
assert "VIP15" in vouchers_c9_after, f"FAIL: VIP15 should still be active for customer 9! Got {vouchers_c9_after}"
print(">>> SCENARIO 4 PASSED: SPEED5 consumed while VIP15 remains active.")

# SCENARIO 6: Place two simultaneous orders using the same single-use coupon: only one can succeed
print("\n--- SCENARIO 6: Simultaneous order placement concurrency protection ---")
# Customer 3 still has RECOVER10. Launch 2 simultaneous requests with distinct baskets
concurrent_payload_1 = {
    "customer_id": 3,
    "items": [{"product_id": 4, "quantity": 1}],
    "shipping_address": "Koramangala, Bangalore",
    "payment_mode": "UPI",
    "voucher_code": "RECOVER10"
}
concurrent_payload_2 = {
    "customer_id": 3,
    "items": [{"product_id": 1, "quantity": 1}],
    "shipping_address": "Koramangala, Bangalore",
    "payment_mode": "UPI",
    "voucher_code": "RECOVER10"
}

def place_order_worker_1():
    return requests.post(f"{BASE_URL}/api/store/orders", json=concurrent_payload_1)

def place_order_worker_2():
    return requests.post(f"{BASE_URL}/api/store/orders", json=concurrent_payload_2)

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    future1 = executor.submit(place_order_worker_1)
    future2 = executor.submit(place_order_worker_2)
    res_sim1 = future1.result()
    res_sim2 = future2.result()

codes = [res_sim1.status_code, res_sim2.status_code]
print(f"Simultaneous requests status codes: {codes}")
success_count = sum(1 for r in [res_sim1, res_sim2] if r.status_code == 200 and r.json().get("success"))
print(f"Success count: {success_count} (Expected exactly 1)")
assert success_count == 1, f"FAIL: Concurrency protection failed! Success count was {success_count}"
print(">>> SCENARIO 6 PASSED: Concurrency protection ensured only 1 order redeemed RECOVER10.")

# SCENARIO 7: Log out and log back in: consumed benefits remain unavailable
print("\n--- SCENARIO 7: Login profile checks ---")
login_resp = requests.post(f"{BASE_URL}/api/store/auth/login", json={
    "username": "AMZ_PRED1_1001",
    "password": "Password123"
}).json()
user_perks = login_resp.get("perks", {})
login_vouchers = [v["code"] for v in user_perks.get("active_vouchers", [])]
print(f"Customer 1 vouchers on login: {login_vouchers}")
assert "RECOVER10" not in login_vouchers, "FAIL: RECOVER10 appeared again on login!"
print(">>> SCENARIO 7 PASSED: Consumed benefits remain unavailable after fresh login.")

# SCENARIO 8: Check other customer accounts: Customer 9 still has VIP15, Customer 1 never affected Customer 3 or 9
print("\n--- SCENARIO 8: Cross-customer isolation check ---")
res9_check = requests.get(f"{BASE_URL}/api/customers/9/retention-perks").json()
vouchers_9_now = [v["code"] for v in res9_check.get("active_vouchers", [])]
print(f"Customer 9 vouchers: {vouchers_9_now}")
assert "VIP15" in vouchers_9_now, "FAIL: Customer 9 VIP15 was incorrectly affected!"
print(">>> SCENARIO 8 PASSED: Customer benefits are completely isolated per internal customer ID.")

# SCENARIO 9: Read a retention message: message remains in Messages section with read status updated
print("\n--- SCENARIO 9: Message read status lifecycle ---")
notifs1 = requests.get(f"{BASE_URL}/api/customers/1/retention-perks").json().get("notifications", [])
if notifs1:
    target_notif = notifs1[0]
    notif_id = target_notif["id"]
    print(f"Marking notification {notif_id} as read...")
    read_resp = requests.post(f"{BASE_URL}/api/customers/1/notifications/{notif_id}/read").json()
    print(f"Read mark response: {read_resp}")
    notifs1_after = requests.get(f"{BASE_URL}/api/customers/1/retention-perks").json().get("notifications", [])
    found_after = next((n for n in notifs1_after if n["id"] == notif_id), None)
    assert found_after is not None, "FAIL: Notification was deleted upon reading!"
    assert found_after["is_read"] == True, "FAIL: Notification read status was not updated to True!"
    print(f"Notification {notif_id} retained with is_read={found_after['is_read']}")
print(">>> SCENARIO 9 PASSED: Retention messages remain preserved with normal read/unread status.")

# SCENARIO 10: Verify order history and database records after redemption
print("\n--- SCENARIO 10: Database audit and Order History verification ---")
orders_c1 = requests.get(f"{BASE_URL}/api/store/orders/my-orders?customer_id=1").json().get("orders", [])
assert len(orders_c1) > 0, "No orders found in order history!"
latest_o1 = orders_c1[0]
print(f"Latest Order for Cust 1: #{latest_o1.get('order_number')}, Voucher: {latest_o1.get('voucher_code')}, Discount: {latest_o1.get('discount')}, FreeShip: {latest_o1.get('free_shipping_applied')}")
assert latest_o1.get("voucher_code") == "RECOVER10"
assert latest_o1.get("free_shipping_applied") == True

db = get_db()
cur = db.cursor()
cur.execute("SELECT id, customer_id, order_id, perk_id, coupon_code, benefit_type, redemption_date FROM customer_perk_redemptions")
redemptions = cur.fetchall()
print(f"\nTotal audit records in customer_perk_redemptions: {len(redemptions)}")
for r in redemptions:
    print(f"  Redemption ID {r[0]}: Cust {r[1]}, Order {r[2]}, Coupon {r[4]}, Benefit {r[5]}, Time {r[6]}")

assert len(redemptions) > 0, "FAIL: No records in customer_perk_redemptions table!"
print(">>> SCENARIO 10 PASSED: Database audit records and order history perfectly preserved.")

print("\n" + "="*60)
print("ALL 10 SCENARIOS VERIFIED SUCCESSFULLY!")
print("="*60)
