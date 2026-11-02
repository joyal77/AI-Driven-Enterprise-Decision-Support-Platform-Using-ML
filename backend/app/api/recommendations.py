import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db.session import get_db
from typing import Optional
from ..db.models import (
    RetentionRecommendation,
    Customer,
    CustomerRetentionPerk,
    CustomerNotification,
    StoreUser
)
from .customers import generate_auto_message

router = APIRouter(prefix="/recommendations", tags=["Retention Recommendations"])

class StatusUpdateSchema(BaseModel):
    status: str # Pending, Approved, Accepted, Completed, Dismissed, Rejected
    force: Optional[bool] = False

@router.get("")
def get_recommendations(
    status: str | None = None,
    risk_category: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(RetentionRecommendation, Customer).join(Customer, RetentionRecommendation.customer_id == Customer.id)

    if status and status.lower() != "all":
        query = query.filter(RetentionRecommendation.status == status)

    if risk_category and risk_category.lower() != "all":
        query = query.filter(RetentionRecommendation.recommendation_type == risk_category)

    total_count = query.count()
    offset = (page - 1) * limit
    results = query.order_by(RetentionRecommendation.created_at.desc()).offset(offset).limit(limit).all()

    recommendations_list = []
    for rec, cust in results:
        recommendations_list.append({
            "id": rec.id,
            "customer_id": rec.customer_id,
            "source_customer_id": cust.source_customer_id,
            "membership_status": cust.membership_status,
            "preferred_category": cust.preferred_category,
            "recommendation_type": rec.recommendation_type, # High Risk, Medium Risk, Low Risk
            "recommendation_description": rec.recommendation_description,
            "status": rec.status,
            "created_at": rec.created_at.isoformat() if rec.created_at else None,
            "updated_at": rec.updated_at.isoformat() if rec.updated_at else None
        })

    return {
        "total": total_count,
        "page": page,
        "limit": limit,
        "recommendations": recommendations_list
    }

@router.patch("/{recommendation_id}/status")
def update_recommendation_status(
    recommendation_id: int,
    payload: StatusUpdateSchema,
    db: Session = Depends(get_db)
):
    allowed_statuses = ["Pending", "Approved", "Accepted", "Completed", "Dismissed", "Rejected"]
    if payload.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {allowed_statuses}")

    rec = db.query(RetentionRecommendation).filter(RetentionRecommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Retention recommendation record not found")

    # Guard against accidental approval of previously rejected recommendation without an explicit state transition
    if rec.status in ["Rejected", "Dismissed"] and payload.status in ["Approved", "Accepted"] and not payload.force:
        raise HTTPException(
            status_code=400,
            detail="Cannot directly accept a previously rejected recommendation without an explicit state transition (e.g. resetting to Pending or explicit force override)."
        )

    now = datetime.datetime.now()
    cust = db.query(Customer).filter(Customer.id == rec.customer_id).first()

    desc = rec.recommendation_description or ""
    desc_lower = desc.lower()

    # Resolve campaign configuration from stored recommendation description
    if "recover10" in desc_lower:
        camp_id = "camp_cart_recovery"
        title = "Automated Cart Recovery with Free Delivery"
        coupon = "RECOVER10"
        perk_type = "discount_voucher"
        val = 10.0
        free_shipping = 1
        channel = "Customer Account Messages"
    elif "speed5" in desc_lower:
        camp_id = "camp_logistics_guarantee"
        title = "Free Express Air Priority Delivery & 5% Delay Apology Coupon"
        coupon = "SPEED5"
        perk_type = "express_shipping"
        val = 5.0
        free_shipping = 1
        channel = "Express Air Logistics & Apology Coupon"
    elif "care10" in desc_lower:
        if any(w in desc_lower for w in ["executive", "sentiment", "director", "apology"]):
            camp_id = "camp_sentiment_recovery"
            title = "Customer Experience Director Direct Apology & 10% Courtesy Coupon"
        else:
            camp_id = "camp_support_vip"
            title = "Priority VIP Support Concierge Callback & 10% Resolution Coupon"
        coupon = "CARE10"
        perk_type = "discount_voucher"
        val = 10.0
        free_shipping = 0
        channel = "VIP Concierge (Phone / Priority Callback)"
    elif "winback15" in desc_lower:
        camp_id = "camp_winback_email"
        title = "Targeted Win-Back Re-engagement Campaign"
        coupon = "WINBACK15"
        perk_type = "discount_voucher"
        val = 15.0
        free_shipping = 1
        channel = "Email & Personalized Storefront Digest"
    elif "freeprime30" in desc_lower or "prime trial" in desc_lower:
        camp_id = "camp_prime_trial"
        title = "Complimentary 30-Day SmartCart Prime Trial & Free Delivery"
        coupon = "FREEPRIME30"
        perk_type = "prime_trial"
        val = 0.0
        free_shipping = 1
        channel = "In-App Push & Email Offer"
    else:
        camp_id = f"camp_rec_{rec.id}"
        title = desc.split(":")[0].replace("Approved", "").strip() or "Customer Retention Action"
        coupon = None
        perk_type = "discount_voucher"
        val = 10.0 if "10%" in desc else 5.0 if "5%" in desc else 15.0 if "15%" in desc else 0.0
        free_shipping = 1 if "free delivery" in desc_lower or "free shipping" in desc_lower else 0
        channel = "In-App Notification"

    if cust and payload.status in ["Approved", "Accepted"]:
        # Deliver retention action to customer's account (idempotent)
        existing_perk = db.query(CustomerRetentionPerk).filter(
            CustomerRetentionPerk.customer_id == cust.id,
            CustomerRetentionPerk.campaign_id == camp_id
        ).first()

        if not existing_perk:
            existing_perk = CustomerRetentionPerk(
                customer_id=cust.id,
                campaign_id=camp_id,
                title=title,
                perk_type=perk_type,
                perk_value=val,
                coupon_code=coupon,
                free_shipping=free_shipping,
                status="Accepted",
                action_summary=desc,
                root_cause_driver=rec.recommendation_type,
                channel=channel,
                created_at=now,
                updated_at=now
            )
            db.add(existing_perk)
        else:
            existing_perk.status = "Accepted"
            existing_perk.title = title
            existing_perk.perk_type = perk_type
            existing_perk.perk_value = val
            existing_perk.coupon_code = coupon
            existing_perk.free_shipping = free_shipping
            existing_perk.action_summary = desc
            existing_perk.updated_at = now

        # Create or update customer notification
        auto_msg = generate_auto_message(existing_perk, cust)
        notif_type = auto_msg.get("notification_type", perk_type)
        nav_target = auto_msg.get("navigation_target", f"/store/cart?coupon={coupon}" if coupon else "/store/cart")

        existing_notif = db.query(CustomerNotification).filter(
            CustomerNotification.customer_id == cust.id,
            CustomerNotification.campaign_id == camp_id
        ).first()

        if not existing_notif:
            existing_notif = CustomerNotification(
                customer_id=cust.id,
                campaign_id=camp_id,
                title=title or auto_msg.get("subject", "Exclusive Customer Privilege"),
                message=auto_msg.get("body", desc),
                notification_type=notif_type,
                navigation_target=nav_target,
                channel=channel,
                sender=auto_msg.get("sender", "SmartCart Official"),
                coupon_code=coupon,
                perk_type=perk_type,
                perk_value=val,
                is_read=0,
                dispatch_status="Delivered",
                created_at=now,
                updated_at=now
            )
            db.add(existing_notif)
        else:
            existing_notif.title = title
            existing_notif.message = auto_msg.get("body", existing_notif.message)
            existing_notif.notification_type = notif_type
            existing_notif.navigation_target = nav_target
            existing_notif.channel = channel
            existing_notif.coupon_code = coupon
            existing_notif.perk_type = perk_type
            existing_notif.perk_value = val
            existing_notif.is_read = 0
            existing_notif.dispatch_status = "Delivered"
            existing_notif.updated_at = now

        if perk_type == "prime_trial":
            cust.membership_status = "Prime"
            su = db.query(StoreUser).filter(StoreUser.customer_id == cust.id).first()
            if su:
                su.membership_status = "Prime"

    elif cust and payload.status in ["Rejected", "Dismissed"]:
        # Revoke/remove customer perks and notifications for this campaign
        existing_perk = db.query(CustomerRetentionPerk).filter(
            CustomerRetentionPerk.customer_id == cust.id,
            CustomerRetentionPerk.campaign_id == camp_id
        ).first()
        if existing_perk:
            existing_perk.status = "Rejected"
            existing_perk.coupon_code = None
            existing_perk.free_shipping = 0
            existing_perk.perk_value = 0.0
            existing_perk.updated_at = now

        existing_notif = db.query(CustomerNotification).filter(
            CustomerNotification.customer_id == cust.id,
            CustomerNotification.campaign_id == camp_id
        ).first()
        if existing_notif:
            db.delete(existing_notif)

        if perk_type == "prime_trial":
            cust.membership_status = "Standard"
            su = db.query(StoreUser).filter(StoreUser.customer_id == cust.id).first()
            if su:
                su.membership_status = "Standard"

    rec.status = payload.status
    rec.updated_at = now
    db.commit()
    db.refresh(rec)

    return {
        "success": True,
        "message": f"Recommendation status updated to '{rec.status}' and delivered to customer account.",
        "recommendation": {
            "id": rec.id,
            "customer_id": rec.customer_id,
            "status": rec.status,
            "updated_at": rec.updated_at.isoformat()
        }
    }
