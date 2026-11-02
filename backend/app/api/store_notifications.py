import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Header, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.models import Customer, StoreUser, CustomerNotification

router = APIRouter(prefix="/store/notifications", tags=["SmartCart Storefront Notifications"])

def resolve_store_customer(
    customer_id: Optional[str] = Query(None),
    x_customer_id: Optional[str] = Header(None, alias="X-Customer-ID"),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Customer:
    """
    Authenticates and resolves the customer for store notification endpoints.
    Accepts:
    1. Query param: ?customer_id=...
    2. Header: X-Customer-ID: ...
    3. Header: Authorization: Bearer <token>
    4. Fallback to default demo customer if none provided.
    """
    cid = customer_id or x_customer_id
    if not cid and authorization:
        token = authorization.replace("Bearer", "").strip()
        if "token-" in token:
            cid = token.split("token-")[-1]
        else:
            cid = token

    if not cid:
        # Fallback to first registered store customer
        first_cust = db.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1001").first()
        if first_cust:
            return first_cust
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please specify customer_id or login token."
        )

    customer = None
    if str(cid).isdigit():
        customer = db.query(Customer).filter(Customer.id == int(cid)).first()
    if not customer:
        customer = db.query(Customer).filter(Customer.source_customer_id == str(cid).strip()).first()
    if not customer:
        # If StoreUser ID was provided
        su = db.query(StoreUser).filter(
            StoreUser.id == int(cid) if str(cid).isdigit() else StoreUser.username == str(cid)
        ).first()
        if su and su.customer_id:
            customer = db.query(Customer).filter(Customer.id == su.customer_id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer account '{cid}' not found."
        )

    return customer

@router.get("")
def get_store_notifications(
    customer: Customer = Depends(resolve_store_customer),
    db: Session = Depends(get_db)
):
    """
    Fetch the authenticated customer's notifications feed directly from the database.
    Persists across sessions, browser tabs, logouts, and re-logins.
    """
    notifs = (
        db.query(CustomerNotification)
        .filter(CustomerNotification.customer_id == customer.id)
        .order_by(CustomerNotification.created_at.desc())
        .all()
    )

    unread_count = sum(1 for n in notifs if n.is_read == 0)

    formatted = []
    for n in notifs:
        formatted.append({
            "id": n.id,
            "customer_id": n.customer_id,
            "source_customer_id": customer.source_customer_id,
            "title": n.title,
            "message": n.message,
            "notification_type": getattr(n, "notification_type", "retention_perk") or "retention_perk",
            "navigation_target": getattr(n, "navigation_target", None) or (f"/store/cart?coupon={n.coupon_code}" if n.coupon_code else "/store/cart"),
            "campaign_id": n.campaign_id,
            "channel": n.channel,
            "sender": n.sender,
            "coupon_code": n.coupon_code,
            "perk_type": n.perk_type,
            "perk_value": n.perk_value,
            "image_url": getattr(n, "image_url", None),
            "is_read": bool(n.is_read),
            "dispatch_status": n.dispatch_status,
            "created_at": n.created_at.isoformat() if hasattr(n.created_at, "isoformat") else str(n.created_at) if n.created_at else None,
            "updated_at": n.updated_at.isoformat() if hasattr(n.updated_at, "isoformat") else str(n.updated_at) if n.updated_at else None,
        })

    return {
        "success": True,
        "customer_id": customer.id,
        "source_customer_id": customer.source_customer_id,
        "unread_count": unread_count,
        "total": len(formatted),
        "notifications": formatted
    }

@router.get("/unread-count")
def get_store_unread_notifications_count(
    customer: Customer = Depends(resolve_store_customer),
    db: Session = Depends(get_db)
):
    """
    Fetch the unread notification count for the authenticated customer.
    Used for realtime notification bell badge updates in StoreNavbar.
    """
    unread_count = db.query(CustomerNotification).filter(
        CustomerNotification.customer_id == customer.id,
        CustomerNotification.is_read == 0
    ).count()

    total_count = db.query(CustomerNotification).filter(
        CustomerNotification.customer_id == customer.id
    ).count()

    return {
        "success": True,
        "customer_id": customer.id,
        "source_customer_id": customer.source_customer_id,
        "unread_count": unread_count,
        "total_count": total_count
    }

@router.post("/{notification_id}/read")
def mark_store_notification_read(
    notification_id: int,
    customer: Customer = Depends(resolve_store_customer),
    db: Session = Depends(get_db)
):
    """Mark a specific notification as read for the authenticated customer."""
    notif = db.query(CustomerNotification).filter(
        CustomerNotification.id == notification_id,
        CustomerNotification.customer_id == customer.id
    ).first()

    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification {notification_id} not found for this account."
        )

    notif.is_read = 1
    notif.updated_at = datetime.datetime.now()
    db.commit()

    unread_count = db.query(CustomerNotification).filter(
        CustomerNotification.customer_id == customer.id,
        CustomerNotification.is_read == 0
    ).count()

    return {
        "success": True,
        "notification_id": notification_id,
        "is_read": True,
        "unread_count": unread_count
    }

@router.post("/read-all")
def mark_all_store_notifications_read(
    customer: Customer = Depends(resolve_store_customer),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for the authenticated customer."""
    now = datetime.datetime.now()
    db.query(CustomerNotification).filter(
        CustomerNotification.customer_id == customer.id,
        CustomerNotification.is_read == 0
    ).update({"is_read": 1, "updated_at": now}, synchronize_session=False)
    db.commit()

    return {
        "success": True,
        "customer_id": customer.id,
        "message": "All notifications marked as read.",
        "unread_count": 0
    }
