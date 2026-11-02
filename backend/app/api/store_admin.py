import datetime
import hashlib
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..db.session import get_db
from ..db.models import StoreUser, User, Customer, Product, Order, OrderItem, CustomerRetentionPerk

router = APIRouter(prefix="/store/admin", tags=["SmartCart Storefront Administration"])

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.strip().encode()).hexdigest()

class CreateAdminRequest(BaseModel):
    username: str
    password: str
    full_name: str
    role: Optional[str] = "admin"

class UpdateOrderStatusRequest(BaseModel):
    status: str

class GrantCustomerPerkRequest(BaseModel):
    customer_id: int
    perk_type: str  # 'wallet_credit' | 'discount_voucher' | 'prime_trial' | 'express_shipping'
    perk_value: float = 0.0
    title: Optional[str] = None
    coupon_code: Optional[str] = None

@router.get("/overview")
def get_store_admin_overview(db: Session = Depends(get_db)):
    """Summary metrics for the store administrator console."""
    total_products = db.query(Product).filter(Product.is_active == 1).count()
    low_stock_count = db.query(Product).filter(Product.is_active == 1, Product.stock_quantity < 35).count()
    total_orders = db.query(Order).count()
    total_revenue = db.query(func.coalesce(func.sum(Order.order_amount), 0.0)).scalar() or 0.0
    total_customers = db.query(Customer).filter(Customer.source_customer_id.like("AMZ_PRED1_%")).count()
    total_staff = db.query(StoreUser).filter(StoreUser.role.in_(["admin", "product_manager"])).count()

    return {
        "success": True,
        "total_products": total_products,
        "low_stock_count": low_stock_count,
        "total_orders": total_orders,
        "total_revenue": round(float(total_revenue), 2),
        "total_customers": total_customers,
        "total_staff": total_staff
    }

@router.post("/create-admin")
def create_admin_account(req: CreateAdminRequest, db: Session = Depends(get_db)):
    """Create a new Administrator or Product Manager account."""
    uname = req.username.strip()
    pw = req.password.strip()
    name = req.full_name.strip()
    role = req.role.strip().lower() if req.role else "admin"

    if len(uname) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters.")
    if len(pw) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters.")
    if role not in ["admin", "product_manager"]:
        role = "admin"

    existing = db.query(StoreUser).filter(StoreUser.username.ilike(uname)).first()
    if existing:
        existing.role = role
        existing.password_hash = hash_pw(pw)
        existing.full_name = name or existing.full_name
        db.commit()
        db.refresh(existing)
        return {
            "success": True,
            "message": f"Account '{existing.username}' upgraded to {role.upper()} successfully.",
            "user": {
                "id": existing.id,
                "username": existing.username,
                "role": existing.role,
                "full_name": existing.full_name
            }
        }

    new_admin = StoreUser(
        username=uname,
        password_hash=hash_pw(pw),
        role=role,
        full_name=name or f"SmartCart {role.title()}"
    )
    db.add(new_admin)

    # Also register in users table for single sign-on with ML Decision Suite
    if "@" in uname:
        existing_ml = db.query(User).filter(User.email.ilike(uname)).first()
        if not existing_ml:
            ml_user = User(
                name=name or uname,
                email=uname,
                password_hash=hash_pw(pw),
                role=role
            )
            db.add(ml_user)

    db.commit()
    db.refresh(new_admin)

    return {
        "success": True,
        "message": f"New Administrator account '{new_admin.username}' created successfully.",
        "user": {
            "id": new_admin.id,
            "username": new_admin.username,
            "role": new_admin.role,
            "full_name": new_admin.full_name
        }
    }

@router.get("/staff-users")
def list_staff_users(db: Session = Depends(get_db)):
    """List all Administrator and Product Manager accounts."""
    staff = db.query(StoreUser).filter(StoreUser.role.in_(["admin", "product_manager"])).order_by(StoreUser.id.asc()).all()
    return {
        "success": True,
        "staff": [
            {
                "id": u.id,
                "username": u.username,
                "role": u.role,
                "full_name": u.full_name or u.username,
                "created_at": u.created_at.isoformat() if hasattr(u.created_at, 'isoformat') else str(u.created_at)
            }
            for u in staff
        ]
    }

