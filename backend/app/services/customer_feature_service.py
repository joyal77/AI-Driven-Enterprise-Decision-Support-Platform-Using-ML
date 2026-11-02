"""
customer_feature_service.py

Centralized Customer Feature & Reconciliation Service.
Establishes the website's Order table as the single authoritative source of truth
for customer purchase history, RFM features, and ML churn predictions.
"""

import os
import json
import datetime
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from ..db.models import Customer, Order, ChurnPrediction, RetentionRecommendation, DataIntegrityAuditLog, PredictionBatch
from ..ml.model_loader import get_ml_artifacts
from ..ml.decision_engine import generate_recommendation, extract_root_causes

# Reference date for days_since_signup expected by the trained Random Forest model
REFERENCE_DATE = datetime.date(2026, 1, 1)

def parse_date_safe(d_val, default_date: datetime.date = None) -> Optional[datetime.date]:
    if not d_val:
        return default_date
    if isinstance(d_val, datetime.date):
        return d_val
    if isinstance(d_val, datetime.datetime):
        return d_val.date()
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y.%m.%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S'):
        try:
            return datetime.datetime.strptime(str(d_val).split('.')[0].strip(), fmt).date()
        except ValueError:
            pass
    return default_date

def clean_spend_to_numeric(val: Any) -> float:
    if pd.isna(val) or val is None or val == '':
        return 0.0
    val_str = str(val).replace('₹', '').replace('INR', '').replace(',', '').strip()
    try:
        f = float(val_str)
        return 0.0 if np.isnan(f) or np.isinf(f) else max(0.0, f)
    except ValueError:
        return 0.0

def compute_customer_transaction_features(customer: Customer, now: datetime.datetime = None) -> Dict[str, Any]:
    """
    Derives customer purchase and behavioral metrics strictly from actual orders in the database.
    Does NOT use hardcoded numbers or blindly copy CSV snapshot fields.
    """
    if now is None:
        now = datetime.datetime.now()

    # 1. Fetch related orders
    orders: List[Order] = customer.orders if customer and customer.orders else []

    # 2. Filter qualifying, cancelled, and returned orders
    # Cancelled orders do NOT count as completed purchases
    qualifying_orders = [
        o for o in orders 
        if str(o.order_status or '').strip().lower() not in ('cancelled', 'rejected')
    ]
    cancelled_orders = [
        o for o in orders 
        if str(o.order_status or '').strip().lower() == 'cancelled'
    ]
    returned_orders = [
        o for o in qualifying_orders 
        if str(o.return_status or '').strip().lower() in ('returned', 'return_requested', 'refunded')
    ]

    total_orders_lifetime = len(qualifying_orders)
    total_spend_num = sum(float(o.order_amount or 0.0) for o in qualifying_orders)
    avg_order_value = round(total_spend_num / total_orders_lifetime, 2) if total_orders_lifetime > 0 else 0.0

    # 3. Recency and purchase windows
    days_since_last_purchase = None
    orders_last_30d = 0
    orders_prev_30_to_60d = 0.0

    if total_orders_lifetime > 0:
        # Sort by order_date descending to find the latest
        qualifying_dates = []
        for o in qualifying_orders:
            d = o.order_date if isinstance(o.order_date, datetime.datetime) else parse_date_safe(o.order_date)
            if d:
                dt_obj = d if isinstance(d, datetime.datetime) else datetime.datetime.combine(d, datetime.time.min)
                qualifying_dates.append(dt_obj)

        if qualifying_dates:
            latest_order_dt = max(qualifying_dates)
            days_since_last_purchase = max(0.0, float((now.date() - latest_order_dt.date()).days))
            orders_last_30d = sum(1 for dt in qualifying_dates if (now - dt).total_seconds() <= 30 * 86400)
            orders_prev_30_to_60d = float(sum(1 for dt in qualifying_dates if 30 * 86400 < (now - dt).total_seconds() <= 60 * 86400))

    # If the customer logged in / engaged with the storefront today (days_since_last_purchase == 0.0),
    # preserve their active status as 0.0 days inactive
    if customer and customer.days_since_last_purchase == 0.0 and total_orders_lifetime > 0:
        days_since_last_purchase = 0.0

    return_count = len(returned_orders)
    return_rate = round(float(return_count) / total_orders_lifetime, 4) if total_orders_lifetime > 0 else 0.0
    cancellations_count = len(cancelled_orders)

    # 4. Payment mode: Use actual storefront payment mode if orders exist, else fallback to profile preference
    preferred_payment = customer.preferred_payment_mode or "UPI"
    if qualifying_orders:
        modes = [o.payment_mode for o in qualifying_orders if o.payment_mode]
        if modes:
            preferred_payment = max(set(modes), key=modes.count)

    # 5. Days since signup
    signup_d = parse_date_safe(customer.signup_date, REFERENCE_DATE)
    days_since_signup = max(0, (REFERENCE_DATE - signup_d).days) if signup_d else 365

    return {
        "total_orders_lifetime": total_orders_lifetime,
        "total_spend_inr_num": total_spend_num,
        "total_spend_num": total_spend_num,
        "total_spend_inr_display": f"₹{total_spend_num:,.2f}",
        "avg_order_value": avg_order_value,
        "days_since_last_purchase": days_since_last_purchase,
        "orders_last_30d": orders_last_30d,
        "orders_prev_30_to_60d": orders_prev_30_to_60d,
        "return_count": return_count,
        "return_rate": return_rate,
        "cancellations_count": cancellations_count,
        "preferred_payment_mode": preferred_payment,
        "days_since_signup": days_since_signup,
        # Engagement & demographic features preserved from profile
        "customer_age": customer.customer_age or 35.0,
        "gender": customer.gender or "Female",
        "city_tier": customer.city_tier or "Tier 1",
        "membership_status": customer.membership_status or "Standard",
        "preferred_category": customer.preferred_category or "General",
        "sessions_last_30d": customer.sessions_last_30d or 0,
        "avg_session_duration_min": customer.avg_session_duration_min or 0.0,
        "cart_abandonments_last_30d": customer.cart_abandonments_last_30d or 0,
        "search_queries_last_30d": customer.search_queries_last_30d or 0.0,
        "late_deliveries_count": customer.late_deliveries_count or 0,
        "customer_service_tickets": customer.customer_service_tickets or 0,
        "avg_rating_given": customer.avg_rating_given or 4.0
    }

