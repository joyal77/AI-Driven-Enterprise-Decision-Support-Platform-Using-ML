import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadDataset, uploadPreviousSalesDataset, downloadSamplePreviousSalesCSV } from '../services/api';
import api from '../services/api';
import './DatasetUpload.css';

const DatasetUpload = () => {
  const [datasetType, setDatasetType] = useState('customers'); // 'customers' | 'previous_sales'
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [result, setResult] = useState(null);
  const [salesResult, setSalesResult] = useState(null);
  const [error, setError] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleFileSelect = (file) => {
    if (!file) return;
    if (!file.name.endsWith('.csv')) {
      setError('Please select a valid CSV dataset file (.csv).');
      setSelectedFile(null);
      return;
    }
    setSelectedFile(file);
    setError(null);
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (!selectedFile) {
      setError(`Please select a ${datasetType === 'customers' ? 'customer' : 'previous sales'} CSV file to upload.`);
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);
    setSalesResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      if (datasetType === 'customers') {
        const data = await uploadDataset(formData);
        setResult(data);
      } else {
        const data = await uploadPreviousSalesDataset(formData);
        setSalesResult(data);
      }
    } catch (err) {
      console.error('Error uploading dataset:', err);
      setError(
        err.response?.data?.detail || 'Failed to upload dataset. Please check columns and ensure backend server is active.'
      );
    } finally {
      setUploading(false);
    }
  };

  const handleClearDatabase = async () => {
    if (!window.confirm('Are you sure you want to clear the customer dataset?')) {
      return;
    }

    setClearing(true);
    setError(null);
    setResult(null);

    try {
      const res = await api.post('/upload-dataset/clear');
      alert(res.data.message || 'Dataset cleared successfully.');
      setSelectedFile(null);
    } catch (err) {
      console.error('Error clearing dataset:', err);
      setError(err.response?.data?.detail || 'Failed to clear dataset.');
    } finally {
      setClearing(false);
    }
  };

  return (
    <div className="animate-fade-in dataset-upload-container">
      {/* Header Banner */}
      <div className="dataset-header-banner">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2 style={{ fontSize: 'clamp(1.25rem, 2.5vw, 1.6rem)', color: '#0f1111', fontWeight: 900 }}>
              Upload Dataset: Customer Churn & Sales Forecast
            </h2>
            <p style={{ color: '#565959', fontSize: 'clamp(0.85rem, 1.8vw, 1.05rem)', marginTop: '0.4rem' }}>
              Upload raw CSV data files to train and update machine learning predictions for Customer Churn or generate Multi-Horizon Sales Forecasts.
            </p>
          </div>
          {datasetType === 'customers' && (
            <button
              onClick={handleClearDatabase}
              disabled={clearing}
              className="btn-amazon-dark"
              style={{ padding: '0.75rem 1.25rem', fontSize: '0.95rem', whiteSpace: 'nowrap' }}
            >
              {clearing ? '⏳ Clearing...' : '🧹 Clear Customer Dataset'}
            </button>
          )}
        </div>
      </div>

      <div style={{ maxWidth: '850px', width: '100%', margin: '0 auto' }}>
        {/* Dataset Type Selector Tabs */}
        <div className="dataset-tabs-row">
          <button
            type="button"
            onClick={() => { setDatasetType('customers'); setSelectedFile(null); setResult(null); setSalesResult(null); setError(null); }}
            className="dataset-type-btn"
            style={{
              border: datasetType === 'customers' ? '2px solid #ff9900' : '1px solid #d5d9d9',
              background: datasetType === 'customers' ? '#fff8e5' : '#ffffff',
              color: datasetType === 'customers' ? '#0f1111' : '#565959',
            }}
          >
            <span>👥 Customer Churn Dataset</span>
          </button>

          <button
            type="button"
            onClick={() => { setDatasetType('previous_sales'); setSelectedFile(null); setResult(null); setSalesResult(null); setError(null); }}
            className="dataset-type-btn"
            style={{
              border: datasetType === 'previous_sales' ? '2px solid #007185' : '1px solid #d5d9d9',
              background: datasetType === 'previous_sales' ? '#f0f9ff' : '#ffffff',
              color: datasetType === 'previous_sales' ? '#0f1111' : '#565959',
            }}
          >
            <span>📈 Sales Forecast Dataset</span>
          </button>
        </div>

        {/* File Upload Box */}
        <form onSubmit={handleUploadSubmit} className="dataset-form-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '8px' }}>
            <h3 style={{ fontSize: 'clamp(1.05rem, 2vw, 1.25rem)', color: '#0f1111', textTransform: 'none', fontWeight: 800 }}>
              {datasetType === 'customers' ? '📦 Upload Customer Churn Dataset (.csv)' : '📊 Upload Previous Sales Dataset (.csv)'}
            </h3>
          </div>

          <p style={{ color: '#565959', fontSize: '0.92rem', marginBottom: '1.25rem' }}>
            {datasetType === 'customers'
              ? 'Upload ecommerce customer transaction records. The backend will parse records and run Random Forest churn risk classification.'
              : 'Upload historical daily sales records. The engine will extract momentum lags, 7/30-day velocity, and project Next 7, 14, 30 Days sales.'}
          </p>

          {/* Hidden native file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />

          {/* Clickable Drop Zone */}
          <div
            onClick={() => fileInputRef.current?.click()}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className="dataset-dropzone"
            style={{
              border: isDragOver ? '3px dashed #ff9900' : selectedFile ? '3px solid #007600' : '3px dashed #cbd5e1',
              backgroundColor: isDragOver ? '#fffbe6' : selectedFile ? '#f0fdf4' : '#f8fafc',
            }}
          >
            <div style={{ fontSize: 'clamp(2.5rem, 5vw, 3.5rem)', marginBottom: '0.75rem' }}>
              {selectedFile ? '📄' : '📁'}
            </div>
            <p style={{ fontWeight: 800, fontSize: 'clamp(1.05rem, 2.5vw, 1.25rem)', color: selectedFile ? '#007600' : '#0f1111', marginBottom: '0.35rem' }}>
              {selectedFile ? selectedFile.name : `Click to Browse or Drag ${datasetType === 'customers' ? 'Customer' : 'Previous Sales'} CSV here`}
            </p>
            <p style={{ fontSize: '0.92rem', color: selectedFile ? '#007600' : '#565959' }}>
              {selectedFile
                ? `${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB — Click to change selected file`
                : datasetType === 'customers'
                  ? 'Supports .csv files (e.g. raw_ecommerce_churn_10k.csv)'
                  : 'Requires columns: Date, Sales_Revenue (e.g. sample_previous_sales_history.csv)'}
            </p>
          </div>

          {error && (
            <div style={{ backgroundColor: '#fde8e8', color: '#cc0c39', padding: '1rem', borderRadius: '8px', border: '1px solid #f8b4b4', marginBottom: '1.5rem', fontSize: '0.95rem', fontWeight: 600 }}>
              ⚠️ {error}
            </div>
          )}

          <button
            type="submit"
            disabled={uploading || !selectedFile}
            className="btn-amazon-gold"
            style={{
              width: '100%',
              padding: '1rem',
              fontSize: '1.05rem',
              fontWeight: 800,
              opacity: uploading || !selectedFile ? 0.6 : 1,
              cursor: uploading || !selectedFile ? 'not-allowed' : 'pointer',
            }}
          >
            {uploading
              ? '⏳ Ingesting Dataset & Running Machine Learning...'
              : datasetType === 'customers'
                ? '🚀 Upload Customer Dataset & Run Prediction'
                : '🚀 Ingest Previous Sales & Seed 7/14/30D Forecast'}
          </button>
        </form>

        {/* Customer Upload Result Card */}
        {result && (
          <div className="stat-card" style={{ marginTop: '2rem', backgroundColor: '#f0fdf4', borderColor: '#bbf7d0', padding: '1.5rem' }}>
            <h3 style={{ color: '#007600', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.15rem', textTransform: 'none', fontWeight: 900 }}>
              ✅ Customer Data Ingestion & Random Forest Inference Completed!
            </h3>

            <div className="dataset-result-grid">
              <div><strong>Dataset Loaded:</strong> {result.filename}</div>
              <div><strong>Total Rows Parsed:</strong> {result.total_rows_parsed?.toLocaleString()}</div>
              <div><strong>New Customers Imported:</strong> {result.imported_customers?.toLocaleString()}</div>
            </div>

            {result.prediction_summary && (
              <div style={{ backgroundColor: '#ffffff', padding: '1.25rem', borderRadius: '8px', border: '1px solid #d5d9d9', marginBottom: '1.5rem' }}>
                <h4 style={{ marginBottom: '0.75rem', color: '#0f1111', fontSize: '1.05rem', fontWeight: 800 }}>Random Forest Prediction Summary</h4>
                <div className="dataset-kpi-summary-grid">
                  <div>
                    <span style={{ fontSize: '0.82rem', color: '#565959' }}>Total Analyzed</span>
                    <div style={{ fontWeight: 900, fontSize: '1.35rem', color: '#0f1111' }}>{result.prediction_summary.total_processed?.toLocaleString()}</div>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.82rem', color: '#cc0c39' }}>High Risk</span>
                    <div style={{ fontWeight: 900, fontSize: '1.35rem', color: '#cc0c39' }}>{result.prediction_summary.high_risk_customers?.toLocaleString()}</div>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.82rem', color: '#c7511f' }}>Medium Risk</span>
                    <div style={{ fontWeight: 900, fontSize: '1.35rem', color: '#c7511f' }}>{result.prediction_summary.medium_risk_customers?.toLocaleString()}</div>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.82rem', color: '#007600' }}>Low Risk</span>
                    <div style={{ fontWeight: 900, fontSize: '1.35rem', color: '#007600' }}>{result.prediction_summary.low_risk_customers?.toLocaleString()}</div>
                  </div>
                </div>
              </div>
            )}

            <div className="dataset-action-buttons">
              <button
                onClick={() => navigate('/dashboard')}
                className="btn-amazon-gold"
                style={{ flex: 1, padding: '0.85rem', fontSize: '0.95rem' }}
              >
                📊 View Executive Dashboard
              </button>
              <button
                onClick={() => navigate('/churn-prediction')}
                className="btn-amazon-dark"
                style={{ flex: 1, padding: '0.85rem', fontSize: '0.95rem' }}
              >
                👥 View Customer Churn Prediction
              </button>
            </div>
          </div>
        )}

        {/* Previous Sales Upload Result Card */}
        {salesResult && (
          <div className="stat-card" style={{ marginTop: '2rem', backgroundColor: '#f0fdf4', borderColor: '#bbf7d0', padding: '1.5rem' }}>
            <h3 style={{ color: '#007600', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.15rem', textTransform: 'none', fontWeight: 900 }}>
              ✅ Previous Sales Dataset Ingested & Forward Forecast Seeded!
            </h3>

            <div className="dataset-result-grid">
              <div><strong>File Name:</strong> {salesResult.filename}</div>
              <div><strong>Date Range:</strong> {salesResult.summary?.start_date} to {salesResult.summary?.end_date}</div>
              <div><strong>Historical Days:</strong> {salesResult.summary?.total_historical_days} days</div>
              <div><strong>Total Historical Sales:</strong> ${salesResult.summary?.total_historical_revenue?.toLocaleString()}</div>
              <div><strong>Historical Daily Pace:</strong> ${salesResult.summary?.average_daily_revenue?.toLocaleString()} / day</div>
              <div><strong>Recent 7-Day Velocity:</strong> ${salesResult.summary?.recent_7d_average?.toLocaleString()} / day</div>
            </div>

            <div style={{ backgroundColor: '#ffffff', padding: '1.25rem', borderRadius: '8px', border: '1px solid #d5d9d9', marginBottom: '1.5rem' }}>
              <h4 style={{ marginBottom: '0.5rem', color: '#0f1111', fontSize: '1.05rem', fontWeight: 800 }}>
                Next 7 Days Forecast (Seeded from Uploaded History)
              </h4>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem', flexWrap: 'wrap', gap: '8px' }}>
                <div>
                  <span style={{ fontSize: '0.85rem', color: '#565959' }}>Projected 7-Day Revenue</span>
                  <div style={{ fontWeight: 900, fontSize: '1.4rem', color: '#007185' }}>
                    ${salesResult.seeded_forecast_7d?.summary?.total_forecasted_revenue?.toLocaleString()}
                  </div>
                </div>
                <div>
                  <span style={{ fontSize: '0.85rem', color: '#565959' }}>Forecast Window</span>
                  <div style={{ fontWeight: 700, fontSize: '1rem', color: '#0f1111' }}>
                    {salesResult.seeded_forecast_7d?.start_date} to {salesResult.seeded_forecast_7d?.end_date}
                  </div>
                </div>
              </div>
            </div>

            <button
              onClick={() => navigate('/sales-forecast')}
              className="btn-amazon-gold"
              style={{ width: '100%', padding: '0.9rem', fontSize: '1rem', fontWeight: 800 }}
            >
              📈 View Next 7, 14, 30 Days Forecast Trajectory →
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default DatasetUpload;
