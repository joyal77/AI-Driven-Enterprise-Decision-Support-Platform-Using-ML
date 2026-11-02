import { useEffect, useState } from "react";
import API from "../services/api";
import Layout from "../components/Layout";
import { Sliders, ShieldCheck, DollarSign, Award, ArrowUpRight, Sparkles } from "lucide-react";
import "./WhatIfSimulator.css";

function WhatIfSimulator() {
  const [reductionPct, setReductionPct] = useState(15);
  const [simResult, setSimResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    runSimulation(reductionPct);
  }, [reductionPct]);

  const runSimulation = async (pct) => {
    try {
      setLoading(true);
      const res = await API.post("/simulation/what-if", { target_reduction_pct: pct });
      setSimResult(res.data);
    } catch (err) {
      console.error("Simulation calculation error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout 
      title="What-If Churn & Revenue Protection Simulator"
      subtitle="Interactive executive decision tool to model churn reduction goals and quantify protected revenue"
    >
      <div className="simulator-container-grid">
        {/* Left Slider Control Card */}
        <div className="simulator-card glass-card">
          <div className="sim-header">
            <div className="sim-tag bg-gold-chip">
              <Sparkles size={16} />
              <span>Interactive Decision Model</span>
            </div>
            <h2>Churn Reduction Scenario Target</h2>
            <p>Adjust the churn reduction percentage target to model retained Skywards members and estimated protected revenue.</p>
          </div>

          <div className="slider-control-box">
            <div className="slider-label-row">
              <span className="slider-lbl font-bold">Target Churn Reduction Goal:</span>
              <span className="slider-val text-gold">{reductionPct}% Reduction</span>
            </div>

            <input 
              type="range" 
              min="5" 
              max="40" 
              step="5" 
              value={reductionPct}
              onChange={(e) => setReductionPct(parseFloat(e.target.value))}
              className="custom-range-slider"
            />

            <div className="slider-ticks">
              <span>5%</span>
              <span>15%</span>
              <span>25%</span>
              <span>35%</span>
              <span>40%</span>
            </div>
          </div>

          <div className="scenario-assumptions-box">
            <h4>Model Assumptions & Impact Formula</h4>
            <p>
              Simulates targeted Skywards VIP retention incentives (bonus miles, upgrade vouchers, route promos) deployed to High-Risk member accounts.
            </p>
          </div>
        </div>

        {/* Right Calculated Results Cards */}
        <div className="sim-results-column">
          <div className="sim-res-card glass-card">
            <div className="res-icon-title">
              <ShieldCheck size={28} className="text-emerald" />
              <div>
                <span className="res-lbl">Estimated Retained Members</span>
                <h1 className="res-val text-emerald">
                  +{simResult?.retained_members || 0} Members
                </h1>
              </div>
            </div>
            <p className="res-desc">High-risk Skywards members retained through targeted incentives</p>
          </div>

          <div className="sim-res-card glass-card">
            <div className="res-icon-title">
              <DollarSign size={28} className="text-gold" />
              <div>
                <span className="res-lbl">Estimated Protected Revenue</span>
                <h1 className="res-val text-gold">
                  ₹{simResult?.protected_revenue?.toLocaleString() || "0.00"}
                </h1>
              </div>
            </div>
            <p className="res-desc">Annual flight ticket spend saved from churn risk exposure</p>
          </div>

          <div className="sim-res-card glass-card">
            <div className="res-icon-title">
              <Award size={28} className="text-cyan" />
              <div>
                <span className="res-lbl">Projected Business Health Score</span>
                <h1 className="res-val text-cyan">
                  {simResult?.new_health_score || 82} / 100
                </h1>
              </div>
            </div>
            <p className="res-desc">Improved enterprise health rating following churn reduction</p>
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default WhatIfSimulator;
