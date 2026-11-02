import json
import time
import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, selectinload
from ..db.session import get_db
from ..db.models import (
    Customer, ChurnPrediction, RetentionRecommendation,
    CustomerRetentionPerk, CustomerPerkRedemption, CustomerNotification,
    StoreUser, Order, OrderItem, Product
)
from ..ml.predictor import run_single_prediction

router = APIRouter(prefix="/customers", tags=["Customer Analytics"])

@router.get("")
def get_customers(
    search: str | None = None,
    risk_category: str | None = None,
    membership_status: str | None = None,
    preferred_category: str | None = None,
    ground_truth_churn: int | None = None,
    source: str | None = None,  # 'store' | 'uploaded' | 'all'
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Customer, ChurnPrediction).outerjoin(
        ChurnPrediction, Customer.id == ChurnPrediction.customer_id
    )

    # Source filtering: 'store' (Live SmartCart accounts) vs 'uploaded' (CSV dataset)
    if source == "store":
        query = query.filter(Customer.source_customer_id.like("AMZ_PRED1_%"))
    elif source == "uploaded":
        query = query.filter(~Customer.source_customer_id.like("AMZ_PRED1_%"))

    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            (Customer.source_customer_id.like(search_fmt)) |
            (Customer.preferred_category.like(search_fmt)) |
            (Customer.membership_status.like(search_fmt))
        )

    if membership_status and membership_status.lower() != "all":
        query = query.filter(Customer.membership_status == membership_status)

    if preferred_category and preferred_category.lower() != "all":
        query = query.filter(Customer.preferred_category == preferred_category)

    if ground_truth_churn is not None and ground_truth_churn in [0, 1]:
        query = query.filter(Customer.ground_truth_churn == ground_truth_churn)

    if risk_category and risk_category.lower() != "all":
        query = query.filter(ChurnPrediction.risk_category == risk_category)

    total_count = query.count()
    offset = (page - 1) * limit
    results = query.offset(offset).limit(limit).all()

    customer_list = []
    for customer, pred in results:
        recs = []
        if pred and pred.recommendations:
            try:
                recs = json.loads(pred.recommendations)
            except Exception:
                recs = [pred.recommendations]

        customer_list.append({
            "id": customer.id,
            "source_customer_id": customer.source_customer_id,
            "signup_date": str(customer.signup_date) if customer.signup_date else None,
            "customer_age": customer.customer_age,
            "gender": customer.gender,
            "city_tier": customer.city_tier,
            "membership_status": customer.membership_status,
            "days_since_last_purchase": customer.days_since_last_purchase,
            "total_orders_lifetime": customer.total_orders_lifetime,
            "orders_last_30d": customer.orders_last_30d,
            "total_spend_inr": customer.total_spend_inr,
            "avg_order_value": customer.avg_order_value,
            "preferred_category": customer.preferred_category,
            "sessions_last_30d": customer.sessions_last_30d,
            "cart_abandonments_last_30d": customer.cart_abandonments_last_30d,
            "customer_service_tickets": customer.customer_service_tickets,
            "preferred_payment_mode": customer.preferred_payment_mode,
            "ground_truth_churn": customer.ground_truth_churn, # Dataset actual churn status (0 or 1)
            "prediction": {
                "churn_probability": pred.churn_probability if pred else None,
                "churn_prediction": pred.churn_prediction if pred else None,
                "risk_category": pred.risk_category if pred else "Unanalyzed",
                "prediction_timestamp": pred.prediction_timestamp.isoformat() if pred and pred.prediction_timestamp else None,
                "recommendations": recs
            }
        })

    return {
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit,
        "customers": customer_list
    }

def is_outreach_campaign(camp_or_perk):
    cid = (getattr(camp_or_perk, "campaign_id", None) or (camp_or_perk.get("id") if isinstance(camp_or_perk, dict) else "") or "").lower()
    ch = (getattr(camp_or_perk, "channel", None) or (camp_or_perk.get("channel") if isinstance(camp_or_perk, dict) else "") or "").lower()
    return any(k in ch or k in cid for k in ["message", "inbox", "notification", "whatsapp", "sms", "concierge", "callback", "phone", "email", "doorstep", "exchange", "outreach", "winback", "ads", "sponsored"])

