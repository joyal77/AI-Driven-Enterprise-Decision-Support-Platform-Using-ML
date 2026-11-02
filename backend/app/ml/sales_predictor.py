import os
import json
import warnings
import joblib
import pandas as pd
import numpy as np
import datetime
from datetime import timedelta
import xgboost as xgb
import sklearn.compose._column_transformer

warnings.filterwarnings("ignore", message=".*unpickle estimator.*")
warnings.filterwarnings("ignore", message=".*InconsistentVersionWarning.*")

# Monkeypatch missing class for scikit-learn version unpickling compatibility
class _RemainderColsList(list):
    pass

sklearn.compose._column_transformer._RemainderColsList = _RemainderColsList

def patch_pipeline(pipe):
    """Patch pipeline steps for scikit-learn unpickling compatibility."""
    if hasattr(pipe, 'named_steps'):
        for _, step_obj in pipe.named_steps.items():
            if hasattr(step_obj, 'transformers_'):
                for _, trans, _ in getattr(step_obj, 'transformers_', []):
                    if hasattr(trans, 'steps'):
                        for _, s_obj in trans.steps:
                            if hasattr(s_obj, '_fit_dtype') and not hasattr(s_obj, '_fill_dtype'):
                                setattr(s_obj, '_fill_dtype', getattr(s_obj, '_fit_dtype'))

# Paths configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(BASE_DIR)
BACKEND_DIR = os.path.dirname(APP_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
SALES_MODELS_DIR = os.path.join(PROJECT_ROOT, "models", "salesforecast")
CHURN_MODELS_DIR = os.path.join(PROJECT_ROOT, "models", "churn")

CLF_PATH = os.path.join(SALES_MODELS_DIR, "sales_classifier.joblib")
REG_PATH = os.path.join(SALES_MODELS_DIR, "sales_forecasting_model.joblib")
METADATA_PATH = os.path.join(SALES_MODELS_DIR, "forecast_metadata.json")
TIMESERIES_MODEL_PATH = os.path.join(CHURN_MODELS_DIR, "sales_model.json")

# Global instances
_sales_classifier = None
_sales_regressor = None
_sales_metadata = None
_timeseries_booster = None

def load_sales_models():
    """Loads the trained serialized models from disk in pure inference mode."""
    global _sales_classifier, _sales_regressor, _sales_metadata, _timeseries_booster
    if _sales_classifier is None and os.path.exists(CLF_PATH):
        try:
            _sales_classifier = joblib.load(CLF_PATH)
            patch_pipeline(_sales_classifier)
            print(f"[Sales ML] Loaded trained classifier pipeline from {CLF_PATH}")
        except Exception as e:
            print(f"[Sales ML Error] Failed loading classifier: {e}")

    if _sales_regressor is None and os.path.exists(REG_PATH):
        try:
            _sales_regressor = joblib.load(REG_PATH)
            patch_pipeline(_sales_regressor)
            print(f"[Sales ML] Loaded trained regressor pipeline from {REG_PATH}")
        except Exception as e:
            print(f"[Sales ML Error] Failed loading regressor: {e}")

    if _sales_metadata is None and os.path.exists(METADATA_PATH):
        try:
            with open(METADATA_PATH, "r") as f:
                _sales_metadata = json.load(f)
            print(f"[Sales ML] Loaded metadata from {METADATA_PATH}")
        except Exception as e:
            print(f"[Sales ML Error] Failed loading metadata: {e}")

    if _timeseries_booster is None and os.path.exists(TIMESERIES_MODEL_PATH):
        try:
            _timeseries_booster = xgb.Booster()
            _timeseries_booster.load_model(TIMESERIES_MODEL_PATH)
            print(f"[Sales ML] Loaded timeseries booster from {TIMESERIES_MODEL_PATH}")
        except Exception as e:
            print(f"[Sales ML Error] Failed loading timeseries booster: {e}")

    return _sales_classifier, _sales_regressor, _sales_metadata, _timeseries_booster

# Load models on module start
load_sales_models()

def get_sales_metadata():
    load_sales_models()
    return _sales_metadata or {
        "training_median_sales_revenue_threshold": 264.275,
        "feature_names": [
            "Store_ID", "Product_ID", "Category", "Units_Sold", "Unit_Price",
            "Discount_Percent", "Promotion_Flag", "Inventory_Level", "Day_Of_Week",
            "Month", "Holiday_Flag", "Marketing_Spend", "Competitor_Price", "Weather_Score"
        ]
    }

# =========================================================================
# CORE MODULE: NEXT 7, 14, 30 DAYS SALES FORECASTER
# =========================================================================

CATEGORY_WEIGHTS = {
    "Home & Kitchen": 0.158,
    "Electronics": 0.145,
    "Groceries": 0.124,
    "Apparel": 0.112,
    "Beverages": 0.098,
    "Snacks & Confectionery": 0.091,
    "Personal Care": 0.082,
    "Sports & Outdoors": 0.072,
    "Office Supplies": 0.061,
    "Household Supplies": 0.057
}

UPLOADED_PREVIOUS_SALES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "uploaded_previous_sales.csv"
)
UPLOADED_PREVIOUS_SALES_META_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "uploaded_previous_sales_meta.json"
)

