import React, { useState } from 'react';
import { runBatchPrediction } from '../services/api';

const ChurnPrediction = () => {
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleRunBatch = async () => {
    setRunning(true);
    setError(null);
    try {
      const res = await runBatchPrediction();
      setResult(res);
    } catch (err) {
      console.error('Error running batch prediction:', err);
      setError('Batch prediction failed. Ensure backend server and database are active.');
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="stat-card" style={{ marginBottom: '2rem', borderLeft: '6px solid #ff9900', padding: '2rem' }}>
        <h2 style={{ fontSize: '1.65rem', color: '#0f1111', fontWeight: 900, marginBottom: '0.5rem' }}>
          Amazon Automated Batch Prediction Control Center
        </h2>
        <p style={{ color: '#565959', fontSize: '1.15rem', marginBottom: '1.75rem' }}>
          Execute end-to-end Random Forest churn inference over all Amazon customer accounts. Automated preprocessing, probability scoring, decision thresholding, and retention action generation.
        </p>

        <button
          onClick={handleRunBatch}
          disabled={running}
          className="btn-amazon-gold"
          style={{
            padding: '0.9rem 2.2rem',
            fontSize: '1.15rem',
            fontWeight: 800,
            opacity: running ? 0.7 : 1,
            cursor: running ? 'not-allowed' : 'pointer',
          }}
        >
          {running ? '⏳ Executing Random Forest Model Batch Inference...' : '🚀 Execute Full Batch Churn Prediction'}
        </button>
      </div>

      {error && (
        <div style={{ backgroundColor: '#fde8e8', color: '#cc0c39', padding: '1.25rem', borderRadius: '8px', border: '1px solid #f8b4b4', marginBottom: '2rem', fontSize: '1.1rem', fontWeight: 600 }}>
          ⚠️ {error}
        </div>
      )}

      {result && (
        <div className="animate-fade-in">
          <h3 style={{ marginBottom: '1.25rem', fontSize: '1.4rem', color: '#0f1111', fontWeight: 800 }}>Latest Batch Predictions Breakdown</h3>
          <div className="card-grid">
            <div className="stat-card" style={{ borderTop: '4px solid #ff9900' }}>
              <h3>Total Evaluated Accounts</h3>
              <div className="value">{result.total_processed?.toLocaleString()}</div>
            </div>
            <div className="stat-card" style={{ borderTop: '4px solid #cc0c39' }}>
              <h3>High Risk Count</h3>
              <div className="value" style={{ color: '#cc0c39' }}>{result.high_risk_customers?.toLocaleString()}</div>
            </div>
            <div className="stat-card" style={{ borderTop: '4px solid #c7511f' }}>
              <h3>Medium Risk Count</h3>
              <div className="value" style={{ color: '#c7511f' }}>{result.medium_risk_customers?.toLocaleString()}</div>
            </div>
            <div className="stat-card" style={{ borderTop: '4px solid #007600' }}>
              <h3>Low Risk Count</h3>
              <div className="value" style={{ color: '#007600' }}>{result.low_risk_customers?.toLocaleString()}</div>
            </div>
          </div>

          <div style={{ backgroundColor: '#f0fdf4', padding: '1.6rem 2rem', borderRadius: '8px', border: '1px solid #bbf7d0' }}>
            <h4 style={{ color: '#007600', marginBottom: '0.5rem', fontSize: '1.25rem', fontWeight: 900 }}>
              ✅ Batch Inference Completed Successfully
            </h4>
            <p style={{ fontSize: '1.1rem', color: '#0f1111' }}>{result.message}</p>
            <p style={{ fontSize: '1.1rem', color: '#0f1111', marginTop: '0.4rem' }}>
              <strong>Portfolio Average Churn Probability:</strong> <span style={{ color: '#cc0c39', fontWeight: 800 }}>{result.average_churn_probability}%</span>
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChurnPrediction;