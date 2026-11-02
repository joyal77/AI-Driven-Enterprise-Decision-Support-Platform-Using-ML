import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  getDashboardKPIs,
  getChurnSummary,
  previewBatchPredictionPDF,
  getHorizonForecast
} from '../services/api';
import {
  TrendingUp,
  DollarSign,
  Users,
  AlertTriangle,
  Calendar,
  ArrowUpRight,
  ShieldCheck,
  Upload,
  ArrowRight,
  FileText,
  CheckCircle,
  Clock,
  Sparkles
} from 'lucide-react';

const Dashboard = () => {
  const [kpis, setKpis] = useState(null);
  const [summary, setSummary] = useState(null);
  const [salesForecast, setSalesForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [previewingPdf, setPreviewingPdf] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handlePdfPreview = async () => {
    setPreviewingPdf(true);
    try {
      await previewBatchPredictionPDF();
    } catch (err) {
      console.error('Failed to preview PDF report:', err);
    } finally {
      setPreviewingPdf(false);
    }
  };

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [kpiData, summaryData, forecastData] = await Promise.all([
        getDashboardKPIs(),
        getChurnSummary(),
        getHorizonForecast(7, 5000, 'expected').catch(() => null),
      ]);
      setKpis(kpiData);
      setSummary(summaryData);
      setSalesForecast(forecastData);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load Amazon Seller dashboard metrics. Please check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '4rem', textAlign: 'center' }}>
        <h2 style={{ color: '#0f1111' }}>Loading Executive Decision Analytics...</h2>
        <p style={{ color: '#565959', marginTop: '0.5rem' }}>
          Consolidating real-time customer churn intelligence and sales forecasting models...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stat-card" style={{ padding: '2rem', borderColor: '#cc0c39', backgroundColor: '#fde8e8' }}>
        <h3 style={{ color: '#cc0c39' }}>⚠️ Amazon Seller Dashboard Error</h3>
        <p style={{ color: '#0f1111', marginTop: '0.5rem' }}>{error}</p>
        <button onClick={fetchDashboardData} className="btn-primary" style={{ marginTop: '1rem' }}>
          🔄 Retry Connection
        </button>
      </div>
    );
  }

  const isSalesDataAvailable = Boolean(
    salesForecast &&
    salesForecast.has_data &&
    salesForecast.is_custom_history_loaded &&
    salesForecast.schedule &&
    salesForecast.schedule.length > 0
  );

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      {/* Executive Header Banner */}
      <div
        style={{
          backgroundColor: '#ffffff',
          border: '1px solid #d5d9d9',
          borderLeft: '6px solid #ff9900',
          borderRadius: '8px',
          padding: '1.6rem 2rem',
          boxShadow: '0 2px 6px rgba(15,17,17,0.06)'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span style={{ background: '#fff8e5', color: '#b7791f', padding: '3px 10px', borderRadius: '999px', fontSize: '12px', fontWeight: 800 }}>
                Amazon Seller Central
              </span>
              <span style={{ background: '#e6f7fa', color: '#007185', padding: '3px 10px', borderRadius: '999px', fontSize: '12px', fontWeight: 800 }}>
                Unified Executive Dashboard
              </span>
            </div>
            <h2 style={{ fontSize: '1.65rem', color: '#0f1111', fontWeight: 900 }}>
              Sales Forecasting & Customer Churn Executive Intelligence
            </h2>
            <p style={{ fontSize: '1.05rem', color: '#565959', marginTop: '0.4rem' }}>
              Dual-engine predictive decision support: Multi-horizon store revenue projections and Random Forest customer retention scoring.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
            <button
              onClick={() => navigate('/upload')}
              className="btn-amazon-dark"
              style={{
                padding: '0.75rem 1.25rem',
                fontSize: '0.95rem',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <Upload size={15} />
              <span>Upload Datasets</span>
            </button>
            <button
              onClick={handlePdfPreview}
              disabled={previewingPdf}
              className="btn-amazon-gold"
              style={{
                padding: '0.75rem 1.25rem',
                fontSize: '0.95rem',
                fontWeight: 800,
                cursor: previewingPdf ? 'wait' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <FileText size={15} />
              <span>{previewingPdf ? 'Opening PDF...' : 'View Churn PDF Report'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* DUAL KPI OVERVIEW: Customer Churn (Left) & Sales Forecast (Right) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        {/* Customer Churn KPIs */}
        <div className="stat-card" style={{ borderTop: '4px solid #ff9900' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '11.5px', fontWeight: 700, color: '#565959', textTransform: 'uppercase' }}>
              Total Customer Profiles
            </span>
            <Users size={16} className="text-cyan" />
          </div>
          <div className="value">{kpis?.total_customers?.toLocaleString() || 0}</div>
          <span style={{ fontSize: '0.95rem', color: '#565959', fontWeight: 600 }}>
            Evaluated for Churn Risk
          </span>
        </div>

        <div className="stat-card" style={{ borderTop: '4px solid #cc0c39' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '11.5px', fontWeight: 700, color: '#cc0c39', textTransform: 'uppercase' }}>
              Predicted Churn Rate
            </span>
            <AlertTriangle size={16} style={{ color: '#cc0c39' }} />
          </div>
          <div className="value" style={{ color: '#cc0c39' }}>
            {kpis?.predicted_churn_rate_pct ?? 0}%
          </div>
          <span style={{ fontSize: '0.95rem', color: '#565959', fontWeight: 600 }}>
            <strong>{kpis?.predicted_churners?.toLocaleString() || 0}</strong> accounts predicted to churn
          </span>
        </div>

        {/* Sales Forecast KPIs */}
        <div className="stat-card" style={{ borderTop: '4px solid #007185' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '11.5px', fontWeight: 700, color: '#007185', textTransform: 'uppercase' }}>
              Total Forecasted Sales (7D)
            </span>
            <DollarSign size={16} className="text-gold" />
          </div>
          <div className="value" style={{ color: isSalesDataAvailable ? '#0f1111' : '#888' }}>
            {isSalesDataAvailable
              ? `$${salesForecast.summary?.total_forecasted_revenue?.toLocaleString()}`
              : 'Pending Upload'}
          </div>
          <span style={{ fontSize: '0.95rem', color: '#565959', fontWeight: 600 }}>
            {isSalesDataAvailable
              ? `Next 7 Days Cumulative Projection`
              : 'Upload previous sales CSV to compute'}
          </span>
        </div>

        <div className="stat-card" style={{ borderTop: '4px solid #007600' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '11.5px', fontWeight: 700, color: '#007600', textTransform: 'uppercase' }}>
              Projected Daily Sales Pace
            </span>
            <TrendingUp size={16} className="text-emerald" />
          </div>
          <div className="value" style={{ color: isSalesDataAvailable ? '#007600' : '#888' }}>
            {isSalesDataAvailable
              ? `$${salesForecast.summary?.average_daily_revenue?.toLocaleString()} / day`
              : '---'}
          </div>
          <span style={{ fontSize: '0.95rem', color: '#565959', fontWeight: 600 }}>
            {isSalesDataAvailable
              ? `Peak Day: ${salesForecast.summary?.peak_day?.day_of_week || 'N/A'}`
              : 'Requires historical dataset'}
          </span>
        </div>
      </div>

      {/* CORE VISUALIZATIONS ROW: Sales Forecast Trajectory (Left) & Customer Risk Distribution (Right) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.45fr 1fr', gap: '20px' }}>
        {/* Sales Forecast Trajectory Chart */}
        <div className="stat-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f1111' }}>
                  📈 Next 7 Days Sales Forecast Trajectory
                </span>
                {isSalesDataAvailable && (
                  <span style={{ background: '#eaf8ea', color: '#007600', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>
                    Active ML Model
                  </span>
                )}
              </div>
              <p style={{ fontSize: '0.9rem', color: '#565959', marginTop: '3px' }}>
                {isSalesDataAvailable
                  ? `Revenue projection curve from ${salesForecast.start_date} to ${salesForecast.end_date} (±8% confidence band)`
                  : 'Predictive revenue curve based on store rolling trends & weekday seasonality'}
              </p>
            </div>
            <button
              onClick={() => navigate('/sales-forecast')}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#007185',
                fontSize: '0.9rem',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <span>Full Forecast Page</span>
              <ArrowRight size={14} />
            </button>
          </div>

          {isSalesDataAvailable ? (
            <div>
              <div
                style={{
                  width: '100%',
                  height: '240px',
                  background: '#0f172a',
                  borderRadius: '8px',
                  padding: '10px',
                  overflow: 'hidden'
                }}
              >
                <svg className="trend-svg" viewBox="0 0 1000 240" preserveAspectRatio="none" style={{ width: '100%', height: '100%' }}>
                  <line x1="50" y1="30" x2="980" y2="30" stroke="rgba(255,255,255,0.08)" strokeDasharray="4 4" />
                  <line x1="50" y1="90" x2="980" y2="90" stroke="rgba(255,255,255,0.08)" strokeDasharray="4 4" />
                  <line x1="50" y1="150" x2="980" y2="150" stroke="rgba(255,255,255,0.08)" strokeDasharray="4 4" />
                  <line x1="50" y1="210" x2="980" y2="210" stroke="rgba(255,255,255,0.2)" />

                  {(() => {
                    const futureData = salesForecast.schedule || [];
                    const allValues = [
                      ...futureData.map((d) => d.upper_bound || d.forecasted_revenue),
                      ...futureData.map((d) => d.lower_bound || d.forecasted_revenue)
                    ];
                    const maxVal = Math.max(...allValues, 6000);
                    const minVal = Math.min(...allValues, 0);

                    const getY = (val) => 210 - ((val - minVal) / (maxVal - minVal || 1)) * 170;
                    const getX = (idx) => 60 + (idx / (futureData.length - 1 || 1)) * 880;

                    const pointsForecast = futureData.map((d, i) => `${getX(i)},${getY(d.forecasted_revenue)}`).join(' ');
                    const pointsUpper = futureData.map((d, i) => `${getX(i)},${getY(d.upper_bound)}`).join(' ');
                    const pointsLower = futureData.slice().reverse().map((d, i) => `${getX(futureData.length - 1 - i)},${getY(d.lower_bound)}`).join(' ');
                    const areaBand = `${pointsUpper} ${pointsLower}`;

                    return (
                      <>
                        <polygon points={areaBand} fill="rgba(56, 189, 248, 0.15)" stroke="none" />
                        <polyline fill="none" stroke="#38bdf8" strokeWidth="3" points={pointsForecast} />
                        {futureData.map((d, i) => (
                          <g key={`dash-fc-${d.day_number}`}>
                            <circle
                              cx={getX(i)}
                              cy={getY(d.forecasted_revenue)}
                              r={d.is_weekend ? 5 : 3.5}
                              fill={d.is_weekend ? '#ffd814' : '#38bdf8'}
                              stroke="#0f172a"
                              strokeWidth="2"
                            />
                            <text
                              x={getX(i)}
                              y="230"
                              fill={d.is_weekend ? '#ffd814' : '#94a3b8'}
                              fontSize="11"
                              textAnchor="middle"
                              fontWeight={d.is_weekend ? 'bold' : 'normal'}
                            >
                              D{d.day_number} ({d.day_of_week.slice(0, 3)})
                            </text>
                          </g>
                        ))}
                      </>
                    );
                  })()}
                </svg>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px', fontSize: '12px', color: '#565959' }}>
                <span>Start: {salesForecast.start_date}</span>
                <span style={{ color: '#b7791f', fontWeight: 700 }}>🟡 Gold dots indicate Weekend peaks</span>
                <span>End: {salesForecast.end_date}</span>
              </div>
            </div>
          ) : (
            <div
              style={{
                border: '2px dashed #cbd5e1',
                borderRadius: '8px',
                padding: '2.5rem 1.5rem',
                textAlign: 'center',
                backgroundColor: '#f8fafc'
              }}
            >
              <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>📊</div>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#0f1111' }}>
                Sales Forecast Trajectory Pending
              </h4>
              <p style={{ color: '#565959', fontSize: '0.92rem', maxWidth: '420px', margin: '0.4rem auto 1.25rem' }}>
                Upload previous store sales history CSV to unlock the 7-day revenue trajectory curve and peak day demand predictions.
              </p>
              <button
                onClick={() => navigate('/upload')}
                className="btn-amazon-gold"
                style={{ padding: '0.65rem 1.25rem', fontSize: '0.95rem', fontWeight: 700 }}
              >
                Upload Sales Dataset (CSV) →
              </button>
            </div>
          )}
        </div>

        {/* Customer Churn Risk Breakdown */}
        <div className="stat-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
            <div>
              <span style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f1111' }}>
                👥 Customer Churn Risk Distribution
              </span>
              <p style={{ fontSize: '0.9rem', color: '#565959', marginTop: '3px' }}>
                Random Forest ML portfolio risk segmentation
              </p>
            </div>
            <button
              onClick={() => navigate('/churn-prediction')}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#007185',
                fontSize: '0.9rem',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <span>Detailed Churn</span>
              <ArrowRight size={14} />
            </button>
          </div>

          {/* Risk Level Progress Bars */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '20px' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.92rem', fontWeight: 700, marginBottom: '5px' }}>
                <span style={{ color: '#cc0c39' }}>High Risk (Immediate Churn Danger)</span>
                <span style={{ color: '#cc0c39' }}>{kpis?.high_risk_count?.toLocaleString() || 0}</span>
              </div>
              <div style={{ width: '100%', height: '8px', background: '#f1f5f9', borderRadius: '4px', overflow: 'hidden' }}>
                <div
                  style={{
                    width: `${Math.min(((kpis?.high_risk_count || 0) / (kpis?.total_customers || 1)) * 100, 100)}%`,
                    height: '100%',
                    backgroundColor: '#cc0c39'
                  }}
                ></div>
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.92rem', fontWeight: 700, marginBottom: '5px' }}>
                <span style={{ color: '#c7511f' }}>Medium Risk (Watchlist)</span>
                <span style={{ color: '#c7511f' }}>{kpis?.medium_risk_count?.toLocaleString() || 0}</span>
              </div>
              <div style={{ width: '100%', height: '8px', background: '#f1f5f9', borderRadius: '4px', overflow: 'hidden' }}>
                <div
                  style={{
                    width: `${Math.min(((kpis?.medium_risk_count || 0) / (kpis?.total_customers || 1)) * 100, 100)}%`,
                    height: '100%',
                    backgroundColor: '#c7511f'
                  }}
                ></div>
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.92rem', fontWeight: 700, marginBottom: '5px' }}>
                <span style={{ color: '#007600' }}>Low Risk (Retained Accounts)</span>
                <span style={{ color: '#007600' }}>{kpis?.low_risk_count?.toLocaleString() || 0}</span>
              </div>
              <div style={{ width: '100%', height: '8px', background: '#f1f5f9', borderRadius: '4px', overflow: 'hidden' }}>
                <div
                  style={{
                    width: `${Math.min(((kpis?.low_risk_count || 0) / (kpis?.total_customers || 1)) * 100, 100)}%`,
                    height: '100%',
                    backgroundColor: '#007600'
                  }}
                ></div>
              </div>
            </div>
          </div>

          {/* Membership Tier Quick Breakdown */}
          <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '14px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#565959', textTransform: 'uppercase' }}>
              Membership Tier Risk Rates
            </span>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', marginTop: '8px' }}>
              {summary?.membership_breakdown?.slice(0, 4).map((m, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '8px 10px',
                    borderRadius: '6px',
                    background: '#f8fafc',
                    border: '1px solid #e2e8f0',
                    fontSize: '12.5px'
                  }}
                >
                  <div style={{ fontWeight: 700, color: '#0f1111' }}>{m.membership}</div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '2px', color: '#565959' }}>
                    <span>{m.total} users</span>
                    <strong style={{ color: m.predicted_churn_rate > 25 ? '#cc0c39' : '#007600' }}>
                      {m.predicted_churn_rate}%
                    </strong>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

    </div>
  );
};

export default Dashboard;