import os
import sys
import sqlite3
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

def inspect_db():
    db_path = os.path.join(os.path.dirname(__file__), 'ecommerce_churn.db')
    if not os.path.exists(db_path):
        print("Database not found at", db_path)
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print("=== TABLES IN DB ===")
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]
    print(tables)

    print("\n=== TOTAL COUNTS ===")
    for t in ['customers', 'store_users', 'orders', 'order_items', 'churn_predictions', 'retention_recommendations', 'products']:
        if t in tables:
            c.execute(f"SELECT COUNT(*) FROM {t}")
            print(f"{t}: {c.fetchone()[0]}")

    print("\n=== CUSTOMER AMZ_PRED1_1041 ===")
    c.execute("SELECT id, source_customer_id, total_orders_lifetime, total_spend_inr, days_since_last_purchase, signup_date FROM customers WHERE source_customer_id = 'AMZ_PRED1_1041'")
    cust = c.fetchone()
    print("Customer row:", cust)

    if cust:
        cid = cust[0]
        c.execute("SELECT id, username, role, customer_id, full_name FROM store_users WHERE customer_id = ? OR username = 'AMZ_PRED1_1041'", (cid,))
        print("Store user accounts:", c.fetchall())

        c.execute("SELECT id, order_number, customer_id, order_date, order_amount, order_status FROM orders")
        all_orders = c.fetchall()
        print(f"\nAll orders in orders table ({len(all_orders)} total):", all_orders)

        c.execute("SELECT id, churn_probability, risk_category, model_version, prediction_timestamp FROM churn_predictions WHERE customer_id = ?", (cid,))
        print("Churn prediction row:", c.fetchall())

    conn.close()

def inspect_csv():
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dataset', 'customer churn', 'prediction_batch_1.csv'))
    if not os.path.exists(csv_path):
        print("CSV not found at", csv_path)
        return

    print("\n=== ANALYZING prediction_batch_1.csv ===")
    df = pd.read_csv(csv_path)
    print("Shape:", df.shape)
    print("Columns:", list(df.columns))
    print("Unique customer_ids:", df['customer_id'].nunique())
    print("Any duplicate customer_ids?:", df['customer_id'].duplicated().any())
    if df['customer_id'].duplicated().any():
        dups = df[df['customer_id'].duplicated(keep=False)]
        print("Duplicate rows count:", len(dups))
        print(dups[['customer_id']].head(10))

    # Look for AMZ_PRED1_1041
    cust_1041 = df[df['customer_id'] == 'AMZ_PRED1_1041']
    print("\nRow for AMZ_PRED1_1041 in prediction_batch_1.csv:")
    if not cust_1041.empty:
        print(cust_1041.to_dict(orient='records')[0])
    else:
        print("AMZ_PRED1_1041 NOT found in prediction_batch_1.csv")

    # Check raw_ecommerce_churn_10k.csv if it exists
    raw_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dataset', 'raw_ecommerce_churn_10k.csv'))
    if os.path.exists(raw_csv):
        print("\n=== ANALYZING raw_ecommerce_churn_10k.csv ===")
        df_raw = pd.read_csv(raw_csv)
        print("Raw shape:", df_raw.shape)
        c_raw_1041 = df_raw[df_raw['customer_id'] == 'AMZ_PRED1_1041']
        if not c_raw_1041.empty:
            print("Raw 10k row for AMZ_PRED1_1041:")
            print(c_raw_1041.to_dict(orient='records')[0])

if __name__ == '__main__':
    inspect_db()
    inspect_csv()
