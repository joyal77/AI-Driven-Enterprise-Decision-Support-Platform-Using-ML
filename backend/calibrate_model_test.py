import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score, f1_score, precision_score, recall_score
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
import sklearn.compose._column_transformer

sys.stdout.reconfigure(encoding='utf-8')

class _RemainderColsList(list):
    pass

sklearn.compose._column_transformer._RemainderColsList = _RemainderColsList

def test_model_calibration():
    # 1. Load artifacts
    rf_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'churn', 'random_forest_model.joblib')
    prep_path = os.path.join(os.path.dirname(__file__), '..', 'preprocessor.joblib')
    raw_feats_path = os.path.join(os.path.dirname(__file__), '..', 'raw_features_list.json')
    data_path = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'customer churn', 'raw_ecommerce_churn_10k.csv')

    if not os.path.exists(rf_path):
        print("Missing rf_path:", rf_path)
        return
    if not os.path.exists(prep_path):
        print("Missing prep_path:", prep_path)
        return
    if not os.path.exists(data_path):
        print("Missing data_path:", data_path)
        return

    rf_model = joblib.load(rf_path)
    preprocessor = joblib.load(prep_path)
    with open(raw_feats_path, 'r') as f:
        raw_features = json.load(f)

    df_raw = pd.read_csv(data_path)
    print(f"Loaded {len(df_raw)} records from {os.path.basename(data_path)}")

    # Clean total_spend_inr
    df_raw['total_spend_inr'] = df_raw['total_spend_inr'].astype(str).str.replace('₹', '').str.replace(',', '').str.replace('INR', '').str.strip()
    df_raw['total_spend_inr'] = pd.to_numeric(df_raw['total_spend_inr'], errors='coerce')
    df_raw['return_rate'] = pd.to_numeric(df_raw['return_rate'], errors='coerce').replace([np.inf, -np.inf], np.nan)

    # Compute days_since_signup
    ref_date = pd.to_datetime("2026-01-01")
    df_raw['signup_dt'] = pd.to_datetime(df_raw['signup_date'], errors='coerce')
    df_raw['days_since_signup'] = (ref_date - df_raw['signup_dt']).dt.days.fillna(365).clip(lower=0)

    # Align columns
    X_raw = df_raw[raw_features]
    y_true = df_raw['churn_label'].astype(int)

    # Transform
    X_trans = preprocessor.transform(X_raw)

    # Base model probabilities
    probs_base = rf_model.predict_proba(X_trans)[:, 1]
    preds_base = (probs_base >= 0.5).astype(int)

    brier_base = brier_score_loss(y_true, probs_base)
    logloss_base = log_loss(y_true, probs_base)
    auc_base = roc_auc_score(y_true, probs_base)
    f1_base = f1_score(y_true, preds_base)

    print("=== BASE RANDOM FOREST MODEL EVALUATION ===")
    print(f"Brier Score Loss: {brier_base:.4f} (lower is better, 0 is perfect)")
    print(f"Log Loss:         {logloss_base:.4f}")
    print(f"ROC-AUC Score:    {auc_base:.4f}")
    print(f"F1 Score:         {f1_base:.4f}")

    # Check calibration curve
    prob_true, prob_pred = calibration_curve(y_true, probs_base, n_bins=10)
    print("\nCalibration Curve (predicted vs true probabilities):")
    for pp, pt in zip(prob_pred, prob_true):
        print(f"  Predicted: {pp:.3f} | Observed True: {pt:.3f}")

    # Test calibration using 5-fold cross-validation calibration or sigmoid calibration on held-out 50%
    np.random.seed(42)
    indices = np.arange(len(df_raw))
    np.random.shuffle(indices)
    split_idx = int(len(df_raw) * 0.7)
    train_idx, val_idx = indices[:split_idx], indices[split_idx:]

    X_val = X_trans[val_idx]
    y_val = y_true.iloc[val_idx]
    probs_val_base = rf_model.predict_proba(X_val)[:, 1]
    brier_val_base = brier_score_loss(y_val, probs_val_base)
    print(f"\nValidation Baseline Brier Score: {brier_val_base:.4f}")

    # Fit sigmoid calibrator on calibration split (prefit)
    calibrator = CalibratedClassifierCV(estimator=rf_model, method='sigmoid', cv='prefit')
    calibrator.fit(X_trans[train_idx], y_true.iloc[train_idx])
    probs_val_cal = calibrator.predict_proba(X_val)[:, 1]
    brier_val_cal = brier_score_loss(y_val, probs_val_cal)
    logloss_val_cal = log_loss(y_val, probs_val_cal)

    print(f"Calibrated (Sigmoid) Brier Score: {brier_val_cal:.4f}")
    print(f"Calibrated Log Loss:              {logloss_val_cal:.4f}")
    print(f"Brier Improvement:                {brier_val_base - brier_val_cal:+.4f}")

if __name__ == '__main__':
    test_model_calibration()
