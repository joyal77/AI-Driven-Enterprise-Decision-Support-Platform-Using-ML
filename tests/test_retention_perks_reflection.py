import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.db.session import SessionLocal
from backend.app.db.models import Customer, CustomerRetentionPerk, Order, Product, ChurnPrediction

client = TestClient(app)

def test_retention_perk_approval_and_account_reflection():
    db = SessionLocal()
    try:
        # 1. Fetch customer AMZ_PRED1_1009
        cust = db.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1009").first()
        if not cust:
            cust = db.query(Customer).first()
        assert cust is not None, "Customer account must exist."

        # Clean existing test perks for this customer
        db.query(CustomerRetentionPerk).filter(CustomerRetentionPerk.customer_id == cust.id).delete()
        db.commit()

        # 2. Check initial perks endpoint
        res = client.get(f"/api/customers/{cust.id}/retention-perks")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert len(data["active_vouchers"]) == 0

        # 3. Admin approves Campaign 1: 10% Grievance Resolution Voucher (CARE10)
        toggle_res1 = client.post(f"/api/customers/{cust.id}/retention-action/toggle", json={
            "campaign_id": "camp_support_vip",
            "status": "Approved",
            "title": "Priority VIP Support Concierge Callback & 10% Resolution Coupon",
            "perk_type": "discount_voucher",
            "perk_value": 10.0,
            "coupon_code": "CARE10",
            "action_summary": "Support Concierge Callback: Resolve open tickets and issue 10% discount voucher (CARE10).",
            "root_cause_driver": "Customer Service & Grievance Overload (3 support tickets filed)",
            "channel": "VIP Concierge (Phone / Priority Callback)"
        })
        assert toggle_res1.status_code == 200
        tdata1 = toggle_res1.json()
        assert tdata1["success"] is True

        # 4. Admin approves Campaign 2: Free Express Air Priority Delivery & 5% Delay Apology Coupon (SPEED5)
        toggle_res2 = client.post(f"/api/customers/{cust.id}/retention-action/toggle", json={
            "campaign_id": "camp_logistics_guarantee",
            "status": "Approved",
            "title": "Free Express Air Priority Delivery & 5% Delay Apology Coupon",
            "perk_type": "express_shipping",
            "perk_value": 5.0,
            "coupon_code": "SPEED5",
            "action_summary": "Fulfillment Guarantee: Permanent Express Air Free Delivery upgrade & 5% apology coupon (SPEED5).",
            "root_cause_driver": "Fulfillment Friction (1 late delivery recorded)",
            "channel": "Express Air Logistics & Apology Coupon"
        })
        assert toggle_res2.status_code == 200

        # 5. Admin approves Campaign 3: 10% Cart Recovery Voucher (RECOVER10)
        toggle_res3 = client.post(f"/api/customers/{cust.id}/retention-action/toggle", json={
            "campaign_id": "camp_cart_recovery",
            "status": "Approved",
            "title": "Automated WhatsApp & SMS Cart Recovery with Free Delivery",
            "perk_type": "discount_voucher",
            "perk_value": 10.0,
            "coupon_code": "RECOVER10",
            "action_summary": "Cart Recovery Nudge: Automated SMS/WhatsApp nudge with 10% coupon (RECOVER10) & Free Delivery.",
            "root_cause_driver": "High Cart Abandonment Friction (3 carts abandoned)",
            "channel": "WhatsApp / SMS Direct Recovery"
        })
        assert toggle_res3.status_code == 200

        # 6. Verify Customer Perks endpoint now reflects all approved coupons and free delivery
        perks_res = client.get(f"/api/customers/{cust.id}/retention-perks")
        assert perks_res.status_code == 200
        pdata = perks_res.json()
        assert pdata["has_express_shipping"] is True
        assert len(pdata["active_vouchers"]) >= 3

        voucher_map = {v["code"]: v["discount_pct"] for v in pdata["active_vouchers"]}
        assert "CARE10" in voucher_map and voucher_map["CARE10"] == 10.0
        assert "SPEED5" in voucher_map and voucher_map["SPEED5"] == 5.0
        assert "RECOVER10" in voucher_map and voucher_map["RECOVER10"] == 10.0

        # 7. Verify Account Isolation: Another customer does NOT receive these perks
        perked_ids = [p.customer_id for p in db.query(CustomerRetentionPerk).all()]
        other_cust = db.query(Customer).filter(Customer.id != cust.id, ~Customer.id.in_(perked_ids)).first()
        if not other_cust:
            other_cust = db.query(Customer).filter(Customer.id != cust.id).first()
            db.query(CustomerRetentionPerk).filter(CustomerRetentionPerk.customer_id == other_cust.id).delete()
            db.commit()
        assert other_cust is not None
        other_res = client.get(f"/api/customers/{other_cust.id}/retention-perks")
        assert other_res.status_code == 200
        odata = other_res.json()
        other_codes = [v["code"] for v in odata.get("active_vouchers", [])]
        assert "CARE10" not in other_codes
        assert "SPEED5" not in other_codes

    finally:
        db.close()