@router.delete("/staff-users/{user_id}")
def delete_staff_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a staff user (protected: cannot delete primary admin)."""
    target = db.query(StoreUser).filter(StoreUser.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Staff account not found.")

    if target.username.lower() in ["admin", "admin@smartcart.com"]:
        raise HTTPException(status_code=400, detail="Cannot delete default primary administrator account.")

    db.delete(target)
    db.commit()
    return {"success": True, "message": f"Staff account '{target.username}' removed."}

@router.post("/bulk-restock")
def bulk_restock_low_inventory(db: Session = Depends(get_db)):
    """Restock all products with stock < 35 back up to 100 units."""
    low_stock_products = db.query(Product).filter(Product.is_active == 1, Product.stock_quantity < 35).all()
    restocked_count = 0

    for prod in low_stock_products:
        prod.stock_quantity = 100
        restocked_count += 1

    db.commit()
    return {
        "success": True,
        "message": f"Successfully replenished inventory for {restocked_count} products back to 100 units.",
        "restocked_count": restocked_count
    }

@router.get("/orders")
def get_admin_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=1000),
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Admin view of all store customer orders with status controls and pagination."""
    q = db.query(Order).join(Customer, Order.customer_id == Customer.id, isouter=True)
    if status_filter and status_filter.lower() != "all":
        q = q.filter(Order.order_status.ilike(status_filter.strip()))

    if search and search.strip():
        term = f"%{search.strip()}%"
        q = q.filter(
            (Order.order_number.ilike(term)) |
            (Customer.source_customer_id.ilike(term)) |
            (Order.payment_mode.ilike(term))
        )

    total = q.count()
    if limit >= 1000:
        orders = q.order_by(Order.order_date.desc()).all()
    else:
        orders = q.order_by(Order.order_date.desc()).offset((page - 1) * limit).limit(limit).all()

    results = []
    for o in orders:
        cust = o.customer
        results.append({
            "order_id": o.id,
            "order_number": o.order_number or f"ORD-{o.id}",
            "order_date": o.order_date.isoformat() if hasattr(o.order_date, 'isoformat') else str(o.order_date),
            "order_amount": o.order_amount,
            "payment_mode": o.payment_mode,
            "order_status": o.order_status,
            "shipping_address": o.shipping_address or "Standard Address",
            "customer": {
                "id": cust.id if cust else None,
                "source_customer_id": cust.source_customer_id if cust else "Unknown",
                "membership_status": cust.membership_status if cust else "Standard",
                "preferred_category": cust.preferred_category if cust else "General"
            },
            "items_count": len(o.items)
        })

    total_pages = max(1, (total + limit - 1) // limit) if limit < 1000 else 1

    return {
        "success": True,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "orders": results
    }

@router.put("/orders/{order_id}/status")
def update_order_status(order_id: int, req: UpdateOrderStatusRequest, db: Session = Depends(get_db)):
    """Admin order status update (Confirmed, Shipped, Delivered, Cancelled)."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    old_status = order.order_status
    new_status = req.status.strip()
    order.order_status = new_status

    # If status changed to Cancelled, restock items back into inventory
    if new_status.lower() in ["cancelled", "canceled"] and old_status.lower() not in ["cancelled", "canceled"]:
        for it in order.items:
            prod = it.product
            if prod:
                prod.stock_quantity += it.quantity

    db.commit()
    db.refresh(order)

    return {
        "success": True,
        "message": f"Order {order.order_number} status updated to '{new_status}'.",
        "order_id": order.id,
        "order_status": order.order_status
    }

@router.post("/grant-perk")
def grant_customer_perk(req: GrantCustomerPerkRequest, db: Session = Depends(get_db)):
    """Admin tool to directly credit wallet, issue custom vouchers, or upgrade to Prime."""
    customer = db.query(Customer).filter(Customer.id == req.customer_id).first()
    if not customer:
        customer = db.query(Customer).filter(Customer.source_customer_id == str(req.customer_id)).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")

    perk_type = req.perk_type.strip().lower()
    value = float(req.perk_value)
    title = req.title.strip() if req.title else None
    coupon_code = req.coupon_code.strip() if req.coupon_code else None

    if perk_type == "wallet_credit":
        if not title:
            title = f"Admin Wallet Credit: INR {value:.0f}"
        if not coupon_code:
            coupon_code = f"ADMINWALLET-{int(datetime.datetime.now().timestamp()) % 10000}"
    elif perk_type in ["discount_voucher", "coupon"]:
        perk_type = "discount_voucher"
        if not title:
            title = f"Admin Special Discount: {value:.0f}% OFF"
        if not coupon_code:
            coupon_code = f"ADMIN{int(value)}OFF"
    elif perk_type in ["prime_trial", "prime_upgrade"]:
        perk_type = "prime_trial"
        if not title:
            title = "Admin Prime Membership Upgrade"
        if not coupon_code:
            coupon_code = "ADMINPRIME"
        customer.membership_status = "Prime"
    elif perk_type in ["express_shipping", "free_shipping"]:
        perk_type = "express_shipping"
        if not title:
            title = "Admin Free Express Shipping Pass"
        if not coupon_code:
            coupon_code = "ADMINEXPRESS"
    else:
        perk_type = "wallet_credit"
        title = title or "Admin Credit"

    campaign_id = f"ADMIN-PERK-{int(datetime.datetime.now().timestamp())}"

    new_perk = CustomerRetentionPerk(
        customer_id=customer.id,
        campaign_id=campaign_id,
        title=title,
        perk_type=perk_type,
        perk_value=value,
        coupon_code=coupon_code,
        status="Approved",
        action_summary=f"Directly granted by Administrator on {datetime.date.today().strftime('%b %d, %Y')}.",
        root_cause_driver="Admin Executive Countermeasure",
        channel="In-App Notification & Storefront Wallet"
    )

    db.add(new_perk)
    db.commit()
    db.refresh(new_perk)

    return {
        "success": True,
        "message": f"Successfully granted '{title}' to customer {customer.source_customer_id}!",
        "perk": {
            "id": new_perk.id,
            "title": new_perk.title,
            "perk_type": new_perk.perk_type,
            "perk_value": new_perk.perk_value,
            "coupon_code": new_perk.coupon_code,
            "status": new_perk.status
        }
    }