def get_previous_sales_summary(df_daily: pd.DataFrame, total_raw_records: int = None, filename: str = None) -> dict:
    if df_daily.empty:
        return {"is_custom_history_loaded": False}

    if not filename and os.path.exists(UPLOADED_PREVIOUS_SALES_META_PATH):
        try:
            with open(UPLOADED_PREVIOUS_SALES_META_PATH, "r") as mf:
                meta = json.load(mf)
                filename = meta.get("filename", "uploaded_sales_data.csv")
        except Exception:
            filename = "uploaded_sales_data.csv"
    elif not filename:
        filename = "uploaded_sales_data.csv"

    start_date = df_daily['Date'].min()
    end_date = df_daily['Date'].max()
    total_rev = round(float(df_daily['daily_revenue'].sum()), 2)
    avg_daily = round(float(df_daily['daily_revenue'].mean()), 2)
    recent_7d = round(float(df_daily['daily_revenue'].tail(7).mean()), 2)
    recent_30d = round(float(df_daily['daily_revenue'].tail(30).mean()), 2)

    recent_tail = df_daily.tail(30).copy()
    recent_history = [
        {
            "date": d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d),
            "actual_revenue": round(float(r), 2),
            "revenue": round(float(r), 2),
            "is_weekend": (pd.to_datetime(d).weekday() in [5, 6]),
            "day_of_week": pd.to_datetime(d).strftime("%A")
        }
        for d, r in zip(recent_tail['Date'], recent_tail['daily_revenue'])
    ]

    return {
        "is_custom_history_loaded": True,
        "filename": filename,
        "total_raw_records": total_raw_records or len(df_daily),
        "total_historical_days": len(df_daily),
        "start_date": start_date.strftime("%Y-%m-%d") if hasattr(start_date, "strftime") else str(start_date),
        "end_date": end_date.strftime("%Y-%m-%d") if hasattr(end_date, "strftime") else str(end_date),
        "total_historical_revenue": total_rev,
        "total_revenue": total_rev,
        "average_daily_revenue": avg_daily,
        "avg_daily_revenue": avg_daily,
        "recent_7d_average": recent_7d,
        "recent_30d_average": recent_30d,
        "recent_history": recent_history
    }

