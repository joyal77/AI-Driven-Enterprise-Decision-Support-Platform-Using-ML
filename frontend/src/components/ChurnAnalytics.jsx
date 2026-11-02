import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import API from "../services/api";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { ShieldAlert, AlertCircle, CheckCircle2, ArrowRight, Sparkles, Star } from "lucide-react";
import "./ChurnAnalytics.css";

function ChurnAnalytics() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchChurnSummary();
  }, []);

  const fetchChurnSummary = async () => {
    try {
      setLoading(true);
      const res = await API.get("/dashboard/churn-summary");
      setSummary(res.data);
    } catch (err) {
      console.error("Error loading churn analytics summary:", err);
    } finally {
      setLoading(false);
    }
  };

  const chartData = summary ? [
    { name: "High Risk", value: summary.high_risk_customers, color: "#c8102e" },
    { name: "Medium Risk", value: summary.medium_risk_customers, color: "#f59e0b" },
    { name: "Low Risk", value: summary.low_risk_customers, color: "#10b981" }
  ] : [];

  return (
    <div className="churn-analytics-section glass-card">
      <div className="section-header-row">
        <div>
          <div className="section-badge bg-gold-chip">
            <Sparkles size={16} />
            <span>XGBoost Churn Classifier + SHAP XAI</span>
          </div>
          <h3 className="section-title">Skywards Member Churn Risk Intelligence</h3>
          <p className="section-subtitle">Real-time risk tier distribution and revenue at risk from database records</p>
        </div>

        <Link to="/churn" className="section-action-btn">
          <span>Manage Members & AI Profiles</span>
          <ArrowRight size={20} />
        </Link>
      </div>

      {loading ? (
        <div className="churn-skeleton skeleton" style={{ height: "220px" }} />
      ) : (
        <div className="churn-summary-grid">
          {/* Risk Pie Chart */}
          <div className="chart-container-box">
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: "#0e1222", borderColor: "#334155", borderRadius: "12px" }}
                  itemStyle={{ color: "#f8fafc", fontWeight: 700 }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="donut-center-info">
              <span className="donut-val">{summary?.total_predictions || 0}</span>
              <span className="donut-lbl">Evaluated</span>
            </div>
          </div>

          {/* KPI Mini Cards Grid */}
          <div className="risk-cards-grid">
            <div className="risk-card high-risk">
              <div className="risk-card-top">
                <ShieldAlert size={24} className="text-rose" />
                <span className="risk-pill high">≥ 70% Prob</span>
              </div>
              <span className="risk-card-lbl">🔴 High Risk Members</span>
              <h2 className="risk-card-val text-rose">{summary?.high_risk_customers || 0}</h2>
              <span className="risk-subtext">Priority retention action required</span>
            </div>

            <div className="risk-card med-risk">
              <div className="risk-card-top">
                <AlertCircle size={24} className="text-amber" />
                <span className="risk-pill med">30% - 69% Prob</span>
              </div>
              <span className="risk-card-lbl">🟡 Medium Risk Members</span>
              <h2 className="risk-card-val text-amber">{summary?.medium_risk_customers || 0}</h2>
              <span className="risk-subtext">Targeted route promos required</span>
            </div>

            <div className="risk-card low-risk">
              <div className="risk-card-top">
                <CheckCircle2 size={24} className="text-emerald" />
                <span className="risk-pill low">&lt; 30% Prob</span>
              </div>
              <span className="risk-card-lbl">🟢 Low Risk Members</span>
              <h2 className="risk-card-val text-emerald">{summary?.low_risk_customers || 0}</h2>
              <span className="risk-subtext">Stable loyal members</span>
            </div>

            <div className="risk-card at-risk-rev">
              <div className="risk-card-top">
                <Star size={24} className="text-gold" />
                <span className="risk-pill gold">Overall Rating</span>
              </div>
              <span className="risk-card-lbl">⭐ Avg Satisfaction</span>
              <h2 className="risk-card-val text-gold">{summary?.avg_satisfaction || "4.2"} / 5.0</h2>
              <span className="risk-subtext">Overall passenger service rating</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChurnAnalytics;