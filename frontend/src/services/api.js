import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const loginUser = async (email, password) => {
  const response = await api.post('/login', { email, password });
  return response.data;
};

export const getDashboardKPIs = async () => {
  const response = await api.get('/dashboard/kpis');
  return response.data;
};

export const getChurnSummary = async () => {
  const response = await api.get('/dashboard/churn-summary');
  return response.data;
};

export const getChurnAnalyticsDeepDive = async () => {
  const response = await api.get('/dashboard/churn-analytics');
  return response.data;
};

export const getCustomers = async (params = {}) => {
  const response = await api.get('/customers', { params });
  return response.data;
};

export const getCustomerDetails = async (id, options = {}) => {
  const response = await api.get(`/customers/${id}`, options);
  return response.data;
};

export const toggleCustomerRetentionAction = async (customerId, payload) => {
  const response = await api.post(`/customers/${customerId}/retention-action/toggle`, payload);
  return response.data;
};

export const getCustomerPerks = async (customerId) => {
  const response = await api.get(`/customers/${customerId}/retention-perks`);
  return response.data;
};

export const predictSingleChurn = async (data) => {
  const response = await api.post('/predict-churn', data);
  return response.data;
};

export const runBatchPrediction = async () => {
  const response = await api.post('/predict-churn/batch');
  return response.data;
};

export const uploadDataset = async (formData) => {
  const response = await api.post('/upload-dataset', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const resetDatabase = async () => {
  const response = await api.post('/upload-dataset/reset');
  return response.data;
};

export const getRecommendations = async (params = {}) => {
  const response = await api.get('/recommendations', { params });
  return response.data;
};

export const updateRecommendationStatus = async (id, status) => {
  const response = await api.patch(`/recommendations/${id}/status`, { status });
  return response.data;
};

export const getModelInfo = async () => {
  const response = await api.get('/model-info');
  return response.data;
};

export const downloadBatchPredictionPDF = async (source = 'store') => {
  const response = await api.get('/reports/batch-prediction-pdf', {
    params: { source },
    responseType: 'blob',
  });
  
  let filename = source === 'uploaded' 
    ? 'uploaded_dataset_customers_churn_report.pdf' 
    : (source === 'all' ? 'amazon_batch_prediction_report.pdf' : 'smartcart_live_store_customers_churn_report.pdf');

  const disposition = response.headers?.['content-disposition'];
  if (disposition && disposition.includes('filename=')) {
    const match = disposition.match(/filename=(.+)/);
    if (match && match[1]) {
      filename = match[1].trim();
    }
  }

  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const previewBatchPredictionPDF = async (source = 'store') => {
  const response = await api.get('/reports/batch-prediction-pdf', {
    params: { source },
    responseType: 'blob',
  });
  const file = new Blob([response.data], { type: 'application/pdf' });
  const fileURL = URL.createObjectURL(file);
  window.open(fileURL, '_blank');
  return fileURL;
};

export const downloadCustomerPDF = async (customerId, sourceCustomerId = 'account') => {
  const response = await api.get(`/reports/customer-pdf/${customerId}`, {
    params: { preview: false },
    responseType: 'blob',
  });
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `customer_${sourceCustomerId}_churn_report.pdf`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const previewCustomerPDF = async (customerId) => {
  const response = await api.get(`/reports/customer-pdf/${customerId}`, {
    params: { preview: true },
    responseType: 'blob',
  });
  const file = new Blob([response.data], { type: 'application/pdf' });
  const fileURL = URL.createObjectURL(file);
  window.open(fileURL, '_blank');
  return fileURL;
};

// ============================================
// Sales Forecasting & Classification API Endpoints
// ============================================

export const predictSalesForecast = async (payload) => {
  const response = await api.post('/sales-forecast/predict', payload);
  return response.data;
};

export const getHorizonForecast = async (horizon = 7, baselineSales = 5000, scenarioMode = 'expected', startDate = null, source = 'store') => {
  const params = { horizon, baseline_sales: baselineSales, scenario_mode: scenarioMode, source };
  if (startDate) params.start_date = startDate;
  const response = await api.get('/sales-forecast/horizon-forecast', { params });
  return response.data;
};

export const exportHorizonForecastCSV = async (horizon = 7, baselineSales = 5000, scenarioMode = 'expected', source = 'store') => {
  const params = { horizon, baseline_sales: baselineSales, scenario_mode: scenarioMode, source };
  const response = await api.get('/sales-forecast/export-horizon-csv', {
    params,
    responseType: 'blob',
  });
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/csv' }));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `sales_forecast_next_${horizon}_days.csv`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const getSalesForecastPDFBlob = async (horizon = 7, baselineSales = 5000, scenarioMode = 'expected', source = 'store', preview = true) => {
  const params = { horizon, baseline_sales: baselineSales, scenario_mode: scenarioMode, source, preview };
  const response = await api.get('/sales-forecast/export-pdf', {
    params,
    responseType: 'blob',
  });
  return new Blob([response.data], { type: 'application/pdf' });
};

export const downloadSalesForecastPDF = async (horizon = 7, baselineSales = 5000, scenarioMode = 'expected', source = 'store') => {
  const params = { horizon, baseline_sales: baselineSales, scenario_mode: scenarioMode, source, preview: false };
  const response = await api.get('/sales-forecast/export-pdf', {
    params,
    responseType: 'blob',
  });
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `sales_forecast_next_${horizon}_days.pdf`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const getTimeSeriesForecast = async (horizon = 30) => {
  const response = await api.get('/sales-forecast/time-series-forecast', { params: { horizon } });
  return response.data;
};

export const getSalesFactorsOverview = async () => {
  const response = await api.get('/sales-forecast/factors-overview');
  return response.data;
};

export const getSalesForecastMetadata = async () => {
  const response = await api.get('/sales-forecast/metadata');
  return response.data;
};

export const getSalesForecastTrends = async (horizon = 30) => {
  const response = await api.get('/sales-forecast/trends', { params: { horizon } });
  return response.data;
};

export const getSalesForecastOptions = async () => {
  const response = await api.get('/sales-forecast/options');
  return response.data;
};

export const uploadSalesBatchForecast = async (formData) => {
  const response = await api.post('/sales-forecast/upload-batch', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const downloadSalesSampleBatch = async () => {
  const response = await api.get('/sales-forecast/download-sample-batch', {
    responseType: 'blob',
  });
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/csv' }));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'unpredicted_sales_forecast_batch.csv');
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const uploadPreviousSalesDataset = async (formData) => {
  const response = await api.post('/sales-forecast/upload-previous-sales', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getPreviousSalesStatus = async () => {
  const response = await api.get('/sales-forecast/previous-sales-status');
  return response.data;
};

export const clearPreviousSalesDataset = async () => {
  const response = await api.post('/sales-forecast/clear-previous-sales');
  return response.data;
};

export const downloadSamplePreviousSalesCSV = async () => {
  const response = await api.get('/sales-forecast/download-sample-previous-sales', {
    responseType: 'blob',
  });
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/csv' }));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'sample_previous_sales_history.csv');
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const loadSamplePreviousSales = async () => {
  const response = await api.post('/sales-forecast/load-sample-previous-sales');
  return response.data;
};

export default api;