def ingest_previous_sales_csv(df_raw: pd.DataFrame, filename: str = "uploaded_sales_data.csv") -> dict:
    if df_raw.empty:
        raise ValueError("The uploaded previous sales file is empty.")

    # Detect Date column
    date_candidates = ['date', 'Date', 'order_date', 'Order_Date', 'timestamp', 'Timestamp', 'invoice_date', 'Invoice_Date', 'sale_date', 'Sale_Date']
    found_date_col = next((c for c in date_candidates if c in df_raw.columns), None)
    if not found_date_col:
        for col in df_raw.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                found_date_col = col
                break

    if not found_date_col:
        raise ValueError("Could not find a 'Date' column in the uploaded dataset. Expected 'Date', 'Order_Date', or 'Timestamp'.")

    # Detect Sales / Revenue column
    rev_candidates = [
        'sales_revenue', 'Sales_Revenue', 'daily_revenue', 'Daily_Revenue',
        'revenue', 'Revenue', 'sales', 'Sales', 'total_amount', 'Total_Amount',
        'amount', 'Amount', 'total_spend', 'Total_Spend', 'net_sales', 'Net_Sales'
    ]
    found_rev_col = next((c for c in rev_candidates if c in df_raw.columns), None)
    if not found_rev_col:
        for col in df_raw.columns:
            if 'rev' in col.lower() or 'sales' in col.lower() or 'amount' in col.lower():
                found_rev_col = col
                break

    df_clean = df_raw.copy()
    df_clean['parsed_date'] = pd.to_datetime(df_clean[found_date_col], errors='coerce').dt.date
    df_clean = df_clean.dropna(subset=['parsed_date'])

    if df_clean.empty:
        raise ValueError("No valid date records could be parsed from the uploaded previous sales dataset.")

    if found_rev_col:
        if df_clean[found_rev_col].dtype == object:
            df_clean['clean_revenue'] = (
                df_clean[found_rev_col].astype(str)
                .str.replace('$', '', regex=False)
                .str.replace(',', '', regex=False)
                .str.strip()
            )
            df_clean['clean_revenue'] = pd.to_numeric(df_clean['clean_revenue'], errors='coerce').fillna(0.0)
        else:
            df_clean['clean_revenue'] = pd.to_numeric(df_clean[found_rev_col], errors='coerce').fillna(0.0)
    else:
        # Check if Units_Sold & Unit_Price exist
        units_col = next((c for c in df_clean.columns if 'unit' in c.lower() and 'sold' in c.lower()), None)
        price_col = next((c for c in df_clean.columns if 'price' in c.lower()), None)
        discount_col = next((c for c in df_clean.columns if 'disc' in c.lower()), None)
        if units_col and price_col:
            units = pd.to_numeric(df_clean[units_col], errors='coerce').fillna(1.0)
            price = pd.to_numeric(df_clean[price_col], errors='coerce').fillna(0.0)
            disc = pd.to_numeric(df_clean[discount_col], errors='coerce').fillna(0.0) if discount_col else 0.0
            df_clean['clean_revenue'] = units * price * (1.0 - disc / 100.0)
        else:
            raise ValueError("Could not find a 'Sales_Revenue' column or ('Units_Sold', 'Unit_Price') columns in the dataset.")

    # Group by Date
    df_daily = df_clean.groupby('parsed_date').agg(
        daily_revenue=('clean_revenue', 'sum'),
        records_count=('clean_revenue', 'count')
    ).reset_index().rename(columns={'parsed_date': 'Date'}).sort_values('Date')

    os.makedirs(os.path.dirname(UPLOADED_PREVIOUS_SALES_PATH), exist_ok=True)
    df_daily.to_csv(UPLOADED_PREVIOUS_SALES_PATH, index=False)
    try:
        with open(UPLOADED_PREVIOUS_SALES_META_PATH, "w") as mf:
            json.dump({
                "filename": filename,
                "uploaded_at": datetime.datetime.now().isoformat()
            }, mf)
    except Exception:
        pass

    return get_previous_sales_summary(df_daily, len(df_raw), filename=filename)

