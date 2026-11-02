"""
shap_engine.py

Generates true individual customer-level SHAP / explainable AI (xAI) attributions
for Random Forest churn predictions using TreeExplainer.
"""

import numpy as np
import pandas as pd

FRIENDLY_LABELS = {
    "customer_service_tickets": "Support Tickets & Grievances",
    "days_since_last_purchase": "Days Since Last Purchase",
    "cart_abandonments_last_30d": "Cart Abandonments (30d)",
    "sessions_last_30d": "App Sessions Frequency (30d)",
    "total_spend_inr": "Total Lifetime Spend",
    "avg_order_value": "Average Order Value",
    "total_orders_lifetime": "Lifetime Orders Count",
    "late_deliveries_count": "Late Delivery Incidents",
    "return_rate": "Product Return Rate",
    "return_count": "Return Count",
    "cancellations_count": "Order Cancellations",
    "avg_rating_given": "Customer Review Sentiment (Stars)",
    "avg_session_duration_min": "Average Session Duration",
    "search_queries_last_30d": "Search Queries Volume",
    "orders_last_30d": "Recent Orders (Last 30d)",
    "orders_prev_30_to_60d": "Orders (30d–60d Window)",
    "customer_age": "Customer Demographics (Age)",
    "membership_status_Prime": "Prime Membership Benefit",
    "membership_status_Plus": "Plus Membership Benefit",
    "membership_status_Standard": "Standard (Non-Prime) Tier",
    "days_since_signup": "Account Tenure (Days Since Signup)"
}

import threading

_tree_explainer = None
_explainer_model_id = None
_explainer_lock = threading.Lock()
_shap_cache = {}

def get_tree_explainer(model):
    global _tree_explainer, _explainer_model_id
    if _tree_explainer is not None and _explainer_model_id == id(model):
        return _tree_explainer
    with _explainer_lock:
        if _tree_explainer is None or _explainer_model_id != id(model):
            try:
                import shap
                _tree_explainer = shap.TreeExplainer(model)
                _explainer_model_id = id(model)
                print(f"[SHAP Engine] TreeExplainer initialized and cached for model {id(model)}.")
            except Exception as e:
                print(f"[SHAP] Error creating TreeExplainer: {e}")
                _tree_explainer = None
    return _tree_explainer

def format_feature_val(raw_feat, val, raw_dict=None):
    if raw_dict and raw_feat in raw_dict:
        v = raw_dict[raw_feat]
        if v is None or pd.isna(v):
            if raw_feat == "days_since_last_purchase":
                return "Never purchased"
            return "N/A"
        try:
            if raw_feat in ["customer_service_tickets", "late_deliveries_count", "cancellations_count"]:
                return f"{int(v)} incidents"
            if raw_feat in ["cart_abandonments_last_30d"]:
                return f"{int(v)} carts"
            if raw_feat in ["total_orders_lifetime", "orders_last_30d"]:
                return f"{int(v)} orders"
            if raw_feat in ["days_since_last_purchase"]:
                return f"{int(v)} days"
            if raw_feat in ["sessions_last_30d"]:
                return f"{int(v)} sessions"
            if raw_feat in ["total_spend_inr", "avg_order_value"]:
                return f"₹{float(v):,.2f}"
            if raw_feat in ["avg_rating_given"]:
                return f"{float(v):.1f} ★"
            if raw_feat in ["return_rate"]:
                return f"{(float(v) * 100):.1f}%"
            return str(v)
        except (ValueError, TypeError):
            return str(v)
    
    if np.issubdtype(type(val), np.number):
        if np.isnan(val) or np.isinf(val):
            return "N/A"
        return f"{val:.2f}"
    return str(val)

def explain_churn(model, X_transformed, preprocessor=None, feature_names=None, raw_dict=None, cache_key=None):
    """
    Computes true customer-specific SHAP attribution values for a single prediction instance.
    Each customer's unique behavioral signals drive their own distinct feature weights,
    direction (Increases Risk vs Protects Account), and observed values.
    """
    if cache_key and cache_key in _shap_cache:
        return _shap_cache[cache_key]
    try:
        # Extract feature names from ColumnTransformer
        names = []
        if preprocessor and hasattr(preprocessor, "get_feature_names_out"):
            try:
                names = list(preprocessor.get_feature_names_out())
            except Exception:
                pass
        
        if not names:
            num_features = X_transformed.shape[1] if hasattr(X_transformed, "shape") else 41
            names = [f"Feature_{i}" for i in range(num_features)]

        row_vals = X_transformed[0] if isinstance(X_transformed, np.ndarray) and X_transformed.ndim > 1 else X_transformed

        explainer = get_tree_explainer(model)
        churn_shap = None

        if explainer is not None:
            try:
                sv = explainer.shap_values(X_transformed)
                # sv can be ndarray of shape (1, num_features, 2) or list of [class0, class1]
                if isinstance(sv, list) and len(sv) >= 2:
                    churn_shap = sv[1][0] if sv[1].ndim > 1 else sv[1]
                elif isinstance(sv, np.ndarray) and sv.ndim == 3:
                    churn_shap = sv[0, :, 1]
                elif isinstance(sv, np.ndarray) and sv.ndim == 2:
                    churn_shap = sv[0]
                elif isinstance(sv, np.ndarray):
                    churn_shap = sv
            except Exception as e:
                print(f"[SHAP] Error running TreeExplainer.shap_values: {e}")

        # Individual customer feature contributions
        if churn_shap is not None and len(churn_shap) > 0:
            abs_shap = np.abs(churn_shap)
            total_abs = float(np.sum(abs_shap)) if np.sum(abs_shap) > 0 else 1.0

            feature_contribs = []
            for i in range(min(len(churn_shap), len(names))):
                raw_feat = str(names[i]).replace("num__", "").replace("cat__", "")
                s_val = float(churn_shap[i])
                pct = round((abs(s_val) / total_abs) * 100, 1)

                friendly_name = FRIENDLY_LABELS.get(raw_feat, raw_feat.replace("_", " ").title())
                norm_val = float(row_vals[i]) if i < len(row_vals) and np.issubdtype(type(row_vals[i]), np.number) else 0.0
                display_val = format_feature_val(raw_feat, norm_val, raw_dict)

                if s_val > 0.005:
                    impact_label = "Increases Risk"
                    direction = "positive"
                elif s_val < -0.005:
                    impact_label = "Protects Account"
                    direction = "negative"
                else:
                    impact_label = "Neutral / Low Impact"
                    direction = "neutral"

                feature_contribs.append({
                    "feature": raw_feat,
                    "label": friendly_name,
                    "importance": round(abs(s_val), 4),
                    "shap_value": round(s_val, 4),
                    "importance_pct": f"{pct}%",
                    "contribution_val": pct,
                    "value": display_val,
                    "normalized_score": round(norm_val, 2),
                    "impact": impact_label,
                    "direction": direction
                })

            # Sort descending by absolute SHAP impact so the most influential drivers appear first
            feature_contribs.sort(key=lambda x: x["importance"], reverse=True)
            res = feature_contribs[:8]
            if cache_key:
                _shap_cache[cache_key] = res
            return res

    except Exception as e:
        print(f"[SHAP Engine Error] Could not compute individual SHAP explanations: {e}")

    # Fallback to feature importance if SHAP fails
    return []
