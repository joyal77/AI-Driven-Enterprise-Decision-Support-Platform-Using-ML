from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import date, datetime

class UserBase(BaseModel):
    name: str
    email: str
    role: Optional[str] = "admin"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CustomerBase(BaseModel):
    source_customer_id: str
    signup_date: Optional[date] = None
    customer_age: Optional[float] = None
    gender: Optional[str] = None
    city_tier: Optional[str] = None
    membership_status: Optional[str] = None
    days_since_last_purchase: Optional[float] = None
    total_orders_lifetime: Optional[int] = None
    orders_last_30d: Optional[int] = None
    orders_prev_30_to_60d: Optional[float] = None
    total_spend_inr: Optional[str] = None
    avg_order_value: Optional[float] = None
    preferred_category: Optional[str] = None
    sessions_last_30d: Optional[int] = None
    avg_session_duration_min: Optional[float] = None
    cart_abandonments_last_30d: Optional[int] = None
    search_queries_last_30d: Optional[float] = None
    return_count: Optional[int] = None
    return_rate: Optional[float] = None
    cancellations_count: Optional[int] = None
    late_deliveries_count: Optional[int] = None
    customer_service_tickets: Optional[int] = None
    avg_rating_given: Optional[float] = None
    preferred_payment_mode: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChurnPredictionResponse(BaseModel):
    id: Optional[int] = None
    customer_id: int
    source_customer_id: Optional[str] = None
    churn_probability: float
    churn_prediction: int
    risk_category: str
    model_version: str
    prediction_timestamp: Optional[datetime] = None
    shap_explanation: Optional[List[Any]] = []
    simple_explanation: Optional[str] = None
    root_causes: Optional[List[str]] = []
    recommendations: Optional[List[str]] = []

    class Config:
        from_attributes = True

class BatchPredictionResponse(BaseModel):
    success: bool
    message: str
    total_processed: int
    high_risk_customers: int
    medium_risk_customers: int
    low_risk_customers: int
    average_churn_probability: float
    batch_id: Optional[int] = None

class DashboardKPIs(BaseModel):
    total_customers: int
    analyzed_customers: int
    churn_rate_pct: float
    predicted_churners: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