def build_raw_feature_dataframe(features_dict: Dict[str, Any], raw_features: List[str]) -> pd.DataFrame:
    """
    Builds the 1-row DataFrame matching the exact schema and ordering of raw_features_list.json.
    """
    # If days_since_last_purchase is None (0 orders placed), pass np.nan so the trained SimpleImputer
    # cleanly applies median imputation as approved during model training.
    days_last_p = features_dict.get("days_since_last_purchase")
    days_last_p_val = np.nan if days_last_p is None else float(days_last_p)

    row = {
        'customer_age': float(features_dict.get('customer_age', 35.0)),
        'gender': str(features_dict.get('gender', 'Female')),
        'city_tier': str(features_dict.get('city_tier', 'Tier 1')),
        'membership_status': str(features_dict.get('membership_status', 'Standard')),
        'days_since_last_purchase': days_last_p_val,
        'total_orders_lifetime': int(features_dict.get('total_orders_lifetime', 0)),
        'orders_last_30d': int(features_dict.get('orders_last_30d', 0)),
        'orders_prev_30_to_60d': float(features_dict.get('orders_prev_30_to_60d', 0.0)),
        'total_spend_inr': float(features_dict.get('total_spend_inr_num', 0.0)),
        'avg_order_value': float(features_dict.get('avg_order_value', 0.0)),
        'preferred_category': str(features_dict.get('preferred_category', 'General')),
        'sessions_last_30d': int(features_dict.get('sessions_last_30d', 0)),
        'avg_session_duration_min': float(features_dict.get('avg_session_duration_min', 0.0)),
        'cart_abandonments_last_30d': int(features_dict.get('cart_abandonments_last_30d', 0)),
        'search_queries_last_30d': float(features_dict.get('search_queries_last_30d', 0.0)),
        'return_count': int(features_dict.get('return_count', 0)),
        'return_rate': float(features_dict.get('return_rate', 0.0)),
        'cancellations_count': int(features_dict.get('cancellations_count', 0)),
        'late_deliveries_count': int(features_dict.get('late_deliveries_count', 0)),
        'customer_service_tickets': int(features_dict.get('customer_service_tickets', 0)),
        'avg_rating_given': float(features_dict.get('avg_rating_given', 4.0)),
        'preferred_payment_mode': str(features_dict.get('preferred_payment_mode', 'UPI')),
        'days_since_signup': int(features_dict.get('days_since_signup', 365))
    }

    df = pd.DataFrame([row])
    if raw_features:
        for c in raw_features:
            if c not in df.columns:
                df[c] = np.nan
        df = df[raw_features]
    return df

