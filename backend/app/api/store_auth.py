import hashlib
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.models import StoreUser, Customer, ChurnPrediction, CustomerRetentionPerk, CustomerPerkRedemption

router = APIRouter(prefix="/store/auth", tags=["SmartCart Storefront Auth"])

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.strip().encode()).hexdigest()

class StoreLoginRequest(BaseModel):
    username: str # Customer ID (e.g. AMZ_PRED3_1001), pm@smartcart.com, or admin@smartcart.com
    password: str

@router.post("/login")
def store_login(req: StoreLoginRequest, db: Session = Depends(get_db)):
    uname = req.username.strip()
    pw = req.password.strip()
    pw_hashed = hash_pw(pw)

    # 1. Lookup in StoreUser table
    user = db.query(StoreUser).filter(
        (StoreUser.username.ilike(uname))
    ).first()

    # Fallback convenience: if logging in with customer ID directly
    customer = None
    if user and user.customer_id:
        customer = db.query(Customer).filter(Customer.id == user.customer_id).first()
    elif not user:
        # Check if username is a Customer source_customer_id directly
        customer = db.query(Customer).filter(Customer.source_customer_id.ilike(uname)).first()
        if customer and (pw == "customer123" or pw_hashed == hash_pw("customer123")):
            user = StoreUser(
                username=customer.source_customer_id,
                password_hash=hash_pw("customer123"),
                role="customer",
                customer_id=customer.id,
                full_name=f"Customer {customer.source_customer_id}"
            )

    # Check password match
    if not user:
        # Fallback check for admin / manager aliases
        if uname.lower() in ["admin", "admin@smartcart.com"] and pw in ["admin123", "admin"]:
            return {
                "success": True,
                "token": "admin-session-token",
                "user": {
                    "id": 1,
                    "username": "admin@smartcart.com",
                    "role": "admin",
                    "full_name": "SmartCart Platform Administrator"
                }
            }
        elif uname.lower() in ["manager", "pm@smartcart.com"] and pw in ["manager123", "manager"]:
            return {
                "success": True,
                "token": "pm-session-token",
                "user": {
                    "id": 2,
                    "username": "pm@smartcart.com",
                    "role": "product_manager",
                    "full_name": "SmartCart Product Manager"
                }
            }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Login ID or Password. For customers, use your Customer ID (e.g. AMZ_PRED3_1001) with password 'customer123'."
        )

    # Validate password
    is_valid_pw = (
        user.password_hash == pw_hashed or 
        user.password_hash == pw or
        (user.role == "customer" and pw == "customer123") or
        (user.role == "product_manager" and pw == "manager123") or
        (user.role == "admin" and pw == "admin123")
    )

    if not is_valid_pw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. For customers, the password is 'customer123'."
        )

    # Fetch latest churn prediction for customer role if applicable
    pred_info = None
    perks_info = {
        "wallet_balance": 0.0,
        "active_vouchers": [],
        "has_express_shipping": False,
        "has_vip_support": False,
        "has_prime_trial": False,
        "approved_actions": []
    }

    if customer:
        # Reset Days Inactive to 0 upon customer login
        customer.days_since_last_purchase = 0.0
        if customer.sessions_last_30d is not None:
            customer.sessions_last_30d += 1
        else:
            customer.sessions_last_30d = 1
        customer.updated_at = datetime.datetime.now()
        db.commit()

        # Re-score churn prediction in real time with 0 days inactive
        try:
            from ..services.customer_feature_service import reconcile_and_predict_customer
            reconcile_and_predict_customer(customer, db, log_discrepancy=False)
            db.refresh(customer)
        except Exception as e:
            print(f"[Store Login Churn Re-score Warning] {e}")

        pred = db.query(ChurnPrediction).filter(ChurnPrediction.customer_id == customer.id).first()
        if pred:
            pred_info = {
                "churn_probability": pred.churn_probability,
                "risk_category": pred.risk_category
            }

        perks = db.query(CustomerRetentionPerk).filter(
            CustomerRetentionPerk.customer_id == customer.id,
            CustomerRetentionPerk.status.in_(["Accepted", "Approved", "Active"])
        ).all()

        redemptions = db.query(CustomerPerkRedemption).filter(
            CustomerPerkRedemption.customer_id == customer.id
        ).all()
        redeemed_codes = set(r.coupon_code.upper() for r in redemptions if r.coupon_code and r.benefit_type == "discount_coupon")

        wallet_bal = sum(p.perk_value for p in perks if p.perk_type == "wallet_credit" and p.perk_value > 0)
        vouchers = [{
            "code": p.coupon_code,
            "title": p.title,
            "perk_type": p.perk_type,
            "discount_pct": p.perk_value if "discount" in p.perk_type and p.perk_value < 100 else 0,
            "discount_amount": p.perk_value if p.perk_value >= 100 else 0,
            "root_cause_driver": p.root_cause_driver,
            "action_summary": p.action_summary
        } for p in perks if p.coupon_code and getattr(p, 'coupon_used', 0) == 0 and p.coupon_code.upper() not in redeemed_codes]

        has_express = any(
            (p.perk_type in ["express_shipping", "priority_shipping", "prime_trial"] or getattr(p, 'free_shipping', 0) == 1)
            and getattr(p, 'shipping_used', 0) == 0
            for p in perks
        )
        has_vip = any(p.perk_type == "vip_support" for p in perks)
        has_prime = (customer.membership_status and "prime" in customer.membership_status.lower()) or any(p.perk_type == "prime_trial" for p in perks)

        perks_info = {
            "wallet_balance": round(wallet_bal, 2),
            "active_vouchers": vouchers,
            "has_express_shipping": has_express or has_prime,
            "has_vip_support": has_vip,
            "has_prime_trial": has_prime,
            "approved_actions": [{
                "id": p.id,
                "campaign_id": p.campaign_id,
                "title": p.title,
                "perk_type": p.perk_type,
                "perk_value": p.perk_value,
                "coupon_code": p.coupon_code,
                "root_cause_driver": p.root_cause_driver,
                "channel": p.channel
            } for p in perks]
        }

    return {
        "success": True,
        "token": f"{user.role}-auth-token-{user.id}",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "full_name": user.full_name or user.username,
            "customer_id": user.customer_id,
            "membership_status": customer.membership_status if customer else None,
            "preferred_category": customer.preferred_category if customer else None,
            "days_since_last_purchase": customer.days_since_last_purchase if customer else None,
            "total_spend_inr": customer.total_spend_inr if customer else None,
            "prediction": pred_info,
            "retention_perks": perks_info
        }
    }

