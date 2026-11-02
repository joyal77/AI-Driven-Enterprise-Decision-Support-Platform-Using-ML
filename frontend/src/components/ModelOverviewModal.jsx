import React from "react";
import { 
  X, 
  Cpu, 
  Target, 
  Search, 
  BarChart3, 
  Briefcase, 
  Wifi, 
  Plane, 
  Ticket, 
  CheckCircle2, 
  Sparkles,
  ShieldCheck,
  TrendingUp,
  DollarSign
} from "lucide-react";
import "./ModelOverviewModal.css";

function ModelOverviewModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="model-modal-container glass-card" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <div className="header-title-box">
            <div className="icon-badge bg-gold-chip">
              <Cpu size={20} />
              <span>Model Architecture & Intelligence</span>
            </div>
            <h2>Tuned XGBoost Customer Churn Prediction Model</h2>
            <p className="sub-text">Airline Passenger Satisfaction & Churn Risk System</p>
          </div>
          <button className="close-btn" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        {/* Modal Scrollable Body */}
        <div className="modal-body-scroll">
          {/* Section 1: What is the Model? */}
          <div className="modal-section-card">
            <div className="section-header-iconic">
              <Cpu size={22} className="text-gold" />
              <h3>1. 🤖 What is the Model?</h3>
            </div>
            <p className="section-desc">
              Your model is a <strong>Tuned XGBoost (eXtreme Gradient Boosting) Classifier</strong>—an advanced, highly accurate ensemble machine learning model trained specifically on airline passenger travel and service satisfaction metrics.
            </p>
            <div className="specs-pill-grid">
              <div className="spec-pill">
                <span className="lbl">Model File:</span>
                <span className="val font-mono">churn_model_xgb.pkl</span>
              </div>
              <div className="spec-pill">
                <span className="lbl">Preprocessing:</span>
                <span className="val font-mono">scaler.pkl + label_encoders.pkl</span>
              </div>
              <div className="spec-pill">
                <span className="lbl">Explainable AI:</span>
                <span className="val font-mono">SHAP TreeExplainer</span>
              </div>
            </div>
          </div>

          {/* Section 2: What Does it Predict? */}
          <div className="modal-section-card">
            <div className="section-header-iconic">
              <Target size={22} className="text-cyan" />
              <h3>2. 🎯 What Does it Predict?</h3>
            </div>
            <p className="section-desc">
              The model predicts <strong>Passenger Dissatisfaction & Churn Probability (0% – 100%)</strong> for every airline member:
            </p>
            <div className="predict-outputs-grid">
              <div className="output-box green">
                <div className="out-val">Class 0</div>
                <div className="out-lbl">Satisfied / Retained Passenger</div>
                <div className="out-desc">Likely to rebook with Emirates</div>
              </div>
              <div className="output-box red">
                <div className="out-val">Class 1</div>
                <div className="out-lbl">Dissatisfied / At-Risk Churner</div>
                <div className="out-desc">Likely to switch to competitor or stop flying</div>
              </div>
            </div>

            <div className="risk-tiers-wrapper">
              <h4 className="sub-heading">Risk Classification Tiers:</h4>
              <div className="risk-tier-item high">
                <span className="tier-badge-pill high">🔴 High Risk (≥ 70%)</span>
                <span>Passengers experiencing severe service friction requiring urgent concierge outreach.</span>
              </div>
              <div className="risk-tier-item med">
                <span className="tier-badge-pill med">🟡 Medium Risk (30% – 69%)</span>
                <span>Moderate friction; candidate for automated digital incentives.</span>
              </div>
              <div className="risk-tier-item low">
                <span className="tier-badge-pill low">🟢 Low Risk (&lt; 30%)</span>
                <span>High satisfaction; low risk of churn.</span>
              </div>
            </div>
          </div>

          {/* Section 3: Key Churn Factors Analyzed */}
          <div className="modal-section-card">
            <div className="section-header-iconic">
              <Search size={22} className="text-amber" />
              <h3>3. 🔍 Key Churn Factors Analyzed (22 Features)</h3>
            </div>
            <p className="section-desc">
              The model evaluates 22 core flight experience and demographic attributes to calculate churn probability. Its top decision drivers are:
            </p>
            <div className="factors-list">
              <div className="factor-card">
                <div className="factor-title">
                  <Wifi size={18} className="text-gold" />
                  <strong>1. Inflight WiFi Service (Rating 1–5):</strong>
                </div>
                <p>Low WiFi ratings dramatically increase dissatisfaction probability, especially among business travellers needing continuous connectivity.</p>
              </div>

              <div className="factor-card">
                <div className="factor-title">
                  <Plane size={18} className="text-cyan" />
                  <strong>2. Type of Travel (Business vs. Personal Travel):</strong>
                </div>
                <p>Personal/leisure travellers are significantly more price and convenience-sensitive compared to corporate business travellers.</p>
              </div>

              <div className="factor-card">
                <div className="factor-title">
                  <Ticket size={18} className="text-emerald" />
                  <strong>3. Online Boarding (Rating 1–5):</strong>
                </div>
                <p>Digital boarding and mobile check-in friction is a primary driver for early passenger drop-off.</p>
              </div>

              <div className="factor-card secondary">
                <strong>4. Secondary Factors:</strong> Flight Delays (Departure/Arrival), Seat Comfort, Inflight Entertainment, Cleanliness, Baggage Handling, and Flight Distance.
              </div>
            </div>
          </div>

          {/* Section 4: Model Performance & Benchmarks */}
          <div className="modal-section-card">
            <div className="section-header-iconic">
              <BarChart3 size={22} className="text-emerald" />
              <h3>4. 📈 Model Performance & Benchmarks</h3>
            </div>
            <div className="benchmarks-table-wrapper">
              <table className="benchmarks-table">
                <thead>
                  <tr>
                    <th>Metric</th>
                    <th>Score</th>
                    <th>What it Means for the Airline</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="font-bold">Recall</td>
                    <td><span className="metric-badge green">0.98 (98%)</span></td>
                    <td><strong>Catches 98 out of 100 potential churners</strong>, ensuring almost no at-risk customer goes undetected.</td>
                  </tr>
                  <tr>
                    <td className="font-bold">F1-Score</td>
                    <td><span className="metric-badge green">0.96 (96%)</span></td>
                    <td>Excellent balance between high precision and high recall (minimal false alarms).</td>
                  </tr>
                  <tr>
                    <td className="font-bold">ROC-AUC</td>
                    <td><span className="metric-badge green">0.99 (99%)</span></td>
                    <td>Exceptional ability to distinguish between satisfied and dissatisfied passengers.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Section 5: Practical Business Use */}
          <div className="modal-section-card">
            <div className="section-header-iconic">
              <Briefcase size={22} className="text-gold" />
              <h3>5. 💼 Practical Business Use</h3>
            </div>
            <p className="section-desc">
              Allows the airline to take proactive, prescriptive retention actions before customers stop flying:
            </p>
            <div className="use-cases-list">
              <div className="use-case-item">
                <DollarSign size={20} className="text-gold" />
                <div>
                  <strong>Revenue Protection:</strong> Estimates Revenue at Risk (e.g., ₹4.8M associated with High-Risk members) so executives can calculate retention ROI.
                </div>
              </div>

              <div className="use-case-item">
                <Sparkles size={20} className="text-cyan" />
                <div>
                  <strong>Targeted Interventions:</strong>
                  <ul className="sub-interventions">
                    <li>Low WiFi score → Issues Complimentary High-Speed WiFi Voucher.</li>
                    <li>Low Online Boarding score → Offers Priority Fast-Track Mobile Boarding Passes.</li>
                    <li>Personal Travel friction → Sends 15% Leisure Promo Code + 5,000 bonus Skywards miles.</li>
                  </ul>
                </div>
              </div>

              <div className="use-case-item">
                <ShieldCheck size={20} className="text-emerald" />
                <div>
                  <strong>Root Cause Diagnostics:</strong> Explains <em>why</em> a customer is leaving using SHAP feature attributions to fix operational bottlenecks.
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          <button className="done-btn" onClick={onClose}>
            <span>Close Overview</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default ModelOverviewModal;
