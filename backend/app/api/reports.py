from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.models import Customer
from ..services.pdf_generator import (
    generate_batch_prediction_pdf,
    generate_customer_prediction_pdf,
    generate_sales_forecast_pdf
)
from ..ml.sales_predictor import generate_multi_horizon_sales_forecast

router = APIRouter(prefix="/reports", tags=["Reports & Export"])

@router.get("/batch-prediction-pdf")
def download_batch_prediction_report(
    source: Optional[str] = Query("store"),
    preview: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Generate and stream an Executive Batch Prediction PDF Report for the specified cohort (store vs uploaded).
    Supports inline preview or attachment download via preview=true/false.
    """
    try:
        source_clean = source.strip().lower() if source else "store"
        if source_clean not in ["store", "uploaded", "all"]:
            source_clean = "store"

        pdf_buffer = generate_batch_prediction_pdf(db, source=source_clean)

        if source_clean == "store":
            filename = "smartcart_live_store_customers_churn_report.pdf"
        elif source_clean == "uploaded":
            filename = "uploaded_dataset_customers_churn_report.pdf"
        else:
            filename = "amazon_batch_prediction_report.pdf"

        disposition_type = "inline" if preview else "attachment"
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"{disposition_type}; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate batch prediction PDF: {str(e)}")

@router.get("/customer-pdf/{customer_id}")
def download_customer_report(
    customer_id: int,
    preview: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Generate and stream an individual Customer Churn Diagnostic PDF Report.
    Supports inline preview or attachment download via preview=true/false.
    """
    cust = db.query(Customer).filter(Customer.id == customer_id).first()
    if not cust:
        raise HTTPException(status_code=404, detail=f"Customer #{customer_id} not found")

    try:
        pdf_buffer = generate_customer_prediction_pdf(customer_id, db)
        filename = f"customer_{cust.source_customer_id}_churn_report.pdf"
        disposition_type = "inline" if preview else "attachment"
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"{disposition_type}; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate customer PDF report: {str(e)}")

@router.get("/sales-forecast-pdf")
def get_sales_forecast_pdf_report(
    horizon: int = Query(7, ge=7, le=30),
    baseline_sales: float = Query(5000.0, ge=100.0),
    scenario_mode: str = Query("expected"),
    source: str = Query("store"),
    preview: bool = Query(False)
):
    """
    Generates and streams an Executive Sales Demand Forecast PDF Report
    for the exact selected horizon (7, 14, or 30 days).
    Supports inline preview or direct attachment download.
    """
    try:
        forecast_result = generate_multi_horizon_sales_forecast(
            horizon_days=horizon,
            baseline_sales=baseline_sales,
            scenario_mode=scenario_mode,
            source=source
        )

        if source == "uploaded" and not forecast_result.get("is_custom_history_loaded"):
            raise HTTPException(
                status_code=400,
                detail="Cannot generate forecast report: No previous sales dataset has been uploaded. Please upload a dataset first."
            )

        pdf_buffer = generate_sales_forecast_pdf(
            forecast_data=forecast_result,
            horizon_days=horizon,
            scenario_mode=scenario_mode,
            source=source
        )

        filename = f"sales_forecast_next_{horizon}_days.pdf"
        disposition_type = "inline" if preview else "attachment"
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"{disposition_type}; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate sales forecast PDF: {str(e)}")