def get_previous_sales_status() -> dict:
    if os.path.exists(UPLOADED_PREVIOUS_SALES_PATH):
        try:
            df_daily = pd.read_csv(UPLOADED_PREVIOUS_SALES_PATH)
            df_daily['Date'] = pd.to_datetime(df_daily['Date']).dt.date
            return get_previous_sales_summary(df_daily)
        except Exception:
            return {"is_custom_history_loaded": False}
    return {"is_custom_history_loaded": False}

def clear_previous_sales_data() -> dict:
    if os.path.exists(UPLOADED_PREVIOUS_SALES_PATH):
        try:
            os.remove(UPLOADED_PREVIOUS_SALES_PATH)
        except Exception:
            pass
    if os.path.exists(UPLOADED_PREVIOUS_SALES_META_PATH):
        try:
            os.remove(UPLOADED_PREVIOUS_SALES_META_PATH)
        except Exception:
            pass
    return {"is_custom_history_loaded": False, "message": "Previous sales dataset cleared."}

def get_store_sales_history():
    """
    Extracts actual store checkouts from the database Order table.
    Generates a daily revenue series for the SmartCart live store without synthetic data.
    """
    daily_order_totals = {}
    total_orders = 0
    try:
        from ..db.session import SessionLocal
        from ..db.models import Order
        db = SessionLocal()
        orders = db.query(Order).filter(
            ~Order.order_status.in_(['cancelled', 'rejected'])
        ).order_by(Order.order_date.asc()).all()
        total_orders = len(orders)
        for o in orders:
            if o.order_date and o.order_amount is not None:
                d = o.order_date.date() if hasattr(o.order_date, 'date') else datetime.datetime.strptime(str(o.order_date)[:10], "%Y-%m-%d").date()
                daily_order_totals[d] = daily_order_totals.get(d, 0.0) + float(o.order_amount)
        db.close()
    except Exception as e:
        print("[Store Sales History Warning]", e)

    today = datetime.date.today()

    if not daily_order_totals:
        # Zero orders recorded
        df_store = pd.DataFrame([
            {"Date": today - timedelta(days=i), "daily_revenue": 0.0}
            for i in range(14, -1, -1)
        ])
        meta = {
            "total_orders": 0,
            "active_sales_days": 0,
            "low_volume": True,
            "data_limitations_notice": "No store orders recorded yet. Projections reflect zero-sales baseline."
        }
        return df_store, meta

    earliest_date = min(daily_order_totals.keys())
    start_timeline = min(earliest_date, today - timedelta(days=13))

    daily_records = []
    curr = start_timeline
    while curr <= today:
        rev = round(daily_order_totals.get(curr, 0.0), 2)
        daily_records.append({
            "Date": curr,
            "daily_revenue": rev
        })
        curr += timedelta(days=1)

    df_store = pd.DataFrame(daily_records)
    active_days = len(daily_order_totals)
    is_low_volume = total_orders < 15 or active_days < 14
    
    if is_low_volume:
        notice = f"SmartCart storefront sales history has early-stage transaction volume ({total_orders} order(s) across {active_days} active sales day(s)). Daily forecasts are baseline empirical projections with widened confidence intervals (+/- 35%) to reflect transaction variance without fabricating artificial data."
    else:
        notice = f"Storefront sales forecasting calibrated with {total_orders} historical transactions across {active_days} active sales days."

    meta = {
        "total_orders": total_orders,
        "active_sales_days": active_days,
        "low_volume": is_low_volume,
        "data_limitations_notice": notice
    }
    return df_store, meta

