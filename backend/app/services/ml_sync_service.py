import datetime
from sqlalchemy.orm import Session
from ..db.models import Customer
from .customer_feature_service import reconcile_and_predict_customer

def sync_order_to_customer_and_ml(customer_id: int, order_amount: float, db: Session):
    """
    Real-Time Bridge:
    When an order is placed on the SmartCart storefront, this service:
    1. Reconciles customer's behavioral and RFM metrics from actual database orders in Order table.
    2. Runs the Random Forest ML model to recalculate churn probability & recommendations.
    3. Persists fresh predictions atomically to the DB so the Decision Suite reflects true transaction metrics live.
    """
    try:
        res = reconcile_and_predict_customer(customer_id, db, log_discrepancy=False)
        return {
            "customer_id": res.get("customer_id"),
            "source_customer_id": res.get("source_customer_id"),
            "days_since_last_purchase": res.get("days_since_last_purchase"),
            "total_orders_lifetime": res.get("total_orders_lifetime"),
            "total_spend_inr": res.get("total_spend_inr"),
            "new_churn_probability": res.get("churn_probability"),
            "new_risk_category": res.get("risk_category"),
            "ml_status": "Synchronized"
        }
    except Exception as e:
        print(f"[ML Sync Bridge Error] Failed syncing customer {customer_id}: {e}")
        return None