def generate_auto_message(camp_or_perk, customer):
    cid = (getattr(camp_or_perk, "campaign_id", None) or (camp_or_perk.get("id") if isinstance(camp_or_perk, dict) else "") or "").lower()
    ch = (getattr(camp_or_perk, "channel", None) or (camp_or_perk.get("channel") if isinstance(camp_or_perk, dict) else "") or "").lower()
    cust_id = customer.source_customer_id if hasattr(customer, 'source_customer_id') else str(customer)
    code = getattr(camp_or_perk, "coupon_code", None) or (camp_or_perk.get("coupon_code") if isinstance(camp_or_perk, dict) else "") or "CARE10"
    title = getattr(camp_or_perk, "title", None) or (camp_or_perk.get("title") if isinstance(camp_or_perk, dict) else "") or "Special Offer"
    title_lower = title.lower()

    # 1. Automated Cart Recovery with Free Delivery (RECOVER10)
    if "cart" in cid or "whatsapp" in ch or "sms" in ch or "cart recovery" in title_lower or code == "RECOVER10":
        return {
            "channel": "Customer Account Messages",
            "sender": "SmartCart",
            "recipient": cust_id,
            "subject": "Cart recovery",
            "body": f"Your cart is waiting! Enjoy 10% off and free delivery with {code}.",
            "image_url": None,
            "dispatch_type": "Cart Recovery",
            "status": "Delivered",
            "sent_at": "Now",
            "notification_type": "cart_recovery",
            "navigation_target": f"/store/cart?coupon={code}"
        }

    # 2. Free Express Air Priority Delivery & 5% Delay Apology Coupon (SPEED5)
    elif "logistics" in cid or "delay" in cid or "speed" in cid or "express air" in title_lower or "fulfillment guarantee" in title_lower or code == "SPEED5":
        return {
            "channel": "Store Message",
            "sender": "SmartCart",
            "recipient": cust_id,
            "subject": "Free delivery offer",
            "body": f"Enjoy free express delivery on your next eligible order with {code}.",
            "image_url": None,
            "dispatch_type": "Express Delivery",
            "status": "Delivered",
            "sent_at": "Now",
            "notification_type": "shipping_and_discount",
            "navigation_target": f"/store/cart?coupon={code}"
        }

    # 3. Customer Experience Director Direct Apology & 10% Courtesy Coupon (CARE10)
    elif "sentiment" in cid or "apology" in cid or "director" in cid or "director" in title_lower:
        return {
            "channel": "Store Message",
            "sender": "SmartCart",
            "recipient": cust_id,
            "subject": "Discount offer",
            "body": f"Enjoy 10% off your next order with {code}.",
            "image_url": None,
            "dispatch_type": "Customer Care",
            "status": "Delivered",
            "sent_at": "Now",
            "notification_type": "courtesy_coupon",
            "navigation_target": f"/store/cart?coupon={code}"
        }

    # 4. Priority VIP Support Concierge Callback & 10% Resolution Coupon (CARE10)
    elif "support" in cid or "concierge" in ch or "concierge" in title_lower or "resolution coupon" in title_lower:
        return {
            "channel": "Store Message",
            "sender": "SmartCart Support",
            "recipient": cust_id,
            "subject": "Customer service message",
            "body": "We're sorry about your recent experience. Our support team is ready to help.",
            "image_url": None,
            "dispatch_type": "Support Desk",
            "status": "Assigned",
            "sent_at": "Now",
            "notification_type": "vip_support",
            "navigation_target": None
        }

    # 5. Targeted Sponsored Product Ads / Electronics / Category Promotion
    elif "ads" in cid or "sponsored" in ch or "ads" in ch or "sponsored product ads" in title_lower or "electronics promotion" in title_lower or "targeted electronics" in title_lower:
        category = getattr(customer, 'preferred_category', 'Electronics') or 'Electronics'
        return {
            "channel": "Store Message",
            "sender": "SmartCart",
            "recipient": cust_id,
            "subject": "Sponsored product announcement",
            "body": f"Discover trending {category} and seasonal arrivals.",
            "image_url": "https://images.unsplash.com/photo-1543512214-318c7553f230?w=600&auto=format&fit=crop&q=80" if category == "Electronics" else "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80",
            "dispatch_type": "Sponsored Announcement",
            "status": "Active",
            "sent_at": "Now",
            "notification_type": "sponsored_ads",
            "navigation_target": f"/store/catalog?category={category}"
        }

    # 6. Winback Email / Discount
    elif "winback" in cid or "email" in ch or "win-back" in title_lower:
        category = getattr(customer, 'preferred_category', 'Fashion') or 'Fashion'
        return {
            "channel": "Store Message",
            "sender": "SmartCart",
            "recipient": cust_id,
            "subject": "Discount offer",
            "body": f"Enjoy 15% off your next order with {code}.",
            "image_url": None,
            "dispatch_type": "Discount Offer",
            "status": "Delivered",
            "sent_at": "Now",
            "notification_type": "winback_offer",
            "navigation_target": f"/store/cart?coupon={code}"
        }

    # 7. Customer Retention Discount (SAVE15 / 10% / 15%)
    elif "retention discount" in title_lower or "discount" in title_lower:
        pct = 15 if "15" in code else (5 if "5" in code else 10)
        return {
            "channel": "Store Message",
            "sender": "SmartCart",
            "recipient": cust_id,
            "subject": "Discount offer",
            "body": f"Enjoy {pct}% off your next order with {code}.",
            "image_url": None,
            "dispatch_type": "Discount Offer",
            "status": "Delivered",
            "sent_at": "Now",
            "notification_type": "discount_voucher",
            "navigation_target": f"/store/cart?coupon={code}"
        }

    # Universal fallback for any custom or retention countermeasure
    return {
        "channel": "Store Message",
        "sender": "SmartCart",
        "recipient": cust_id,
        "subject": title,
        "body": f"Enjoy special savings on your next order with {code}." if code else f"{title}: Your account privileges are now active.",
        "image_url": None,
        "dispatch_type": "Store Message",
        "status": "Delivered",
        "sent_at": "Now",
        "notification_type": getattr(camp_or_perk, "perk_type", "retention_perk") or "retention_perk",
        "navigation_target": f"/store/cart?coupon={code}" if code else "/store/cart"
    }