def reconcile_and_predict_customer(customer_id_or_obj: Any, db: Session, log_discrepancy: bool = True) -> Dict[str, Any]:
    """
    Central reconciliation and prediction function for a single customer.
    1. Computes transaction features directly from the Order table.
    2. Logs discrepancies between legacy/CSV values and database truth.
    3. Persists reconciled metrics to the Customer record.
    4. Evaluates the Random Forest model and updates ChurnPrediction & RetentionRecommendation.
    """
    if isinstance(customer_id_or_obj, Customer):
        customer = customer_id_or_obj
    else:
        customer = db.query(Customer).filter(Customer.id == customer_id_or_obj).first()
        if not customer:
            customer = db.query(Customer).filter(Customer.source_customer_id == str(customer_id_or_obj)).first()

    if not customer:
        raise ValueError(f"Customer '{customer_id_or_obj}' not found in canonical customer records.")

    now = datetime.datetime.now()

    # Capture previous values for discrepancy audit
    prev_orders = customer.total_orders_lifetime
    prev_spend_str = customer.total_spend_inr
    prev_spend = clean_spend_to_numeric(prev_spend_str)
    prev_days_inactive = customer.days_since_last_purchase

    is_live_store = bool(customer.source_customer_id and customer.source_customer_id.startswith("AMZ_PRED1_"))

    if is_live_store:
        # 1. Compute authoritative transaction features from live Order table
        tf = compute_customer_transaction_features(customer, now=now)
        actual_orders = tf["total_orders_lifetime"]
        actual_spend = tf["total_spend_inr_num"]

        # 2. Check for mismatch and record audit log entry if needed
        if prev_orders is not None and prev_orders != actual_orders:
            if log_discrepancy:
                audit_entry = DataIntegrityAuditLog(
                    check_type="Customer-Order Reconciliation",
                    customer_id=customer.source_customer_id,
                    severity="WARNING" if prev_orders > actual_orders else "INFO",
                    expected_value=f"DB Verified Orders: {actual_orders}, Spend: ₹{actual_spend:,.2f}",
                    observed_value=f"Stale/CSV Orders: {prev_orders}, Spend: {prev_spend_str}",
                    resolution_status="Reconciled",
                    details=(
                        f"Customer {customer.source_customer_id} had {prev_orders} orders recorded in profile "
                        f"but {actual_orders} actual qualifying orders in the database. "
                        f"Metrics reconciled to live database orders."
                    ),
                    created_at=now
                )
                db.add(audit_entry)

        # 3. Synchronize canonical Customer record attributes with authoritative values
        customer.total_orders_lifetime = actual_orders
        customer.total_spend_inr = tf["total_spend_inr_display"]
        customer.avg_order_value = tf["avg_order_value"]
        customer.days_since_last_purchase = tf["days_since_last_purchase"]
        customer.orders_last_30d = tf["orders_last_30d"]
        customer.orders_prev_30_to_60d = tf["orders_prev_30_to_60d"]
        customer.return_count = tf["return_count"]
        customer.return_rate = tf["return_rate"]
        customer.cancellations_count = tf["cancellations_count"]
        customer.preferred_payment_mode = tf["preferred_payment_mode"]
        customer.updated_at = now
    else:
        # Uploaded dataset customer: features come from their uploaded profile record
        actual_orders = customer.total_orders_lifetime or 0
        signup_d = parse_date_safe(customer.signup_date, REFERENCE_DATE)
        days_since_signup = max(0, (REFERENCE_DATE - signup_d).days) if signup_d else 365
        num_spend = clean_spend_to_numeric(customer.total_spend_inr)
        tf = {
            "total_orders_lifetime": actual_orders,
            "total_spend_inr_num": num_spend,
            "total_spend_num": num_spend,
            "total_spend_inr_display": customer.total_spend_inr or f"₹{num_spend:,.2f}",
            "avg_order_value": customer.avg_order_value or (round(num_spend / actual_orders, 2) if actual_orders > 0 else 0.0),
            "days_since_last_purchase": customer.days_since_last_purchase,
            "orders_last_30d": customer.orders_last_30d or 0,
            "orders_prev_30_to_60d": customer.orders_prev_30_to_60d or 0.0,
            "return_count": customer.return_count or 0,
            "return_rate": customer.return_rate or 0.0,
            "cancellations_count": customer.cancellations_count or 0,
            "preferred_payment_mode": customer.preferred_payment_mode or "UPI",
            "days_since_signup": days_since_signup,
            "customer_age": customer.customer_age or 35.0,
            "gender": customer.gender or "Female",
            "city_tier": customer.city_tier or "Tier 1",
            "membership_status": customer.membership_status or "Standard",
            "preferred_category": customer.preferred_category or "General",
            "sessions_last_30d": customer.sessions_last_30d or 0,
            "avg_session_duration_min": customer.avg_session_duration_min or 0.0,
            "cart_abandonments_last_30d": customer.cart_abandonments_last_30d or 0,
            "search_queries_last_30d": customer.search_queries_last_30d or 0.0,
            "late_deliveries_count": customer.late_deliveries_count or 0,
            "customer_service_tickets": customer.customer_service_tickets or 0,
            "avg_rating_given": customer.avg_rating_given or 4.0
        }

    # 4. Generate prediction with existing Random Forest model
    rf_model, preprocessor, metadata, raw_features = get_ml_artifacts()
    prob_pct = None
    churn_class = None
    risk_cat = "Unanalyzed"
    recs = []
    root_causes_list = []

    if rf_model and preprocessor:
        raw_df = build_raw_feature_dataframe(tf, raw_features)
        X_trans = preprocessor.transform(raw_df)
        prob_raw = float(rf_model.predict_proba(X_trans)[0, 1])
        prob_pct = round(prob_raw * 100, 2)
        threshold = float(metadata.get("optimal_decision_threshold", 0.5))
        churn_class = 1 if prob_raw >= threshold else 0

        if prob_raw >= 0.70:
            risk_cat = "High Risk"
        elif prob_raw >= 0.30:
            risk_cat = "Medium Risk"
        else:
            risk_cat = "Low Risk"

        recs = generate_recommendation(risk_cat, prob_pct, customer)
        root_causes_list = extract_root_causes(customer, risk_cat)

        # 5. Atomic Upsert of ChurnPrediction (single row per customer)
        pred_entry = db.query(ChurnPrediction).filter(ChurnPrediction.customer_id == customer.id).first()
        if not pred_entry:
            pred_entry = ChurnPrediction(
                customer_id=customer.id,
                churn_probability=prob_pct,
                churn_prediction=churn_class,
                risk_category=risk_cat,
                model_version="Random Forest v1.0",
                prediction_timestamp=now,
                root_causes=json.dumps(root_causes_list),
                recommendations=json.dumps(recs)
            )
            db.add(pred_entry)
        else:
            pred_entry.churn_probability = prob_pct
            pred_entry.churn_prediction = churn_class
            pred_entry.risk_category = risk_cat
            pred_entry.model_version = "Random Forest v1.0"
            pred_entry.prediction_timestamp = now
            pred_entry.root_causes = json.dumps(root_causes_list)
            pred_entry.recommendations = json.dumps(recs)

        # 6. Update RetentionRecommendation table
        db.query(RetentionRecommendation).filter(RetentionRecommendation.customer_id == customer.id).delete()
        for rec_desc in recs:
            db.add(RetentionRecommendation(
                customer_id=customer.id,
                recommendation_type=risk_cat,
                recommendation_description=rec_desc,
                status="Pending",
                created_at=now
            ))

    db.commit()
    db.refresh(customer)

    return {
        "customer_id": customer.id,
        "source_customer_id": customer.source_customer_id,
        "total_orders_lifetime": actual_orders,
        "total_spend_inr": tf["total_spend_inr_display"],
        "avg_order_value": tf["avg_order_value"],
        "days_since_last_purchase": tf["days_since_last_purchase"],
        "churn_probability": prob_pct,
        "churn_prediction": churn_class,
        "risk_category": risk_cat,
        "recommendations": recs,
        "reconciled": True
    }