def generate_multi_horizon_sales_forecast(
    horizon_days: int = 7,
    baseline_sales: float = 5000.0,
    scenario_mode: str = "expected",
    start_date_str: str = None,
    use_uploaded_history: bool = True,
    source: str = "store"
):
    """
    Predicts sales for the Next 7, 14, or 30 Days using the time-series forecasting model.
    Steps day-by-day into the future with sequential lags, rolling statistics, and calendar cycles.
    Supports two independent data sources:
      1) 'store': Uses live SmartCart storefront shopping orders & transactions.
      2) 'uploaded': Uses uploaded previous sales dataset CSV (strictly requires upload).
    """
    load_sales_models()
    if hasattr(horizon_days, "default"):
        horizon_days = horizon_days.default
    horizon_days = int(horizon_days)

    if hasattr(baseline_sales, "default"):
        baseline_sales = baseline_sales.default
    baseline_sales = float(baseline_sales)

    if hasattr(scenario_mode, "default"):
        scenario_mode = scenario_mode.default
    scenario_mode = str(scenario_mode)

    if hasattr(start_date_str, "default"):
        start_date_str = start_date_str.default

    if hasattr(source, "default"):
        source = source.default
    source = str(source).lower() if source else "store"

    # Restrict to valid horizons
    if horizon_days not in [7, 14, 30]:
        horizon_days = 7 if horizon_days <= 10 else (14 if horizon_days <= 20 else 30)

    # 1. Source: Uploaded CSV Dataset
    if source == "uploaded":
        uploaded_history_summary = get_previous_sales_status() if use_uploaded_history else {"is_custom_history_loaded": False}
        has_uploaded_history = uploaded_history_summary.get("is_custom_history_loaded", False)

        if not (has_uploaded_history and os.path.exists(UPLOADED_PREVIOUS_SALES_PATH)):
            return {
                "source": "uploaded",
                "source_label": "Uploaded Previous Sales CSV Dataset",
                "horizon_days": horizon_days,
                "scenario_mode": scenario_mode,
                "total_forecasted_revenue": 0.0,
                "average_daily_revenue": 0.0,
                "generated_at": datetime.datetime.now().isoformat(),
                "has_data": False,
                "is_custom_history_loaded": False,
                "message": "No previous sales data uploaded. Please upload a previous sales dataset CSV to generate forecasts.",
                "start_date": None,
                "end_date": None,
                "summary": {
                    "total_forecasted_revenue": 0.0,
                    "average_daily_revenue": 0.0
                },
                "category_projections": [],
                "schedule": [],
                "forecast_schedule": [],
                "history_summary": None,
                "historical_recent_schedule": []
            }

        df_hist = pd.read_csv(UPLOADED_PREVIOUS_SALES_PATH)
        df_hist['Date'] = pd.to_datetime(df_hist['Date']).dt.date
        hist_summary = uploaded_history_summary
        source_label = "Uploaded Previous Sales CSV Dataset"
        is_low_volume = len(df_hist) < 14
        data_limitations_notice = (
            f"Uploaded dataset contains {len(df_hist)} historical days (< 14 days). Wider confidence intervals (+/- 35%) applied."
            if is_low_volume else ""
        )

    # 2. Source: SmartCart Live Website Transactions
    else:
        df_hist, store_meta = get_store_sales_history()
        source = "store"
        source_label = "SmartCart Live Storefront Transactions"
        is_low_volume = store_meta.get("low_volume", False)
        data_limitations_notice = store_meta.get("data_limitations_notice", "")
        hist_summary = get_previous_sales_summary(
            df_hist,
            total_raw_records=store_meta.get("total_orders", len(df_hist)),
            filename="SmartCart Live Storefront Orders"
        )
        hist_summary.update({
            "total_orders": store_meta.get("total_orders", 0),
            "active_sales_days": store_meta.get("active_sales_days", 0),
            "low_transaction_volume": is_low_volume,
            "data_limitation_notice": data_limitations_notice,
            "total_revenue": hist_summary.get("total_historical_revenue", 0.0),
            "avg_daily_revenue": hist_summary.get("average_daily_revenue", 0.0),
        })

    hist_revs = [float(x) for x in df_hist['daily_revenue'].values]
    last_hist_date = df_hist['Date'].max()

    if not start_date_str:
        start_date = last_hist_date + timedelta(days=1)
    else:
        try:
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except Exception:
            start_date = last_hist_date + timedelta(days=1)

    # Ensure at least 35 elements for 30d lags using empirical average
    if len(hist_revs) < 35:
        pad_val = float(np.mean(hist_revs)) if hist_revs else 0.0
        hist_revs = [pad_val] * (35 - len(hist_revs)) + hist_revs

    revs = list(hist_revs)
    base = max(100.0, float(np.mean(revs[-7:])))

    multiplier = 1.0
    if scenario_mode == "conservative":
        multiplier = 0.90
    elif scenario_mode == "optimistic":
        multiplier = 1.15

    ci_factor = 0.35 if is_low_volume else 0.12
    future_schedule = []
    ts_features = ['Year', 'Month', 'Day', 'Weekday', 'Quarter', 'Week', 'Lag_1', 'Lag_7', 'Lag_30', 'Rolling_7', 'Rolling_30', 'Rolling_STD_7']

    for step in range(1, horizon_days + 1):
        target_date = start_date + timedelta(days=step - 1)

        lag_1 = float(revs[-1])
        lag_7 = float(revs[-7])
        lag_30 = float(revs[-30])
        rolling_7 = float(np.mean(revs[-7:]))
        rolling_30 = float(np.mean(revs[-30:]))
        rolling_std_7 = float(np.std(revs[-7:]))

        feat_dict = {
            'Year': target_date.year,
            'Month': target_date.month,
            'Day': target_date.day,
            'Weekday': target_date.weekday(),
            'Quarter': (target_date.month - 1) // 3 + 1,
            'Week': int(target_date.isocalendar()[1]),
            'Lag_1': lag_1,
            'Lag_7': lag_7,
            'Lag_30': lag_30,
            'Rolling_7': rolling_7,
            'Rolling_30': rolling_30,
            'Rolling_STD_7': rolling_std_7
        }

        # Predict day step
        if _timeseries_booster is not None and not is_low_volume:
            df_step = pd.DataFrame([feat_dict])[ts_features]
            dmat = xgb.DMatrix(df_step)
            raw_pred = float(_timeseries_booster.predict(dmat)[0])
            pred_rev = max(0.0, round(raw_pred * multiplier, 2))
        else:
            dow_weight = 1.20 if target_date.weekday() in [4, 5] else 0.95
            pred_rev = max(0.0, round((0.5 * lag_1 + 0.3 * rolling_7 + 0.2 * rolling_30) * dow_weight * multiplier, 2))

        revs.append(pred_rev)

        is_weekend = target_date.weekday() in [4, 5, 6] # Fri, Sat, Sun
        demand_status = "Peak Demand" if pred_rev > (base * 1.25) else ("High Demand" if pred_rev > base else "Normal")

        lower_bound = max(0.0, round(pred_rev * (1.0 - ci_factor), 2))
        upper_bound = round(pred_rev * (1.0 + ci_factor), 2)

        future_schedule.append({
            "day_number": step,
            "date": target_date.strftime("%Y-%m-%d"),
            "day_of_week": target_date.strftime("%A"),
            "is_weekend": is_weekend,
            "forecasted_revenue": pred_rev,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "confidence_interval_width": f"+/- {int(ci_factor * 100)}%",
            "demand_status": demand_status,
            "rolling_trend_7d": round(rolling_7, 2)
        })

    total_revenue = round(sum(d["forecasted_revenue"] for d in future_schedule), 2)
    avg_daily = round(total_revenue / horizon_days, 2)
    peak_day = max(future_schedule, key=lambda x: x["forecasted_revenue"])
    lowest_day = min(future_schedule, key=lambda x: x["forecasted_revenue"])

    weekend_days = [d["forecasted_revenue"] for d in future_schedule if d["is_weekend"]]
    weekday_days = [d["forecasted_revenue"] for d in future_schedule if not d["is_weekend"]]
    weekend_avg = np.mean(weekend_days) if weekend_days else avg_daily
    weekday_avg = np.mean(weekday_days) if weekday_days else avg_daily
    weekend_lift_pct = round(((weekend_avg - weekday_avg) / weekday_avg * 100), 1) if weekday_avg > 0 else 0.0

    # Projected Category Breakdown
    category_projections = [
        {
            "category": cat,
            "share_pct": round(weight * 100, 1),
            "projected_revenue": round(total_revenue * weight, 2)
        }
        for cat, weight in CATEGORY_WEIGHTS.items()
    ]

    return {
        "horizon_days": horizon_days,
        "scenario_mode": scenario_mode,
        "start_date": future_schedule[0]["date"],
        "end_date": future_schedule[-1]["date"],
        "total_forecasted_revenue": total_revenue,
        "average_daily_revenue": avg_daily,
        "generated_at": datetime.datetime.now().isoformat(),
        "low_transaction_volume": is_low_volume,
        "data_limitation_notice": data_limitations_notice,
        "summary": {
            "total_forecasted_revenue": total_revenue,
            "average_daily_revenue": avg_daily,
            "low_transaction_volume": is_low_volume,
            "data_limitation_notice": data_limitations_notice,
            "peak_day": {
                "day_number": peak_day["day_number"],
                "date": peak_day["date"],
                "day_of_week": peak_day["day_of_week"],
                "forecasted_revenue": peak_day["forecasted_revenue"]
            },
            "lowest_day": {
                "day_number": lowest_day["day_number"],
                "date": lowest_day["date"],
                "day_of_week": lowest_day["day_of_week"],
                "forecasted_revenue": lowest_day["forecasted_revenue"]
            },
            "weekend_sales_lift_pct": weekend_lift_pct
        },
        "category_projections": category_projections,
        "schedule": future_schedule,
        "forecast_schedule": future_schedule,
        "has_data": True,
        "is_custom_history_loaded": True,
        "source": source,
        "source_label": source_label,
        "history_summary": hist_summary,
        "historical_recent_schedule": hist_summary.get("recent_history", [])
    }

