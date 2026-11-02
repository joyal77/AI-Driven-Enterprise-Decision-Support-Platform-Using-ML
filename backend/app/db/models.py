import os
import sys
from sqlalchemy import Column, Integer, String, Float, Date, TIMESTAMP, Text, ForeignKey, text, UniqueConstraint
from sqlalchemy.orm import relationship
from .session import Base

# =========================
# Users Table
# =========================
class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="admin")
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


# =========================
# Customers Table (E-Commerce Customer Metrics)
# =========================
class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_customer_id = Column(String(50), unique=True, index=True, nullable=False)
    signup_date = Column(Date, nullable=True)
    customer_age = Column(Float, nullable=True)
    gender = Column(String(50), nullable=True)
    city_tier = Column(String(50), nullable=True, index=True)
    membership_status = Column(String(50), nullable=True, index=True)
    days_since_last_purchase = Column(Float, nullable=True, index=True)
    total_orders_lifetime = Column(Integer, nullable=True)
    orders_last_30d = Column(Integer, nullable=True)
    orders_prev_30_to_60d = Column(Float, nullable=True)
    total_spend_inr = Column(String(100), nullable=True)
    avg_order_value = Column(Float, nullable=True)
    preferred_category = Column(String(100), nullable=True, index=True)
    sessions_last_30d = Column(Integer, nullable=True)
    avg_session_duration_min = Column(Float, nullable=True)
    cart_abandonments_last_30d = Column(Integer, nullable=True)
    search_queries_last_30d = Column(Float, nullable=True)
    return_count = Column(Integer, nullable=True)
    return_rate = Column(Float, nullable=True)
    cancellations_count = Column(Integer, nullable=True)
    late_deliveries_count = Column(Integer, nullable=True)
    customer_service_tickets = Column(Integer, nullable=True)
    avg_rating_given = Column(Float, nullable=True)
    preferred_payment_mode = Column(String(50), nullable=True)
    ground_truth_churn = Column(Integer, nullable=True, index=True) # Dataset churn_label (0 or 1)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # Relationships
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    predictions = relationship("ChurnPrediction", back_populates="customer", cascade="all, delete-orphan")
    recommendations = relationship("RetentionRecommendation", back_populates="customer", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="customer", cascade="all, delete-orphan")


# =========================
# Store Users Table (Multi-Role Authentication: Customer, PM, Admin)
# =========================
class StoreUser(Base):
    __tablename__ = "store_users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True) # customer_id (e.g. AMZ_PRED3_1001) or email
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, index=True) # "customer", "product_manager", "admin"
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    full_name = Column(String(150), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    customer = relationship("Customer", backref="store_account")


# =========================
# Orders Table
# =========================
class Order(Base):
    __tablename__ = "orders"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(50), unique=True, index=True, nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    order_date = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    order_amount = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=True)
    tax_amount = Column(Float, default=0.0)
    shipping_amount = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    payment_mode = Column(String(50), default="UPI")
    order_status = Column(String(50), default="Confirmed", index=True)
    shipping_address = Column(Text, nullable=True)
    return_status = Column(String(50), default="None")
    voucher_code = Column(String(50), nullable=True)
    wallet_credit_used = Column(Float, default=0.0)
    free_shipping_applied = Column(Integer, default=0)

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


