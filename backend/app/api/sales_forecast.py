import io
import os
import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Response
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional
from pydantic import BaseModel
from ..ml.sales_predictor import (
    generate_multi_horizon_sales_forecast,
    predict_new_scenario,
    predict_batch_dataset,
    get_sales_metadata,
    get_static_options,
    ingest_previous_sales_csv,
    get_previous_sales_status,
    clear_previous_sales_data
)
from ..services.pdf_generator import generate_sales_forecast_pdf

router = APIRouter(prefix="/sales-forecast", tags=["Sales Forecasting & Predictive Analytics"])

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SAMPLE_DATASETS_DIR = os.path.join(PROJECT_ROOT, "sample_datasets")

class ScenarioInput(BaseModel):
    Store_ID: Optional[str] = "STORE_01"
    Product_ID: Optional[str] = "PROD_001"
    Category: Optional[str] = "Electronics"
    Units_Sold: Optional[float] = 10.0
    Unit_Price: Optional[float] = 29.99
    Discount_Percent: Optional[float] = 5.0
    Promotion_Flag: Optional[int] = 1
    Inventory_Level: Optional[float] = 85.0
    Day_Of_Week: Optional[str] = "Monday"
    Month: Optional[int] = 6
    Holiday_Flag: Optional[int] = 0
    Marketing_Spend: Optional[float] = 25.0
    Competitor_Price: Optional[float] = 31.0
    Weather_Score: Optional[float] = 7.5

@router.get("/horizon-forecast")
def get_horizon_forecast(
    horizon: int = Query(7, ge=7, le=30),
    baseline_sales: float = Query(5000.0, ge=100.0),
    scenario_mode: str = Query("expected"),
    start_date: Optional[str] = Query(None),
    source: str = Query("store")
):
    """
    Dedicated Multi-Horizon Sales Forecaster:
    Predicts day-by-day sales for the Next 7 Days, Next 14 Days, or Next 30 Days
    using the trained time-series XGBoost booster model and autoregressive sequential stepping.
    Supports source='store' (live SmartCart storefront orders) and source='uploaded' (uploaded CSV).
    """
    try:
        forecast_result = generate_multi_horizon_sales_forecast(
            horizon_days=horizon,
            baseline_sales=baseline_sales,
            scenario_mode=scenario_mode,
            start_date_str=start_date,
            source=source
        )
        return forecast_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Horizon forecast error: {str(e)}")

@router.get("/export-horizon-csv")
def export_horizon_csv(
    horizon: int = Query(7, ge=7, le=30),
    baseline_sales: float = Query(5000.0, ge=100.0),
    scenario_mode: str = Query("expected"),
    source: str = Query("store")
):
    """
    Generates and downloads a clean CSV schedule of the Next 7, 14, or 30 Days Forecast.
    """
    try:
        forecast_result = generate_multi_horizon_sales_forecast(
            horizon_days=horizon,
            baseline_sales=baseline_sales,
            scenario_mode=scenario_mode,
            source=source
        )
        if not forecast_result.get("is_custom_history_loaded") or not forecast_result.get("schedule"):
            raise HTTPException(
                status_code=400,
                detail="Cannot export forecast: No previous sales dataset has been uploaded. Please upload a previous sales data CSV file first."
            )
        df_export = pd.DataFrame(forecast_result["schedule"])
        df_export = df_export.rename(columns={
            "day_number": "Day_Number",
            "date": "Forecast_Date",
            "day_of_week": "Day_Of_Week",
            "is_weekend": "Is_Weekend",
            "forecasted_revenue": "Forecasted_Revenue_USD",
            "lower_bound": "Confidence_Lower_Bound_USD",
            "upper_bound": "Confidence_Upper_Bound_USD",
            "demand_status": "Demand_Volume_Status"
        })

        output = io.StringIO()
        df_export.to_csv(output, index=False)
        output.seek(0)

        filename = f"sales_forecast_next_{horizon}_days.csv"
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV export error: {str(e)}")