# =========================================================================
# SECONDARY SCENARIO AND BATCH FORECASTERS
# =========================================================================

def standardize_input_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    meta = get_sales_metadata()
    feature_names = meta.get("feature_names", [
        "Store_ID", "Product_ID", "Category", "Units_Sold", "Unit_Price",
        "Discount_Percent", "Promotion_Flag", "Inventory_Level", "Day_Of_Week",
        "Month", "Holiday_Flag", "Marketing_Spend", "Competitor_Price", "Weather_Score"
    ])
    df_clean = df.copy()
    col_mapping = {col.lower(): col for col in df_clean.columns}
    for feat in feature_names:
        if feat not in df_clean.columns:
            if feat.lower() in col_mapping:
                df_clean[feat] = df_clean[col_mapping[feat.lower()]]
            else:
                if feat in ["Units_Sold", "Month"]:
                    df_clean[feat] = 10 if feat == "Units_Sold" else 6
                elif feat in ["Promotion_Flag", "Holiday_Flag"]:
                    df_clean[feat] = 0
                elif feat in ["Inventory_Level"]:
                    df_clean[feat] = 100
                elif feat in ["Unit_Price", "Competitor_Price"]:
                    df_clean[feat] = 25.0
                elif feat in ["Discount_Percent", "Marketing_Spend"]:
                    df_clean[feat] = 5.0
                elif feat == "Weather_Score":
                    df_clean[feat] = 7.0
                elif feat == "Store_ID":
                    df_clean[feat] = "STORE_01"
                elif feat == "Category":
                    df_clean[feat] = "Electronics"
                elif feat == "Product_ID":
                    df_clean[feat] = "PROD_001"
                elif feat == "Day_Of_Week":
                    df_clean[feat] = "Monday"
    return df_clean[feature_names]