# =========================
# Products Table (Amazon-Style Catalog & Inventory)
# =========================
class Product(Base):
    __tablename__ = "products"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String(50), unique=True, index=True, nullable=True)
    title = Column(String(200), nullable=False, index=True)
    product_name = Column(String(200), nullable=True) # legacy fallback
    category = Column(String(100), nullable=False, index=True)
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    stock_quantity = Column(Integer, default=100)
    rating = Column(Float, default=4.5)
    rating_count = Column(Integer, default=120)
    image_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    is_prime = Column(Integer, default=1)
    is_active = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    order_items = relationship("OrderItem", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")


# =========================
# Order Items Table
# =========================
class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


# =========================
# Cart Items Table (Isolated Per-Customer Shopping Cart)
# =========================
class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    customer = relationship("Customer", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")


# =========================
# Churn Predictions Table
# =========================
class ChurnPrediction(Base):
    __tablename__ = "churn_predictions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    churn_probability = Column(Float, nullable=False)
    churn_prediction = Column(Integer, nullable=False) # 0 or 1
    risk_category = Column(String(50), nullable=False, index=True) # High Risk, Medium Risk, Low Risk
    model_version = Column(String(50), default="Random Forest v1.0")
    prediction_timestamp = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    shap_explanation = Column(Text, nullable=True)
    root_causes = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)

    customer = relationship("Customer", back_populates="predictions")


# =========================
# Retention Recommendations Table
# =========================
class RetentionRecommendation(Base):
    __tablename__ = "retention_recommendations"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    recommendation_type = Column(String(100), nullable=False)
    recommendation_description = Column(Text, nullable=False)
    status = Column(String(50), default="Pending", index=True) # Pending, Approved, Completed, Dismissed
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    customer = relationship("Customer", back_populates="recommendations")


# =========================
# Prediction Batches Table
# =========================
class PredictionBatch(Base):
    __tablename__ = "prediction_batches"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_status = Column(String(50), default="Completed", index=True)
    total_customers = Column(Integer, default=0)
    processed_customers = Column(Integer, default=0)
    failed_customers = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    completed_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


# =========================
# Data Integrity Audit Log Table
# =========================
class DataIntegrityAuditLog(Base):
    __tablename__ = "data_integrity_audit_log"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    check_type = Column(String(100), nullable=False, index=True)
    customer_id = Column(String(50), nullable=True, index=True)
    severity = Column(String(20), default="INFO", index=True) # "CRITICAL", "WARNING", "INFO"
    expected_value = Column(Text, nullable=True)
    observed_value = Column(Text, nullable=True)
    resolution_status = Column(String(50), default="Reconciled", index=True) # "Reconciled", "Flagged"
    details = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


# =========================
# Customer Retention Perks & Countermeasures Table
# =========================
class CustomerRetentionPerk(Base):
    __tablename__ = "customer_retention_perks"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    campaign_id = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    perk_type = Column(String(50), nullable=False) # 'wallet_credit', 'discount_voucher', 'express_shipping', 'prime_trial', 'vip_support'
    perk_value = Column(Float, default=0.0)
    coupon_code = Column(String(50), nullable=True)
    free_shipping = Column(Integer, default=0) # 1 if free shipping / express delivery included
    status = Column(String(50), default="Approved", index=True) # 'Approved', 'Accepted', 'Used', 'Completed', 'Rejected'
    coupon_used = Column(Integer, default=0) # 1 if coupon code was used
    shipping_used = Column(Integer, default=0) # 1 if free shipping / express delivery was consumed
    used_order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    used_at = Column(TIMESTAMP, nullable=True)
    is_single_use = Column(Integer, default=1) # 1 = single use, 0 = reusable
    action_summary = Column(Text, nullable=True)
    root_cause_driver = Column(String(255), nullable=True)
    channel = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    customer = relationship("Customer", backref="retention_perks")


# =========================
# Customer Account Notifications Table (Storefront Inbox)
# =========================
class CustomerNotification(Base):
    __tablename__ = "customer_notifications"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    campaign_id = Column(String(100), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    notification_type = Column(String(50), default="retention_perk") # 'retention_perk', 'voucher', 'shipping', 'concierge', 'system'
    navigation_target = Column(String(255), nullable=True, default="/store/cart") # target URL / route in storefront
    channel = Column(String(100), default="Storefront Notification")
    sender = Column(String(150), default="SmartCart Concierge")
    coupon_code = Column(String(50), nullable=True)
    perk_type = Column(String(50), nullable=True)
    perk_value = Column(Float, default=0.0)
    is_read = Column(Integer, default=0) # 0 = unread, 1 = read
    dispatch_status = Column(String(50), default="Delivered") # "Delivered", "Sent"
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    customer = relationship("Customer", backref="account_notifications")


# =========================
# Customer Retention Perk Redemptions (Audit & Lifecycle Enforcement)
# =========================
class CustomerPerkRedemption(Base):
    __tablename__ = "customer_perk_redemptions"
    __table_args__ = (
        UniqueConstraint('customer_id', 'coupon_code', 'benefit_type', name='uq_cust_coupon_benefit_redemption'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    order_number = Column(String(50), nullable=False, index=True)
    perk_id = Column(Integer, ForeignKey("customer_retention_perks.id"), nullable=True)
    campaign_id = Column(String(100), nullable=True, index=True)
    benefit_type = Column(String(50), nullable=False) # 'discount_coupon', 'free_shipping', 'wallet_credit'
    coupon_code = Column(String(50), nullable=True, index=True)
    discount_amount = Column(Float, default=0.0)
    redemption_date = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    status = Column(String(50), default="Redeemed")

    customer = relationship("Customer", backref="perk_redemptions")
    order = relationship("Order", backref="perk_redemptions")
    perk = relationship("CustomerRetentionPerk", backref="redemptions")



