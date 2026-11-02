import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.db.session import SessionLocal
from backend.app.db.models import (
    Customer,
    CustomerRetentionPerk,
    CustomerNotification,
    RetentionRecommendation,
    Product,
    Order
)

client = TestClient(app)

def setup_test_customers():
    db = SessionLocal()
    try:
        cust1 = db.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1001").first()
        if not cust1:
            cust1 = db.query(Customer).first()
        cust2 = db.query(Customer).filter(Customer.id != cust1.id).first()
        assert cust1 is not None and cust2 is not None

        cust1.membership_status = "Standard"
        cust2.membership_status = "Standard"

        # Clean existing test perks and notifications
        db.query(CustomerRetentionPerk).filter(CustomerRetentionPerk.customer_id.in_([cust1.id, cust2.id])).delete()
        db.query(CustomerNotification).filter(CustomerNotification.customer_id.in_([cust1.id, cust2.id])).delete()
        db.commit()
        return cust1.id, cust2.id
    finally:
        db.close()

def test_campaign_delivery_benefit_mappings_and_persistence():
    cust1_id, cust2_id = setup_test_customers()
    db = SessionLocal()
    try:
        # Campaign 1: Automated WhatsApp & SMS Cart Recovery with Free Delivery (RECOVER10)
        res1 = client.post(f"/api/customers/{cust1_id}/retention-action/toggle", json={
            "campaign_id": "camp_cart_recovery",
            "status": "Accepted",
            "title": "Automated WhatsApp & SMS Cart Recovery with Free Delivery",
            "perk_type": "discount_voucher",
            "perk_value": 10.0,
            "coupon_code": "RECOVER10",
            "free_shipping": True,
            "action_summary": "Cart Recovery Nudge: Automated SMS/WhatsApp nudge with 10% coupon (RECOVER10) & Free Delivery.",
            "channel": "WhatsApp / SMS Direct Recovery"
        })
        assert res1.status_code == 200
        assert res1.json()["success"] is True

        # Campaign 2: Priority VIP Support Concierge Callback & 10% Resolution Coupon (CARE10 - no free shipping)
        res2 = client.post(f"/api/customers/{cust1_id}/retention-action/toggle", json={
            "campaign_id": "camp_support_vip",
            "status": "Accepted",
            "title": "Priority VIP Support Concierge Callback & 10% Resolution Coupon",
            "perk_type": "discount_voucher",
            "perk_value": 10.0,
            "coupon_code": "CARE10",
            "free_shipping": False,
            "action_summary": "Support Concierge Callback: Resolve open tickets and issue 10% discount voucher (CARE10).",
            "channel": "VIP Concierge (Phone / Priority Callback)"
        })
        assert res2.status_code == 200

        # Campaign 3: Free Express Air Priority Delivery & 5% Delay Apology Coupon (SPEED5)
        res3 = client.post(f"/api/customers/{cust1_id}/retention-action/toggle", json={
            "campaign_id": "camp_logistics_guarantee",
            "status": "Accepted",
            "title": "Free Express Air Priority Delivery & 5% Delay Apology Coupon",
            "perk_type": "express_shipping",
            "perk_value": 5.0,
            "coupon_code": "SPEED5",
            "free_shipping": True,
            "action_summary": "Fulfillment Guarantee: Permanent Express Air Free Delivery upgrade & 5% apology coupon (SPEED5).",
            "channel": "Express Air Logistics & Apology Coupon"
        })
        assert res3.status_code == 200

        # Verify DB persistence directly
        perks = db.query(CustomerRetentionPerk).filter(CustomerRetentionPerk.customer_id == cust1_id).all()
        perk_map = {p.campaign_id: p for p in perks}

        assert "camp_cart_recovery" in perk_map
        assert perk_map["camp_cart_recovery"].coupon_code == "RECOVER10"
        assert perk_map["camp_cart_recovery"].free_shipping == 1
        assert perk_map["camp_cart_recovery"].perk_value == 10.0

        assert "camp_support_vip" in perk_map
        assert perk_map["camp_support_vip"].coupon_code == "CARE10"
        assert perk_map["camp_support_vip"].free_shipping == 0
        assert perk_map["camp_support_vip"].perk_value == 10.0

        assert "camp_logistics_guarantee" in perk_map
        assert perk_map["camp_logistics_guarantee"].coupon_code == "SPEED5"
        assert perk_map["camp_logistics_guarantee"].free_shipping == 1
        assert perk_map["camp_logistics_guarantee"].perk_value == 5.0

        # Verify notifications created with all required fields
        notifs = db.query(CustomerNotification).filter(CustomerNotification.customer_id == cust1_id).all()
        assert len(notifs) >= 3
        for n in notifs:
            assert n.id is not None
            assert n.customer_id == cust1_id
            assert n.title is not None and len(n.title) > 0
            assert n.message is not None and len(n.message) > 0
            assert n.notification_type is not None
            assert n.created_at is not None
            assert n.is_read == 0
            assert n.navigation_target is not None

        # Verify API perks response
        perks_res = client.get(f"/api/customers/{cust1_id}/retention-perks")
        assert perks_res.status_code == 200
        pdata = perks_res.json()
        assert pdata["has_express_shipping"] is True
        vouchers = {v["code"]: v for v in pdata["active_vouchers"]}
        assert "RECOVER10" in vouchers and vouchers["RECOVER10"]["free_shipping"] is True
        assert "CARE10" in vouchers and vouchers["CARE10"]["free_shipping"] is False
        assert "SPEED5" in vouchers and vouchers["SPEED5"]["free_shipping"] is True

    finally:
        db.close()