def reconcile_all_registered_customers(db: Session) -> Dict[str, Any]:
    """
    Scans every registered customer in the database, reconciles their behavior
    against the actual Order table, logs discrepancies, and generates fresh predictions.
    Safe and idempotent to rerun anytime.
    """
    customers = db.query(Customer).order_by(Customer.id.asc()).all()
    total_customers = len(customers)
    discrepancies_found = 0
    reconciled_count = 0

    high_risk = 0
    med_risk = 0
    low_risk = 0
    prob_sum = 0.0

    now_time = datetime.datetime.now()

    for c in customers:
        prev_orders = c.total_orders_lifetime
        res = reconcile_and_predict_customer(c, db, log_discrepancy=True)
        reconciled_count += 1
        
        if prev_orders is not None and prev_orders != res["total_orders_lifetime"]:
            discrepancies_found += 1

        prob = res.get("churn_probability")
        if prob is not None:
            prob_sum += prob
            cat = res.get("risk_category")
            if cat == "High Risk":
                high_risk += 1
            elif cat == "Medium Risk":
                med_risk += 1
            else:
                low_risk += 1

    # Record batch prediction tracking
    batch_record = PredictionBatch(
        batch_status="Completed",
        total_customers=total_customers,
        processed_customers=reconciled_count,
        failed_customers=0,
        completed_at=now_time
    )
    db.add(batch_record)
    db.commit()

    avg_prob = round(prob_sum / total_customers, 2) if total_customers > 0 else 0.0

    return {
        "success": True,
        "total_customers": total_customers,
        "reconciled_count": reconciled_count,
        "discrepancies_reconciled": discrepancies_found,
        "high_risk_customers": high_risk,
        "medium_risk_customers": med_risk,
        "low_risk_customers": low_risk,
        "average_churn_probability": avg_prob,
        "batch_id": batch_record.id,
        "message": f"Successfully reconciled and re-scored {reconciled_count} customers against website transactions."
    }

