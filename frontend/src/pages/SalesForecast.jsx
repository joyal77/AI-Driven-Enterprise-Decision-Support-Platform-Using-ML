import React, { useState, useEffect, useRef } from "react";
import {
  getHorizonForecast,
  exportHorizonForecastCSV,
  getSalesForecastPDFBlob,
  downloadSalesForecastPDF,
  uploadPreviousSalesDataset,
  clearPreviousSalesDataset,
  downloadSamplePreviousSalesCSV
} from "../services/api";
import {
  TrendingUp,
  ArrowUpRight,
  Calendar,
  DollarSign,
  AlertCircle,
  Download,
  Upload,
  FileSpreadsheet,
  CheckCircle2,
  RefreshCw,
  Trash2,
  X,
  FileText,
  ShoppingBag,
  Eye,
  ZoomIn,
  ZoomOut,
  Sparkles
} from "lucide-react";
import "./SalesForecast.css";

function SalesForecast() {
  // Multi-Horizon Controls: 7, 14, 30 Days
  const [horizonDays, setHorizonDays] = useState(7);
  const [baselineSales, setBaselineSales] = useState(5000);
  const [scenarioMode, setScenarioMode] = useState("expected"); // 'expected' | 'conservative' | 'optimistic'
  const [activeTab, setActiveTab] = useState("forecast"); // 'forecast' | 'history'
  const [dataSource, setDataSource] = useState("store"); // 'store' (Live Website) | 'uploaded' (CSV Dataset)

  // Forecast Result State
  const [horizonData, setHorizonData] = useState(null);
  const [loadingForecast, setLoadingForecast] = useState(true);
  const [exportingCSV, setExportingCSV] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  // PDF In-App Preview State
  const [showPdfModal, setShowPdfModal] = useState(false);
  const [pdfBlobUrl, setPdfBlobUrl] = useState(null);
  const [loadingPdf, setLoadingPdf] = useState(false);
  const [pdfError, setPdfError] = useState(null);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(100);

  // File Upload State
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [showReplaceUpload, setShowReplaceUpload] = useState(false);

  const fileInputRef = useRef(null);
  const replaceFileInputRef = useRef(null);

  useEffect(() => {
    fetchHorizonData();
  }, [horizonDays, scenarioMode, dataSource]);

  const fetchHorizonData = async () => {
    setLoadingForecast(true);
    setError(null);
    try {
      const res = await getHorizonForecast(horizonDays, baselineSales, scenarioMode, null, dataSource);
      setHorizonData(res);
    } catch (err) {
      console.error("Failed to load horizon forecast:", err);
      setError("Unable to compute horizon sales forecast. Please verify backend service.");
    } finally {
      setLoadingForecast(false);
    }
  };

  const handleFileSelect = (file) => {
    if (!file) return;
    if (!file.name.endsWith(".csv")) {
      setError("Please select a valid CSV dataset file (.csv).");
      setSelectedFile(null);
      return;
    }
    setSelectedFile(file);
    setError(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleUploadSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!selectedFile) {
      setError("Please select a previous sales CSV file to upload.");
      return;
    }

    setUploading(true);
    setError(null);
    setSuccessMessage(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await uploadPreviousSalesDataset(formData);
      setSuccessMessage(
        `Previous sales dataset "${res.filename || selectedFile.name}" ingested successfully! Forecast seeded with ${res.summary?.total_historical_days || 0} historical days.`
      );
      setSelectedFile(null);
      setShowReplaceUpload(false);
      await fetchHorizonData();
    } catch (err) {
      console.error("Failed to upload previous sales:", err);
      setError(
        err.response?.data?.detail || "Failed to upload previous sales CSV. Please verify file format and columns."
      );
    } finally {
      setUploading(false);
    }
  };

  const handleClearData = async () => {
    if (!window.confirm("Are you sure you want to clear the uploaded sales history? Forecast data will only be displayed when you upload a new previous sales CSV file.")) {
      return;
    }
    setClearing(true);
    setError(null);
    setSuccessMessage(null);
    try {
      await clearPreviousSalesDataset();
      setHorizonData(null);
      setSelectedFile(null);
      setShowReplaceUpload(false);
      setSuccessMessage("Previous sales history cleared. Please upload a new dataset to generate forecasts.");
      await fetchHorizonData();
    } catch (err) {
      console.error("Failed to clear previous sales dataset:", err);
      setError("Failed to clear dataset.");
    } finally {
      setClearing(false);
    }
  };

  const handleExportCSV = async () => {
    setExportingCSV(true);
    try {
      await exportHorizonForecastCSV(horizonDays, baselineSales, scenarioMode, dataSource);
    } catch (err) {
      console.error("Export error:", err);
      setError(err.response?.data?.detail || "Failed to export forecast CSV.");
    } finally {
      setExportingCSV(false);
    }
  };

  // In-App PDF Preview Handlers
  const handleOpenPdfPreview = async (overrideHorizon = null) => {
    const targetHorizon = overrideHorizon !== null ? overrideHorizon : horizonDays;
    setShowPdfModal(true);
    setLoadingPdf(true);
    setPdfError(null);

    // Revoke previous blob URL if any
    if (pdfBlobUrl) {
      window.URL.revokeObjectURL(pdfBlobUrl);
      setPdfBlobUrl(null);
    }

    try {
      const blob = await getSalesForecastPDFBlob(targetHorizon, baselineSales, scenarioMode, dataSource, true);
      const url = window.URL.createObjectURL(blob);
      setPdfBlobUrl(url);
    } catch (err) {
      console.error("Failed to generate PDF preview:", err);
      setPdfError(
        err.response?.data?.detail ||
        "Failed to generate sales forecast PDF report. If using an uploaded dataset, ensure a valid CSV has been uploaded."
      );
    } finally {
      setLoadingPdf(false);
    }
  };

  const handleClosePdfPreview = () => {
    setShowPdfModal(false);
    if (pdfBlobUrl) {
      window.URL.revokeObjectURL(pdfBlobUrl);
      setPdfBlobUrl(null);
    }
    setPdfError(null);
  };

  const handleDownloadPdf = async (targetHorizon = horizonDays) => {
    setDownloadingPdf(true);
    try {
      await downloadSalesForecastPDF(targetHorizon, baselineSales, scenarioMode, dataSource);
    } catch (err) {
      console.error("Failed to download PDF report:", err);
      alert(err.response?.data?.detail || "Failed to download PDF report.");
    } finally {
      setDownloadingPdf(false);
    }
  };

  // Revoke Blob URL on unmount
  useEffect(() => {
    return () => {
      if (pdfBlobUrl) {
        window.URL.revokeObjectURL(pdfBlobUrl);
      }
    };
  }, [pdfBlobUrl]);

  const isDataAvailable = Boolean(
    horizonData &&
    horizonData.has_data &&
    horizonData.is_custom_history_loaded &&
    horizonData.schedule &&
    horizonData.schedule.length > 0
  );

  // Historical records and rolling momentum metrics with robust calculation fallbacks
  const historySchedule = horizonData?.historical_recent_schedule || horizonData?.history_summary?.recent_history || [];

  const last7Records = historySchedule.slice(-7);
  const calculated7dAvg = last7Records.length > 0
    ? last7Records.reduce((sum, r) => sum + (Number(r.actual_revenue ?? r.revenue) || 0), 0) / last7Records.length
    : 0;

  const last30Records = historySchedule.slice(-30);
  const calculated30dAvg = last30Records.length > 0
    ? last30Records.reduce((sum, r) => sum + (Number(r.actual_revenue ?? r.revenue) || 0), 0) / last30Records.length
    : 0;

  const totalHistoricalRev = horizonData?.history_summary?.total_historical_revenue 
    ?? horizonData?.history_summary?.total_revenue 
    ?? (historySchedule.length > 0 ? historySchedule.reduce((sum, r) => sum + (Number(r.actual_revenue ?? r.revenue) || 0), 0) : 0);

  const avgDailyRev = horizonData?.history_summary?.average_daily_revenue 
    ?? horizonData?.history_summary?.avg_daily_revenue 
    ?? (historySchedule.length > 0 ? totalHistoricalRev / Math.max(horizonData?.history_summary?.total_historical_days || historySchedule.length, 1) : 0);

  const recent7dAvg = (horizonData?.history_summary?.recent_7d_average !== undefined && horizonData?.history_summary?.recent_7d_average !== null && Number(horizonData.history_summary.recent_7d_average) > 0)
    ? Number(horizonData.history_summary.recent_7d_average)
    : calculated7dAvg;

  const recent30dAvg = (horizonData?.history_summary?.recent_30d_average !== undefined && horizonData?.history_summary?.recent_30d_average !== null && Number(horizonData.history_summary.recent_30d_average) > 0)
    ? Number(horizonData.history_summary.recent_30d_average)
    : calculated30dAvg;

  // Application Configured Currency
  const CURRENCY_SYMBOL = "₹";

  const formatCurrency = (val) => {
    const num = Number(val) || 0;
    return `${CURRENCY_SYMBOL}${num.toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  };

  // Two Main Forecast Metrics: Mathematically Consistent
  const totalForecast = Number(
    horizonData?.total_forecasted_revenue ??
    horizonData?.summary?.total_forecasted_revenue ??
    (horizonData?.schedule ? horizonData.schedule.reduce((acc, d) => acc + (d.forecasted_revenue || 0), 0) : 0)
  );

  const avgDailyForecast = horizonDays > 0 ? (totalForecast / horizonDays) : 0;

  return (
    <div className="sales-forecast-page">
      {/* Forecast Data Source Selector */}
      <div className="source-selector-ribbon">
        <div className="source-selector-label">
          <span>FORECAST DATA SOURCE:</span>
        </div>
        <div className="source-selector-tabs">
          <button
            type="button"
            className={`source-tab-btn ${dataSource === 'store' ? 'active' : ''}`}
            onClick={() => setDataSource('store')}
          >
            <ShoppingBag size={16} />
            <div className="source-tab-text">
              <strong>SmartCart Website Sales</strong>
              <span className="source-tab-sub">Real store orders & live checkout revenue</span>
            </div>
            <span className="source-badge live">Live Auto-Sync</span>
          </button>

          <button
            type="button"
            className={`source-tab-btn ${dataSource === 'uploaded' ? 'active' : ''}`}
            onClick={() => setDataSource('uploaded')}
          >
            <Upload size={16} />
            <div className="source-tab-text">
              <strong>Uploaded Sales Dataset (.csv)</strong>
              <span className="source-tab-sub">Previous sales history file</span>
            </div>
            <span className="source-badge csv">CSV Ingestion</span>
          </button>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <div className="forecast-error-alert glass-card">
          <AlertCircle size={18} className="text-danger" />
          <span>{error}</span>
          <button onClick={() => setError(null)} className="alert-dismiss-btn" title="Dismiss">
            <X size={14} />
          </button>
        </div>
      )}

      {successMessage && (
        <div className="forecast-success-alert glass-card">
          <div className="forecast-success-left">
            <CheckCircle2 size={18} className="text-emerald" />
            <span>{successMessage}</span>
          </div>
          <button onClick={() => setSuccessMessage(null)} className="alert-dismiss-btn" title="Dismiss">
            <X size={14} />
          </button>
        </div>
      )}

      {/* Main Content Area */}
      {loadingForecast && !horizonData ? (
        <div className="stat-card" style={{ padding: "3rem", textAlign: "center" }}>
          <RefreshCw size={32} className="text-cyan animate-spin" style={{ margin: "0 auto 1rem" }} />
          <h3>Checking sales history & initializing forecast engine...</h3>
          <p style={{ color: "#565959", marginTop: "0.5rem" }}>
            Verifying previous sales dataset ingestion status...
          </p>
        </div>
      ) : !isDataAvailable ? (
        /* NO DATA LOADED: Show Upload Prompt & Dropzone */
        <div className="previous-upload-card glass-card">
          <div className="upload-card-header" style={{ display: "flex", alignItems: "flex-start", gap: "16px" }}>
            <div className="kpi-icon-box bg-gold-subtle" style={{ width: "52px", height: "52px" }}>
              <FileSpreadsheet size={26} className="text-gold" />
            </div>
            <div>
              <h2>Upload Previous Sales Dataset (.csv) to Generate Forecast</h2>
              <p className="upload-help-text">
                Sales predictions, confidence bands, and revenue pace schedules are <strong>strictly computed from your actual store sales history</strong>. To generate forecasts, please upload your previous sales data CSV file below.
              </p>
            </div>
          </div>

          {/* Hidden File Input */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                handleFileSelect(e.target.files[0]);
              }
            }}
            style={{ display: "none" }}
          />

          {/* Interactive Dropzone */}
          <div
            className={`dropzone-area ${isDragOver ? "drag-over" : ""} ${selectedFile ? "has-file" : ""}`}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragOver(true);
            }}
            onDragLeave={(e) => {
              e.preventDefault();
              setIsDragOver(false);
            }}
            onDrop={handleDrop}
          >
            {selectedFile ? (
              <div className="dropzone-selected-content">
                <div className="dropzone-file-icon-wrapper">
                  <FileText size={32} className="text-emerald" />
                </div>
                <div className="dropzone-file-details">
                  <span className="dropzone-file-name">{selectedFile.name}</span>
                  <span className="dropzone-file-size">
                    {(selectedFile.size / 1024).toFixed(1)} KB — Ready to Ingest
                  </span>
                </div>
                <div className="dropzone-file-actions">
                  <span className="dropzone-replace-badge">Click to select different file</span>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedFile(null);
                    }}
                    className="dropzone-clear-file-btn"
                  >
                    <X size={12} /> Remove
                  </button>
                </div>
              </div>
            ) : (
              <div className="dropzone-idle-content">
                <Upload size={40} className="dropzone-icon" />
                <span className="dropzone-main-text">
                  Drag and drop your Previous Sales CSV here, or browse
                </span>
                <span className="dropzone-sub-text">
                  Requires columns: <code>Date</code> and <code>Sales_Revenue</code> (or <code>Units_Sold</code> + <code>Unit_Price</code>)
                </span>
                <span className="dropzone-browse-cta">Browse Computer</span>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="previous-upload-actions" style={{ justifyContent: "space-between" }}>
            <button
              type="button"
              onClick={handleUploadSubmit}
              disabled={!selectedFile || uploading}
              className="ingest-history-btn"
            >
              <Upload size={16} />
              <span>
                {uploading ? "Ingesting & Computing Forecast..." : "Upload & Generate Sales Forecast"}
              </span>
            </button>

            <button
              type="button"
              onClick={downloadSamplePreviousSalesCSV}
              className="download-template-btn"
              title="Download sample previous sales template"
            >
              <Download size={14} />
              <span>Download Sample CSV Template</span>
            </button>
          </div>
        </div>
      ) : (
        /* DATA LOADED: Show Active Dataset Banner, Controls, KPIs, Trajectory Chart & Breakdowns */
        <div className="horizon-forecast-main">
          {/* Active Dataset Status Banner */}
          <div className="history-active-banner glass-card">
            <div className="history-banner-left">
              <div className="kpi-icon-box bg-emerald-subtle" style={{ width: "42px", height: "42px" }}>
                <CheckCircle2 size={22} className="text-emerald" />
              </div>
              <div>
                <div className="history-banner-title">
                  {dataSource === "store"
                    ? "Active Data Source: SmartCart Live Storefront Orders"
                    : `Active Dataset: ${horizonData.history_summary?.filename || "Uploaded Previous Sales History"}`}
                </div>
                <div className="history-banner-desc">
                  Historical Window: <strong>{horizonData.history_summary?.start_date}</strong> to <strong>{horizonData.history_summary?.end_date}</strong> ({horizonData.history_summary?.total_historical_days} historical days).
                </div>
                <div className="history-stats-pill-row">
                  <span className="history-stat-pill">
                    Historical Period: <strong>{horizonData.history_summary?.total_historical_days || 0} Days</strong>
                  </span>
                  <span className="history-stat-pill">
                    Total Historical Sales: <strong>{formatCurrency(totalHistoricalRev)}</strong>
                  </span>
                  <span className="history-stat-pill">
                    Historical Daily Average: <strong>{formatCurrency(avgDailyRev)} / day</strong>
                  </span>
                </div>
              </div>
            </div>

            <div className="history-banner-actions">
              {dataSource === "store" ? (
                <button
                  type="button"
                  onClick={fetchHorizonData}
                  disabled={loadingForecast}
                  className="history-view-btn"
                  title="Refresh store orders and recalculate forecast"
                >
                  <RefreshCw size={14} className={loadingForecast ? "animate-spin" : ""} />
                  <span>{loadingForecast ? "Refreshing..." : "Sync Store Orders"}</span>
                </button>
              ) : (
                <>
                  <button
                    type="button"
                    onClick={() => setShowReplaceUpload(!showReplaceUpload)}
                    className="history-view-btn"
                    title="Upload another CSV file to replace current sales history"
                  >
                    <Upload size={14} />
                    <span>{showReplaceUpload ? "Cancel Replace" : "Replace / Upload New CSV"}</span>
                  </button>

                  <button
                    type="button"
                    onClick={handleClearData}
                    disabled={clearing}
                    className="history-clear-btn"
                    title="Clear current dataset and reset forecast"
                  >
                    <Trash2 size={14} />
                    <span>{clearing ? "Clearing..." : "Clear Dataset"}</span>
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Collapsible Replace Upload Box */}
          {showReplaceUpload && (
            <div className="previous-upload-card glass-card" style={{ marginBottom: "20px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                <h3 style={{ fontSize: "16px", fontWeight: "800", color: "#0f1111" }}>
                  Upload Replacement Previous Sales Dataset (.csv)
                </h3>
                <button
                  onClick={() => setShowReplaceUpload(false)}
                  style={{ background: "transparent", border: "none", cursor: "pointer" }}
                >
                  <X size={18} />
                </button>
              </div>

              <input
                ref={replaceFileInputRef}
                type="file"
                accept=".csv"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleFileSelect(e.target.files[0]);
                  }
                }}
                style={{ display: "none" }}
              />

              <div
                className={`dropzone-area ${selectedFile ? "has-file" : ""}`}
                onClick={() => replaceFileInputRef.current?.click()}
              >
                {selectedFile ? (
                  <div className="dropzone-selected-content">
                    <FileText size={28} className="text-emerald" />
                    <span className="dropzone-file-name">{selectedFile.name}</span>
                    <span className="dropzone-file-size">{(selectedFile.size / 1024).toFixed(1)} KB</span>
                  </div>
                ) : (
                  <div className="dropzone-idle-content">
                    <Upload size={32} className="dropzone-icon" />
                    <span className="dropzone-main-text">Click to choose replacement CSV file</span>
                  </div>
                )}
              </div>

              <div style={{ marginTop: "12px", display: "flex", gap: "10px" }}>
                <button
                  onClick={handleUploadSubmit}
                  disabled={!selectedFile || uploading}
                  className="ingest-history-btn"
                >
                  <Upload size={14} />
                  <span>{uploading ? "Uploading & Ingesting..." : "Submit New Dataset"}</span>
                </button>
                <button
                  onClick={() => {
                    setShowReplaceUpload(false);
                    setSelectedFile(null);
                  }}
                  className="download-template-btn"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Horizon & Scenario Toolbar */}
          <div className="horizon-control-panel glass-card">
            <div className="horizon-left">
              <span className="horizon-title">Select Forecasting Window:</span>
              <div className="horizon-button-group">
                {[7, 14, 30].map((days) => (
                  <button
                    key={days}
                    className={`horizon-pill ${horizonDays === days ? "active" : ""}`}
                    onClick={() => setHorizonDays(days)}
                  >
                    Next {days} Days
                  </button>
                ))}
              </div>
            </div>

            <div className="horizon-right">
              <div className="scenario-selector-group">
                <span className="scenario-label">Trajectory Scenario:</span>
                <select
                  value={scenarioMode}
                  onChange={(e) => setScenarioMode(e.target.value)}
                  className="scenario-select"
                >
                  <option value="expected">Standard Pace (1.0x Momentum)</option>
                  <option value="optimistic">Accelerated Peak (+15% Lift)</option>
                  <option value="conservative">Prudent Buffer (-10% Safety)</option>
                </select>
              </div>

              {/* View PDF Report (Preview) Button */}
              <button
                onClick={() => handleOpenPdfPreview(horizonDays)}
                disabled={loadingForecast || loadingPdf}
                className="view-pdf-btn"
                title={`Preview Next ${horizonDays} Days Sales Forecast PDF`}
              >
                <Eye size={14} />
                <span>{loadingPdf ? "Opening..." : `Preview Next ${horizonDays}D PDF`}</span>
              </button>
            </div>
          </div>

          {/* Prominent Two Forecast KPI Cards */}
          <div className="forecast-two-kpis-grid">
            {/* Card 1: Total Forecasted Sales */}
            <div className="kpi-main-forecast-card glass-card">
              <div className="kpi-main-header">
                <span className="kpi-horizon-tag">Next {horizonDays} Days</span>
                <div className="kpi-main-icon-box bg-gold-subtle">
                  <DollarSign size={22} className="text-gold" />
                </div>
              </div>
              <div className="kpi-main-body">
                <span className="kpi-main-title">Total Forecasted Sales</span>
                <div className="kpi-main-value text-gold">
                  {formatCurrency(totalForecast)}
                </div>
                <p className="kpi-main-desc">
                  Total projected sales revenue over the selected period.
                </p>
              </div>
              <div className="kpi-main-footer">
                <span>Forecast Window: <strong>{horizonData?.start_date}</strong> to <strong>{horizonData?.end_date}</strong></span>
              </div>
            </div>

            {/* Card 2: Average Daily Sales */}
            <div className="kpi-main-forecast-card glass-card">
              <div className="kpi-main-header">
                <span className="kpi-horizon-tag cyan">Daily Pace</span>
                <div className="kpi-main-icon-box bg-cyan-subtle">
                  <TrendingUp size={22} className="text-cyan" />
                </div>
              </div>
              <div className="kpi-main-body">
                <span className="kpi-main-title">Average Daily Sales</span>
                <div className="kpi-main-value text-cyan">
                  {formatCurrency(avgDailyForecast)} <span className="value-unit">/ day</span>
                </div>
                <p className="kpi-main-desc">
                  Average projected sales revenue per day over the selected period.
                </p>
              </div>
              <div className="kpi-main-footer">
                <span>Formula: <strong>{formatCurrency(totalForecast)} ÷ {horizonDays} Days</strong></span>
              </div>
            </div>
          </div>

          {/* Forecasting Period & Analytical Methodology Info */}
          <div className="forecast-methodology-card glass-card">
            <div className="methodology-header">
              <Sparkles size={16} className="text-gold" />
              <h4>Forecasting Period & Analytical Methodology</h4>
            </div>
            <div className="methodology-grid">
              <div className="methodology-item">
                <span className="m-label">Forecast Horizon</span>
                <span className="m-value">Next {horizonDays} Calendar Days ({horizonData?.start_date} to {horizonData?.end_date})</span>
              </div>
              <div className="methodology-item">
                <span className="m-label">Selected Scenario</span>
                <span className="m-value">
                  {scenarioMode === "expected"
                    ? "Standard Pace (1.0x Momentum)"
                    : (scenarioMode === "optimistic" ? "Accelerated Peak (+15% Lift)" : "Prudent Buffer (-10% Safety)")}
                </span>
              </div>
              <div className="methodology-item">
                <span className="m-label">Data Calibration Source</span>
                <span className="m-value">
                  {dataSource === "store"
                    ? "SmartCart Live Storefront Transactions"
                    : (horizonData?.history_summary?.filename || "Uploaded Sales CSV Dataset")}
                </span>
              </div>
              <div className="methodology-item">
                <span className="m-label">Mathematical Consistency</span>
                <span className="m-value font-mono">
                  {formatCurrency(totalForecast)} ÷ {horizonDays} = {formatCurrency(avgDailyForecast)} / day
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* In-App PDF Preview Modal */}
      {showPdfModal && (
        <div className="pdf-modal-overlay" onClick={handleClosePdfPreview}>
          <div className="pdf-modal-container glass-card" onClick={(e) => e.stopPropagation()}>
            {/* Modal Header */}
            <div className="pdf-modal-header">
              <div className="pdf-modal-title-area">
                <FileText size={22} className="text-gold" />
                <div>
                  <h3 className="pdf-modal-title">Sales Demand Forecast Report</h3>
                  <span className="pdf-modal-subtitle">
                    Horizon: <strong>Next {horizonDays} Days</strong> • {scenarioMode.toUpperCase()} Pace • {dataSource === "store" ? "SmartCart Live Storefront" : "Uploaded CSV Dataset"}
                  </span>
                </div>
              </div>

              {/* In-Modal Horizon Switcher */}
              <div className="pdf-modal-horizon-switch">
                <span className="pdf-modal-switch-label">Horizon:</span>
                {[7, 14, 30].map((days) => (
                  <button
                    key={days}
                    className={`pdf-horizon-chip ${horizonDays === days ? "active" : ""}`}
                    onClick={() => {
                      setHorizonDays(days);
                      handleOpenPdfPreview(days);
                    }}
                    disabled={loadingPdf}
                  >
                    {days}D
                  </button>
                ))}
              </div>

              {/* Toolbar Controls */}
              <div className="pdf-modal-controls">
                {/* Zoom controls */}
                <div className="pdf-zoom-controls">
                  <button
                    onClick={() => setZoomLevel((prev) => Math.max(75, prev - 15))}
                    disabled={loadingPdf || zoomLevel <= 75}
                    className="pdf-control-btn"
                    title="Zoom Out"
                  >
                    <ZoomOut size={15} />
                  </button>
                  <span className="pdf-zoom-text">{zoomLevel}%</span>
                  <button
                    onClick={() => setZoomLevel((prev) => Math.min(175, prev + 15))}
                    disabled={loadingPdf || zoomLevel >= 175}
                    className="pdf-control-btn"
                    title="Zoom In"
                  >
                    <ZoomIn size={15} />
                  </button>
                  <button
                    onClick={() => setZoomLevel(100)}
                    disabled={loadingPdf || zoomLevel === 100}
                    className="pdf-control-btn reset-zoom-btn"
                    title="Reset Zoom to 100%"
                  >
                    Reset
                  </button>
                </div>

                {/* Download PDF button */}
                <button
                  onClick={() => handleDownloadPdf(horizonDays)}
                  disabled={downloadingPdf || loadingPdf}
                  className="pdf-download-btn"
                  title="Download this PDF report"
                >
                  <Download size={15} />
                  <span>{downloadingPdf ? "Downloading..." : "Download PDF"}</span>
                </button>

                {/* Close button */}
                <button
                  onClick={handleClosePdfPreview}
                  className="pdf-close-btn"
                  title="Close Preview (Esc)"
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            {/* Modal Body / Viewer */}
            <div className="pdf-modal-body">
              {loadingPdf ? (
                <div className="pdf-loading-state">
                  <RefreshCw size={36} className="spinning text-gold" />
                  <p className="pdf-loading-text">Generating Next {horizonDays}-Day Sales Forecast PDF...</p>
                  <span className="pdf-loading-sub">Calibrating time-series schedule, confidence intervals, and category projections</span>
                </div>
              ) : pdfError ? (
                <div className="pdf-error-state">
                  <AlertCircle size={40} className="text-danger" />
                  <h4 className="pdf-error-title">Unable to Generate PDF Preview</h4>
                  <p className="pdf-error-desc">{pdfError}</p>
                  <div className="pdf-error-actions">
                    <button onClick={() => handleOpenPdfPreview(horizonDays)} className="pdf-retry-btn">
                      <RefreshCw size={14} /> Retry Generation
                    </button>
                    <button onClick={handleClosePdfPreview} className="pdf-cancel-btn">
                      Close
                    </button>
                  </div>
                </div>
              ) : pdfBlobUrl ? (
                <div className="pdf-viewer-wrapper" style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: "top center", transition: "transform 0.15s ease" }}>
                  <iframe
                    src={pdfBlobUrl}
                    title={`Sales Forecast Next ${horizonDays} Days Report`}
                    className="pdf-iframe-viewer"
                  />
                </div>
              ) : null}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SalesForecast;