@router.get("/{customer_id}")
def get_customer_details(
    customer_id: str,
    include_shap: bool = True,
    force_refresh: bool = False,
    db: Session = Depends(get_db)
):
    t_start = time.perf_counter()
    customer = None
    query = db.query(Customer).options(
        selectinload(Customer.orders).selectinload(Order.items).selectinload(OrderItem.product)
    )
    if str(customer_id).isdigit():
        customer = query.filter(Customer.id == int(customer_id)).first()
    if not customer:
        customer = query.filter(Customer.source_customer_id == str(customer_id).strip()).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    t_cust = time.perf_counter()
    pred_res = run_single_prediction(
        {"customer_id": customer.id}, 
        db, 
        force_refresh=force_refresh, 
        include_shap=include_shap
    )
    t_pred = time.perf_counter()
    
    # Fetch historical recommendations (limit to 15 latest entries)
    recs_db = (
        db.query(RetentionRecommendation)
        .filter(RetentionRecommendation.customer_id == customer.id)
        .order_by(RetentionRecommendation.created_at.desc())
        .limit(15)
        .all()
    )
    rec_history = [{
        "id": r.id,
        "recommendation_type": r.recommendation_type,
        "recommendation_description": r.recommendation_description,
        "status": r.status,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None
    } for r in recs_db]

    # Fetch live customer retention perks from database
    perks_db = db.query(CustomerRetentionPerk).filter(CustomerRetentionPerk.customer_id == customer.id).all()
    perks_status_map = {p.campaign_id: p.status for p in perks_db}

    # Synchronize database approval status into prediction retention plan
    if pred_res and "retention_plan" in pred_res:
        for camp in pred_res["retention_plan"]:
            cid = camp.get("id")
            if cid in perks_status_map:
                camp["status"] = perks_status_map[cid]
            camp["is_outreach"] = is_outreach_campaign(camp)
            camp["automated_message"] = generate_auto_message(camp, customer)

    # Calculate active wallet credits and active vouchers
    wallet_balance = sum(
        p.perk_value for p in perks_db 
        if p.perk_type == "wallet_credit" and p.status in ["Accepted", "Approved", "Active", "Completed"]
    )
    active_perks_list = [{
        "id": p.id,
        "campaign_id": p.campaign_id,
        "title": p.title,
        "perk_type": p.perk_type,
        "perk_value": p.perk_value,
        "coupon_code": p.coupon_code,
        "status": p.status,
        "root_cause_driver": p.root_cause_driver,
        "action_summary": p.action_summary,
        "channel": p.channel,
        "created_at": p.created_at.isoformat() if p.created_at else None
    } for p in perks_db if p.status in ["Accepted", "Approved", "Active", "Completed"]]

    # Fetch customer's real storefront orders from database (in-memory traversal, 0 additional queries)
    orders_list = []
    if customer.orders:
        sorted_orders = sorted(customer.orders, key=lambda x: str(x.order_date or ''), reverse=True)
        for o in sorted_orders:
            orders_list.append({
                "order_id": o.id,
                "order_number": o.order_number or f"ORD-{o.id}",
                "order_date": o.order_date.isoformat() if hasattr(o.order_date, 'isoformat') else str(o.order_date),
                "order_amount": o.order_amount,
                "order_status": o.order_status,
                "payment_mode": o.payment_mode,
                "items": [{
                    "product_id": it.product_id,
                    "title": it.product.title if it.product else "Item",
                    "quantity": it.quantity,
                    "unit_price": it.unit_price,
                    "total_price": it.total_price
                } for it in o.items] if o.items else []
            })

    # Fetch customer's delivered account notifications
    notifs_db = (
        db.query(CustomerNotification)
        .filter(CustomerNotification.customer_id == customer.id)
        .order_by(CustomerNotification.created_at.desc())
        .limit(20)
        .all()
    )
    account_notifs_list = [{
        "id": n.id,
        "campaign_id": n.campaign_id,
        "title": n.title,
        "message": n.message,
        "image_url": getattr(n, "image_url", None),
        "channel": n.channel,
        "sender": n.sender,
        "coupon_code": n.coupon_code,
        "perk_type": n.perk_type,
        "perk_value": n.perk_value,
        "is_read": bool(n.is_read),
        "dispatch_status": n.dispatch_status,
        "created_at": n.created_at.isoformat() if n.created_at else None
    } for n in notifs_db]

    t_end = time.perf_counter()
    total_ms = (t_end - t_start) * 1000
    cust_ms = (t_cust - t_start) * 1000
    pred_ms = (t_pred - t_cust) * 1000
    db_ms = (t_end - t_pred) * 1000
    print(f"[Perf API] Customer {customer_id}: Lookup={cust_ms:.1f}ms, Prediction={pred_ms:.1f}ms, DB_Rel={db_ms:.1f}ms, Total={total_ms:.1f}ms (Cached: {pred_res.get('cached', False)})")

    return {
        "customer": {
            "id": customer.id,
            "source_customer_id": customer.source_customer_id,
            "signup_date": str(customer.signup_date) if customer.signup_date else None,
            "customer_age": customer.customer_age,
            "gender": customer.gender,
            "city_tier": customer.city_tier,
            "membership_status": customer.membership_status,
            "days_since_last_purchase": customer.days_since_last_purchase,
            "total_orders_lifetime": customer.total_orders_lifetime,
            "orders_last_30d": customer.orders_last_30d,
            "orders_prev_30_to_60d": customer.orders_prev_30_to_60d,
            "total_spend_inr": customer.total_spend_inr,
            "avg_order_value": customer.avg_order_value,
            "preferred_category": customer.preferred_category,
            "sessions_last_30d": customer.sessions_last_30d,
            "avg_session_duration_min": customer.avg_session_duration_min,
            "cart_abandonments_last_30d": customer.cart_abandonments_last_30d,
            "search_queries_last_30d": customer.search_queries_last_30d,
            "return_count": customer.return_count,
            "return_rate": customer.return_rate,
            "cancellations_count": customer.cancellations_count,
            "late_deliveries_count": customer.late_deliveries_count,
            "customer_service_tickets": customer.customer_service_tickets,
            "avg_rating_given": customer.avg_rating_given,
            "preferred_payment_mode": customer.preferred_payment_mode,
            "ground_truth_churn": customer.ground_truth_churn,
            "is_live_store": customer.source_customer_id.startswith("AMZ_PRED1_"),
            "wallet_balance": round(wallet_balance, 2)
        },
        "orders": orders_list,
        "prediction": pred_res,
        "recommendation_history": rec_history,
        "retention_perks": active_perks_list,
        "account_notifications": account_notifs_list,
        "wallet_balance": round(wallet_balance, 2),
        "_perf_ms": round(total_ms, 2)
    }

