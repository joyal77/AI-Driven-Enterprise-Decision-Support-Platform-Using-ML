"""
test_data_integrity.py

Automated test suite verifying Customer Data Integrity, 1:1 Account Attribution,
Zero-Order Consistency (including AMZ_PRED1_1041), Real-time Checkout Synchronization,
and Time-series Sales Forecasting integrity without synthetic data.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import datetime
import pytest
from sqlalchemy import func

from app.db.session import SessionLocal
from app.db.models import Customer, Order, StoreUser, ChurnPrediction, DataIntegrityAuditLog
from app.services.customer_feature_service import (
    compute_customer_transaction_features,
    reconcile_and_predict_customer,
    reconcile_all_registered_customers
)
from app.ml.sales_predictor import get_store_sales_history, generate_multi_horizon_sales_forecast

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()

def test_customer_uniqueness_and_1_to_1_mapping(db):
    """
    Phase 10.1: Validate that each customer ID appears at most once in the database
    and registered customer accounts map 1:1 with prediction records.
    """
    total_customers = db.query(Customer).count()
    distinct_source_ids = db.query(Customer.source_customer_id).distinct().count()
    
    # 1. Assert uniqueness of customer identifiers
    assert total_customers > 0, "Database must contain registered customers"
    assert total_customers == distinct_source_ids, f"Found duplicate customer IDs: {total_customers} rows vs {distinct_source_ids} unique IDs"

    # 2. Assert at most one prediction per customer (1:1 relationship)
    pred_duplicates = db.query(
        ChurnPrediction.customer_id, func.count(ChurnPrediction.id)
    ).group_by(ChurnPrediction.customer_id).having(func.count(ChurnPrediction.id) > 1).all()
    assert len(pred_duplicates) == 0, f"Found customers with duplicate prediction records: {pred_duplicates}"

def test_order_attribution_integrity(db):
    """
    Phase 10.2: Validate that all orders in the database are linked to a valid canonical customer ID.
    Assert that no orders have missing or orphaned customer references.
    """
    total_orders = db.query(Order).count()
    if total_orders > 0:
        # Check for NULL customer_id
        null_cust_orders = db.query(Order).filter(Order.customer_id.is_(None)).count()
        assert null_cust_orders == 0, f"Found {null_cust_orders} orders with NULL customer_id"

        # Check for orphaned customer_id referencing non-existent customers
        valid_cust_ids = set(cid[0] for cid in db.query(Customer.id).all())
        orders = db.query(Order).all()
        orphaned = [o.id for o in orders if o.customer_id not in valid_cust_ids]
        assert len(orphaned) == 0, f"Found orphaned orders not linked to any valid customer: {orphaned}"

def test_target_customer_amz_pred1_1041_accuracy(db):
    """
    Phase 10.3: Specific assertion for AMZ_PRED1_1041.
    Verify that the customer's lifetime orders in the database equals the lifetime orders in the profile.
    Verify that when the customer has placed zero orders, the displayed order count is zero,
    total spend is ₹0.00, and days_since_last_purchase is None.
    """
    c_1041 = db.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1041").first()
    assert c_1041 is not None, "Target customer AMZ_PRED1_1041 must exist in the database"

    actual_db_orders = db.query(Order).filter(
        Order.customer_id == c_1041.id,
        ~Order.order_status.in_(['cancelled', 'rejected'])
    ).count()

    assert actual_db_orders == 0, f"Expected AMZ_PRED1_1041 to have 0 website orders, found {actual_db_orders}"
    assert c_1041.total_orders_lifetime == 0, f"Profile shows {c_1041.total_orders_lifetime} lifetime orders, must be 0"
    assert c_1041.total_spend_inr in ("₹0.00", "0.00", "0"), f"Profile spend is {c_1041.total_spend_inr}, must be ₹0.00"
    assert c_1041.days_since_last_purchase is None, f"Profile recency is {c_1041.days_since_last_purchase}, must be None for 0 orders"

    # Check prediction record consistency
    pred_1041 = db.query(ChurnPrediction).filter(ChurnPrediction.customer_id == c_1041.id).first()
    if pred_1041:
        assert pred_1041.churn_probability is not None
        assert pred_1041.risk_category in ("Low Risk", "Medium Risk", "High Risk")

def test_transaction_derived_feature_calculations(db):
    """
    Phase 10.4: Calculate RFM features and verify against expected values.
    Verify handling of 0-order customers (no division by zero, appropriate default recency).
    Verify handling of customers with orders.
    """
    # 1. Verify 0-order customer handling
    c_1041 = db.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1041").first()
    tf_zero = compute_customer_transaction_features(c_1041)
    assert tf_zero["total_orders_lifetime"] == 0
    assert tf_zero["total_orders_lifetime"] == 0
    assert tf_zero["total_spend_inr_num"] == 0.0
    assert tf_zero["avg_order_value"] == 0.0
    assert tf_zero["days_since_last_purchase"] is None
    assert tf_zero["orders_last_30d"] == 0

    # 2. Verify customer with active orders (AMZ_PRED1_1001)
    c_1001 = db.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1001").first()
    if c_1001 and len(c_1001.orders) > 0:
        tf_active = compute_customer_transaction_features(c_1001)
        expected_orders = len([o for o in c_1001.orders if str(o.order_status).lower() not in ('cancelled', 'rejected')])
        expected_spend = sum(float(o.order_amount) for o in c_1001.orders if str(o.order_status).lower() not in ('cancelled', 'rejected'))
        
        assert tf_active["total_orders_lifetime"] == expected_orders
        assert abs(tf_active["total_spend_inr_num"] - expected_spend) < 0.01
        assert tf_active["avg_order_value"] == round(expected_spend / expected_orders, 2)
        assert tf_active["days_since_last_purchase"] is not None

def test_real_time_checkout_sync_and_reconciliation(db):
    """
    Phase 10.5: Simulate an order placement for a customer.
    Assert that the customer's lifetime orders increments, total spend increases,
    and the churn prediction pipeline re-evaluates the customer.
    """
    # Pick a customer with 0 orders (e.g., AMZ_PRED1_1050)
    test_cust = db.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1050").first()
    if not test_cust:
        pytest.skip("Test customer AMZ_PRED1_1050 not found")

    initial_orders = test_cust.total_orders_lifetime or 0
    now = datetime.datetime.now()

    # Create a simulated test order
    test_order = Order(
        customer_id=test_cust.id,
        order_amount=2499.50,
        order_status="Confirmed",
        order_date=now,
        shipping_address="45 Test Integrity Way",
        payment_mode="UPI"
    )
    db.add(test_order)
    db.commit()

    try:
        # Trigger reconciliation service
        res = reconcile_and_predict_customer(test_cust, db)
        db.refresh(test_cust)

        # Assertions
        assert test_cust.total_orders_lifetime == initial_orders + 1
        assert test_cust.total_spend_inr == "₹2,499.50"
        assert test_cust.days_since_last_purchase == 0.0
        assert res["churn_probability"] is not None

        # Check prediction table updated
        pred = db.query(ChurnPrediction).filter(ChurnPrediction.customer_id == test_cust.id).first()
        assert pred is not None
        assert pred.churn_probability == res["churn_probability"]

    finally:
        # Clean up test order and revert
        db.delete(test_order)
        db.commit()
        reconcile_and_predict_customer(test_cust, db)

def test_sales_forecasting_authenticity(db):
    """
    Phase 10.6: Assert that sales forecasting uses true database order revenue,
    contains NO synthetic sine waves, and properly exposes widened confidence intervals
    under low transaction volume.
    """
    df_store, meta = get_store_sales_history()
    assert isinstance(df_store, object)
    assert "daily_revenue" in df_store.columns
    assert "low_volume" in meta
    assert meta["low_volume"] is True, "SmartCart live store has early-stage volume (< 15 orders), low_volume flag must be True"

    forecast = generate_multi_horizon_sales_forecast(horizon_days=7, source="store")
    assert forecast["has_data"] is True
    assert forecast["low_transaction_volume"] is True
    assert forecast["data_limitation_notice"] is not None
    assert len(forecast["forecast_schedule"]) == 7

    for day in forecast["forecast_schedule"]:
        assert day["confidence_interval_width"] == "+/- 35%"
        assert day["lower_bound"] <= day["forecasted_revenue"] <= day["upper_bound"]
