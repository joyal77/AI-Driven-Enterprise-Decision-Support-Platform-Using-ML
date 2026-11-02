import json
import datetime
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from .model_loader import get_ml_artifacts
from .shap_engine import explain_churn
from .decision_engine import (
    generate_recommendation,
    extract_root_causes,
    extract_detailed_root_causes,
    generate_structured_retention_plan,
    generate_simple_explanation
)
from ..db.models import Customer, ChurnPrediction, RetentionRecommendation, PredictionBatch

def parse_date(d_val, ref_date):
    if not d_val:
        return ref_date
    if isinstance(d_val, datetime.date):
        return d_val
    if isinstance(d_val, datetime.datetime):
        return d_val.date()
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y.%m.%d'):
        try:
            return datetime.datetime.strptime(str(d_val).strip(), fmt).date()
        except ValueError:
            pass
    return ref_date

def clean_spend(val):
    if pd.isna(val) or val == '' or val is None:
        return np.nan
    val_str = str(val).replace('₹', '').replace('INR', '').replace(',', '').strip()
    try:
        return float(val_str)
    except ValueError:
        return np.nan

def clean_return_rate(val):
    try:
        fval = float(val)
        if np.isinf(fval) or np.isnan(fval):
            return np.nan
        return fval
    except (ValueError, TypeError):
        return np.nan

