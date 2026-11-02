import { useEffect, useState } from "react";
import API, { downloadBatchPredictionPDF, previewBatchPredictionPDF } from "../services/api";
import Layout from "../components/Layout";
import { FileText, Printer, Download, Eye, Sparkles, Plane, ShieldAlert, Award } from "lucide-react";
import "./ExecutiveReports.css";

function ExecutiveReports() {
  const [kpi, setKpi] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [previewingPdf, setPreviewingPdf] = useState(false);

  useEffect(() => {
    fetchReportData();
  }, []);

  const fetchReportData = async () => {
    try {
      setLoading(true);
      const [kpiRes, sumRes] = await Promise.all([
        API.get("/dashboard/kpis"),
        API.get("/dashboard/churn-summary")
      ]);
      setKpi(kpiRes.data);
      setSummary(sumRes.data);
    } catch (err) {
      console.error("Error loading report data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    setDownloadingPdf(true);
    try {
      await downloadBatchPredictionPDF();
    } catch (err) {
      console.error("Failed to download PDF report:", err);
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handlePreviewPdf = async () => {
    setPreviewingPdf(true);
    try {
      await previewBatchPredictionPDF();
    } catch (err) {
      console.error("Failed to preview PDF report:", err);
    } finally {
      setPreviewingPdf(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <Layout 
      title="Amazon Executive Analytics Report"
      subtitle="Executive report covering customer portfolio performance, churn risk exposure, and prescriptive retention action plan"
    >
      <div className="report-action-bar no-print" style={{ display: 'flex', gap: '1rem' }}>
        <button onClick={handlePreviewPdf} disabled={previewingPdf} className="print-btn" style={{ backgroundColor: '#ff9900', color: '#0f1111' }}>
          <Eye size={20} />
          <span>{previewingPdf ? 'Opening PDF...' : 'View PDF (Preview)'}</span>
        </button>
        <button onClick={handlePrint} className="print-btn">
          <Printer size={20} />
          <span>Print Report</span>
        </button>
      </div>

      <div className="report-document glass-card">
        {/* Report Document Header */}
        <div className="report-header">
          <div className="report-brand">
            <div className="report-logo">
              <Plane size={28} />
            </div>
            <div>
              <h1 className="report-title">Emirates Revenue & Customer Analytics</h1>
              <span className="report-tagline">Predict Revenue. Understand Customers. Improve Retention.</span>
            </div>
          </div>

          <div className="report-meta font-mono">
            <div>Date: {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</div>
            <div>Classification: Confidential Executive Demo</div>
            <div>Author: XGBoost & SHAP Intelligence Engine</div>
          </div>
        </div>

        <div className="report-divider" />

        {/* Section 1: Executive Summary */}
        <div className="report-section">
          <h2>1. Executive Summary</h2>
          <p>
            This report presents an operational and predictive summary of Emirates Skywards member portfolios, revenue trajectories, and retention risk exposure evaluated by the platform's XGBoost machine learning models.
          </p>

          <div className="report-kpi-grid">
            <div className="rep-kpi">
              <span className="rep-kpi-lbl">Total Flight Revenue</span>
              <span className="rep-kpi-val text-emerald">₹{kpi?.total_sales?.toLocaleString() || "0"}</span>
            </div>
            <div className="rep-kpi">
              <span className="rep-kpi-lbl">XGBoost Forecasted Revenue</span>
              <span className="rep-kpi-val text-cyan">₹{kpi?.forecasted_revenue?.toLocaleString() || "0"}</span>
            </div>
            <div className="rep-kpi">
              <span className="rep-kpi-lbl">💰 Revenue at Risk</span>
              <span className="rep-kpi-val text-rose">₹{kpi?.revenue_at_risk?.toLocaleString() || "0"}</span>
            </div>
            <div className="rep-kpi">
              <span className="rep-kpi-lbl">Business Health Score</span>
              <span className="rep-kpi-val text-gold">{kpi?.business_health_score || 82} / 100 ({kpi?.health_status})</span>
            </div>
          </div>
        </div>

        {/* Section 2: Churn Risk Exposure */}
        <div className="report-section">
          <h2>2. Skywards Member Churn Risk Breakdown</h2>
          <table className="report-table">
            <thead>
              <tr>
                <th>Risk Classification</th>
                <th>Threshold</th>
                <th>Member Count</th>
                <th>Action Strategy</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="font-bold text-rose">🔴 High Risk</td>
                <td>≥ 70% Churn Probability</td>
                <td className="font-bold">{summary?.high_risk_customers || 0}</td>
                <td>Priority VIP Retention Outreach, 20% Bonus Miles Voucher, Business Upgrade</td>
              </tr>
              <tr>
                <td className="font-bold text-amber">🟡 Medium Risk</td>
                <td>30% – 69% Churn Probability</td>
                <td className="font-bold">{summary?.medium_risk_customers || 0}</td>
                <td>Targeted Route Promotions, 5,000 Bonus Skywards Miles Campaign</td>
              </tr>
              <tr>
                <td className="font-bold text-emerald">🟢 Low Risk</td>
                <td>&lt; 30% Churn Probability</td>
                <td className="font-bold">{summary?.low_risk_customers || 0}</td>
                <td>Loyalty Rewards, Cabin Class Upselling & Lounge Passes</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Section 3: Root Cause Analysis & Prescriptive Recommendations */}
        <div className="report-section">
          <h2>3. Operational Root Causes & Prescriptive Recommendations</h2>
          <ul className="report-bullet-list">
            <li><strong>Fading Travel Engagement (&gt;30 Days Gap):</strong> Trigger personalized re-engagement flight schedule recommendations for preferred routes.</li>
            <li><strong>High Booking Cancellation Friction:</strong> Offer flexible zero-fee reschedule options and priority concierge assistance.</li>
            <li><strong>Non-Tier Economy Member Exposure:</strong> Deploy Skywards tier-upgrade promotions to incentivize Gold/Platinum tier commitments.</li>
          </ul>
        </div>

        <div className="report-footer-signature">
          <span>Approved by Emirates Revenue & Customer Analytics Committee</span>
          <span className="font-mono">Document Signature ID: EMR-XGB-2026-CONFIDENTIAL</span>
        </div>
      </div>
    </Layout>
  );
}

export default ExecutiveReports;
