"""
test_order_distribution.py

Automated test suite verifying:
1. Zero-order integrity for benchmark customer AMZ_PRED1_1041.
2. Unique order history and distinct products for customer AMZ_PRED1_1001.
3. Multi-customer order distribution and unique order numbers across the platform.
4. Backend idempotency and duplicate submission prevention within the 60-second window.
5. RFM feature calculation and churn prediction synchronization.
"""

import sys
import os
import pytest
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.db.session import SessionLocal
from app.db.models import Customer, Product, Order, OrderItem, ChurnPrediction
from app.services.customer_feature_service import compute_customer_transaction_features
from app.api.store_orders import place_store_order, PlaceOrderRequest, OrderItemInput

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_benchmark_customer_1041_zero_orders(db_session):
    """Verify that benchmark customer AMZ_PRED1_1041 remains strictly at 0 orders and ₹0.00 spend."""
    c1041 = db_session.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1041").first()
    assert c1041 is not None, "Customer AMZ_PRED1_1041 must exist in the database."
    
    order_count = db_session.query(Order).filter(Order.customer_id == c1041.id).count()
    assert order_count == 0, f"Expected 0 orders in database for AMZ_PRED1_1041, found {order_count}."
    assert c1041.total_orders_lifetime == 0, f"Expected total_orders_lifetime=0, got {c1041.total_orders_lifetime}."
    assert c1041.days_since_last_purchase is None, f"Expected days_since_last_purchase=None, got {c1041.days_since_last_purchase}."
    assert "0" in str(c1041.total_spend_inr), f"Expected 0 spend, got {c1041.total_spend_inr}."

def test_customer_1001_orders_are_unique(db_session):
    """Verify customer AMZ_PRED1_1001 has unique orders with distinct products and amounts."""
    c1001 = db_session.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1001").first()
    assert c1001 is not None, "Customer AMZ_PRED1_1001 must exist."
    
    orders = db_session.query(Order).filter(Order.customer_id == c1001.id).all()
    assert len(orders) >= 2, f"Expected at least 2 orders for AMZ_PRED1_1001, found {len(orders)}."
    
    # Check that product sets in each order are distinct
    order_product_sets = []
    order_amounts = []
    for o in orders:
        prod_ids = tuple(sorted([it.product_id for it in o.items]))
        order_product_sets.append(prod_ids)
        order_amounts.append(o.order_amount)
    
    # Verify no two orders have the identical product set and identical total amount
    assert len(set(order_product_sets)) == len(orders), f"Duplicate product sets detected in AMZ_PRED1_1001 orders: {order_product_sets}"
    assert len(set(order_amounts)) == len(orders), f"Duplicate order amounts detected in AMZ_PRED1_1001 orders: {order_amounts}"

def test_platform_order_numbers_are_globally_unique(db_session):
    """Verify that all order numbers across the entire platform are unique."""
    all_orders = db_session.query(Order).all()
    order_numbers = [o.order_number for o in all_orders if o.order_number]
    assert len(order_numbers) == len(set(order_numbers)), "Detected duplicate order numbers in orders table!"

def test_multi_customer_order_distribution(db_session):
    """Verify that orders are distributed across multiple distinct customer accounts."""
    customer_ids_with_orders = db_session.query(Order.customer_id).distinct().all()
    unique_customer_count = len(customer_ids_with_orders)
    assert unique_customer_count >= 30, f"Expected orders distributed across >= 30 customers, found {unique_customer_count}."

def test_backend_idempotency_prevents_duplicate_orders(db_session):
    """Verify that placing an identical order within 60s is deduplicated and returns the existing order."""
    # Find a test customer (e.g. AMZ_PRED1_1002)
    test_cust = db_session.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1002").first()
    test_prod = db_session.query(Product).filter(Product.stock_quantity > 10).first()
    assert test_cust is not None and test_prod is not None
    
    payload = PlaceOrderRequest(
        customer_id=test_cust.id,
        items=[OrderItemInput(product_id=test_prod.id, quantity=1)],
        shipping_address="Test Idempotency Address, Test City 123456",
        payment_mode="UPI"
    )
    
    initial_order_count = db_session.query(Order).filter(Order.customer_id == test_cust.id).count()
    
    # 1st Submission
    res1 = place_store_order(payload, db_session)
    assert res1["success"] is True
    order_id_1 = res1["order"]["order_id"]
    
    # 2nd Immediate Submission (Duplicate request within 60s)
    res2 = place_store_order(payload, db_session)
    assert res2["success"] is True
    assert res2.get("is_duplicate_suppressed") is True
    assert res2["order"]["order_id"] == order_id_1
    
    # Verify database order count increased by exactly 1, not 2
    final_order_count = db_session.query(Order).filter(Order.customer_id == test_cust.id).count()
    assert final_order_count == initial_order_count + 1

    # Cleanup test order
    test_order = db_session.query(Order).filter(Order.id == order_id_1).first()
    if test_order:
        test_prod.stock_quantity += 1
        db_session.delete(test_order)
        db_session.commit()

def test_rfm_and_churn_sync_consistency(db_session):
    """Verify that compute_customer_transaction_features accurately derives metrics from orders."""
    c1001 = db_session.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1001").first()
    tf = compute_customer_transaction_features(c1001)
    
    db_orders = db_session.query(Order).filter(
        Order.customer_id == c1001.id,
        Order.order_status != "Cancelled"
    ).all()
    
    expected_orders = len(db_orders)
    expected_spend = sum(o.order_amount for o in db_orders)
    
    assert tf["total_orders_lifetime"] == expected_orders
    assert abs(tf["total_spend_inr_num"] - expected_spend) < 0.05
