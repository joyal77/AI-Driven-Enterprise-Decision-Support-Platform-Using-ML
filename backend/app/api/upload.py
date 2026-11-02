import os
import io
import datetime
import pandas as pd
import numpy as np
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..db.models import Customer, ChurnPrediction, RetentionRecommendation
from ..ml.predictor import run_batch_prediction

router = APIRouter(prefix="/upload-dataset", tags=["Dataset Upload"])

def parse_date(d_str):
    if pd.isna(d_str) or not d_str:
        return None
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y.%m.%d'):
        try:
            return datetime.datetime.strptime(str(d_str).strip(), fmt).date()
        except ValueError:
            pass
    return None

def import_dataframe_to_db(df: pd.DataFrame, db: Session):
    # Detect if the uploaded dataset is for live store customers (AMZ_PRED1_) or uploaded dataset customers
    first_ids = [str(x).strip() for x in df['customer_id'].dropna().head(10).tolist()]
    is_live_store_batch = any(cid.startswith('AMZ_PRED1_') for cid in first_ids)

    if is_live_store_batch:
        target_custs = db.query(Customer).filter(Customer.source_customer_id.like("AMZ_PRED1_%")).all()
    else:
        target_custs = db.query(Customer).filter(~Customer.source_customer_id.like("AMZ_PRED1_%")).all()

    target_ids = [c.id for c in target_custs]
    if target_ids:
        db.query(RetentionRecommendation).filter(RetentionRecommendation.customer_id.in_(target_ids)).delete(synchronize_session=False)
        db.query(ChurnPrediction).filter(ChurnPrediction.customer_id.in_(target_ids)).delete(synchronize_session=False)
        db.query(Customer).filter(Customer.id.in_(target_ids)).delete(synchronize_session=False)
        db.commit()
    
    new_customers = []
    imported_count = 0
    existing_ids = set()

    for idx, row in df.iterrows():
        cust_id_str = str(row['customer_id']).strip()
        
        if cust_id_str in existing_ids:
            continue

        existing_ids.add(cust_id_str)

        age_val = float(row['customer_age']) if ('customer_age' in row and pd.notna(row['customer_age'])) else None
        city_tier_val = str(row['city_tier']) if ('city_tier' in row and pd.notna(row['city_tier'])) else None
        mem_status_val = str(row['membership_status']) if ('membership_status' in row and pd.notna(row['membership_status'])) else None
        gender_val = str(row['gender']) if ('gender' in row and pd.notna(row['gender'])) else None
        cat_val = str(row['preferred_category']) if ('preferred_category' in row and pd.notna(row['preferred_category'])) else None
        pay_val = str(row['preferred_payment_mode']) if ('preferred_payment_mode' in row and pd.notna(row['preferred_payment_mode'])) else None

        days_last_p = float(row['days_since_last_purchase']) if ('days_since_last_purchase' in row and pd.notna(row['days_since_last_purchase'])) else None
        tot_orders = int(row['total_orders_lifetime']) if ('total_orders_lifetime' in row and pd.notna(row['total_orders_lifetime'])) else 1
        orders_30d = int(row['orders_last_30d']) if ('orders_last_30d' in row and pd.notna(row['orders_last_30d'])) else 0
        orders_prev = float(row['orders_prev_30_to_60d']) if ('orders_prev_30_to_60d' in row and pd.notna(row['orders_prev_30_to_60d'])) else None
        spend_str = str(row['total_spend_inr']) if ('total_spend_inr' in row and pd.notna(row['total_spend_inr'])) else ""
        aov = float(row['avg_order_value']) if ('avg_order_value' in row and pd.notna(row['avg_order_value'])) else None
        sessions = int(row['sessions_last_30d']) if ('sessions_last_30d' in row and pd.notna(row['sessions_last_30d'])) else 0
        sess_dur = float(row['avg_session_duration_min']) if ('avg_session_duration_min' in row and pd.notna(row['avg_session_duration_min'])) else None
        cart_ab = int(row['cart_abandonments_last_30d']) if ('cart_abandonments_last_30d' in row and pd.notna(row['cart_abandonments_last_30d'])) else 0
        queries = float(row['search_queries_last_30d']) if ('search_queries_last_30d' in row and pd.notna(row['search_queries_last_30d'])) else None
        ret_cnt = int(row['return_count']) if ('return_count' in row and pd.notna(row['return_count'])) else 0
        ret_rate = float(row['return_rate']) if ('return_rate' in row and pd.notna(row['return_rate'])) else None
        cancels = int(row['cancellations_count']) if ('cancellations_count' in row and pd.notna(row['cancellations_count'])) else 0
        late_del = int(row['late_deliveries_count']) if ('late_deliveries_count' in row and pd.notna(row['late_deliveries_count'])) else 0
        tickets = int(row['customer_service_tickets']) if ('customer_service_tickets' in row and pd.notna(row['customer_service_tickets'])) else 0
        rating = float(row['avg_rating_given']) if ('avg_rating_given' in row and pd.notna(row['avg_rating_given'])) else None
        gt_churn = int(row['churn_label']) if ('churn_label' in row and pd.notna(row['churn_label'])) else None

        c_obj = Customer(
            source_customer_id=cust_id_str,
            signup_date=parse_date(row.get('signup_date')),
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

    # Automatically execute batch prediction
    prediction_summary = run_batch_prediction(db)
    return imported_count, prediction_summary


@router.post("")
async def upload_csv_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Please upload a valid CSV file (.csv)."
        )

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse CSV file: {str(e)}"
        )

    # Validate essential columns
    required_cols = ['customer_id', 'signup_date', 'customer_age', 'gender', 'membership_status']
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Uploaded CSV is missing required columns: {', '.join(missing_cols)}"
        )

    imported_count, prediction_summary = import_dataframe_to_db(df, db)

    return {
        "success": True,
        "filename": file.filename,
        "file_size_bytes": len(contents),
        "total_rows_parsed": len(df),
        "imported_customers": imported_count,
        "prediction_summary": prediction_summary
    }