def test_idempotency_repeated_accept_no_duplicates():
    cust1_id, _ = setup_test_customers()
    db = SessionLocal()
    try:
        payload = {
            "campaign_id": "camp_cart_recovery",
            "status": "Accepted",
            "title": "Automated WhatsApp & SMS Cart Recovery with Free Delivery",
            "perk_type": "discount_voucher",
            "perk_value": 10.0,
            "coupon_code": "RECOVER10",
            "free_shipping": True,
            "action_summary": "Cart Recovery Nudge: Automated SMS/WhatsApp nudge with 10% coupon (RECOVER10) & Free Delivery.",
            "channel": "WhatsApp / SMS Direct Recovery"
        }

        # Submit 3 times consecutively
        res1 = client.post(f"/api/customers/{cust1_id}/retention-action/toggle", json=payload)
        res2 = client.post(f"/api/customers/{cust1_id}/retention-action/toggle", json=payload)
        res3 = client.post(f"/api/customers/{cust1_id}/retention-action/toggle", json=payload)

        assert res1.status_code == 200
        assert res2.status_code == 200
        assert res3.status_code == 200

        # Verify only 1 perk record exists
        perks = db.query(CustomerRetentionPerk).filter(
            CustomerRetentionPerk.customer_id == cust1_id,
            CustomerRetentionPerk.campaign_id == "camp_cart_recovery"
        ).all()
        assert len(perks) == 1, f"Expected exactly 1 perk, found {len(perks)}"

        # Verify only 1 notification record exists
        notifs = db.query(CustomerNotification).filter(
            CustomerNotification.customer_id == cust1_id,
            CustomerNotification.campaign_id == "camp_cart_recovery"
        ).all()
        assert len(notifs) == 1, f"Expected exactly 1 notification, found {len(notifs)}"

        # Verify recommendation log is also not duplicated
        recs = db.query(RetentionRecommendation).filter(
            RetentionRecommendation.customer_id == cust1_id,
            RetentionRecommendation.recommendation_description.like("%camp_cart_recovery%")
        ).all()
        assert len(recs) <= 1

    finally:
        db.close()

