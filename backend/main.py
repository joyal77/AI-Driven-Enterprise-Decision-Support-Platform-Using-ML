import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.db.session import engine, Base
from backend.app.api import (
    auth, dashboard, churn, customers, model_info, recommendations,
    upload, reports, sales_forecast, store_auth, store_products, store_orders, store_cart,
    store_admin, store_notifications
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema exists on startup
    print("[Startup] Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    print("[Startup] Database tables initialized.")
    try:
        from sqlalchemy import text
        if engine.name == "sqlite":
            with engine.connect() as conn:
                # Check customer_retention_perks
                try:
                    res = conn.execute(text("PRAGMA table_info(customer_retention_perks)")).fetchall()
                    cols = [r[1] for r in res] if res else []
                    if cols and "free_shipping" not in cols:
                        conn.execute(text("ALTER TABLE customer_retention_perks ADD COLUMN free_shipping INTEGER DEFAULT 0"))
                        conn.commit()
                    if cols and "coupon_used" not in cols:
                        conn.execute(text("ALTER TABLE customer_retention_perks ADD COLUMN coupon_used INTEGER DEFAULT 0"))
                        conn.commit()
                    if cols and "shipping_used" not in cols:
                        conn.execute(text("ALTER TABLE customer_retention_perks ADD COLUMN shipping_used INTEGER DEFAULT 0"))
                        conn.commit()
                    if cols and "used_order_id" not in cols:
                        conn.execute(text("ALTER TABLE customer_retention_perks ADD COLUMN used_order_id INTEGER NULL"))
                        conn.commit()
                    if cols and "used_at" not in cols:
                        conn.execute(text("ALTER TABLE customer_retention_perks ADD COLUMN used_at TIMESTAMP NULL"))
                        conn.commit()
                    if cols and "is_single_use" not in cols:
                        conn.execute(text("ALTER TABLE customer_retention_perks ADD COLUMN is_single_use INTEGER DEFAULT 1"))
                        conn.commit()
                except Exception:
                    pass
                # Check orders
                try:
                    res = conn.execute(text("PRAGMA table_info(orders)")).fetchall()
                    cols = [r[1] for r in res] if res else []
                    if cols and "voucher_code" not in cols:
                        conn.execute(text("ALTER TABLE orders ADD COLUMN voucher_code VARCHAR(50) NULL"))
                        conn.commit()
                    if cols and "wallet_credit_used" not in cols:
                        conn.execute(text("ALTER TABLE orders ADD COLUMN wallet_credit_used FLOAT DEFAULT 0.0"))
                        conn.commit()
                    if cols and "free_shipping_applied" not in cols:
                        conn.execute(text("ALTER TABLE orders ADD COLUMN free_shipping_applied INTEGER DEFAULT 0"))
                        conn.commit()
                except Exception:
                    pass
                # Check customer_notifications
                try:
                    res = conn.execute(text("PRAGMA table_info(customer_notifications)")).fetchall()
                    cols = [r[1] for r in res] if res else []
                    if cols and "notification_type" not in cols:
                        conn.execute(text("ALTER TABLE customer_notifications ADD COLUMN notification_type VARCHAR(50) DEFAULT 'retention_perk'"))
                        conn.commit()
                    if cols and "navigation_target" not in cols:
                        conn.execute(text("ALTER TABLE customer_notifications ADD COLUMN navigation_target VARCHAR(255) DEFAULT '/store/cart'"))
                        conn.commit()
                    if cols and "image_url" not in cols:
                        conn.execute(text("ALTER TABLE customer_notifications ADD COLUMN image_url VARCHAR(500) NULL"))
                        conn.commit()
                except Exception:
                    pass
    except Exception as e:
        print(f"[Startup Warning] Schema migration check: {e}")
    try:
        from backend.app.db.session import SessionLocal
        from backend.app.services.customer_feature_service import ensure_live_store_customers_seeded
        init_db = SessionLocal()
        ensure_live_store_customers_seeded(init_db)
        init_db.close()
    except Exception as e:
        print(f"[Startup Warning] Could not verify live store customers: {e}")

    # Background warmup for ML TreeExplainer to eliminate cold-start delay
    import threading
    def _warmup_ml():
        try:
            from backend.app.ml.model_loader import get_ml_artifacts
            from backend.app.ml.shap_engine import get_tree_explainer
            rf, _, _, _ = get_ml_artifacts()
            if rf is not None:
                get_tree_explainer(rf)
                print("[Startup] TreeExplainer initialized and warmed up in background.")
        except Exception as e:
            print(f"[Startup Warning] Background ML warmup error: {e}")
    threading.Thread(target=_warmup_ml, daemon=True).start()

    print("[Startup] System ready for ML prediction & store interactions.")
    yield

app = FastAPI(
    title="Enterprise Decision Support & Analytics Platform API",
    description="Enterprise Machine Learning Decision Support: Churn Analytics & Sales Forecasting System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "smartcart-backend",
        "database": engine.name
    }

# Include API Routers with /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(churn.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(model_info.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(sales_forecast.router, prefix="/api")
app.include_router(store_auth.router, prefix="/api")
app.include_router(store_products.router, prefix="/api")
app.include_router(store_orders.router, prefix="/api")
app.include_router(store_cart.router, prefix="/api")
app.include_router(store_admin.router, prefix="/api")
app.include_router(store_notifications.router, prefix="/api")

# Also include un-prefixed routers for direct compatibility
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(churn.router)
app.include_router(customers.router)
app.include_router(recommendations.router)
app.include_router(upload.router)
app.include_router(model_info.router)
app.include_router(reports.router)
app.include_router(sales_forecast.router)
app.include_router(store_auth.router)
app.include_router(store_products.router)
app.include_router(store_orders.router)
app.include_router(store_cart.router)
app.include_router(store_admin.router)
app.include_router(store_notifications.router)

@app.get("/")
def root():
    return {
        "system": "Amazon Customer Churn Analytics Platform API",
        "status": "Operational",
        "version": "1.0.0",
        "architecture": "FastAPI + React + Supabase PostgreSQL"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)