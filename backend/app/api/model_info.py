from fastapi import APIRouter
from ..ml.model_loader import get_ml_artifacts

router = APIRouter(prefix="/model-info", tags=["Model Information"])

@router.get("")
def get_model_information():
    rf_model, preprocessor, metadata, raw_features = get_ml_artifacts()

    model_loaded = rf_model is not None
    preprocessor_loaded = preprocessor is not None

    return {
        "model_name": metadata.get("selected_model_name", "Random Forest Classifier"),
        "model_version": "v1.0 (Google Colab Trained)",
        "optimal_decision_threshold": metadata.get("optimal_decision_threshold", 0.5),
        "reference_date_for_days_since_signup": metadata.get("reference_date_for_days_since_signup", "2026-01-01"),
        "model_loaded": model_loaded,
        "preprocessor_loaded": preprocessor_loaded,
        "num_raw_features": len(raw_features),
        "raw_features": raw_features,
        "training_dataset_info": {
            "name": "raw_ecommerce_churn_10k.csv",
            "total_records": 10000,
            "target_variable": "churn_label",
            "class_balance_churn_pct": 18.88
        },
        "performance_metrics": {
            "training_accuracy": 0.9487,
            "decision_threshold": metadata.get("optimal_decision_threshold", 0.5),
            "algorithm": "RandomForestClassifier(n_estimators=100, max_depth=12, class_weight='balanced')"
        }
    }