def run_single_prediction(data: dict, db: Session, force_refresh: bool = False, include_shap: bool = True):
    rf_model, preprocessor, metadata, raw_features = get_ml_artifacts()
    
    if not rf_model or not preprocessor:
        return {"error": "ML model or preprocessor artifact not loaded."}

    customer_id = data.get("customer_id")
    customer = None
    if customer_id:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            customer = db.query(Customer).filter(Customer.source_customer_id == str(customer_id)).first()

    # Fast path: Check for valid existing prediction in DB if force_refresh is False
    if customer and not force_refresh:
        prev_pred = db.query(ChurnPrediction).filter(ChurnPrediction.customer_id == customer.id).first()
        if prev_pred and prev_pred.prediction_timestamp:
            # Check if customer has newer orders placed after the existing prediction
            has_newer_order = False
            if customer.orders:
                for o in customer.orders:
                    od = o.order_date
                    if isinstance(od, str):
                        try:
                            od = datetime.datetime.fromisoformat(od)
                        except Exception:
                            od = None
                    if od and od > prev_pred.prediction_timestamp:
                        has_newer_order = True
                        break

            if not has_newer_order:
                decision_threshold = float(metadata.get("optimal_decision_threshold", 0.5))
                
                cached_shap = []
                if prev_pred.shap_explanation:
                    try:
                        cached_shap = json.loads(prev_pred.shap_explanation)
                    except Exception:
                        cached_shap = []

                # Only return cached prediction if SHAP is not requested, or if SHAP was already computed and cached
                if not (include_shap and not cached_shap):
                    root_causes_detailed = extract_detailed_root_causes(customer, prev_pred.risk_category)
                    structured_retention_plan = generate_structured_retention_plan(
                        customer, prev_pred.risk_category, prev_pred.churn_probability, root_causes_detailed
                    )
                    recommendations = [p["action_summary"] for p in structured_retention_plan]
                    simple_explanation = generate_simple_explanation(
                        prev_pred.churn_probability, prev_pred.risk_category, cached_shap
                    )

                    return {
                        "prediction_id": prev_pred.id,
                        "customer_id": customer.id,
                        "source_customer_id": customer.source_customer_id,
                        "churn_probability": prev_pred.churn_probability,
                        "churn_prediction": prev_pred.churn_prediction,
                        "risk_category": prev_pred.risk_category,
                        "decision_threshold": decision_threshold,
                        "model_version": prev_pred.model_version or "Random Forest v1.0",
                        "shap_explanation": cached_shap,
                        "simple_explanation": simple_explanation,
                        "root_causes": root_causes_detailed,
                        "recommendations": recommendations,
                        "retention_plan": structured_retention_plan,
                        "status": "Success",
                        "cached": True
                    }

    # Reference date for days_since_signup
    ref_date_str = metadata.get("reference_date_for_days_since_signup", "2026-01-01")
    try:
        ref_date = datetime.datetime.strptime(ref_date_str, "%Y-%m-%d").date()
    except Exception:
        ref_date = datetime.date(2026, 1, 1)

    # Build raw input dictionary matching raw_features_list.json
    if customer:
        from ..services.customer_feature_service import compute_customer_transaction_features
        tf = compute_customer_transaction_features(customer)
        # Keep customer record in sync with transactions
        customer.total_orders_lifetime = tf["total_orders_lifetime"]
        customer.total_spend_inr = tf["total_spend_inr_display"]
        customer.avg_order_value = tf["avg_order_value"]
        customer.days_since_last_purchase = tf["days_since_last_purchase"]
        customer.orders_last_30d = tf["orders_last_30d"]
        customer.orders_prev_30_to_60d = tf["orders_prev_30_to_60d"]
        customer.return_count = tf["return_count"]
        customer.return_rate = tf["return_rate"]
        customer.cancellations_count = tf["cancellations_count"]
        customer.preferred_payment_mode = tf["preferred_payment_mode"]

        signup_d = parse_date(customer.signup_date, ref_date)
        days_since_signup = max(0, (ref_date - signup_d).days)
        
        raw_dict = {
            'customer_age': customer.customer_age,
            'gender': customer.gender,
            'city_tier': customer.city_tier,
            'membership_status': customer.membership_status,
            'days_since_last_purchase': customer.days_since_last_purchase if customer.days_since_last_purchase is not None else np.nan,
            'total_orders_lifetime': customer.total_orders_lifetime,
            'orders_last_30d': customer.orders_last_30d,
            'orders_prev_30_to_60d': customer.orders_prev_30_to_60d,
            'total_spend_inr': tf.get("total_spend_inr_num", tf.get("total_spend_num", 0.0)),
            'avg_order_value': customer.avg_order_value,
            'preferred_category': customer.preferred_category,
            'sessions_last_30d': customer.sessions_last_30d,
            'avg_session_duration_min': customer.avg_session_duration_min,
            'cart_abandonments_last_30d': customer.cart_abandonments_last_30d,
            'search_queries_last_30d': customer.search_queries_last_30d,
            'return_count': customer.return_count,
            'return_rate': clean_return_rate(customer.return_rate),
            'cancellations_count': customer.cancellations_count,
            'late_deliveries_count': customer.late_deliveries_count,
            'customer_service_tickets': customer.customer_service_tickets,
            'avg_rating_given': customer.avg_rating_given,
            'preferred_payment_mode': customer.preferred_payment_mode,
            'days_since_signup': days_since_signup
        }
    else:
        signup_d = parse_date(data.get('signup_date'), ref_date)
        days_since_signup = max(0, (ref_date - signup_d).days)
        
        raw_dict = {
            'customer_age': data.get('customer_age', 35.0),
            'gender': data.get('gender', 'Female'),
            'city_tier': data.get('city_tier', 'Tier 1'),
            'membership_status': data.get('membership_status', 'Prime'),
            'days_since_last_purchase': data.get('days_since_last_purchase', 30.0),
            'total_orders_lifetime': data.get('total_orders_lifetime', 10),
            'orders_last_30d': data.get('orders_last_30d', 2),
            'orders_prev_30_to_60d': data.get('orders_prev_30_to_60d', 2.0),
            'total_spend_inr': clean_spend(data.get('total_spend_inr', 5000)),
            'avg_order_value': data.get('avg_order_value', 500.0),
            'preferred_category': data.get('preferred_category', 'Fashion'),
            'sessions_last_30d': data.get('sessions_last_30d', 15),
            'avg_session_duration_min': data.get('avg_session_duration_min', 12.0),
            'cart_abandonments_last_30d': data.get('cart_abandonments_last_30d', 1),
            'search_queries_last_30d': data.get('search_queries_last_30d', 10.0),
            'return_count': data.get('return_count', 1),
            'return_rate': clean_return_rate(data.get('return_rate', 0.1)),
            'cancellations_count': data.get('cancellations_count', 0),
            'late_deliveries_count': data.get('late_deliveries_count', 0),
            'customer_service_tickets': data.get('customer_service_tickets', 0),
            'avg_rating_given': data.get('avg_rating_given', 4.0),
            'preferred_payment_mode': data.get('preferred_payment_mode', 'UPI'),
            'days_since_signup': days_since_signup
        }

    input_df = pd.DataFrame([raw_dict])
    
    # Ensure correct feature ordering
    if raw_features:
        for col in raw_features:
            if col not in input_df.columns:
                input_df[col] = np.nan
        input_df = input_df[raw_features]

    # Preprocess
    X_trans = preprocessor.transform(input_df)

    # Predict probability and class
    prob_raw = float(rf_model.predict_proba(X_trans)[0][1])
    churn_probability_pct = round(prob_raw * 100, 2)
    
    decision_threshold = float(metadata.get("optimal_decision_threshold", 0.5))
    churn_pred_class = 1 if prob_raw >= decision_threshold else 0

    # Risk categorization
    if prob_raw >= 0.70:
        risk_category = "High Risk"
    elif prob_raw >= 0.30:
        risk_category = "Medium Risk"
    else:
        risk_category = "Low Risk"

    shap_explanation = []
    if include_shap:
        shap_explanation = explain_churn(
            rf_model, 
            X_trans, 
            preprocessor, 
            raw_dict=raw_dict,
            cache_key=f"cust_{customer.id}" if customer else None
        )
    root_causes_detailed = extract_detailed_root_causes(customer or raw_dict, risk_category)
    root_causes_list = [f"{d['title']} ({d['metric']})" for d in root_causes_detailed]
    structured_retention_plan = generate_structured_retention_plan(customer or raw_dict, risk_category, churn_probability_pct, root_causes_detailed)
    recommendations = [p["action_summary"] for p in structured_retention_plan]

    # Persist prediction in DB if customer exists
    pred_record_id = None
    if customer:
        prev_pred = db.query(ChurnPrediction).filter(ChurnPrediction.customer_id == customer.id).first()
        if prev_pred:
            prev_pred.churn_probability = churn_probability_pct
            prev_pred.churn_prediction = churn_pred_class
            prev_pred.risk_category = risk_category
            prev_pred.prediction_timestamp = datetime.datetime.now()
            if shap_explanation:
                prev_pred.shap_explanation = json.dumps(shap_explanation)
            prev_pred.root_causes = json.dumps(root_causes_list)
            prev_pred.recommendations = json.dumps(recommendations)
            db.commit()
            pred_record_id = prev_pred.id
        else:
            new_pred = ChurnPrediction(
                customer_id=customer.id,
                churn_probability=churn_probability_pct,
                churn_prediction=churn_pred_class,
                risk_category=risk_category,
                model_version="Random Forest v1.0",
                shap_explanation=json.dumps(shap_explanation) if shap_explanation else None,
                root_causes=json.dumps(root_causes_list),
                recommendations=json.dumps(recommendations)
            )
            db.add(new_pred)
            db.commit()
            db.refresh(new_pred)
            pred_record_id = new_pred.id

        # Insert retention recommendations only if not already recorded (prevent duplicates)
        existing_recs = db.query(RetentionRecommendation.recommendation_description).filter(
            RetentionRecommendation.customer_id == customer.id
        ).all()
        existing_desc_set = {r[0] for r in existing_recs}
        new_recs_added = False
        for rec in recommendations:
            if rec not in existing_desc_set:
                rec_entry = RetentionRecommendation(
                    customer_id=customer.id,
                    recommendation_type=risk_category,
                    recommendation_description=rec,
                    status="Active"
                )
                db.add(rec_entry)
                new_recs_added = True
        if new_recs_added:
            db.commit()

    simple_explanation = generate_simple_explanation(
        churn_probability_pct, risk_category, shap_explanation
    )

    return {
        "prediction_id": pred_record_id,
        "customer_id": customer.id if customer else None,
        "source_customer_id": customer.source_customer_id if customer else None,
        "churn_probability": churn_probability_pct,
        "churn_prediction": churn_pred_class,
        "risk_category": risk_category,
        "decision_threshold": decision_threshold,
        "model_version": "Random Forest v1.0",
        "shap_explanation": shap_explanation,
        "simple_explanation": simple_explanation,
        "root_causes": root_causes_detailed,
        "recommendations": recommendations,
        "retention_plan": structured_retention_plan,
        "status": "Success"
    }

