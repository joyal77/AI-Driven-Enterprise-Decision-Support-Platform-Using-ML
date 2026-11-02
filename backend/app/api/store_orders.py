import datetime
import random
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..db.session import get_db
from ..db.models import (
    Order, OrderItem, Product, Customer,
    CustomerRetentionPerk, CustomerPerkRedemption, CartItem
)
from ..services.ml_sync_service import sync_order_to_customer_and_ml

router = APIRouter(prefix="/store/orders", tags=["SmartCart Storefront Orders"])

class OrderItemInput(BaseModel):
    product_id: int
    quantity: int

class PlaceOrderRequest(BaseModel):
    customer_id: int
    items: List[OrderItemInput]
    shipping_address: str
    payment_mode: str = "UPI" # 'UPI' | 'Credit/Debit Card' | 'Net Banking' | 'Cash on Delivery'
    wallet_credit_applied: Optional[float] = 0.0
    voucher_code: Optional[str] = None

class ValidateVoucherRequest(BaseModel):
    customer_id: int
    voucher_code: str
    cart_subtotal: Optional[float] = 0.0

@router.post("/validate-voucher")
def validate_store_voucher(payload: ValidateVoucherRequest, db: Session = Depends(get_db)):
    """
    Validates a discount coupon or retention voucher for a specific authenticated customer.
    Checks customer ownership, active/used lifecycle status, and prevents repeated use.
    """
    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not customer:
        customer = db.query(Customer).filter(Customer.source_customer_id == str(payload.customer_id)).first()

    if not customer:
        return {"valid": False, "message": "Customer account not found."}

    code_str = (payload.voucher_code or "").strip().upper()
    if not code_str:
        return {"valid": False, "message": "Please enter a voucher code."}

    # 1. Check if already redeemed in audit table
    prior_redemption = db.query(CustomerPerkRedemption).filter(
        CustomerPerkRedemption.customer_id == customer.id,
        CustomerPerkRedemption.coupon_code.ilike(code_str),
        CustomerPerkRedemption.benefit_type == "discount_coupon"
    ).first()

    if prior_redemption:
        return {
            "valid": False,
            "code": code_str,
            "message": f"Coupon '{code_str}' has already been redeemed on order {prior_redemption.order_number} and cannot be used again."
        }

    # 2. Check retention perks database
    perk = db.query(CustomerRetentionPerk).filter(
        CustomerRetentionPerk.customer_id == customer.id,
        CustomerRetentionPerk.coupon_code.ilike(code_str)
    ).first()

    if perk:
        if perk.status == "Rejected":
            return {"valid": False, "code": code_str, "message": f"Coupon '{code_str}' is no longer active."}
        if perk.status in ["Used", "USED"] or getattr(perk, 'coupon_used', 0) == 1:
            return {"valid": False, "code": code_str, "message": f"Coupon '{code_str}' has already been used on a previous order."}
        if perk.status not in ["Accepted", "Approved", "Active"]:
            return {"valid": False, "code": code_str, "message": f"Coupon '{code_str}' is not active on your account."}

        # Calculate discount
        pct = perk.perk_value if (perk.perk_value > 0 and perk.perk_value <= 50) else (10.0 if not (perk.perk_value > 50) else 0.0)
        amt = perk.perk_value if perk.perk_value > 50 else 0.0
        free_del = bool(getattr(perk, 'free_shipping', 0) == 1 and getattr(perk, 'shipping_used', 0) == 0)

        free_text = " + Free Delivery" if free_del else ""
        disc_text = f"{pct}% OFF" if pct > 0 else f"₹{amt} OFF"
        return {
            "valid": True,
            "code": code_str,
            "title": perk.title,
            "discount_pct": pct,
            "discount_amount": amt,
            "free_shipping": free_del,
            "message": f"Coupon '{code_str}' ({disc_text}{free_text}) applied successfully!"
        }

    # 3. Check generic retention coupon patterns if not recorded yet
    if any(code_str.startswith(pfx) for pfx in ["CARE", "SPEED", "RECOVER", "WINBACK", "WELCOME", "VIP", "FLEX", "DISCOVER", "LOYALTY"]):
        pct = 10.0
        if "15" in code_str and "150" not in code_str:
            pct = 15.0
        elif "5" in code_str and "50" not in code_str:
            pct = 5.0

        free_del = any(pfx in code_str for pfx in ["RECOVER", "SPEED", "FLEX", "WINBACK", "WELCOME"])
        free_text = " + Free Delivery" if free_del else ""
        return {
            "valid": True,
            "code": code_str,
            "title": f"Retention Coupon {code_str}",
            "discount_pct": pct,
            "discount_amount": 0.0,
            "free_shipping": free_del,
            "message": f"Coupon '{code_str}' ({pct}% OFF{free_text}) applied successfully!"
        }

    return {"valid": False, "code": code_str, "message": f"Voucher code '{code_str}' is invalid or expired for this account."}