@router.get("/profile/{identifier}")
def get_store_user_profile(identifier: str, db: Session = Depends(get_db)):
    """
    Returns updated user profile and real-time retention perks.
    """
    customer = None
    if identifier.isdigit():
        customer = db.query(Customer).filter(Customer.id == int(identifier)).first()
    if not customer:
        customer = db.query(Customer).filter(Customer.source_customer_id == identifier.strip()).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer account not found.")

    perks = db.query(CustomerRetentionPerk).filter(
        CustomerRetentionPerk.customer_id == customer.id,
        CustomerRetentionPerk.status.in_(["Accepted", "Approved", "Active"])
    ).all()

    redemptions = db.query(CustomerPerkRedemption).filter(
        CustomerPerkRedemption.customer_id == customer.id
    ).all()
    redeemed_codes = set(r.coupon_code.upper() for r in redemptions if r.coupon_code and r.benefit_type == "discount_coupon")

    wallet_bal = sum(p.perk_value for p in perks if p.perk_type == "wallet_credit" and p.perk_value > 0)
    vouchers = [{
        "code": p.coupon_code,
        "title": p.title,
        "perk_type": p.perk_type,
        "discount_pct": p.perk_value if "discount" in p.perk_type and p.perk_value < 100 else 0,
        "discount_amount": p.perk_value if p.perk_value >= 100 else 0,
        "root_cause_driver": p.root_cause_driver,
        "action_summary": p.action_summary
    } for p in perks if p.coupon_code and getattr(p, 'coupon_used', 0) == 0 and p.coupon_code.upper() not in redeemed_codes]

    has_express = any(
        (p.perk_type in ["express_shipping", "priority_shipping", "prime_trial"] or getattr(p, 'free_shipping', 0) == 1)
        and getattr(p, 'shipping_used', 0) == 0
        for p in perks
    )
    has_vip = any(p.perk_type == "vip_support" for p in perks)
    has_prime = (customer.membership_status and "prime" in customer.membership_status.lower()) or any(p.perk_type == "prime_trial" for p in perks)

    return {
        "success": True,
        "customer_id": customer.id,
        "source_customer_id": customer.source_customer_id,
        "membership_status": "Prime" if has_prime else (customer.membership_status or "Standard"),
        "wallet_balance": round(wallet_bal, 2),
        "active_vouchers": vouchers,
        "has_express_shipping": has_express or has_prime,
        "has_vip_support": has_vip,
        "has_prime_trial": has_prime,
        "approved_actions": [{
            "id": p.id,
            "campaign_id": p.campaign_id,
            "title": p.title,
            "perk_type": p.perk_type,
            "perk_value": p.perk_value,
            "coupon_code": p.coupon_code,
            "root_cause_driver": p.root_cause_driver,
            "channel": p.channel
        } for p in perks]
    }

@router.get("/demo-customers")
def get_demo_customers(db: Session = Depends(get_db)):
    """
    Returns list of top demo customers for the Storefront Switcher widget
    so users/examiners can click any customer to log in instantly.
    """
    customers = db.query(Customer).order_by(Customer.id.asc()).limit(30).all()
    results = []

    for c in customers:
        pred = db.query(ChurnPrediction).filter(ChurnPrediction.customer_id == c.id).first()
        results.append({
            "id": c.id,
            "source_customer_id": c.source_customer_id,
            "membership_status": c.membership_status or "Standard",
            "preferred_category": c.preferred_category or "General",
            "days_since_last_purchase": c.days_since_last_purchase or 0,
            "total_spend_inr": c.total_spend_inr or "₹0",
            "risk_category": pred.risk_category if pred else "Low Risk",
            "churn_probability": pred.churn_probability if pred else 5.0
        })

    return {
        "count": len(results),
        "default_password": "customer123",
        "customers": results
    }

@router.post("/record-login/{customer_id}")
def record_customer_login(customer_id: int, db: Session = Depends(get_db)):
    """
    Called whenever a customer signs in or switches accounts in the storefront.
    Resets Days Inactive (days_since_last_purchase) to 0 and recalculates real-time churn metrics.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        customer = db.query(Customer).filter(Customer.source_customer_id == str(customer_id)).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")

    customer.days_since_last_purchase = 0.0
    if customer.sessions_last_30d is not None:
        customer.sessions_last_30d += 1
    else:
        customer.sessions_last_30d = 1
    customer.updated_at = datetime.datetime.now()
    db.commit()

    try:
        from ..services.customer_feature_service import reconcile_and_predict_customer
        reconcile_and_predict_customer(customer, db, log_discrepancy=False)
        db.refresh(customer)
    except Exception as e:
        print(f"[Record Login ML Sync Error] {e}")

    return {
        "success": True,
        "customer_id": customer.id,
        "source_customer_id": customer.source_customer_id,
        "days_since_last_purchase": customer.days_since_last_purchase
    }

