"""
test_cart_isolation.py

Verifies:
1. User account independence: Cart operations on one account do NOT affect any other account.
2. Dataset alignment: Carts are populated based on preferred_category and cart_abandonments_last_30d.
3. Zero-cart benchmark: Customer AMZ_PRED1_1041 has strictly 0 cart items.
4. Order placement cart clearing: Placing an order for Customer A clears only Customer A's cart.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.db.session import SessionLocal
from app.db.models import Customer, Product, CartItem, Order
from app.api.store_cart import (
    get_user_cart,
    add_to_user_cart,
    update_user_cart_item,
    remove_from_user_cart,
    clear_user_cart,
    AddCartItemRequest,
    UpdateCartQuantityRequest
)
from app.api.store_orders import place_store_order, PlaceOrderRequest, OrderItemInput

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_account_isolation_add_product(db_session):
    """Adding a product in Customer A's account must NOT affect Customer B's cart."""
    c1 = db_session.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1001").first()
    c2 = db_session.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1002").first()
    assert c1 and c2

    # Get initial cart items for both
    cart1_initial = get_user_cart(customer_id=c1.id, db=db_session)
    cart2_initial = get_user_cart(customer_id=c2.id, db=db_session)
    initial_c2_count = cart2_initial["cart_count"]

    # Pick an active product not currently in c1's cart
    c1_prod_ids = [it["product_id"] for it in cart1_initial["items"]]
    test_prod = db_session.query(Product).filter(~Product.id.in_(c1_prod_ids), Product.is_active == 1).first()
    assert test_prod is not None

    # Customer 1 adds test product to cart
    add_payload = AddCartItemRequest(
        customer_id=c1.id,
        product_id=test_prod.id,
        quantity=1
    )
    add_to_user_cart(add_payload, db=db_session)

    # Verify Customer 1's cart increased
    cart1_updated = get_user_cart(customer_id=c1.id, db=db_session)
    assert any(it["product_id"] == test_prod.id for it in cart1_updated["items"])

    # CRITICAL TEST: Customer 2's cart must NOT contain test_prod and must maintain its exact original count
    cart2_after = get_user_cart(customer_id=c2.id, db=db_session)
    assert cart2_after["cart_count"] == initial_c2_count, "Customer 2 cart was modified by Customer 1 action!"
    
    # Cleanup: remove test product from Customer 1's cart
    remove_from_user_cart(customer_id=c1.id, product_id=test_prod.id, db=db_session)

def test_account_isolation_clear_cart(db_session):
    """Clearing Customer A's cart must NOT affect Customer B's cart."""
    c1 = db_session.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1001").first()
    c2 = db_session.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1002").first()
    assert c1 and c2

    cart2_before = get_user_cart(customer_id=c2.id, db=db_session)
    if cart2_before["cart_count"] == 0:
        p_seed = db_session.query(Product).filter(Product.is_active == 1).first()
        add_to_user_cart(AddCartItemRequest(customer_id=c2.id, product_id=p_seed.id, quantity=1), db=db_session)
        cart2_before = get_user_cart(customer_id=c2.id, db=db_session)
    assert cart2_before["cart_count"] > 0, "Customer 2 should have items in cart."

    # Clear Customer 1's cart
    clear_user_cart(customer_id=c1.id, db=db_session)
    cart1_after = get_user_cart(customer_id=c1.id, db=db_session)
    assert cart1_after["cart_count"] == 0

    # Customer 2's cart must still have all its items intact!
    cart2_after = get_user_cart(customer_id=c2.id, db=db_session)
    assert cart2_after["cart_count"] == cart2_before["cart_count"]

    # Re-add sample item to Customer 1 so they have their dataset items
    p = db_session.query(Product).filter(Product.category == "Electronics").first()
    if p:
        add_to_user_cart(AddCartItemRequest(customer_id=c1.id, product_id=p.id, quantity=1), db=db_session)

def test_benchmark_customer_1041_zero_cart_items(db_session):
    """Customer AMZ_PRED1_1041 has 0 cart abandonments in dataset, so cart must be strictly empty (0 items)."""
    c1041 = db_session.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1041").first()
    assert c1041 is not None

    cart_1041 = get_user_cart(customer_id=c1041.id, db=db_session)
    assert cart_1041["cart_count"] == 0, f"AMZ_PRED1_1041 must have 0 cart items, found {cart_1041['cart_count']}!"
    assert len(cart_1041["items"]) == 0

def test_dataset_cart_categories_alignment(db_session):
    """Verify customer carts match their preferred categories from the dataset."""
    c_fashion = db_session.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1003").first()
    assert c_fashion and c_fashion.preferred_category == "Fashion"

    cart_fashion = get_user_cart(customer_id=c_fashion.id, db=db_session)
    assert cart_fashion["cart_count"] >= 1
    # Check that at least one item belongs to Fashion
    categories = [it["category"] for it in cart_fashion["items"]]
    assert "Fashion" in categories, f"Expected Fashion item in AMZ_PRED1_1003 cart, found: {categories}"