@router.post("")
def place_store_order(payload: PlaceOrderRequest, db: Session = Depends(get_db)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Cannot place an empty order. Cart is empty.")

    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not customer:
        customer = db.query(Customer).filter(Customer.source_customer_id == str(payload.customer_id)).first()

    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer account with ID '{payload.customer_id}' not found.")

    # 0. Idempotency & Duplicate Submission Protection (60-second window)
    now = datetime.datetime.now()
    current_item_signature = sorted([(it.product_id, it.quantity) for it in payload.items])

    recent_orders = (
        db.query(Order)
        .filter(Order.customer_id == customer.id)
        .order_by(Order.id.desc())
        .limit(5)
        .all()
    )

    for recent in recent_orders:
        if not recent.order_date:
            continue
        o_date = recent.order_date
        if isinstance(o_date, str):
            try:
                o_date = datetime.datetime.fromisoformat(o_date)
            except Exception:
                continue
        # Check if within 3-second rapid double-click deduplication window
        time_diff = abs((now - o_date).total_seconds())
        if time_diff <= 3:
            recent_signature = sorted([(it.product_id, it.quantity) for it in recent.items])
            if (
                recent_signature == current_item_signature
                and recent.shipping_address == payload.shipping_address
            ):
                return {
                    "success": True,
                    "message": f"Order {recent.order_number} already placed (duplicate submission prevented).",
                    "is_duplicate_suppressed": True,
                    "order": {
                        "order_id": recent.id,
                        "order_number": recent.order_number,
                        "order_date": recent.order_date.isoformat() if hasattr(recent.order_date, 'isoformat') else str(recent.order_date),
                        "subtotal": recent.subtotal,
                        "tax": recent.tax_amount,
                        "shipping": recent.shipping_amount,
                        "shipping_fee": recent.shipping_amount,
                        "discount": recent.discount or 0.0,
                        "total_amount": recent.order_amount,
                        "payment_mode": recent.payment_mode,
                        "order_status": recent.order_status,
                        "items_count": len(recent.items),
                    },
                    "realtime_ml_sync": None,
                }

    # 1. Validate line items & stock availability
    subtotal = 0.0
    order_items_to_create = []

    for item in payload.items:
        prod = db.query(Product).filter(Product.id == item.product_id).first()
        if not prod:
            raise HTTPException(status_code=400, detail=f"Product with ID {item.product_id} no longer exists.")
        
        if prod.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient inventory for '{prod.title}'. Only {prod.stock_quantity} left in stock."
            )

        line_total = round(prod.price * item.quantity, 2)
        subtotal += line_total

        # Decrement inventory stock
        prod.stock_quantity -= item.quantity

        order_items_to_create.append({
            "product_id": prod.id,
            "quantity": item.quantity,
            "unit_price": prod.price,
            "total_price": line_total
        })

    # 2. Validate Discount Voucher & Check Prior Redemption (Transaction Safe)
    voucher_discount = 0.0
    applied_voucher_perk = None
    coupon_grants_free_shipping = False
    normalized_coupon_code = None

    if payload.voucher_code:
        normalized_coupon_code = payload.voucher_code.strip().upper()

        # Check audit redemption table
        prior_redemption = db.query(CustomerPerkRedemption).filter(
            CustomerPerkRedemption.customer_id == customer.id,
            CustomerPerkRedemption.coupon_code.ilike(normalized_coupon_code),
            CustomerPerkRedemption.benefit_type == "discount_coupon"
        ).first()

        if prior_redemption:
            raise HTTPException(
                status_code=400,
                detail=f"Coupon '{normalized_coupon_code}' has already been used on order {prior_redemption.order_number} and cannot be redeemed again."
            )

        # Check existing perk record
        perk = db.query(CustomerRetentionPerk).filter(
            CustomerRetentionPerk.customer_id == customer.id,
            CustomerRetentionPerk.coupon_code.ilike(normalized_coupon_code)
        ).first()

        if perk:
            if perk.status == "Rejected":
                raise HTTPException(status_code=400, detail=f"Coupon '{normalized_coupon_code}' is no longer active.")
            if perk.status in ["Used", "USED"] or getattr(perk, 'coupon_used', 0) == 1:
                raise HTTPException(
                    status_code=400,
                    detail=f"Coupon '{normalized_coupon_code}' has already been redeemed on a previous order."
                )
            if perk.status not in ["Accepted", "Approved", "Active"]:
                raise HTTPException(status_code=400, detail=f"Coupon '{normalized_coupon_code}' is not active.")

            applied_voucher_perk = perk
            if perk.perk_value > 0 and perk.perk_value <= 50:
                voucher_discount = round(subtotal * (perk.perk_value / 100.0), 2)
            elif perk.perk_value > 50:
                voucher_discount = min(subtotal, perk.perk_value)
            else:
                voucher_discount = round(subtotal * 0.10, 2)

            if (
                getattr(perk, 'free_shipping', 0) == 1
                or perk.perk_type in ["express_shipping", "priority_shipping", "prime_trial"]
                or "free delivery" in (perk.title or "").lower()
                or "express" in (perk.title or "").lower()
                or any(pfx in normalized_coupon_code for pfx in ["RECOVER", "SPEED", "FLEX", "WINBACK", "WELCOME"])
            ):
                coupon_grants_free_shipping = True
        else:
            # Fallback for valid retention coupon codes when not pre-created
            if any(normalized_coupon_code.startswith(pfx) for pfx in ["CARE", "SPEED", "RECOVER", "WINBACK", "WELCOME", "EASY", "VIP", "FLEX", "DISCOVER", "LOYALTY"]):
                pct = 10.0
                if "15" in normalized_coupon_code and "150" not in normalized_coupon_code:
                    pct = 15.0
                elif "5" in normalized_coupon_code and "50" not in normalized_coupon_code:
                    pct = 5.0
                voucher_discount = round(subtotal * (pct / 100.0), 2)
                if any(pfx in normalized_coupon_code for pfx in ["RECOVER", "SPEED", "FLEX", "WINBACK", "WELCOME"]):
                    coupon_grants_free_shipping = True
            else:
                raise HTTPException(status_code=400, detail=f"Voucher code '{normalized_coupon_code}' is invalid or expired for this account.")

    # 3. Check Free Delivery & Express Shipping Retention Perks
    is_prime = bool(customer.membership_status and "prime" in customer.membership_status.lower())
    is_subtotal_qualified = (subtotal >= 500.0)

    # Active unused free shipping / express delivery perks
    active_shipping_perks = db.query(CustomerRetentionPerk).filter(
        CustomerRetentionPerk.customer_id == customer.id,
        CustomerRetentionPerk.status.in_(["Accepted", "Approved", "Active"]),
        (CustomerRetentionPerk.shipping_used == 0) | (CustomerRetentionPerk.shipping_used.is_(None))
    ).filter(
        (CustomerRetentionPerk.free_shipping == 1) |
        (CustomerRetentionPerk.perk_type.in_(["express_shipping", "priority_shipping", "prime_trial"])) |
        (CustomerRetentionPerk.title.ilike("%express%")) |
        (CustomerRetentionPerk.title.ilike("%free delivery%")) |
        (CustomerRetentionPerk.title.ilike("%free shipping%"))
    ).all()

    has_retention_free_delivery = bool(active_shipping_perks or coupon_grants_free_shipping)
    shipping_fee = 0.0 if (is_prime or is_subtotal_qualified or has_retention_free_delivery) else 40.0

    # Determine whether a retention free delivery benefit was consumed
    consumed_free_delivery = False
    consumed_shipping_perk = None

    if shipping_fee == 0.0 and not is_prime:
        # If order benefited from retention free delivery or coupon bundled free shipping:
        if coupon_grants_free_shipping:
            consumed_free_delivery = True
        elif active_shipping_perks and (not is_subtotal_qualified or any(p.perk_type in ["express_shipping", "priority_shipping"] for p in active_shipping_perks)):
            consumed_free_delivery = True
            consumed_shipping_perk = active_shipping_perks[0]

    # 4. Wallet Credit Processing
    wallet_discount = 0.0
    credit_perks_used = []
    if payload.wallet_credit_applied and payload.wallet_credit_applied > 0:
        credit_perks = db.query(CustomerRetentionPerk).filter(
            CustomerRetentionPerk.customer_id == customer.id,
            CustomerRetentionPerk.perk_type == "wallet_credit",
            CustomerRetentionPerk.status.in_(["Accepted", "Approved", "Active"]),
            CustomerRetentionPerk.perk_value > 0
        ).all()
        avail_credit = sum(p.perk_value for p in credit_perks)
        requested_credit = min(avail_credit, float(payload.wallet_credit_applied), max(0.0, subtotal - voucher_discount))
        wallet_discount = max(0.0, round(requested_credit, 2))

        if wallet_discount > 0:
            rem = wallet_discount
            for cp in credit_perks:
                if rem <= 0:
                    break
                if cp.perk_value <= rem:
                    rem -= cp.perk_value
                    credit_perks_used.append((cp, cp.perk_value, True))
                else:
                    credit_perks_used.append((cp, rem, False))
                    rem = 0.0

    total_discount = round(voucher_discount + wallet_discount, 2)
    taxable_amount = max(0.0, subtotal - total_discount)
    tax_fee = round(taxable_amount * 0.05, 2) # 5% GST on net subtotal
    final_total = max(0.0, round(taxable_amount + shipping_fee + tax_fee, 2))

    # 5. Generate Order Number & Commit within DB Transaction
    order_num = f"SMART-{now.strftime('%y%m%d')}-{random.randint(10000, 99999)}"

    try:
        new_order = Order(
            order_number=order_num,
            customer_id=customer.id,
            order_date=now,
            order_amount=final_total,
            subtotal=round(subtotal, 2),
            tax_amount=tax_fee,
            shipping_amount=shipping_fee,
            discount=total_discount,
            payment_mode=payload.payment_mode,
            order_status="Confirmed",
            shipping_address=payload.shipping_address,
            voucher_code=normalized_coupon_code if voucher_discount > 0 else None,
            wallet_credit_used=wallet_discount,
            free_shipping_applied=1 if (shipping_fee == 0.0 and (is_prime or has_retention_free_delivery)) else 0
        )
        db.add(new_order)
        db.flush() # Allocates new_order.id

        # Insert line items
        for oi in order_items_to_create:
            item_obj = OrderItem(
                order_id=new_order.id,
                product_id=oi["product_id"],
                quantity=oi["quantity"],
                unit_price=oi["unit_price"],
                total_price=oi["total_price"]
            )
            db.add(item_obj)

        # 6. Lifecycle: Consume Discount Voucher
        if normalized_coupon_code and voucher_discount > 0:
            if applied_voucher_perk:
                # Atomic check to ensure no concurrent checkout grabbed it
                rows_updated = db.query(CustomerRetentionPerk).filter(
                    CustomerRetentionPerk.id == applied_voucher_perk.id,
                    CustomerRetentionPerk.status.in_(["Accepted", "Approved", "Active"]),
                    (CustomerRetentionPerk.coupon_used == 0) | (CustomerRetentionPerk.coupon_used.is_(None))
                ).update({
                    "coupon_used": 1,
                    "shipping_used": 1 if consumed_free_delivery and getattr(applied_voucher_perk, 'free_shipping', 0) == 1 else getattr(applied_voucher_perk, 'shipping_used', 0),
                    "status": "Used",
                    "used_order_id": new_order.id,
                    "used_at": now,
                    "updated_at": now
                }, synchronize_session=False)

                if rows_updated == 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Coupon '{normalized_coupon_code}' was already redeemed by another concurrent checkout."
                    )
            else:
                # Create historical record marked as Used
                fallback_perk = CustomerRetentionPerk(
                    customer_id=customer.id,
                    campaign_id=f"camp_used_{normalized_coupon_code.lower()}",
                    title=f"Retention Coupon {normalized_coupon_code}",
                    perk_type="discount_voucher",
                    perk_value=voucher_discount,
                    coupon_code=normalized_coupon_code,
                    status="Used",
                    coupon_used=1,
                    shipping_used=1 if consumed_free_delivery else 0,
                    used_order_id=new_order.id,
                    used_at=now,
                    action_summary=f"Redeemed on order {new_order.order_number}"
                )
                db.add(fallback_perk)
                db.flush()
                applied_voucher_perk = fallback_perk

            # Insert immutable redemption audit record
            db.add(CustomerPerkRedemption(
                customer_id=customer.id,
                order_id=new_order.id,
                order_number=new_order.order_number,
                perk_id=applied_voucher_perk.id if applied_voucher_perk else None,
                campaign_id=applied_voucher_perk.campaign_id if applied_voucher_perk else f"camp_{normalized_coupon_code.lower()}",
                benefit_type="discount_coupon",
                coupon_code=normalized_coupon_code,
                discount_amount=voucher_discount,
                redemption_date=now,
                status="Redeemed"
            ))

        # 7. Lifecycle: Consume Free Delivery Perk (Independent tracking)
        if consumed_shipping_perk and (not applied_voucher_perk or consumed_shipping_perk.id != applied_voucher_perk.id):
            consumed_shipping_perk.shipping_used = 1
            consumed_shipping_perk.used_order_id = new_order.id
            consumed_shipping_perk.used_at = now
            consumed_shipping_perk.updated_at = now
            if getattr(consumed_shipping_perk, 'coupon_code', None) is None or getattr(consumed_shipping_perk, 'coupon_used', 0) == 1:
                consumed_shipping_perk.status = "Used"

            db.add(CustomerPerkRedemption(
                customer_id=customer.id,
                order_id=new_order.id,
                order_number=new_order.order_number,
                perk_id=consumed_shipping_perk.id,
                campaign_id=consumed_shipping_perk.campaign_id,
                benefit_type="free_shipping",
                coupon_code=consumed_shipping_perk.coupon_code,
                discount_amount=40.0,
                redemption_date=now,
                status="Redeemed"
            ))

        # 8. Lifecycle: Consume Wallet Credit Perks
        for cp, deducted_val, is_fully_exhausted in credit_perks_used:
            if is_fully_exhausted:
                cp.perk_value = 0.0
                cp.status = "Used"
                cp.used_order_id = new_order.id
                cp.used_at = now
            else:
                cp.perk_value = round(cp.perk_value - deducted_val, 2)
            cp.updated_at = now

            db.add(CustomerPerkRedemption(
                customer_id=customer.id,
                order_id=new_order.id,
                order_number=new_order.order_number,
                perk_id=cp.id,
                campaign_id=cp.campaign_id,
                benefit_type="wallet_credit",
                coupon_code=None,
                discount_amount=deducted_val,
                redemption_date=now,
                status="Redeemed"
            ))

        # 9. Clear customer's active shopping cart in database
        db.query(CartItem).filter(CartItem.customer_id == customer.id).delete()

        db.commit()
        db.refresh(new_order)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="A benefit in this order has already been redeemed by another simultaneous transaction."
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Order placement failed: {str(e)}")

    # 10. Synchronize to Customer Profile & Automatically Re-score with ML Churn Model
    ml_sync_result = sync_order_to_customer_and_ml(customer.id, final_total, db)

    return {
        "success": True,
        "message": f"Order {order_num} successfully placed! Payment verified via {payload.payment_mode}.",
        "order": {
            "order_id": new_order.id,
            "order_number": new_order.order_number,
            "order_date": new_order.order_date.isoformat(),
            "subtotal": new_order.subtotal,
            "tax": new_order.tax_amount,
            "shipping": new_order.shipping_amount,
            "shipping_fee": new_order.shipping_amount,
            "discount": new_order.discount,
            "voucher_code": new_order.voucher_code,
            "wallet_credit_used": new_order.wallet_credit_used,
            "free_shipping_applied": new_order.free_shipping_applied,
            "total_amount": new_order.order_amount,
            "payment_mode": new_order.payment_mode,
            "order_status": new_order.order_status,
            "items_count": len(order_items_to_create)
        },
        "realtime_ml_sync": ml_sync_result
    }