@router.get("/export-pdf")
def export_sales_forecast_pdf_endpoint(
    horizon: int = Query(7, ge=7, le=30),
    baseline_sales: float = Query(5000.0, ge=100.0),
    scenario_mode: str = Query("expected"),
    source: str = Query("store"),
    preview: bool = Query(False)
):
    """
    Generates and streams an executive Sales Demand Forecast PDF report
    for the exact selected horizon (7, 14, or 30 days).
    Supports inline preview or attachment download via preview=true/false.
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
        raise HTTPException(status_code=500, detail=f"PDF export error: {str(e)}")

@router.post("/predict")
def predict_scenario_endpoint(scenario: ScenarioInput):
    """Predicts future revenue and volume tier for an individual upcoming product or campaign."""
    try:
        result = predict_new_scenario(scenario.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failure: {str(e)}")

@router.post("/upload-batch")
async def upload_batch_sales_forecast(file: UploadFile = File(...)):
    """Accepts an uploaded CSV of unpredicted upcoming sales items and scores every row."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    try:
        contents = await file.read()
        df_uploaded = pd.read_csv(io.BytesIO(contents))
        if df_uploaded.empty:
            raise HTTPException(status_code=400, detail="Uploaded CSV file is empty.")

        batch_result = predict_batch_dataset(df_uploaded)
        return {
            "success": True,
            "filename": file.filename,
            "summary": batch_result["summary"],
            "records": batch_result["scored_records"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch forecast error: {str(e)}")

@router.get("/download-sample-batch")
def download_sample_unpredicted_batch():
    sample_path = os.path.join(SAMPLE_DATASETS_DIR, "unpredicted_sales_forecast_batch.csv")
    if os.path.exists(sample_path):
        return FileResponse(
            path=sample_path,
            filename="unpredicted_sales_forecast_batch.csv",
            media_type="text/csv"
        )
    raise HTTPException(status_code=404, detail="Sample template not found.")

@router.get("/metadata")
def get_sales_forecast_metadata():
    metadata = get_sales_metadata()
    if not metadata:
        raise HTTPException(status_code=404, detail="Sales forecast metadata is not available.")
    return metadata

@router.get("/options")
def get_ui_options():
    return get_static_options()

# Backward compatibility alias
@router.get("/time-series-forecast")
def get_legacy_ts_forecast(horizon: int = Query(7, ge=7, le=30)):
    return generate_multi_horizon_sales_forecast(horizon_days=horizon)

# =========================================================================
# PREVIOUS SALES DATASET UPLOAD & SEEDING ENDPOINTS
# =========================================================================

@router.post("/upload-previous-sales")
async def upload_previous_sales_dataset(file: UploadFile = File(...)):
    """
    Ingests an uploaded CSV dataset of previous/historical sales, calculates date range,
    daily revenue aggregate, rolling momentum, and seeds the Next 7, 14, 30 Days Forecast.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported for previous sales dataset.")

    try:
        contents = await file.read()
        df_uploaded = pd.read_csv(io.BytesIO(contents))
        if df_uploaded.empty:
            raise HTTPException(status_code=400, detail="Uploaded previous sales CSV file is empty.")

        summary = ingest_previous_sales_csv(df_uploaded, filename=file.filename)

        # Generate fresh 7-day forecast seeded from uploaded history
        forecast_7d = generate_multi_horizon_sales_forecast(horizon_days=7, use_uploaded_history=True, source="uploaded")

        return {
            "success": True,
            "filename": file.filename,
            "summary": summary,
            "seeded_forecast_7d": forecast_7d
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest previous sales dataset: {str(e)}")

@router.get("/previous-sales-status")
def check_previous_sales_status():
    """Returns the current ingestion status and summary metrics of uploaded previous sales data."""
    return get_previous_sales_status()

@router.post("/clear-previous-sales")
def clear_uploaded_previous_sales():
    """Clears uploaded previous sales and resets the multi-horizon forecaster to default baseline."""
    return clear_previous_sales_data()

@router.post("/load-sample-previous-sales")
def load_sample_previous_sales():
    """Loads 90-day sample previous sales history CSV to seed forecasts."""
    sample_path = os.path.join(SAMPLE_DATASETS_DIR, "sample_previous_sales_history.csv")
    if not os.path.exists(sample_path):
        raise HTTPException(status_code=404, detail="Sample previous sales template not found.")

    try:
        df_sample = pd.read_csv(sample_path)
        summary = ingest_previous_sales_csv(df_sample, filename="sample_previous_sales_history.csv")
        forecast_7d = generate_multi_horizon_sales_forecast(horizon_days=7, use_uploaded_history=True, source="uploaded")
        return {
            "success": True,
            "filename": "sample_previous_sales_history.csv",
            "summary": summary,
            "seeded_forecast_7d": forecast_7d
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load sample previous sales: {str(e)}")

@router.get("/download-sample-previous-sales")
def download_sample_previous_sales_template():
    """Downloads sample 90-day previous sales history CSV template."""
    sample_path = os.path.join(SAMPLE_DATASETS_DIR, "sample_previous_sales_history.csv")
    if os.path.exists(sample_path):
        return FileResponse(
            path=sample_path,
            filename="sample_previous_sales_history.csv",
            media_type="text/csv"
        )
    raise HTTPException(status_code=404, detail="Sample previous sales template not found.")