def predict_new_scenario(data: dict):
    load_sales_models()
    if _sales_classifier is None or _sales_regressor is None:
        raise RuntimeError("Sales forecasting models are not loaded.")

    meta = get_sales_metadata()
    threshold = meta.get("training_median_sales_revenue_threshold", 264.275)

    df_input = pd.DataFrame([data])
    df_standard = standardize_input_dataframe(df_input)

    clf_pred = int(_sales_classifier.predict(df_standard)[0])
    probabilities = {}
    if hasattr(_sales_classifier, "predict_proba"):
        prob_vals = _sales_classifier.predict_proba(df_standard)[0]
        probabilities = {
            "low_sales_probability": float(round(prob_vals[0], 4)),
            "high_sales_probability": float(round(prob_vals[1], 4))
        }

    reg_raw = float(_sales_regressor.predict(df_standard)[0])
    forecasted_revenue = max(0.0, round(reg_raw, 2))
    lift_pct = round(((forecasted_revenue - threshold) / threshold) * 100, 2)

    return {
        "forecasted_revenue": forecasted_revenue,
        "forecasted_sales_tier": "High Sales Volume" if clf_pred == 1 else "Low Sales Volume",
        "classification_prediction": clf_pred,
        "probabilities": probabilities,
        "historical_median_baseline": threshold,
        "lift_over_baseline_pct": lift_pct,
        "input_features": df_standard.iloc[0].to_dict()
    }