def test_rejection_clears_perks_and_prevents_accidental_approval():
    cust1_id, _ = setup_test_customers()
    db = SessionLocal()
    try:
        # 1. Reject Campaign
        reject_payload = {
            "campaign_id": "camp_support_vip",
            "status": "Rejected",
            "title": "Priority VIP Support Concierge Callback & 10% Resolution Coupon",
            "perk_type": "discount_voucher",
            "perk_value": 10.0,
            "coupon_code": "CARE10",
            "action_summary": "Support Concierge Callback",
            "channel": "VIP Concierge"
        }
        rej_res = client.post(f"/api/customers/{cust1_id}/retention-action/toggle", json=reject_payload)
        assert rej_res.status_code == 200

        # Verify no active voucher or notification for this campaign
        perks_res = client.get(f"/api/customers/{cust1_id}/retention-perks").json()
        assert "CARE10" not in [v["code"] for v in perks_res.get("active_vouchers", [])]
        assert len(perks_res.get("notifications", [])) == 0

        # 2. Attempting to directly Accept without explicit state transition (force=False) must be blocked
        accept_payload = {
            "campaign_id": "camp_support_vip",
            "status": "Accepted",
            "title": "Priority VIP Support Concierge Callback & 10% Resolution Coupon",
            "perk_type": "discount_voucher",
            "perk_value": 10.0,
            "coupon_code": "CARE10",
            "force": False
        }
        acc_res = client.post(f"/api/customers/{cust1_id}/retention-action/toggle", json=accept_payload)
        assert acc_res.status_code == 400
        assert "state transition" in acc_res.json()["detail"].lower()

        # 3. Explicit supported state transition with force=True is allowed
        accept_payload["force"] = True
        acc_ok = client.post(f"/api/customers/{cust1_id}/retention-action/toggle", json=accept_payload)
        assert acc_ok.status_code == 200
        assert acc_ok.json()["success"] is True

    finally:
        db.close()

def test_dedicated_store_notification_endpoints():
    cust1_id, _ = setup_test_customers()
    db = SessionLocal()
    try:
        # Create an accepted campaign to seed notification
        client.post(f"/api/customers/{cust1_id}/retention-action/toggle", json={
            "campaign_id": "camp_cart_recovery",
            "status": "Accepted",
            "title": "Automated WhatsApp & SMS Cart Recovery with Free Delivery",
            "perk_type": "discount_voucher",
            "perk_value": 10.0,
            "coupon_code": "RECOVER10",
            "free_shipping": True
        })

        # 1. GET /api/store/notifications
        res = client.get(f"/api/store/notifications?customer_id={cust1_id}")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert len(data["notifications"]) >= 1
        notif = data["notifications"][0]
        assert notif["customer_id"] == cust1_id
        assert notif["campaign_id"] == "camp_cart_recovery"
        assert notif["notification_type"] is not None
        assert notif["navigation_target"] is not None
        assert notif["is_read"] is False

        # 2. GET /api/store/notifications/unread-count
        unread_res = client.get(f"/api/store/notifications/unread-count?customer_id={cust1_id}")
        assert unread_res.status_code == 200
        udata = unread_res.json()
        assert udata["success"] is True
        assert udata["unread_count"] >= 1

        # 3. POST /api/store/notifications/{id}/read
        read_res = client.post(f"/api/store/notifications/{notif['id']}/read?customer_id={cust1_id}")
        assert read_res.status_code == 200
        assert read_res.json()["success"] is True

        # Verify unread count decreased
        unread_res2 = client.get(f"/api/store/notifications/unread-count?customer_id={cust1_id}")
        assert unread_res2.json()["unread_count"] == 0

        # 4. POST /api/store/notifications/read-all
        read_all = client.post(f"/api/store/notifications/read-all?customer_id={cust1_id}")
        assert read_all.status_code == 200
        assert read_all.json()["success"] is True

    finally:
        db.close()

