import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from app.db.session import SessionLocal
from app.db.models import Customer, Order, ChurnPrediction, DataIntegrityAuditLog
from app.services.customer_feature_service import reconcile_all_registered_customers, reconcile_and_predict_customer

def main():
    db = SessionLocal()
    try:
        print("=== BEFORE RECONCILIATION ===")
        c_1041 = db.query(Customer).filter(Customer.source_customer_id == "AMZ_PRED1_1041").first()
        if c_1041:
            order_count = db.query(Order).filter(Order.customer_id == c_1041.id).count()
            print(f"Customer AMZ_PRED1_1041 DB orders: {order_count}")
            print(f"Customer AMZ_PRED1_1041 Customer record: lifetime_orders={c_1041.total_orders_lifetime}, spend={c_1041.total_spend_inr}, days_since_last_purchase={c_1041.days_since_last_purchase}")
            p_1041 = db.query(ChurnPrediction).filter(ChurnPrediction.customer_id == c_1041.id).first()
            if p_1041:
                print(f"Prediction: prob={p_1041.churn_probability}, risk={p_1041.risk_category}")

        print("\nStarting full reconciliation across all registered customers...")
        summary = reconcile_all_registered_customers(db)
        print("Reconciliation Summary:", summary)

        print("\n=== AFTER RECONCILIATION ===")
        db.refresh(c_1041)
        print(f"Customer AMZ_PRED1_1041 DB orders: {order_count}")
        print(f"Customer AMZ_PRED1_1041 Customer record: lifetime_orders={c_1041.total_orders_lifetime}, spend={c_1041.total_spend_inr}, days_since_last_purchase={c_1041.days_since_last_purchase}")
        p_1041_after = db.query(ChurnPrediction).filter(ChurnPrediction.customer_id == c_1041.id).first()
        if p_1041_after:
            print(f"Prediction after: prob={p_1041_after.churn_probability}, risk={p_1041_after.risk_category}")

        logs_count = db.query(DataIntegrityAuditLog).count()
        print(f"Total discrepancy logs recorded in DataIntegrityAuditLog: {logs_count}")
        sample_log = db.query(DataIntegrityAuditLog).first()
        if sample_log:
            print(f"Sample discrepancy log: customer_id={sample_log.customer_id}, prev_orders={sample_log.previous_orders}, actual_orders={sample_log.actual_orders}, reason={sample_log.reason}")

    finally:
        db.close()

if __name__ == "__main__":
    main()