def ensure_live_store_customers_seeded(db: Session) -> int:
    """
    Guarantees the 150 SmartCart live store customer accounts exist, are correctly mapped
    to StoreUser accounts, and are fully scored with ML predictions and transaction metrics.
    """
    store_cust_count = db.query(Customer).filter(Customer.source_customer_id.like("AMZ_PRED1_%")).count()
    if store_cust_count >= 150:
        return store_cust_count

    print("[Seed Helper] Live store customers missing or incomplete. Restoring 150 live accounts...")
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    csv_path = os.path.join(root_dir, 'dataset', 'customer churn', 'prediction_batch_1.csv')
    if not os.path.exists(csv_path):
        print(f"[Seed Helper Warning] CSV not found at {csv_path}")
        return 0

    df = pd.read_csv(csv_path)
    existing_ids = set(r[0] for r in db.query(Customer.source_customer_id).all())

    cust_objs = []
    for idx, row in df.iterrows():
        expected_id = idx + 1
        cust_id_str = str(row['customer_id']).strip()
        if cust_id_str in existing_ids:
            continue

        c = Customer(
            id=expected_id,
            source_customer_id=cust_id_str,
            signup_date=parse_date_safe(row.get('signup_date')),
            customer_age=float(row['customer_age']) if ('customer_age' in row and pd.notna(row['customer_age'])) else None,
            gender=str(row['gender']) if ('gender' in row and pd.notna(row['gender'])) else None,
            city_tier=str(row['city_tier']) if ('city_tier' in row and pd.notna(row['city_tier'])) else None,
            membership_status=str(row['membership_status']) if ('membership_status' in row and pd.notna(row['membership_status'])) else None,
            days_since_last_purchase=float(row['days_since_last_purchase']) if ('days_since_last_purchase' in row and pd.notna(row['days_since_last_purchase'])) else None,
            total_orders_lifetime=int(row['total_orders_lifetime']) if ('total_orders_lifetime' in row and pd.notna(row['total_orders_lifetime'])) else 0,
            orders_last_30d=int(row['orders_last_30d']) if ('orders_last_30d' in row and pd.notna(row['orders_last_30d'])) else 0,
            orders_prev_30_to_60d=float(row['orders_prev_30_to_60d']) if ('orders_prev_30_to_60d' in row and pd.notna(row['orders_prev_30_to_60d'])) else None,
            total_spend_inr=str(row['total_spend_inr']) if ('total_spend_inr' in row and pd.notna(row['total_spend_inr'])) else "",
            avg_order_value=float(row['avg_order_value']) if ('avg_order_value' in row and pd.notna(row['avg_order_value'])) else None,
            preferred_category=str(row['preferred_category']) if ('preferred_category' in row and pd.notna(row['preferred_category'])) else None,
            sessions_last_30d=int(row['sessions_last_30d']) if ('sessions_last_30d' in row and pd.notna(row['sessions_last_30d'])) else 0,
            avg_session_duration_min=float(row['avg_session_duration_min']) if ('avg_session_duration_min' in row and pd.notna(row['avg_session_duration_min'])) else None,
            cart_abandonments_last_30d=int(row['cart_abandonments_last_30d']) if ('cart_abandonments_last_30d' in row and pd.notna(row['cart_abandonments_last_30d'])) else 0,
            search_queries_last_30d=float(row['search_queries_last_30d']) if ('search_queries_last_30d' in row and pd.notna(row['search_queries_last_30d'])) else None,
            return_count=int(row['return_count']) if ('return_count' in row and pd.notna(row['return_count'])) else 0,
            return_rate=float(row['return_rate']) if ('return_rate' in row and pd.notna(row['return_rate'])) else None,
            cancellations_count=int(row['cancellations_count']) if ('cancellations_count' in row and pd.notna(row['cancellations_count'])) else 0,
            late_deliveries_count=int(row['late_deliveries_count']) if ('late_deliveries_count' in row and pd.notna(row['late_deliveries_count'])) else 0,
            customer_service_tickets=int(row['customer_service_tickets']) if ('customer_service_tickets' in row and pd.notna(row['customer_service_tickets'])) else 0,
            avg_rating_given=float(row['avg_rating_given']) if ('avg_rating_given' in row and pd.notna(row['avg_rating_given'])) else None,
            preferred_payment_mode=str(row['preferred_payment_mode']) if ('preferred_payment_mode' in row and pd.notna(row['preferred_payment_mode'])) else None,
            ground_truth_churn=0
        )
        cust_objs.append(c)

    if cust_objs:
        db.add_all(cust_objs)
        db.commit()
        print(f"[Seed Helper] Successfully restored {len(cust_objs)} live store customer accounts.")

    # Reconnect StoreUser foreign keys
    from ..db.models import StoreUser
    for c in db.query(Customer).filter(Customer.source_customer_id.like("AMZ_PRED1_%")).all():
        su = db.query(StoreUser).filter(StoreUser.username == c.source_customer_id).first()
        if su and su.customer_id != c.id:
            su.customer_id = c.id
    db.commit()

    # Reconcile orders and predictions
    reconcile_all_registered_customers(db)
    return 150

