import React, { useEffect, useState } from 'react';
import { getChurnAnalyticsDeepDive } from '../services/api';

const ChurnAnalyticsPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDeepDiveData();
  }, []);

  const fetchDeepDiveData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getChurnAnalyticsDeepDive();
      setData(res);
    } catch (err) {
      console.error('Error loading churn analytics:', err);
      setError('Failed to fetch Amazon analytics deep dive.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '4rem', textAlign: 'center' }}>
        <p style={{ color: '#565959' }}>Loading Amazon Behavioral Deep Dive Analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stat-card" style={{ padding: '2rem', borderColor: '#cc0c39', backgroundColor: '#fde8e8' }}>
        <h3 style={{ color: '#cc0c39' }}>⚠️ Analytics Error</h3>
        <p style={{ color: '#0f1111', marginTop: '0.5rem' }}>{error}</p>
        <button onClick={fetchDeepDiveData} className="btn-amazon-gold" style={{ marginTop: '1rem' }}>
          🔄 Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <div className="stat-card" style={{ marginBottom: '1.25rem', borderLeft: '5px solid #ff9900' }}>
        <h2 style={{ fontSize: '1.25rem', color: '#0f1111', fontWeight: 800 }}>
          Amazon Customer Behavior & Friction Analytics
        </h2>
        <p style={{ color: '#565959', fontSize: '0.85rem', marginTop: '0.2rem' }}>
          Real-time analytics derived from live customer database records analyzing inactivity windows, order frequencies, and customer service friction.
        </p>
      </div>

      {/* Inactivity Analysis Table */}
      <div className="stat-card" style={{ marginBottom: '1.25rem' }}>
        <h3 style={{ marginBottom: '1rem', fontSize: '1rem', color: '#0f1111', textTransform: 'none', fontWeight: 700 }}>
          📅 Account Inactivity Period vs. Churn Rate
        </h3>
        <table className="data-table">
          <thead>
            <tr>
              <th>Inactivity Window</th>
              <th>Total Customers</th>
              <th>Dataset Actual Churners</th>
              <th>Actual Churn Rate %</th>
              <th>Predicted Churners (ML)</th>
              <th>Predicted Risk Rate %</th>
            </tr>
          </thead>
          <tbody>
            {data?.inactivity_analysis?.map((item, idx) => (
              <tr key={idx}>
                <td><strong>{item.activity_period}</strong></td>
                <td>{item.total_customers?.toLocaleString()}</td>
                <td>{item.actual_churners?.toLocaleString()}</td>
                <td>
                  <span className={item.actual_churn_rate > 30 ? 'badge-high' : 'badge-low'}>
                    {item.actual_churn_rate}%
                  </span>
                </td>
                <td>{item.predicted_churners?.toLocaleString()}</td>
                <td>
                  <span className={item.predicted_churn_rate > 30 ? 'badge-high' : 'badge-low'}>
                    {item.predicted_churn_rate}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', marginBottom: '2rem' }}>
        {/* Purchase Frequency Table */}
        <div className="stat-card">
          <h3 style={{ marginBottom: '1rem', fontSize: '0.95rem', color: '#0f1111', textTransform: 'none', fontWeight: 700 }}>
            🛍️ Purchase Frequency vs. Churn Rate
          </h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>Lifetime Orders</th>
                <th>Total Accounts</th>
                <th>Actual Churners</th>
                <th>Churn Rate</th>
              </tr>
            </thead>
            <tbody>
              {data?.purchase_frequency?.map((item, idx) => (
                <tr key={idx}>
                  <td><strong>{item.order_range}</strong></td>
                  <td>{item.total_customers?.toLocaleString()}</td>
                  <td>{item.actual_churners?.toLocaleString()}</td>
                  <td>
                    <span className={item.actual_churn_rate > 20 ? 'badge-medium' : 'badge-low'}>
                      {item.actual_churn_rate}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Customer Support Friction Table */}
        <div className="stat-card">
          <h3 style={{ marginBottom: '1rem', fontSize: '0.95rem', color: '#0f1111', textTransform: 'none', fontWeight: 700 }}>
            🎧 Customer Service Ticket Friction
          </h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>Tickets Count</th>
                <th>Total Accounts</th>
                <th>Actual Churners</th>
                <th>Churn Rate</th>
              </tr>
            </thead>
            <tbody>
              {data?.ticket_friction_analysis?.map((item, idx) => (
                <tr key={idx}>
                  <td><strong>{item.ticket_range}</strong></td>
                  <td>{item.total_customers?.toLocaleString()}</td>
                  <td>{item.actual_churners?.toLocaleString()}</td>
                  <td>
                    <span className={item.actual_churn_rate > 25 ? 'badge-high' : 'badge-low'}>
                      {item.actual_churn_rate}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ChurnAnalyticsPage;