@router.post("/sample/{sample_name}")
def load_sample_dataset(sample_name: str, db: Session = Depends(get_db)):
    """
    1-Click Quick Load for prediction sample datasets: '150_rows', '200_rows', '250_rows'.
    """
    valid_samples = {
        '150_rows': ('prediction_batch_1_150rows.csv', '150 Rows Mixed Risk Batch'),
        '200_rows': ('prediction_batch_2_200rows.csv', '200 Rows High Churn Risk Batch'),
        '250_rows': ('prediction_batch_3_250rows.csv', '250 Rows Active Low Risk Batch'),
    }

    if sample_name not in valid_samples:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sample dataset name. Options: {', '.join(valid_samples.keys())}"
        )

    filename, label = valid_samples[sample_name]
    
    # Try sample_datasets in project root, then dataset folder
    possible_paths = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'sample_datasets', filename)),
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'dataset', filename))
    ]

    sample_path = None
    for p in possible_paths:
        if os.path.exists(p):
            sample_path = p
            break

    if not sample_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sample dataset file '{filename}' not found on server."
        )

    df = pd.read_csv(sample_path)
    imported_count, prediction_summary = import_dataframe_to_db(df, db)

    return {
        "success": True,
        "filename": filename,
        "sample_label": label,
        "total_rows_parsed": len(df),
        "imported_customers": imported_count,
        "prediction_summary": prediction_summary
    }


@router.post("/clear")
def clear_all_customer_records(db: Session = Depends(get_db)):
    """
    Clears uploaded dataset customer records and predictions from database.
    Preserves live SmartCart store customers so live store accounts and orders remain functional.
    """
    try:
        # Only target non-live store customer records
        target_custs = db.query(Customer).filter(~Customer.source_customer_id.like("AMZ_PRED1_%")).all()
        target_ids = [c.id for c in target_custs]
        
        if target_ids:
            db.query(RetentionRecommendation).filter(RetentionRecommendation.customer_id.in_(target_ids)).delete(synchronize_session=False)
            db.query(ChurnPrediction).filter(ChurnPrediction.customer_id.in_(target_ids)).delete(synchronize_session=False)
            db.query(Customer).filter(Customer.id.in_(target_ids)).delete(synchronize_session=False)
            db.commit()
        
        return {
            "success": True,
            "message": f"Cleared {len(target_ids)} uploaded dataset customer records. Live store accounts preserved."
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear uploaded dataset: {str(e)}"
        )