def test_order_placement_with_percentage_voucher_and_free_delivery():
    db = SessionLocal()
    try:
        cust = db.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1009").first()
        if not cust:
            cust = db.query(Customer).first()
        prod = db.query(Product).filter(Product.stock_quantity >= 5).first()
        assert prod is not None

        # Ensure customer has active CARE10 voucher (10% discount) and express shipping perk
        care_perk = db.query(CustomerRetentionPerk).filter(
            CustomerRetentionPerk.customer_id == cust.id,
            CustomerRetentionPerk.coupon_code == "CARE10",
            CustomerRetentionPerk.status == "Approved"
        ).first()
        if not care_perk:
            care_perk = CustomerRetentionPerk(
                customer_id=cust.id,
                campaign_id="camp_support_vip",
                title="10% Resolution Coupon",
                perk_type="discount_voucher",
                perk_value=10.0,
                coupon_code="CARE10",
                status="Approved"
            )
            db.add(care_perk)

        express_perk = db.query(CustomerRetentionPerk).filter(
            CustomerRetentionPerk.customer_id == cust.id,
            CustomerRetentionPerk.perk_type == "express_shipping",
            CustomerRetentionPerk.status == "Approved"
        ).first()
        if not express_perk:
            express_perk = CustomerRetentionPerk(
                customer_id=cust.id,
                campaign_id="camp_logistics_guarantee",
                title="Free Express Delivery",
                perk_type="express_shipping",
                perk_value=5.0,
                coupon_code="SPEED5",
                status="Approved"
            )
            db.add(express_perk)
        db.commit()

        # Place order with CARE10 coupon
        order_payload = {
            "customer_id": cust.id,
            "items": [{"product_id": prod.id, "quantity": 1}],
            "shipping_address": "Flat 101, Test Residency, Bengaluru",
            "payment_mode": "UPI",
            "wallet_credit_applied": 0.0,
            "voucher_code": "CARE10"
        }

        order_res = client.post("/api/store/orders", json=order_payload)
        assert order_res.status_code == 200
        odata = order_res.json()
        assert odata["success"] is True

        order_data = odata["order"]
        subtotal = prod.price * 1
        expected_discount = round(subtotal * 0.10, 2)
        assert abs(order_data["discount"] - expected_discount) <= 0.05
        assert order_data["shipping_fee"] == 0.0  # Free Delivery perk applied

    finally:
        db.close()

def test_low_risk_customer_simple_ads_retention_plan():
    from backend.app.ml.decision_engine import extract_detailed_root_causes, generate_structured_retention_plan
    db = SessionLocal()
    try:
        # Find any Low Risk customer from predictions or fallback to first customer
        low_risk_pred = db.query(ChurnPrediction).filter(ChurnPrediction.risk_category == "Low Risk").first()
        if low_risk_pred:
            cust = db.query(Customer).filter(Customer.id == low_risk_pred.customer_id).first()
        else:
            cust = db.query(Customer).first()
        assert cust is not None, "A customer must exist in test database"

        # 1. Test unit functions for Low Risk
        causes = extract_detailed_root_causes(cust, "Low Risk")
        assert len(causes) == 1
        assert causes[0]["id"] == "low_risk_healthy_standing"
        assert "Healthy Engagement" in causes[0]["title"]
        assert "Sponsored Product Ads" in causes[0]["how_to_overcome"]

        plan = generate_structured_retention_plan(cust, "Low Risk", 12.5, causes)
        assert len(plan) == 1
        ad_camp = plan[0]
        assert ad_camp["id"] == "camp_sponsored_ads_retention"
        assert ad_camp["perk_type"] == "sponsored_ads"
        assert "Digital Ads" in ad_camp["channel"]
        assert ad_camp["priority"] == "Low Touch"
        assert ad_camp["coupon_code"] is None
        assert "Sponsored Product Ads" in ad_camp["title"]

        # 2. Test API endpoint for Low Risk customer
        res = client.get(f"/api/customers/{cust.id}")
        assert res.status_code == 200
        data = res.json()
        if data.get("prediction") and data["prediction"].get("risk_category") == "Low Risk":
            ret_plan = data["prediction"]["retention_plan"]
            assert len(ret_plan) == 1
            assert ret_plan[0]["id"] == "camp_sponsored_ads_retention"
            assert ret_plan[0]["perk_type"] == "sponsored_ads"
            assert ret_plan[0]["is_outreach"] is True
            assert ret_plan[0]["automated_message"] is not None
            assert "SmartCart Ad Server" in ret_plan[0]["automated_message"]["sender"]

        # 3. Test approving the simple Ads campaign
        toggle_res = client.post(f"/api/customers/{cust.id}/retention-action/toggle", json={
            "campaign_id": "camp_sponsored_ads_retention",
            "status": "Approved",
            "title": ad_camp["title"],
            "perk_type": "sponsored_ads",
            "perk_value": 0.0,
            "coupon_code": None,
            "action_summary": ad_camp["action_summary"],
            "root_cause_driver": ad_camp["root_cause_driver"],
            "channel": ad_camp["channel"]
        })
        assert toggle_res.status_code == 200
        tdata = toggle_res.json()
        assert tdata["success"] is True

        # 4. Verify customer perks endpoint has the approved ad campaign and no unnecessary coupons
        perks_res = client.get(f"/api/customers/{cust.id}/retention-perks")
        assert perks_res.status_code == 200
        pdata = perks_res.json()
        assert any(a["campaign_id"] == "camp_sponsored_ads_retention" for a in pdata["approved_actions"])
        # Clean up
        db.query(CustomerRetentionPerk).filter(
            CustomerRetentionPerk.customer_id == cust.id,
            CustomerRetentionPerk.campaign_id == "camp_sponsored_ads_retention"
        ).delete()
        db.commit()

    finally:
        db.close()


