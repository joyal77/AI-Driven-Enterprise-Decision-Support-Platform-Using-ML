import sys
import os
import io

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
    load_dotenv(os.path.join(PROJECT_ROOT, "backend", ".env"))
except ImportError:
    pass

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("=" * 75)
print(" APPLICATION REGRESSION & END-TO-END VERIFICATION SUITE")
print("=" * 75)

test_results = []

def run_test(name, func):
    try:
        res = func()
        print(f" [PASS] {name}: {res}")
        test_results.append((name, "PASS", res))
    except Exception as e:
        print(f" [FAIL] {name}: {e}")
        test_results.append((name, "FAIL", str(e)))

# 1. Health
def test_health():
    r = client.get("/health")
    assert r.status_code == 200, f"Status: {r.status_code}"
    return f"Service={r.json().get('service')}, DB={r.json().get('database')}"
run_test("Health Endpoint", test_health)

# 2. Executive Dashboard KPIs
def test_dashboard_kpis():
    r = client.get("/api/dashboard/kpis")
    assert r.status_code == 200, f"Status: {r.status_code}"
    data = r.json()
    return f"Total Customers={data.get('total_customers')}, Analyzed={data.get('analyzed_customers')}, High Risk={data.get('high_risk_count')}"
run_test("Executive Dashboard KPIs", test_dashboard_kpis)

# 3. Executive Dashboard Churn Summary
def test_churn_summary():
    r = client.get("/api/dashboard/churn-summary")
    assert r.status_code == 200, f"Status: {r.status_code}"
    return f"Breakdown Categories={len(r.json().get('membership_breakdown', []))}"
run_test("Dashboard Churn Summary", test_churn_summary)

# 4. Customer Listing & RFM
def test_customer_list():
    r = client.get("/api/customers?limit=10")
    assert r.status_code == 200, f"Status: {r.status_code}"
    custs = r.json().get("customers", [])
    return f"Retrieved {len(custs)} customers, Total={r.json().get('total')}"
run_test("Customer Management (Pagination & List)", test_customer_list)

# 5. Customer Details & Features
def test_customer_detail():
    r = client.get("/api/customers/1")
    assert r.status_code == 200, f"Status: {r.status_code}"
    return f"Cust ID={r.json().get('id')}, Source={r.json().get('source_customer_id')}"
run_test("Customer Detail & RFM Metrics", test_customer_detail)

# 6. Store Products
def test_store_products():
    r = client.get("/api/store/products")
    assert r.status_code == 200, f"Status: {r.status_code}"
    prods = r.json().get("products", [])
    return f"Active Catalog Items={len(prods)}"
run_test("SmartCart Product Catalog", test_store_products)

# 7. Store Orders My-Orders
def test_store_orders():
    r = client.get("/api/store/orders/my-orders?customer_id=1")
    assert r.status_code == 200, f"Status: {r.status_code}"
    return f"Retrieved {len(r.json())} customer orders for ID=1"
run_test("Storefront Orders Endpoint", test_store_orders)

# 8. Churn Prediction & Model Inference
def test_ml_prediction():
    payload = {
        "customer_age": 35,
        "days_since_last_purchase": 45,
        "total_orders_lifetime": 8,
        "orders_last_30d": 1,
        "total_spend_inr": 8500.0,
        "avg_order_value": 1062.5,
        "return_count": 1,
        "cancellations_count": 0,
        "membership_status": "Gold",
        "city_tier": "Tier 1",
        "preferred_category": "Electronics"
    }
    r = client.post("/api/predict-churn", json=payload)
    assert r.status_code == 200, f"Status: {r.status_code}, Body: {r.text}"
    prob = r.json().get("churn_probability")
    risk = r.json().get("risk_category")
    return f"Churn Prob={prob}, Risk={risk}"
run_test("Random Forest Churn Prediction", test_ml_prediction)

# 9. Customer Churn Prediction Details & Root Causes
def test_churn_prediction_detail():
    r = client.get("/api/churn-predictions/1")
    assert r.status_code == 200, f"Status: {r.status_code}"
    data = r.json()
    return f"Risk Category={data.get('risk_category')}, Prob={data.get('churn_probability')}"
run_test("Customer Churn Prediction Detail", test_churn_prediction_detail)

# 10. Decision Engine Retention Perks
def test_retention_perks():
    r = client.get("/api/customers/1/retention-perks")
    assert r.status_code == 200, f"Status: {r.status_code}"
    perks = r.json().get("perks", [])
    return f"Retrieved {len(perks)} customer retention perks"
run_test("Decision Engine Retention Perks", test_retention_perks)

# 11. Multi-Horizon Sales Forecasting (XGBoost)
def test_sales_forecasting():
    r = client.get("/api/sales-forecast/horizon-forecast?horizon=7")
    assert r.status_code == 200, f"Status: {r.status_code}"
    total_orders = r.json().get("metadata", {}).get("total_orders", 0)
    return f"Horizon=7 Days, Historical Store Orders Analysed={total_orders}"
run_test("XGBoost Multi-Horizon Sales Forecasting", test_sales_forecasting)

# 12. PDF Report Generator
def test_pdf_generation():
    from backend.app.services.pdf_generator import generate_sales_forecast_pdf
    forecast_data = {
        "horizon_days": 7,
        "total_projected_sales": 35000.0,
        "daily_forecast": [{"day": i, "date": f"2026-11-0{i}", "projected_sales": 5000.0} for i in range(1, 8)],
        "baseline_sales": 4800.0,
        "scenario_mode": "expected"
    }
    buf = generate_sales_forecast_pdf(forecast_data)
    pdf_bytes = buf.getvalue()
    assert len(pdf_bytes) > 1000, "PDF bytes too small"
    return f"Generated Sales Forecast PDF ({len(pdf_bytes):,} bytes)"
run_test("ReportLab Executive PDF Generation", test_pdf_generation)

print("\n" + "=" * 75)
pass_count = sum(1 for _, s, _ in test_results if s == "PASS")
fail_count = sum(1 for _, s, _ in test_results if s == "FAIL")
print(f" SUMMARY: {pass_count} PASSED, {fail_count} FAILED out of {len(test_results)} Tests")
print("=" * 75)
sys.exit(0 if fail_count == 0 else 1)
