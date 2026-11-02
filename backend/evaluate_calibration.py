import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss
from sklearn.calibration import calibration_curve

from app.db.session import SessionLocal
from app.db.models import Customer, ChurnPrediction

def main():
    db = SessionLocal()
    try:
        # Join Customer and ChurnPrediction
        results = db.query(Customer, ChurnPrediction).join(
            ChurnPrediction, Customer.id == ChurnPrediction.customer_id
        ).all()

        y_true = []
        y_prob = []

        for cust, pred in results:
            if cust.ground_truth_churn is not None and pred.churn_probability is not None:
                y_true.append(int(cust.ground_truth_churn))
                y_prob.append(float(pred.churn_probability) / 100.0)

        y_true = np.array(y_true)
        y_prob = np.array(y_prob)

        print("=== PROBABILITY CALIBRATION EVALUATION ===")
        print(f"Total evaluated customers: {len(y_true)}")
        if len(y_true) < 10:
            print("Insufficient ground truth samples to evaluate calibration.")
            return

        brier = brier_score_loss(y_true, y_prob)
        print(f"Brier Score Loss: {brier:.4f} (Benchmark: lower is better, 0 = perfect, 0.25 = random coin flip)")

        try:
            ll = log_loss(y_true, y_prob)
            print(f"Log Loss: {ll:.4f}")
        except Exception as e:
            print(f"Log Loss error: {e}")

        # Compute calibration curve
        prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=5, strategy='uniform')
        print("\nReliability Diagram / Calibration Curve (5 Bins):")
        for i, (pt, pp) in enumerate(zip(prob_true, prob_pred)):
            print(f"  Bin {i+1}: Mean Predicted Probability = {pp:.3f}, Observed Fraction of Positives = {pt:.3f}, Gap = {abs(pp - pt):.3f}")

        # Assess calibration status
        mean_gap = np.mean(np.abs(prob_pred - prob_true)) if len(prob_true) > 0 else 0.0
        print(f"\nMean Absolute Calibration Error (Expected Calibration Error): {mean_gap:.4f}")
        
        status = "Uncalibrated / Unverified (raw Random Forest ensemble tree vote probabilities)"
        print(f"Model Calibration Status: {status}")

    finally:
        db.close()

if __name__ == "__main__":
    main()