class ToggleRetentionActionRequest(BaseModel):
    campaign_id: str
    status: str # "Approved", "Completed", "Pending", "Accepted", "Rejected"
    title: Optional[str] = None
    channel: Optional[str] = None
    action_summary: Optional[str] = None
    root_cause_driver: Optional[str] = None
    perk_type: Optional[str] = None
    perk_value: Optional[float] = 0.0
    coupon_code: Optional[str] = None
    perk_display: Optional[str] = None
    free_shipping: Optional[bool] = None
    notification_type: Optional[str] = None
    navigation_target: Optional[str] = None
    force: Optional[bool] = False

@router.post("/{customer_id}/retention-action/toggle")
def toggle_customer_retention_action(
    customer_id: str,
    payload: ToggleRetentionActionRequest,
    db: Session = Depends(get_db)
):
    """
    Approves or updates an Automated Retention Action Plan campaign for a customer.
    Persists the decision and automatically unlocks concrete perks on the customer's account!
    """
    # Lookup customer
    customer = None
    if str(customer_id).isdigit():
        customer = db.query(Customer).filter(Customer.id == int(customer_id)).first()
    if not customer:
        customer = db.query(Customer).filter(Customer.source_customer_id == str(customer_id).strip()).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer record not found.")

    now = datetime.datetime.now()
    existing_perk = db.query(CustomerRetentionPerk).filter(
        CustomerRetentionPerk.customer_id == customer.id,
        CustomerRetentionPerk.campaign_id == payload.campaign_id
    ).first()

    # Guard against accidental approval of a previously rejected campaign without an explicit state transition
    if existing_perk and existing_perk.status == "Rejected" and payload.status in ["Accepted", "Approved"] and not payload.force:
        raise HTTPException(
            status_code=400,
            detail="Cannot directly accept a previously rejected retention action without an explicit state transition (e.g. reset or explicit approval)."
        )

    # Determine free shipping benefit
    has_free_del = 0
    if payload.free_shipping is True:
        has_free_del = 1
    elif payload.perk_type in ["express_shipping", "priority_shipping", "prime_trial"]:
        has_free_del = 1
    else:
        title_lower = (payload.title or "").lower()
        summary_lower = (payload.action_summary or "").lower()
        code_upper = (payload.coupon_code or "").upper()
        if any(k in title_lower for k in ["free delivery", "free shipping", "express air", "express priority"]):
            has_free_del = 1
        elif any(k in summary_lower for k in ["free delivery", "free shipping", "express air"]):
            has_free_del = 1
        elif any(k in code_upper for k in ["RECOVER", "SPEED", "FLEX"]):
            has_free_del = 1

    if payload.status in ["Approved", "Accepted"]:
        target_status = "Accepted"
        if not existing_perk:
            existing_perk = CustomerRetentionPerk(
                customer_id=customer.id,
                campaign_id=payload.campaign_id,
                title=payload.title or "Retention Campaign",
                perk_type=payload.perk_type or "wallet_credit",
                perk_value=float(payload.perk_value or 0.0),
                coupon_code=payload.coupon_code,
                free_shipping=has_free_del,
                status=target_status,
                action_summary=payload.action_summary,
                root_cause_driver=payload.root_cause_driver,
                channel=payload.channel,
                created_at=now,
                updated_at=now
            )
            db.add(existing_perk)
        else:
            existing_perk.status = target_status
            existing_perk.title = payload.title or existing_perk.title
            existing_perk.perk_type = payload.perk_type or existing_perk.perk_type
            existing_perk.perk_value = float(payload.perk_value or existing_perk.perk_value)
            existing_perk.coupon_code = payload.coupon_code or existing_perk.coupon_code
            existing_perk.free_shipping = has_free_del
            existing_perk.action_summary = payload.action_summary or existing_perk.action_summary
            existing_perk.root_cause_driver = payload.root_cause_driver or existing_perk.root_cause_driver
            existing_perk.updated_at = now

        # Generate automated notification message for this customer
        auto_msg = generate_auto_message(payload, customer)
        notif_type = payload.notification_type or auto_msg.get("notification_type", payload.perk_type or "retention_perk")
        nav_target = payload.navigation_target or auto_msg.get("navigation_target", f"/store/cart?coupon={payload.coupon_code}" if payload.coupon_code else "/store/cart")

        # Dispatch message directly into customer's account notification inbox!
        existing_notif = db.query(CustomerNotification).filter(
            CustomerNotification.customer_id == customer.id,
            CustomerNotification.campaign_id == payload.campaign_id
        ).first()

        if not existing_notif:
            existing_notif = CustomerNotification(
                customer_id=customer.id,
                campaign_id=payload.campaign_id,
                title=payload.title or auto_msg.get("subject", "Exclusive Customer Privilege"),
                message=auto_msg.get("body", payload.action_summary or "Exclusive privilege unlocked."),
                image_url=auto_msg.get("image_url"),
                notification_type=notif_type,
                navigation_target=nav_target,
                channel=payload.channel or auto_msg.get("channel", "In-App Notification"),
                sender=auto_msg.get("sender", "SmartCart Official"),
                coupon_code=payload.coupon_code,
                perk_type=payload.perk_type,
                perk_value=float(payload.perk_value or 0.0),
                is_read=0,
                dispatch_status="Delivered",
                created_at=now,
                updated_at=now
            )
            db.add(existing_notif)
        else:
            existing_notif.title = payload.title or existing_notif.title
            existing_notif.message = auto_msg.get("body", existing_notif.message)
            existing_notif.image_url = auto_msg.get("image_url") or existing_notif.image_url
            existing_notif.notification_type = notif_type
            existing_notif.navigation_target = nav_target
            existing_notif.channel = payload.channel or existing_notif.channel
            existing_notif.sender = auto_msg.get("sender", existing_notif.sender)
            existing_notif.coupon_code = payload.coupon_code or existing_notif.coupon_code
            existing_notif.perk_type = payload.perk_type or existing_notif.perk_type
            existing_notif.perk_value = float(payload.perk_value or existing_notif.perk_value)
            existing_notif.is_read = 0
            existing_notif.dispatch_status = "Delivered"
            existing_notif.updated_at = now

        # If prime trial, update customer membership to Prime
        if payload.perk_type == "prime_trial":
            customer.membership_status = "Prime"
            su = db.query(StoreUser).filter(StoreUser.customer_id == customer.id).first()
            if su:
                su.membership_status = "Prime"

        # Also log to RetentionRecommendation table (idempotent: update if existing, insert if new)
        existing_rec = db.query(RetentionRecommendation).filter(
            RetentionRecommendation.customer_id == customer.id,
            RetentionRecommendation.recommendation_description.like(f"%{payload.campaign_id}%")
        ).first()
        if not existing_rec:
            rec_log = RetentionRecommendation(
                customer_id=customer.id,
                recommendation_type="Approved Retention Action",
                recommendation_description=f"Approved: {payload.title or payload.campaign_id} - {payload.action_summary or ''}",
                status="Accepted",
                created_at=now,
                updated_at=now
            )
            db.add(rec_log)
        else:
            existing_rec.status = "Accepted"
            existing_rec.updated_at = now

    elif payload.status == "Completed":
        if existing_perk:
            existing_perk.status = "Completed"
            existing_perk.updated_at = now
        existing_notif = db.query(CustomerNotification).filter(
            CustomerNotification.customer_id == customer.id,
            CustomerNotification.campaign_id == payload.campaign_id
        ).first()
        if existing_notif:
            existing_notif.dispatch_status = "Delivered (Completed)"
            existing_notif.updated_at = now

    elif payload.status == "Rejected":
        target_status = "Rejected"
        if not existing_perk:
            existing_perk = CustomerRetentionPerk(
                customer_id=customer.id,
                campaign_id=payload.campaign_id,
                title=payload.title or "Retention Campaign",
                perk_type=payload.perk_type or "discount_voucher",
                perk_value=0.0,
                coupon_code=None,
                free_shipping=0,
                status=target_status,
                action_summary=payload.action_summary,
                root_cause_driver=payload.root_cause_driver,
                channel=payload.channel,
                created_at=now,
                updated_at=now
            )
            db.add(existing_perk)
        else:
            existing_perk.status = target_status
            existing_perk.perk_value = 0.0
            existing_perk.coupon_code = None
            existing_perk.free_shipping = 0
            existing_perk.updated_at = now

        # Delete any notifications for this campaign so customer receives no perk
        existing_notif = db.query(CustomerNotification).filter(
            CustomerNotification.customer_id == customer.id,
            CustomerNotification.campaign_id == payload.campaign_id
        ).first()
        if existing_notif:
            db.delete(existing_notif)

        if payload.perk_type == "prime_trial":
            customer.membership_status = "Standard"
            su = db.query(StoreUser).filter(StoreUser.customer_id == customer.id).first()
            if su:
                su.membership_status = "Standard"

        # Log rejection in RetentionRecommendation (idempotent)
        existing_rec = db.query(RetentionRecommendation).filter(
            RetentionRecommendation.customer_id == customer.id,
            RetentionRecommendation.recommendation_description.like(f"%{payload.campaign_id}%")
        ).first()
        if not existing_rec:
            rec_log = RetentionRecommendation(
                customer_id=customer.id,
                recommendation_type="Rejected Retention Action",
                recommendation_description=f"Rejected: {payload.title or payload.campaign_id} - {payload.action_summary or ''}",
                status="Rejected",
                created_at=now,
                updated_at=now
            )
            db.add(rec_log)
        else:
            existing_rec.status = "Rejected"
            existing_rec.updated_at = now

    else:
        # Reset / Pending: Revoke perk & notification
        if existing_perk:
            db.delete(existing_perk)
        existing_notif = db.query(CustomerNotification).filter(
            CustomerNotification.customer_id == customer.id,
            CustomerNotification.campaign_id == payload.campaign_id
        ).first()
        if existing_notif:
            db.delete(existing_notif)
        if payload.perk_type == "prime_trial":
            customer.membership_status = "Standard"

    db.commit()

    # Recalculate live perks & notifications
    perks_db = db.query(CustomerRetentionPerk).filter(CustomerRetentionPerk.customer_id == customer.id).all()
    wallet_balance = sum(
        p.perk_value for p in perks_db 
        if p.perk_type == "wallet_credit" and p.status in ["Accepted", "Approved", "Active", "Completed"]
    )
    unread_notifs = db.query(CustomerNotification).filter(
        CustomerNotification.customer_id == customer.id,
        CustomerNotification.is_read == 0
    ).count()

    return {
        "success": True,
        "message": f"Campaign '{payload.title or payload.campaign_id}' updated to {payload.status}.",
        "campaign_id": payload.campaign_id,
        "status": payload.status,
        "wallet_balance": round(wallet_balance, 2),
        "total_active_perks": len([p for p in perks_db if p.status in ["Accepted", "Approved", "Active", "Completed"]]),
        "unread_notifications": unread_notifs
    }