def test_accept_and_reject_retention_plan_persistence():
    db = SessionLocal()
    try:
        cust = db.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1009").first()
        if not cust:
            cust = db.query(Customer).first()
        assert cust is not None

        # Clean existing test perks for this customer
        db.query(CustomerRetentionPerk).filter(CustomerRetentionPerk.customer_id == cust.id).delete()
        db.commit()

        # 1. Accept Campaign A: Customer Retention Discount
        res_accept = client.post(f"/api/customers/{cust.id}/retention-action/toggle", json={
            "campaign_id": "camp_test_discount",
            "status": "Accepted",
            "title": "Customer Retention Discount",
            "perk_type": "discount_voucher",
            "perk_value": 15.0,
            "coupon_code": "SAVE15",
            "action_summary": "Customer Retention Discount: Offer a 15% discount voucher (SAVE15) to high churn risk customer.",
            "channel": "In-App Offer"
        })
        assert res_accept.status_code == 200
        data_accept = res_accept.json()
        assert data_accept["success"] is True
        assert data_accept["status"] == "Accepted"

        # 2. Reject Campaign B: Priority Support Concierge
        res_reject = client.post(f"/api/customers/{cust.id}/retention-action/toggle", json={
            "campaign_id": "camp_test_support",
            "status": "Rejected",
            "title": "Priority Support Concierge",
            "perk_type": "vip_support",
            "perk_value": 0.0,
            "coupon_code": "VIPCARE",
            "action_summary": "Priority Support: Concierge phone call outreach.",
            "channel": "Phone"
        })
        assert res_reject.status_code == 200
        data_reject = res_reject.json()
        assert data_reject["success"] is True
        assert data_reject["status"] == "Rejected"

        # 3. Verify Customer Perks: Only Campaign A's coupon is active, Campaign B's coupon is NOT active
        perks_res = client.get(f"/api/customers/{cust.id}/retention-perks")
        assert perks_res.status_code == 200
        pdata = perks_res.json()
        active_codes = [v["code"] for v in pdata.get("active_vouchers", [])]
        assert "SAVE15" in active_codes
        assert "VIPCARE" not in active_codes

        # 4. Verify persistence on re-fetching customer details (refresh simulation)
        cust_details = client.get(f"/api/customers/{cust.id}").json()
        retention_perks = cust_details.get("retention_perks", [])
        perk_status_map = {p["campaign_id"]: p["status"] for p in retention_perks}

        # Accepted perk must be listed with Accepted status
        assert perk_status_map.get("camp_test_discount") == "Accepted"
        # Rejected perk must NOT be listed in active retention_perks
        assert "camp_test_support" not in perk_status_map

        # Check DB directly to ensure rejection is persisted in database
        rejected_perk = db.query(CustomerRetentionPerk).filter(
            CustomerRetentionPerk.customer_id == cust.id,
            CustomerRetentionPerk.campaign_id == "camp_test_support"
        ).first()
        assert rejected_perk is not None
        assert rejected_perk.status == "Rejected"

        # Clean up
        db.query(CustomerRetentionPerk).filter(
            CustomerRetentionPerk.customer_id == cust.id,
            CustomerRetentionPerk.campaign_id.in_(["camp_test_discount", "camp_test_support"])
        ).delete()
        db.commit()

    finally:
        db.close()

