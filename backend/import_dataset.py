"""
import_dataset.py

Idempotently imports raw_ecommerce_churn_10k.csv dataset into MySQL/SQLite database.
Prevents duplicate row imports by tracking source_customer_id.
Stores ground_truth_churn (dataset churn_label).
"""

import os
import sys
import datetime
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine, Base, SessionLocal
from app.db.models import Customer, Order, Product, User

def parse_date(d_str):
    if pd.isna(d_str) or not d_str:
        return None
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y.%m.%d'):
        try:
            return datetime.datetime.strptime(str(d_str).strip(), fmt).date()
        except ValueError:
            pass
    return None

def import_data():
    # 1. Create all database tables
    print("Creating database tables if not exist...")
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    # Create default admin user if not existing
    admin_user = db.query(User).filter(User.email == "admin@ecommerce.com").first()
    if not admin_user:
        db.add(User(
            name="Platform Administrator",
            email="admin@ecommerce.com",
            password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", # hashed 'admin123'
            role="admin"
        ))
        db.commit()

    # 2. Find dataset CSV file
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'dataset', 'raw_ecommerce_churn_10k.csv'))
    if not os.path.exists(dataset_path):
        dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'raw_ecommerce_churn_10k.csv'))

    print(f"Reading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)

    # Track existing source customer IDs in database for idempotency
    existing_ids = set(r[0] for r in db.query(Customer.source_customer_id).all())
    print(f"Found {len(existing_ids)} existing customers in database.")

    new_customers = []
    imported_count = 0
    duplicate_count = 0

    for idx, row in df.iterrows():
        cust_id_str = str(row['customer_id']).strip()
        
        # Idempotent check: skip if customer source ID already imported
        if cust_id_str in existing_ids:
            duplicate_count += 1
            continue

        existing_ids.add(cust_id_str)
        
        # Helper conversions
        age_val = float(row['customer_age']) if pd.notna(row['customer_age']) else None
        city_tier_val = str(row['city_tier']) if pd.notna(row['city_tier']) else None
        mem_status_val = str(row['membership_status']) if pd.notna(row['membership_status']) else None
        gender_val = str(row['gender']) if pd.notna(row['gender']) else None
        cat_val = str(row['preferred_category']) if pd.notna(row['preferred_category']) else None
        pay_val = str(row['preferred_payment_mode']) if pd.notna(row['preferred_payment_mode']) else None
        
        days_last_p = float(row['days_since_last_purchase']) if pd.notna(row['days_since_last_purchase']) else None
        tot_orders = int(row['total_orders_lifetime']) if pd.notna(row['total_orders_lifetime']) else 1
        orders_30d = int(row['orders_last_30d']) if pd.notna(row['orders_last_30d']) else 0
        orders_prev = float(row['orders_prev_30_to_60d']) if pd.notna(row['orders_prev_30_to_60d']) else None
        spend_str = str(row['total_spend_inr']) if pd.notna(row['total_spend_inr']) else ""
        aov = float(row['avg_order_value']) if pd.notna(row['avg_order_value']) else None
        sessions = int(row['sessions_last_30d']) if pd.notna(row['sessions_last_30d']) else 0
        sess_dur = float(row['avg_session_duration_min']) if pd.notna(row['avg_session_duration_min']) else None
        cart_ab = int(row['cart_abandonments_last_30d']) if pd.notna(row['cart_abandonments_last_30d']) else 0
        queries = float(row['search_queries_last_30d']) if pd.notna(row['search_queries_last_30d']) else None
        ret_cnt = int(row['return_count']) if pd.notna(row['return_count']) else 0
        ret_rate = float(row['return_rate']) if pd.notna(row['return_rate']) else None
        cancels = int(row['cancellations_count']) if pd.notna(row['cancellations_count']) else 0
        late_del = int(row['late_deliveries_count']) if pd.notna(row['late_deliveries_count']) else 0
        tickets = int(row['customer_service_tickets']) if pd.notna(row['customer_service_tickets']) else 0
        rating = float(row['avg_rating_given']) if pd.notna(row['avg_rating_given']) else None
        gt_churn = int(row['churn_label']) if pd.notna(row['churn_label']) else None

        c_obj = Customer(
            source_customer_id=cust_id_str,
            signup_date=parse_date(row['signup_date']),
            customer_age=age_val,
            gender=gender_val,
            city_tier=city_tier_val,
            membership_status=mem_status_val,
            days_since_last_purchase=days_last_p,
            total_orders_lifetime=tot_orders,
            orders_last_30d=orders_30d,
            orders_prev_30_to_60d=orders_prev,
            total_spend_inr=spend_str,
            avg_order_value=aov,
            preferred_category=cat_val,
            sessions_last_30d=sessions,
            avg_session_duration_min=sess_dur,
            cart_abandonments_last_30d=cart_ab,
            search_queries_last_30d=queries,
            return_count=ret_cnt,
            return_rate=ret_rate,
            cancellations_count=cancels,
            late_deliveries_count=late_del,
            customer_service_tickets=tickets,
            avg_rating_given=rating,
            preferred_payment_mode=pay_val,
            ground_truth_churn=gt_churn
        )
        new_customers.append(c_obj)
        imported_count += 1

        if len(new_customers) >= 1000:
            db.bulk_save_objects(new_customers)
            db.commit()
            new_customers = []

    if new_customers:
        db.bulk_save_objects(new_customers)
        db.commit()

    db.close()
    print(f"\n[Import Summary] Successfully imported {imported_count} new customer records. Skipped {duplicate_count} duplicate IDs.")

if __name__ == '__main__':
    import_data()
