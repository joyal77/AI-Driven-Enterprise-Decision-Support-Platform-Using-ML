import { useEffect, useState } from "react";
import API from "../services/api";
import Layout from "../components/Layout";
import { ShieldAlert, AlertTriangle, CheckCircle2, ChevronRight, Sparkles } from "lucide-react";
import "./RiskAnalysis.css";

function RiskAnalysis() {
  const [activeTab, setActiveTab] = useState("high risk");
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRiskMembers();
  }, [activeTab]);

  const fetchRiskMembers = async () => {
    try {
      setLoading(true);
      const res = await API.get("/churn/customers", {
        params: { risk_level: activeTab }
      });
      setMembers(res.data.customers || []);
    } catch (err) {
      console.error("Error fetching risk members:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout 
      title="Skywards Member Risk Analysis" 
      subtitle="Categorized risk analysis interface for priority VIP retention, targeted engagement, and loyalty upselling"
    >
      <div className="risk-analysis-container">
        {/* Risk Tabs Header */}
        <div className="risk-tabs-header glass-card">
          <button 
            className={`risk-tab-btn high ${activeTab === 'high risk' ? 'active' : ''}`}
            onClick={() => setActiveTab('high risk')}
          >
            <ShieldAlert size={22} />
            <span>🔴 High Risk (≥ 70%)</span>
          </button>

          <button 
            className={`risk-tab-btn med ${activeTab === 'medium risk' ? 'active' : ''}`}
            onClick={() => setActiveTab('medium risk')}
          >
            <AlertTriangle size={22} />
            <span>🟡 Medium Risk (30-69%)</span>
          </button>

          <button 
            className={`risk-tab-btn low ${activeTab === 'low risk' ? 'active' : ''}`}
            onClick={() => setActiveTab('low risk')}
          >
            <CheckCircle2 size={22} />
            <span>🟢 Low Risk (&lt; 30%)</span>
          </button>
        </div>

        {/* Members List Table */}
        <div className="risk-members-card glass-card">
          <div className="card-top-title">
            <h3>
              {activeTab === 'high risk' ? '🔴 Priority High Risk Members Requiring Urgent VIP Outreach' :
               activeTab === 'medium risk' ? '🟡 Medium Risk Members Candidate for Targeted Flight Promos' :
               '🟢 Low Risk Stable Members Candidate for Loyalty & Cabin Upselling'}
            </h3>
            <span className="count-pill bg-gold-chip">{members.length} Members Found</span>
          </div>

          {loading ? (
            <div className="skeleton" style={{ height: "300px" }} />
          ) : (
            <div className="table-scroll-wrapper">
              <table className="risk-table">
                <thead>
                  <tr>
                    <th>Member ID</th>
                    <th>Member Name</th>
                    <th>Skywards Tier</th>
                    <th>Cabin Class</th>
                    <th>Flight Frequency</th>
                    <th>Days Since Last Flight</th>
                    <th>Total Spend</th>
                    <th>Churn Probability</th>
                  </tr>
                </thead>
                <tbody>
                  {members.length === 0 ? (
                    <tr>
                      <td colSpan="8" className="empty-td">No members in this risk tier.</td>
                    </tr>
                  ) : (
                    members.map((m) => (
                      <tr key={m.customer_id} className="risk-row">
                        <td className="font-mono">EMR-{1000 + m.customer_id}</td>
                        <td className="font-bold">{m.customer_name}</td>
                        <td><span className="tier-tag">{m.subscription_type}</span></td>
                        <td>{m.contract_length}</td>
                        <td>{m.usage_frequency} Flights/Yr</td>
                        <td>{m.last_interaction} Days ago</td>
                        <td className="font-bold text-gold">₹{m.total_spend?.toLocaleString()}</td>
                        <td>
                          <span className={`prob-tag-bold ${m.churn_probability >= 70 ? 'high' : m.churn_probability >= 30 ? 'med' : 'low'}`}>
                            {m.churn_probability}%
                          </span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

export default RiskAnalysis;