def predict_batch_dataset(df_raw: pd.DataFrame):
    load_sales_models()
    if _sales_classifier is None or _sales_regressor is None:
        raise RuntimeError("Sales forecasting models are not loaded.")

    meta = get_sales_metadata()
    threshold = meta.get("training_median_sales_revenue_threshold", 264.275)
    df_standard = standardize_input_dataframe(df_raw)

    clf_preds = _sales_classifier.predict(df_standard)
    reg_preds = _sales_regressor.predict(df_standard)

    probs = [0.5] * len(df_standard)
    if hasattr(_sales_classifier, "predict_proba"):
        probs = [round(float(p[1]), 4) for p in _sales_classifier.predict_proba(df_standard)]

    df_result = df_raw.copy()
    df_result["Forecasted_Revenue"] = [max(0.0, round(float(r), 2)) for r in reg_preds]
    df_result["Forecasted_Sales_Tier"] = ["High Sales Volume" if c == 1 else "Low Sales Volume" for c in clf_preds]
    df_result["High_Sales_Probability"] = probs
    df_result["Lift_vs_Baseline_Pct"] = [round(((r - threshold) / threshold) * 100, 1) for r in df_result["Forecasted_Revenue"]]

    total_forecasted = round(float(df_result["Forecasted_Revenue"].sum()), 2)
    avg_per_item = round(float(df_result["Forecasted_Revenue"].mean()), 2)
    high_volume_count = int(sum(clf_preds == 1))
    low_volume_count = int(sum(clf_preds == 0))

    return {
        "summary": {
            "total_items_scored": len(df_result),
            "total_forecasted_revenue": total_forecasted,
            "average_forecast_per_item": avg_per_item,
            "high_volume_items_count": high_volume_count,
            "low_volume_items_count": low_volume_count,
            "high_volume_percentage": round(high_volume_count / len(df_result) * 100, 1) if len(df_result) > 0 else 0.0
        },
        "scored_records": df_result.to_dict(orient="records")
    }

def get_static_options():
    return {
        "stores": [f"STORE_{i:02d}" for i in range(1, 11)],
        "categories": [
            "Home & Kitchen", "Electronics", "Groceries", "Apparel", "Beverages",
            "Snacks & Confectionery", "Personal Care", "Office Supplies", "Household Supplies", "Sports & Outdoors"
        ],
        "products": [f"PROD_{i:03d}" for i in range(1, 51)],
        "days_of_week": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    }

# Backward compatibility aliases
predict_single_transaction = predict_new_scenario
forecast_planned_scenario = predict_new_scenario
get_forward_time_series_forecast = generate_multi_horizon_sales_forecast