@router.get("/{customer_id}/notifications")
def get_customer_notifications(customer_id: str, db: Session = Depends(get_db)):
    """
    Returns all notifications and retention messages dispatched to a customer's storefront account.
    """
    customer = None
    if str(customer_id).isdigit():
        customer = db.query(Customer).filter(Customer.id == int(customer_id)).first()
    if not customer:
        customer = db.query(Customer).filter(Customer.source_customer_id == str(customer_id).strip()).first()

    if not customer:
        return {"success": False, "notifications": [], "unread_count": 0}

    # Fetch notifications from database
    notifs = db.query(CustomerNotification).filter(
        CustomerNotification.customer_id == customer.id
    ).order_by(CustomerNotification.created_at.desc()).all()

    # Auto-backfill if customer has approved perks but no notification records yet
    if not notifs:
        approved_perks = db.query(CustomerRetentionPerk).filter(
            CustomerRetentionPerk.customer_id == customer.id,
            CustomerRetentionPerk.status.in_(["Accepted", "Approved", "Active", "Completed"])
        ).all()
        now = datetime.datetime.now()
        for p in approved_perks:
            msg = generate_auto_message(p, customer)
            new_notif = CustomerNotification(
                customer_id=customer.id,
                campaign_id=p.campaign_id,
                title=p.title or msg["subject"],
                message=msg["body"],
                channel=p.channel or msg["channel"],
                sender=msg.get("sender", "SmartCart Official"),
                coupon_code=p.coupon_code,
                perk_type=p.perk_type,
                perk_value=float(p.perk_value or 0.0),
                is_read=0,
                dispatch_status="Delivered",
                created_at=p.created_at or now,
                updated_at=now
            )
            db.add(new_notif)
        db.commit()
        notifs = db.query(CustomerNotification).filter(
            CustomerNotification.customer_id == customer.id
        ).order_by(CustomerNotification.created_at.desc()).all()

    unread_count = sum(1 for n in notifs if n.is_read == 0)

    return {
        "success": True,
        "customer_id": customer.id,
        "source_customer_id": customer.source_customer_id,
        "unread_count": unread_count,
        "notifications": [{
            "id": n.id,
            "customer_id": n.customer_id,
            "campaign_id": n.campaign_id,
            "title": n.title,
            "message": n.message,
            "notification_type": getattr(n, "notification_type", "retention_perk") or "retention_perk",
            "navigation_target": getattr(n, "navigation_target", None) or (f"/store/cart?coupon={n.coupon_code}" if n.coupon_code else "/store/cart"),
            "channel": n.channel,
            "sender": n.sender,
            "coupon_code": n.coupon_code,
            "perk_type": n.perk_type,
            "perk_value": n.perk_value,
            "image_url": getattr(n, "image_url", None),
            "is_read": bool(n.is_read),
            "dispatch_status": n.dispatch_status,
            "created_at": n.created_at.isoformat() if hasattr(n.created_at, "isoformat") and n.created_at else str(n.created_at) if n.created_at else None
        } for n in notifs]
    }

