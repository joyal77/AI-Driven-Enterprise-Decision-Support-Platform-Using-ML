import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.models import CartItem, Product, Customer

router = APIRouter(prefix="/store/cart", tags=["SmartCart User-Isolated Shopping Cart"])

class AddCartItemRequest(BaseModel):
    customer_id: int
    product_id: int
    quantity: int = 1

class UpdateCartQuantityRequest(BaseModel):
    customer_id: int
    product_id: int
    quantity: int

def resolve_customer(customer_id: int, db: Session) -> Optional[Customer]:
    cust = db.query(Customer).filter(Customer.id == customer_id).first()
    if not cust:
        cust = db.query(Customer).filter(Customer.source_customer_id == str(customer_id)).first()
    return cust

@router.get("")
def get_user_cart(customer_id: int = Query(...), db: Session = Depends(get_db)):
    """Fetch current cart items strictly isolated for the specified customer."""
    customer = resolve_customer(customer_id, db)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer account {customer_id} not found.")

    cart_records = db.query(CartItem).filter(CartItem.customer_id == customer.id).all()
    
    items = []
    subtotal = 0.0

    for ci in cart_records:
        prod = ci.product
        if not prod or prod.is_active == 0:
            continue
        line_total = round(prod.price * ci.quantity, 2)
        subtotal += line_total
        items.append({
            "id": prod.id, # matches frontend item.id expectations
            "cart_item_id": ci.id,
            "product_id": prod.id,
            "title": prod.title,
            "category": prod.category,
            "price": prod.price,
            "original_price": prod.original_price,
            "quantity": ci.quantity,
            "image_url": prod.image_url,
            "is_prime": bool(prod.is_prime),
            "stock_quantity": prod.stock_quantity,
            "total_price": line_total
        })

    cart_count = sum(it["quantity"] for it in items)

    return {
        "success": True,
        "customer_id": customer.id,
        "source_customer_id": customer.source_customer_id,
        "cart_count": cart_count,
        "cart_subtotal": round(subtotal, 2),
        "items": items
    }

@router.post("")
def add_to_user_cart(payload: AddCartItemRequest, db: Session = Depends(get_db)):
    """Add a product to the specified customer's isolated cart."""
    if payload.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1.")

    customer = resolve_customer(payload.customer_id, db)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer account {payload.customer_id} not found.")

    product = db.query(Product).filter(Product.id == payload.product_id, Product.is_active == 1).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {payload.product_id} not found.")

    if product.stock_quantity < payload.quantity:
        raise HTTPException(status_code=400, detail=f"Only {product.stock_quantity} units available in stock.")

    # Check if item is already in customer's cart
    existing_item = db.query(CartItem).filter(
        CartItem.customer_id == customer.id,
        CartItem.product_id == product.id
    ).first()

    if existing_item:
        existing_item.quantity += payload.quantity
        existing_item.updated_at = datetime.datetime.now()
    else:
        new_item = CartItem(
            customer_id=customer.id,
            product_id=product.id,
            quantity=payload.quantity
        )
        db.add(new_item)

    db.commit()

    return get_user_cart(customer_id=customer.id, db=db)

@router.put("/item")
def update_user_cart_item(payload: UpdateCartQuantityRequest, db: Session = Depends(get_db)):
    """Update quantity for a product in customer's cart. If quantity <= 0, remove item."""
    customer = resolve_customer(payload.customer_id, db)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer account {payload.customer_id} not found.")

    existing_item = db.query(CartItem).filter(
        CartItem.customer_id == customer.id,
        CartItem.product_id == payload.product_id
    ).first()

    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found in customer cart.")

    if payload.quantity <= 0:
        db.delete(existing_item)
    else:
        existing_item.quantity = payload.quantity
        existing_item.updated_at = datetime.datetime.now()

    db.commit()
    return get_user_cart(customer_id=customer.id, db=db)

@router.delete("/item")
def remove_from_user_cart(
    customer_id: int = Query(...),
    product_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Remove a single product from customer's isolated cart."""
    customer = resolve_customer(customer_id, db)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer account {customer_id} not found.")

    existing_item = db.query(CartItem).filter(
        CartItem.customer_id == customer.id,
        CartItem.product_id == product_id
    ).first()

    if existing_item:
        db.delete(existing_item)
        db.commit()

    return get_user_cart(customer_id=customer.id, db=db)

@router.delete("")
def clear_user_cart(customer_id: int = Query(...), db: Session = Depends(get_db)):
    """Clear all items in customer's isolated cart."""
    customer = resolve_customer(customer_id, db)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer account {customer_id} not found.")

    db.query(CartItem).filter(CartItem.customer_id == customer.id).delete()
    db.commit()

    return {
        "success": True,
        "message": f"Cart cleared for customer {customer.source_customer_id}.",
        "customer_id": customer.id,
        "cart_count": 0,
        "cart_subtotal": 0.0,
        "items": []
    }