def run_batch_prediction(db: Session):
    """
    Executes authoritative batch churn prediction by reconciling all customer records
    against real storefront order transactions and applying the trained Random Forest model.
    """
    from ..services.customer_feature_service import reconcile_all_registered_customers
    res = reconcile_all_registered_customers(db)
    res["total_processed"] = res.get("total_customers", 0)
    return res
    if not customers:
        return {
            "success": False,
            "message": "No customer records found in database to analyze.",
            "total_processed": 0
        }

    ref_date_str = metadata.get("reference_date_for_days_since_signup", "2026-01-01")
    try:
        ref_date = datetime.datetime.strptime(ref_date_str, "%Y-%m-%d").date()
    except Exception:
        ref_date = datetime.date(2026, 1, 1)

    # 1. Build batch DataFrame
    rows = []
    cust_map = []

    for c in customers:
        signup_d = parse_date(c.signup_date, ref_date)
        days_since_signup = max(0, (ref_date - signup_d).days)

        r = {
            'customer_age': c.customer_age,
            'gender': c.gender,
            'city_tier': c.city_tier,
            'membership_status': c.membership_status,
            'days_since_last_purchase': c.days_since_last_purchase,
            'total_orders_lifetime': c.total_orders_lifetime,
            'orders_last_30d': c.orders_last_30d,
            'orders_prev_30_to_60d': c.orders_prev_30_to_60d,
            'total_spend_inr': clean_spend(c.total_spend_inr),
            'avg_order_value': c.avg_order_value,
            'preferred_category': c.preferred_category,
            'sessions_last_30d': c.sessions_last_30d,
            'avg_session_duration_min': c.avg_session_duration_min,
            'cart_abandonments_last_30d': c.cart_abandonments_last_30d,
            'search_queries_last_30d': c.search_queries_last_30d,
            'return_count': c.return_count,
            'return_rate': clean_return_rate(c.return_rate),
            'cancellations_count': c.cancellations_count,
            'late_deliveries_count': c.late_deliveries_count,
            'customer_service_tickets': c.customer_service_tickets,
            'avg_rating_given': c.avg_rating_given,
            'preferred_payment_mode': c.preferred_payment_mode,
            'days_since_signup': days_since_signup
        }
        rows.append(r)
        cust_map.append(c)

    batch_df = pd.DataFrame(rows)
    if raw_features:
        for col in raw_features:
            if col not in batch_df.columns:
                batch_df[col] = np.nan
        batch_df = batch_df[raw_features]

    # 2. Transform and Predict in batch
    X_trans = preprocessor.transform(batch_df)
    probs_raw = rf_model.predict_proba(X_trans)[:, 1]

    decision_threshold = float(metadata.get("optimal_decision_threshold", 0.5))

    high_risk = 0
    med_risk = 0
    low_risk = 0
    proba_sum = 0.0

    # Clear previous predictions and recommendations to keep campaigns aligned with the loaded dataset
    db.query(RetentionRecommendation).delete()
    db.query(ChurnPrediction).delete()
    db.commit()

    new_predictions = []
    new_recommendations = []
    now_time = datetime.datetime.now()

    for idx, prob_raw in enumerate(probs_raw):
        c = cust_map[idx]
        prob_pct = round(float(prob_raw) * 100, 2)
        proba_sum += prob_pct
        churn_class = 1 if prob_raw >= decision_threshold else 0

        if prob_raw >= 0.70:
            risk_cat = "High Risk"
            high_risk += 1
        elif prob_raw >= 0.30:
            risk_cat = "Medium Risk"
            med_risk += 1
        else:
            risk_cat = "Low Risk"
            low_risk += 1

        recs = generate_recommendation(risk_cat, prob_pct, c)
        root_causes_list = extract_root_causes(c, risk_cat)

        pred_obj = ChurnPrediction(
            customer_id=c.id,
            churn_probability=prob_pct,
            churn_prediction=churn_class,
            risk_category=risk_cat,
            model_version="Random Forest v1.0",
            prediction_timestamp=now_time,
            root_causes=json.dumps(root_causes_list),
            recommendations=json.dumps(recs)
        )
        new_predictions.append(pred_obj)

        # Generate actionable campaign recommendation records for Retention Campaigns
        for rec_desc in recs:
            rec_entry = RetentionRecommendation(
                customer_id=c.id,
                recommendation_type=risk_cat,
                recommendation_description=rec_desc,
                status="Pending",
                created_at=now_time
            )
            new_recommendations.append(rec_entry)

    db.bulk_save_objects(new_predictions)
    db.bulk_save_objects(new_recommendations)
    
    # Save batch tracking record
    batch_record = PredictionBatch(
        batch_status="Completed",
        total_customers=len(customers),
        processed_customers=len(customers),
        failed_customers=0,
        completed_at=now_time
    )
    db.add(batch_record)
    db.commit()

    total_cnt = len(customers)
    avg_proba = round(proba_sum / total_cnt, 2) if total_cnt > 0 else 0.0

    return {
        "success": True,
        "message": f"Batch prediction successfully completed for {total_cnt} e-commerce customers.",
        "total_processed": total_cnt,
        "high_risk_customers": high_risk,
        "medium_risk_customers": med_risk,
        "low_risk_customers": low_risk,
        "average_churn_probability": avg_proba,
        "batch_id": batch_record.id
    }