@router.post("/{customer_id}/notifications/{notification_id}/read")
def mark_notification_read(customer_id: str, notification_id: int, db: Session = Depends(get_db)):
    """Mark a customer notification as read."""
    notif = db.query(CustomerNotification).filter(CustomerNotification.id == notification_id).first()
    if notif:
        notif.is_read = 1
        db.commit()
    return {"success": True}

@router.post("/{customer_id}/notifications/read-all")
def mark_all_notifications_read(customer_id: str, db: Session = Depends(get_db)):
    """Mark all notifications as read for a customer."""
    customer = None
    if str(customer_id).isdigit():
        customer = db.query(Customer).filter(Customer.id == int(customer_id)).first()
    if not customer:
        customer = db.query(Customer).filter(Customer.source_customer_id == str(customer_id).strip()).first()
    if customer:
        db.query(CustomerNotification).filter(
            CustomerNotification.customer_id == customer.id
        ).update({"is_read": 1})
        db.commit()
    return {"success": True}

@router.get("/{customer_id}/retention-perks")
def get_customer_retention_perks(customer_id: str, db: Session = Depends(get_db)):
    """
    Returns active perks, wallet credits, discount vouchers and notifications for a customer account.
    Used by SmartCart Storefront to render retention benefits, vouchers, wallet credits and notifications.
    """
    customer = None
    if str(customer_id).isdigit():
        customer = db.query(Customer).filter(Customer.id == int(customer_id)).first()
    if not customer:
        customer = db.query(Customer).filter(Customer.source_customer_id == str(customer_id).strip()).first()

    if not customer:
        return {
            "success": False,
            "wallet_balance": 0.0,
            "active_vouchers": [],
            "has_express_shipping": False,
            "has_vip_support": False,
            "has_prime_trial": False,
            "approved_actions": [],
            "active_notifications": [],
            "notifications": [],
            "unread_count": 0
        }

    perks = db.query(CustomerRetentionPerk).filter(
        CustomerRetentionPerk.customer_id == customer.id,
        CustomerRetentionPerk.status.in_(["Accepted", "Approved", "Active"])
    ).all()

    # Query customer perk redemptions to ensure used benefits are completely excluded
    redemptions = db.query(CustomerPerkRedemption).filter(
        CustomerPerkRedemption.customer_id == customer.id
    ).order_by(CustomerPerkRedemption.redemption_date.desc()).all()

    redeemed_coupon_codes = set(
        r.coupon_code.upper() for r in redemptions if r.coupon_code and r.benefit_type == "discount_coupon"
    )

    wallet_balance = sum(p.perk_value for p in perks if p.perk_type == "wallet_credit" and p.perk_value > 0)

    def get_voucher_pct(p):
        if p.perk_value and 0 < p.perk_value <= 50:
            return p.perk_value
        if p.coupon_code:
            code_u = p.coupon_code.upper()
            if "15" in code_u and "150" not in code_u:
                return 15.0
            elif "10" in code_u:
                return 10.0
            elif "5" in code_u and "50" not in code_u:
                return 5.0
        return 10.0 if (p.perk_type == "discount_voucher") else 0.0

    active_vouchers = [{
        "code": p.coupon_code,
        "title": p.title,
        "perk_type": p.perk_type,
        "discount_pct": get_voucher_pct(p),
        "free_shipping": bool(getattr(p, 'free_shipping', 0) == 1 and getattr(p, 'shipping_used', 0) == 0),
        "discount_amount": p.perk_value if (p.perk_value and p.perk_value > 50) else 0,
        "root_cause_driver": p.root_cause_driver,
        "action_summary": p.action_summary
    } for p in perks if p.coupon_code and getattr(p, 'coupon_used', 0) == 0 and p.coupon_code.upper() not in redeemed_coupon_codes]

    has_express = any(
        (getattr(p, 'free_shipping', 0) == 1
         or p.perk_type in ["express_shipping", "priority_shipping", "prime_trial"]
         or "express" in (p.title or "").lower()
         or "free delivery" in (p.title or "").lower()
         or "free shipping" in (p.title or "").lower())
        and getattr(p, 'shipping_used', 0) == 0
        for p in perks
    )
    has_vip = any(p.perk_type == "vip_support" for p in perks)
    has_prime = (customer.membership_status and "prime" in customer.membership_status.lower()) or any(p.perk_type == "prime_trial" for p in perks)

    # Fetch stored notifications
    notifs = db.query(CustomerNotification).filter(
        CustomerNotification.customer_id == customer.id
    ).order_by(CustomerNotification.created_at.desc()).all()

    notifs_formatted = [{
        "id": n.id,
        "customer_id": n.customer_id,
        "source_customer_id": customer.source_customer_id,
        "campaign_id": n.campaign_id,
        "title": n.title,
        "message": n.message,
        "image_url": getattr(n, "image_url", None),
        "notification_type": getattr(n, "notification_type", "retention_perk") or "retention_perk",
        "navigation_target": getattr(n, "navigation_target", None) or (f"/store/cart?coupon={n.coupon_code}" if n.coupon_code else "/store/cart"),
        "channel": n.channel,
        "sender": n.sender,
        "coupon_code": n.coupon_code,
        "is_coupon_used": bool(n.coupon_code and n.coupon_code.upper() in redeemed_coupon_codes),
        "perk_type": n.perk_type,
        "perk_value": n.perk_value,
        "is_read": bool(n.is_read),
        "dispatch_status": n.dispatch_status,
        "created_at": n.created_at.isoformat() if n.created_at else None
    } for n in notifs]

    unread_count = sum(1 for n in notifs if n.is_read == 0)

    # Legacy fallback list
    active_notifications = []
    for p in perks:
        msg = generate_auto_message(p, customer)
        if msg:
            active_notifications.append(msg)

    return {
        "success": True,
        "customer_id": customer.id,
        "source_customer_id": customer.source_customer_id,
        "wallet_balance": round(wallet_balance, 2),
        "active_vouchers": active_vouchers,
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
            "free_shipping": bool(getattr(p, 'free_shipping', 0) == 1 and getattr(p, 'shipping_used', 0) == 0),
            "status": p.status,
            "root_cause_driver": p.root_cause_driver,
            "channel": p.channel,
            "is_outreach": is_outreach_campaign(p),
            "automated_message": generate_auto_message(p, customer)
        } for p in perks],
        "redeemed_perks": [{
            "id": r.id,
            "order_number": r.order_number,
            "benefit_type": r.benefit_type,
            "coupon_code": r.coupon_code,
            "discount_amount": r.discount_amount,
            "redemption_date": r.redemption_date.isoformat() if r.redemption_date else None,
            "status": r.status
        } for r in redemptions],
        "active_notifications": active_notifications,
        "notifications": notifs_formatted,
        "unread_count": unread_count
    }

