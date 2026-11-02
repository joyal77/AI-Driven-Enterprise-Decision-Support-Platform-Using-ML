import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.models import ChurnPrediction, Customer
from ..ml.predictor import run_single_prediction, run_batch_prediction

router = APIRouter(tags=["Churn Prediction"])

@router.post("/predict-churn")
def predict_churn_endpoint(data: dict, db: Session = Depends(get_db)):
    return run_single_prediction(data, db)

@router.post("/predict-churn/batch")
def predict_churn_batch_endpoint(db: Session = Depends(get_db)):
    return run_batch_prediction(db)

@router.get("/churn-predictions")
def get_churn_predictions(
    risk_category: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(ChurnPrediction, Customer).join(Customer, ChurnPrediction.customer_id == Customer.id)

    if risk_category and risk_category.lower() != "all":
        query = query.filter(ChurnPrediction.risk_category == risk_category)

    total_count = query.count()
    offset = (page - 1) * limit
    results = query.offset(offset).limit(limit).all()

    predictions_list = []
    for pred, cust in results:
        recs = []
        if pred.recommendations:
            try:
                recs = json.loads(pred.recommendations)
            except Exception:
                recs = [pred.recommendations]

        predictions_list.append({
            "id": pred.id,
            "customer_id": pred.customer_id,
            "source_customer_id": cust.source_customer_id,
            "churn_probability": pred.churn_probability,
            "churn_prediction": pred.churn_prediction,
            "risk_category": pred.risk_category,
            "model_version": pred.model_version,
            "prediction_timestamp": pred.prediction_timestamp.isoformat() if pred.prediction_timestamp else None,
            "recommendations": recs,
            "customer_details": {
                "membership_status": cust.membership_status,
                "preferred_category": cust.preferred_category,
                "days_since_last_purchase": cust.days_since_last_purchase,
                "customer_service_tickets": cust.customer_service_tickets
            }
        })

    return {
        "total": total_count,
        "page": page,
        "limit": limit,
        "predictions": predictions_list
    }

@router.get("/churn-predictions/{customer_id}")
def get_customer_prediction(customer_id: int, db: Session = Depends(get_db)):
    pred = db.query(ChurnPrediction).filter(ChurnPrediction.customer_id == customer_id).first()
    if not pred:
        return run_single_prediction({"customer_id": customer_id}, db)
    
    recs = []
    if pred.recommendations:
        try:
            recs = json.loads(pred.recommendations)
        except Exception:
            recs = [pred.recommendations]

    return {
        "id": pred.id,
        "customer_id": pred.customer_id,
        "churn_probability": pred.churn_probability,
        "churn_prediction": pred.churn_prediction,
        "risk_category": pred.risk_category,
        "model_version": pred.model_version,
        "prediction_timestamp": pred.prediction_timestamp.isoformat() if pred.prediction_timestamp else None,
        "recommendations": recs
    }