def test_checkout_shipping_fee_reflection():
    cust1_id, _ = setup_test_customers()
    db = SessionLocal()
    try:
        # Find a product with price < 500
        prod = db.query(Product).filter(Product.price < 500, Product.stock_quantity >= 5).first()
        if not prod:
            prod = Product(
                title="Test Budget Item",
                description="Affordable item",
                price=200.0,
                stock_quantity=50,
                category="Accessories",
                image_url="https://images.unsplash.com/photo-1523275335684-37898b6baf30"
            )
            db.add(prod)
            db.commit()
            db.refresh(prod)

        # Ensure customer is not Prime
        cust = db.query(Customer).filter(Customer.id == cust1_id).first()
        cust.membership_status = "Standard"
        db.commit()

        # Approve CARE10 (discount only, free_shipping = False)
        client.post(f"/api/customers/{cust1_id}/retention-action/toggle", json={
            "campaign_id": "camp_support_vip",
            "status": "Accepted",
            "title": "Priority VIP Support Concierge Callback & 10% Resolution Coupon",
            "perk_type": "discount_voucher",
            "perk_value": 10.0,
            "coupon_code": "CARE10",
            "free_shipping": False
        })

        # Place order with CARE10: subtotal < 500, so shipping_fee must be 40.0
        res_care = client.post("/api/store/orders", json={
            "customer_id": cust1_id,
            "items": [{"product_id": prod.id, "quantity": 1}],
            "shipping_address": "Test St 101, Bengaluru",
            "payment_mode": "UPI",
            "wallet_credit_applied": 0.0,
            "voucher_code": "CARE10"
        })
        assert res_care.status_code == 200
        order_care = res_care.json()["order"]
        assert order_care["shipping_fee"] == 40.0, f"CARE10 should not grant free shipping on subtotal < 500, got {order_care['shipping_fee']}"

        # Now approve RECOVER10 (discount + free delivery, free_shipping = True)
        client.post(f"/api/customers/{cust1_id}/retention-action/toggle", json={
            "campaign_id": "camp_cart_recovery",
            "status": "Accepted",
            "title": "Automated WhatsApp & SMS Cart Recovery with Free Delivery",
            "perk_type": "discount_voucher",
            "perk_value": 10.0,
            "coupon_code": "RECOVER10",
            "free_shipping": True
        })

        # Place order with RECOVER10: distinct address avoids duplicate-order suppression window
        res_rec = client.post("/api/store/orders", json={
            "customer_id": cust1_id,
            "items": [{"product_id": prod.id, "quantity": 1}],
            "shipping_address": "Test St 102, Bengaluru",
            "payment_mode": "UPI",
            "wallet_credit_applied": 0.0,
            "voucher_code": "RECOVER10"
        })
        assert res_rec.status_code == 200
        order_rec = res_rec.json()["order"]
        assert order_rec["shipping_fee"] == 0.0, f"RECOVER10 must grant free shipping, got {order_rec['shipping_fee']}"

    finally:
        db.close()

def test_account_isolation_no_leakage():
    cust1_id, cust2_id = setup_test_customers()
    db = SessionLocal()
    try:
        # Deliver perks to Customer 1 only
        client.post(f"/api/customers/{cust1_id}/retention-action/toggle", json={
            "campaign_id": "camp_cart_recovery",
            "status": "Accepted",
            "title": "Automated WhatsApp & SMS Cart Recovery with Free Delivery",
            "perk_type": "discount_voucher",
            "perk_value": 10.0,
            "coupon_code": "RECOVER10",
            "free_shipping": True
        })

        # Verify Customer 2 has zero perks and zero notifications
        c2_perks = client.get(f"/api/customers/{cust2_id}/retention-perks").json()
        assert len(c2_perks["active_vouchers"]) == 0
        assert c2_perks["has_express_shipping"] is False

        c2_notifs = client.get(f"/api/store/notifications?customer_id={cust2_id}").json()
        assert len(c2_notifs["notifications"]) == 0
        assert c2_notifs["unread_count"] == 0

    finally:
        db.close()
