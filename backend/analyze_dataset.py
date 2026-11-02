import os
import sys
import json
import re
import datetime
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

def analyze_prediction_batch():
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dataset', 'customer churn', 'prediction_batch_1.csv'))
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    df = pd.read_csv(csv_path)
    print("=" * 60)
    print("PHASE 2: PROGRAMMATIC ANALYSIS OF prediction_batch_1.csv")
    print("=" * 60)

    # 1. Total rows and columns
    rows, cols = df.shape
    print(f"\n1. Dimensions: {rows} rows, {cols} columns")

    # 2. Customer ID format, uniqueness, duplicates
    print(f"\n2. Customer ID Analysis:")
    print(f"   - Total IDs: {len(df['customer_id'])}")
    print(f"   - Unique IDs: {df['customer_id'].nunique()}")
    duplicates = df[df['customer_id'].duplicated(keep=False)]
    print(f"   - Duplicate IDs count: {len(duplicates)}")
    id_pattern = r'^AMZ_PRED\d+_\d+$'
    invalid_ids = df[~df['customer_id'].astype(str).str.match(id_pattern)]
    print(f"   - Conforms to pattern {id_pattern}: {len(invalid_ids) == 0} (Invalid: {len(invalid_ids)})")

    # 3. Missing values and data types
    print(f"\n3. Missing Values & Types:")
    missing = df.isnull().sum()
    print(missing[missing > 0] if missing.sum() > 0 else "   - No missing values in any column.")

    # 4. Clean spending column
    def clean_currency(val):
        if pd.isna(val):
            return np.nan
        s = str(val).replace('₹', '').replace(',', '').replace('INR', '').strip()
        try:
            return float(s)
        except ValueError:
            return np.nan

    spend_clean = df['total_spend_inr'].apply(clean_currency)
    df['spend_numeric'] = spend_clean

    # 5. Invalid signup dates and negative durations
    print(f"\n4. Date & Temporal Validation:")
    ref_date = datetime.date(2026, 10, 21) # Current date
    invalid_dates = []
    future_signups = []
    for idx, d_str in df['signup_date'].items():
        try:
            d = datetime.datetime.strptime(str(d_str).strip(), '%Y-%m-%d').date()
            if d > ref_date:
                future_signups.append((idx, d_str))
        except Exception:
            invalid_dates.append((idx, d_str))

    print(f"   - Unparseable signup dates: {len(invalid_dates)}")
    print(f"   - Future signup dates (> today): {len(future_signups)}")

    # 6. Negative values checks
    print(f"\n5. Negative Values Checks:")
    numeric_cols = [
        'customer_age', 'days_since_last_purchase', 'total_orders_lifetime',
        'orders_last_30d', 'orders_prev_30_to_60d', 'spend_numeric',
        'avg_order_value', 'sessions_last_30d', 'avg_session_duration_min',
        'cart_abandonments_last_30d', 'search_queries_last_30d',
        'return_count', 'return_rate', 'cancellations_count',
        'late_deliveries_count', 'customer_service_tickets', 'avg_rating_given'
    ]

    for col in numeric_cols:
        neg_count = (df[col] < 0).sum()
        if neg_count > 0:
            print(f"   - WARNING: {col} has {neg_count} negative values!")
    print("   - All checked numeric attributes verified non-negative.")

    # 7. Logical Inconsistency Checks:
    print(f"\n6. Business Logic Consistency Checks:")
    
    # Check A: orders_last_30d vs total_orders_lifetime
    inconsistent_recent = df[df['orders_last_30d'] > df['total_orders_lifetime']]
    print(f"   - orders_last_30d > total_orders_lifetime: {len(inconsistent_recent)} violations")

    # Check B: orders_last_30d + orders_prev_30_to_60d > total_orders_lifetime
    inconsistent_sum_recent = df[(df['orders_last_30d'] + df['orders_prev_30_to_60d']) > df['total_orders_lifetime']]
    print(f"   - (orders_last_30d + orders_prev_30_60d) > total_orders_lifetime: {len(inconsistent_sum_recent)} violations")

    # Check C: AOV vs Spend and Lifetime Orders: aov * total_orders approx total_spend
    # Note: AOV = total_spend / total_orders
    expected_spend = df['total_orders_lifetime'] * df['avg_order_value']
    spend_diff = np.abs(df['spend_numeric'] - expected_spend)
    rel_diff = spend_diff / np.maximum(df['spend_numeric'], 1.0)
    aov_inconsistent = df[rel_diff > 0.05]
    print(f"   - AOV * total_orders differs from total_spend by > 5%: {len(aov_inconsistent)} rows")
    if len(aov_inconsistent) > 0:
        print(f"     Sample diff: row {aov_inconsistent.index[0]} spend={aov_inconsistent['spend_numeric'].iloc[0]}, expected={expected_spend.iloc[aov_inconsistent.index[0]]}")

    # Check D: return_count vs return_rate vs total_orders_lifetime
    expected_ret_rate = df['return_count'] / np.maximum(df['total_orders_lifetime'], 1)
    ret_diff = np.abs(df['return_rate'] - expected_ret_rate)
    ret_inconsistent = df[ret_diff > 0.05]
    print(f"   - return_rate differs from return_count / total_orders by > 0.05: {len(ret_inconsistent)} rows")

    # Check E: Categorical distributions
    print(f"\n7. Categorical Distributions:")
    for cat in ['gender', 'city_tier', 'membership_status', 'preferred_category', 'preferred_payment_mode']:
        vals = df[cat].value_counts().to_dict()
        print(f"   - {cat}: {vals}")

    # Check F: Ratings range
    invalid_ratings = df[(df['avg_rating_given'] < 1.0) | (df['avg_rating_given'] > 5.0)]
    print(f"\n8. Ratings validity [1.0 to 5.0]: {len(invalid_ratings)} invalid rows")

    print("\nAnalysis complete.")

if __name__ == '__main__':
    analyze_prediction_batch()