@router.get("/my-orders")
def get_customer_orders(customer_id: int, db: Session = Depends(get_db)):
    """Fetch orders for active customer account with complete discount and delivery audit trail."""
    orders = db.query(Order).filter(Order.customer_id == customer_id).order_by(Order.order_date.desc()).all()
    results = []

    for o in orders:
        items_detail = []
        for it in o.items:
            items_detail.append({
                "product_id": it.product_id,
                "title": it.product.title if it.product else "Item",
                "image_url": it.product.image_url if it.product else None,
                "quantity": it.quantity,
                "unit_price": it.unit_price,
                "total_price": it.total_price
            })

        results.append({
            "order_id": o.id,
            "order_number": o.order_number or f"ORD-{o.id}",
            "order_date": o.order_date.isoformat() if hasattr(o.order_date, 'isoformat') else str(o.order_date),
            "order_amount": o.order_amount,
            "subtotal": o.subtotal,
            "discount": o.discount or 0.0,
            "shipping_amount": o.shipping_amount or 0.0,
            "tax_amount": o.tax_amount or 0.0,
            "voucher_code": getattr(o, 'voucher_code', None),
            "wallet_credit_used": getattr(o, 'wallet_credit_used', 0.0),
            "free_shipping_applied": getattr(o, 'free_shipping_applied', 0),
            "payment_mode": o.payment_mode,
            "order_status": o.order_status,
            "items": items_detail
        })

    return {
        "customer_id": customer_id,
        "total_orders": len(results),
        "orders": results
    }

@router.get("/all")
def get_all_store_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Admin endpoint to inspect live storefront transactions."""
    total_count = db.query(Order).count()
    orders = db.query(Order).order_by(Order.order_date.desc()).offset((page - 1) * limit).limit(limit).all()

    order_list = []
    for o in orders:
        cust = o.customer
        order_list.append({
            "order_id": o.id,
            "order_number": o.order_number or f"ORD-{o.id}",
            "order_date": o.order_date.isoformat() if hasattr(o.order_date, 'isoformat') else str(o.order_date),
            "order_amount": o.order_amount,
            "subtotal": o.subtotal,
            "discount": o.discount or 0.0,
            "shipping_amount": o.shipping_amount or 0.0,
            "voucher_code": getattr(o, 'voucher_code', None),
            "payment_mode": o.payment_mode,
            "order_status": o.order_status,
            "customer": {
                "id": cust.id if cust else None,
                "source_customer_id": cust.source_customer_id if cust else "Unknown",
                "membership_status": cust.membership_status if cust else "Standard",
                "preferred_category": cust.preferred_category if cust else "General"
            },
            "items_count": len(o.items)
        })

    return {
        "total": total_count,
        "page": page,
        "limit": limit,
        "orders": order_list
    }
