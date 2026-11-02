import React, { useEffect, useState, useRef } from 'react';
import { createPortal } from 'react-dom';
import { Link } from 'react-router-dom';
import { ShoppingBag, Upload, Users, Sparkles, CheckCircle2, AlertCircle, XCircle, Copy, Check, Download } from 'lucide-react';
import {
  getCustomers,
  getCustomerDetails,
  downloadBatchPredictionPDF,
  previewBatchPredictionPDF,
  downloadCustomerPDF,
  previewCustomerPDF,
  runBatchPrediction,
  toggleCustomerRetentionAction
} from '../services/api';
import './CustomerAnalytics.css';

const CustomerAnalytics = () => {
  const [customers, setCustomers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [riskCategory, setRiskCategory] = useState('all');
  const [groundTruthFilter, setGroundTruthFilter] = useState('all');
  const [customerSource, setCustomerSource] = useState('store'); // 'store' | 'uploaded' | 'all'
  const [loading, setLoading] = useState(true);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [downloadingBatch, setDownloadingBatch] = useState(false);
  const [previewingBatch, setPreviewingBatch] = useState(false);
  const [runningBatch, setRunningBatch] = useState(false);
  const [downloadingCust, setDownloadingCust] = useState(false);
  const [previewingCust, setPreviewingCust] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const [loadingModalId, setLoadingModalId] = useState(null);
  const [actionStatusMap, setActionStatusMap] = useState({});
  const [processingMap, setProcessingMap] = useState({});
  const [retentionToast, setRetentionToast] = useState(null);
  const [isDetailsLoading, setIsDetailsLoading] = useState(false);
  const customerCacheRef = useRef({});
  const abortControllerRef = useRef(null);

  const cleanPlanString = (str) => {
    if (!str) return '';
    return str
      .replace(/Automated WhatsApp & SMS Cart Recovery with Free Delivery/gi, 'Automated Cart Recovery with Free Delivery')
      .replace(/Automated SMS\/WhatsApp nudge with/gi, 'Send')
      .replace(/Automated SMS\/WhatsApp nudge/gi, 'Automated message')
      .replace(/SMS\/WhatsApp nudge/gi, 'customer message')
      .replace(/WhatsApp \/ SMS Direct Recovery/gi, 'Customer Account Messages')
      .replace(/WhatsApp \/ SMS/gi, 'Customer Account')
      .replace(/instant WhatsApp nudge/gi, 'customer account message')
      .replace(/WhatsApp nudge/gi, 'customer message')
      .replace(/WhatsApp/gi, 'Customer Message');
  };

  const getConcisePlanText = (camp) => {
    if (typeof camp === 'string') return cleanPlanString(camp);
    let raw = camp.action_summary || camp.objective || camp.title || '';
    if (raw.includes(':')) {
      const parts = raw.split(':');
      const afterColon = parts.slice(1).join(':').trim();
      if (afterColon) raw = afterColon;
    }
    return cleanPlanString(raw);
  };

  const generateSimpleExplanation = (churnProbability, riskCategory, shapExplanation) => {
    if (!shapExplanation || !Array.isArray(shapExplanation) || shapExplanation.length === 0) {
      return "The exact reason for this customer's risk profile cannot be determined from the available data. Additional shopping or interaction history is required to identify specific behavioral drivers.";
    }

    let prob = parseFloat(String(churnProbability || 0).replace("%", ""));
    if (prob > 0 && prob <= 1.0) {
      prob = prob * 100;
    }

    let risk = (riskCategory || "").toLowerCase();
    if (!risk) {
      if (prob >= 65.0) risk = "high risk";
      else if (prob >= 35.0) risk = "medium risk";
      else risk = "low risk";
    }

    const isHigh = risk.includes("high");
    const isMed = risk.includes("medium") || risk.includes("moderate");
    const isLow = risk.includes("low");

    // Sentence 1: Overall Risk State
    let s1 = isHigh
      ? "This customer has a high predicted risk of leaving."
      : isMed
      ? "This customer has a moderate predicted risk of leaving."
      : "This customer has a low predicted risk of leaving.";

    // Top 2-3 most relevant factors
    let topItems = shapExplanation.slice(0, 3);
    if (
      topItems.length > 2 &&
      (topItems[2].importance || 0) < 0.005 &&
      (parseFloat(topItems[2].importance_pct) || topItems[2].contribution_val || 0) < 5.0
    ) {
      topItems = topItems.slice(0, 2);
    }

    const describeFeature = (item) => {
      const feat = (item.feature || "").toLowerCase();
      const lbl = (item.label || feat).toLowerCase();
      const val = String(item.value || "").trim();

      // Customer Service Tickets
      if (feat.includes("ticket") || lbl.includes("ticket") || feat.includes("service")) {
        const digits = val.replace(/\D/g, "");
        const num = digits ? parseInt(digits, 10) : null;
        if (num !== null) {
          if (num === 0) return { full: "having no customer support complaints", short: "a clean support record" };
          if (num === 1) return { full: "one customer support ticket", short: "one support ticket" };
          return { full: `${num} customer support tickets`, short: `${num} support tickets` };
        }
        return { full: `customer support ticket history (${val})`, short: "support tickets" };
      }

      // App Sessions
      if (feat.includes("session") || lbl.includes("session")) {
        const digits = val.replace(/\D/g, "");
        const num = digits ? parseInt(digits, 10) : null;
        if (num !== null) {
          if (num === 0) return { full: "no app visits in the past month", short: "lack of app visits" };
          return { full: `recent app activity (${num} visits in the last 30 days)`, short: "recent app activity" };
        }
        return { full: `app engagement levels (${val})`, short: "recent app activity" };
      }

      // Recency / Days Since Last Purchase
      if (feat.includes("days_since") || (feat.includes("purchase") && feat.includes("last")) || feat.includes("recency")) {
        const digits = val.replace(/\D/g, "");
        const num = digits ? parseInt(digits, 10) : null;
        if (num !== null) {
          if (num <= 7) return { full: "a very recent purchase", short: "recent purchase history" };
          return { full: `their last purchase being ${num} days ago`, short: "purchase history" };
        }
        return { full: `purchase recency (${val})`, short: "purchase history" };
      }

      // Cart Abandonment
      if (feat.includes("abandon") || lbl.includes("abandon")) {
        const digits = val.replace(/\D/g, "");
        const num = digits ? parseInt(digits, 10) : null;
        if (num !== null && num > 0) {
          if (num === 1) return { full: "one abandoned shopping cart", short: "an abandoned cart" };
          return { full: `leaving items behind in ${num} shopping carts`, short: `${num} cart abandonments` };
        }
        return { full: "cart abandonment patterns", short: "cart abandonment" };
      }

      // Late Deliveries
      if (feat.includes("late") || feat.includes("delivery")) {
        const digits = val.replace(/\D/g, "");
        const num = digits ? parseInt(digits, 10) : null;
        if (num !== null && num > 0) {
          return { full: `experiencing ${num} delayed delivery package${num > 1 ? "s" : ""}`, short: "delivery delays" };
        }
        return { full: "shipping delivery times", short: "delivery timing" };
      }

      // Returns
      if (feat.includes("return")) {
        const digits = val.replace(/\D/g, "");
        const num = digits ? parseInt(digits, 10) : null;
        if (num !== null && num > 0) {
          return { full: `returning ${num} item${num > 1 ? "s" : ""}`, short: "product returns" };
        }
        return { full: "product return frequency", short: "product returns" };
      }

      // Cancellations
      if (feat.includes("cancel")) {
        const digits = val.replace(/\D/g, "");
        const num = digits ? parseInt(digits, 10) : null;
        if (num !== null && num > 0) {
          return { full: `canceling ${num} order${num > 1 ? "s" : ""}`, short: "order cancellations" };
        }
        return { full: "order cancellations", short: "order cancellations" };
      }

      // Orders Lifetime
      if (feat.includes("lifetime") || (feat.includes("total_orders") && !feat.includes("30d"))) {
        const digits = val.replace(/\D/g, "");
        const num = digits ? parseInt(digits, 10) : null;
        if (num !== null) {
          if (num === 0) return { full: "having zero completed orders to date", short: "an unactivated order history" };
          return { full: `a lifetime total of ${num} orders`, short: "lifetime order history" };
        }
        return { full: "lifetime order volume", short: "lifetime order history" };
      }

      // Orders last 30d
      if (feat.includes("orders_last_30d")) {
        const digits = val.replace(/\D/g, "");
        const num = digits ? parseInt(digits, 10) : null;
        if (num !== null) {
          if (num === 0) return { full: "placing no orders in the last month", short: "a lack of recent orders" };
          return { full: `placing ${num} order${num > 1 ? "s" : ""} in the last 30 days`, short: "recent order frequency" };
        }
        return { full: "recent order frequency", short: "recent orders" };
      }

      // Membership
      if (feat.includes("membership") || feat.includes("prime") || feat.includes("tier")) {
        return { full: `their ${val} membership status`, short: "membership status" };
      }

      // Average Order Value / Spend
      if (feat.includes("spend") || feat.includes("aov") || feat.includes("order_value")) {
        return { full: `their average spend level (${val})`, short: "average spend" };
      }

      const cleanTitle = (item.label || feat.replace(/_/g, " ")).trim();
      return { full: `${cleanTitle.toLowerCase()} (${val})`, short: cleanTitle.toLowerCase() };
    };

    const riskFactors = [];
    const protectiveFactors = [];

    topItems.forEach((item) => {
      const impactStr = (item.impact || "").toLowerCase();
      const direction = (item.direction || "").toLowerCase();
      const desc = describeFeature(item);

      if (impactStr.includes("increase") || direction === "positive") {
        riskFactors.push(desc);
      } else if (impactStr.includes("protect") || direction === "negative") {
        protectiveFactors.push(desc);
      } else {
        const sVal = parseFloat(item.shap_value) || 0.0;
        if (sVal > 0) {
          riskFactors.push(desc);
        } else {
          protectiveFactors.push(desc);
        }
      }
    });

    const sentences = [s1];

    if (riskFactors.length > 0 && protectiveFactors.length > 0) {
      if (riskFactors.length === 1 && protectiveFactors.length >= 1) {
        const rf = riskFactors[0];
        const pfList = protectiveFactors.map((p) => p.short).join(" and ");
        const rfCap = rf.full.charAt(0).toUpperCase() + rf.full.slice(1);

        if (isLow) {
          sentences.push(`${rfCap} is the main factor highlighted as increasing concern, while ${pfList} help explain the prediction.`);
          sentences.push("The customer has not shown enough evidence to suggest a high likelihood of leaving.");
        } else if (isHigh) {
          sentences.push(`${rfCap} is a primary factor increasing their likelihood of leaving, though ${pfList} offer some account stability.`);
          sentences.push("However, the risk signals remain dominant and require attention.");
        } else {
          sentences.push(`${rfCap} is contributing to increased attrition risk, while ${pfList} help offset some of this concern.`);
          sentences.push("Proactive retention outreach can help keep this account engaged.");
        }
      } else if (riskFactors.length >= 2 && protectiveFactors.length >= 1) {
        const rfCombined = `${riskFactors[0].full} and ${riskFactors[1].short}`;
        const rfCap = rfCombined.charAt(0).toUpperCase() + rfCombined.slice(1);
        const pfShort = protectiveFactors[0].short;

        sentences.push(`${rfCap} are the primary factors driving their elevated risk of leaving.`);
        sentences.push(`Although ${pfShort} provides some positive balance, these friction points currently outweigh the account's strengths.`);
      } else {
        const rfStr = riskFactors.map((r) => r.short).join(" and ");
        const pfStr = protectiveFactors.map((p) => p.short).join(" and ");
        sentences.push(`Issues such as ${rfStr} are increasing the risk of departure, while ${pfStr} help reduce it.`);
      }
    } else if (riskFactors.length > 0 && protectiveFactors.length === 0) {
      if (riskFactors.length === 1) {
        const rf = riskFactors[0].full;
        sentences.push(`${rf.charAt(0).toUpperCase() + rf.slice(1)} is the main driver increasing this customer's risk of leaving.`);
        sentences.push("Addressing this friction point should be the primary focus to preserve the relationship.");
      } else if (riskFactors.length === 2) {
        const rf1 = riskFactors[0].full;
        const rf2 = riskFactors[1].short;
        sentences.push(`${rf1.charAt(0).toUpperCase() + rf1.slice(1)} and ${rf2} are the main factors increasing their likelihood of leaving.`);
        sentences.push("These friction points indicate growing dissatisfaction and require proactive attention.");
      } else {
        const rf1 = riskFactors[0].full;
        const rf2 = riskFactors[1].short;
        const rf3 = riskFactors[2].short;
        sentences.push(`${rf1.charAt(0).toUpperCase() + rf1.slice(1)}, ${rf2}, and ${rf3} are the main factors increasing their likelihood of leaving.`);
        sentences.push("Multiple customer service or order friction points are contributing to this elevated risk.");
      }
    } else if (protectiveFactors.length > 0 && riskFactors.length === 0) {
      if (protectiveFactors.length === 1) {
        const pf = protectiveFactors[0].full;
        sentences.push(`${pf.charAt(0).toUpperCase() + pf.slice(1)} is strongly helping to reduce the risk of departure.`);
        sentences.push("The customer continues to demonstrate healthy engagement with the platform.");
      } else {
        const pf1 = protectiveFactors[0].full;
        const pf2 = protectiveFactors[1].short;
        sentences.push(`${pf1.charAt(0).toUpperCase() + pf1.slice(1)} and ${pf2} are the primary factors reducing their likelihood of leaving.`);
        sentences.push("The customer has not shown evidence to suggest an immediate likelihood of departure.");
      }
    } else {
      sentences.push("Key behavioral factors remain balanced between risk drivers and protective habits.");
    }

    return sentences.join(" ");
  };

  const handleRetentionDecision = async (camp, decision) => {
    if (!selectedCustomer?.customer?.id) return;
    const campId = camp.id || camp.title;
    if (processingMap[campId]) return;

    setProcessingMap((prev) => ({ ...prev, [campId]: decision }));

    try {
      const res = await toggleCustomerRetentionAction(selectedCustomer.customer.id, {
        campaign_id: camp.id || `camp_${campId}`,
        status: decision,
        title: camp.title,
        perk_type: camp.perk_type || 'discount_voucher',
        perk_value: camp.perk_value || 0.0,
        coupon_code: camp.coupon_code || null,
        free_shipping: Boolean(camp.free_shipping),
        action_summary: camp.action_summary || '',
        root_cause_driver: camp.root_cause_driver || '',
        channel: camp.channel || ''
      });

      if (res && res.success) {
        setActionStatusMap((prev) => ({ ...prev, [campId]: decision }));

        const toastText = decision === 'Accepted'
          ? `Plan "${camp.title}" accepted. Customer benefits unlocked.`
          : `Plan "${camp.title}" rejected.`;

        setRetentionToast({
          type: decision === 'Accepted' ? 'success' : 'info',
          text: toastText
        });
        setTimeout(() => setRetentionToast(null), 4000);

        // Refresh customer details to synchronize wallet balance and active perks
        try {
          const updated = await getCustomerDetails(selectedCustomer.customer.id, { params: { force_refresh: true } });
          if (updated && updated.customer) {
            customerCacheRef.current[selectedCustomer.customer.id] = updated;
            setSelectedCustomer(updated);
          }
        } catch (e) {
          console.warn('Could not refresh customer details after decision:', e);
        }
      } else {
        throw new Error(res?.message || 'Failed to update retention plan.');
      }
    } catch (err) {
      console.error('Failed to submit retention decision:', err);
      setRetentionToast({
        type: 'error',
        text: err?.response?.data?.detail || err?.message || 'Network error updating retention plan.'
      });
      setTimeout(() => setRetentionToast(null), 4000);
    } finally {
      setProcessingMap((prev) => ({ ...prev, [campId]: false }));
    }
  };

  const handleCopyId = (id) => {
    if (!id) return;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(id).catch(() => fallbackCopy(id));
    } else {
      fallbackCopy(id);
    }
    setCopiedId(id);
    setTimeout(() => {
      setCopiedId(null);
    }, 2000);
  };

  const fallbackCopy = (text) => {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      document.execCommand('copy');
    } catch (err) {
      console.error('Fallback copy failed', err);
    }
    document.body.removeChild(textArea);
  };

  useEffect(() => {
    fetchCustomerData();
  }, [page, riskCategory, groundTruthFilter, customerSource]);

  // Lock body scroll and reset scroll position when opening modal
  useEffect(() => {
    if (selectedCustomer) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [selectedCustomer]);

  const fetchCustomerData = async () => {
    setLoading(true);
    try {
      const params = {
        search,
        risk_category: riskCategory,
        page,
        limit: 15,
      };
      if (customerSource !== 'all') {
        params.source = customerSource;
      }
      if (groundTruthFilter !== 'all') {
        params.ground_truth_churn = parseInt(groundTruthFilter);
      }

      const data = await getCustomers(params);
      setCustomers(data.customers || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error('Error fetching customers:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchCustomerData();
  };

  const handleBatchPdfDownload = async () => {
    setDownloadingBatch(true);
    try {
      await downloadBatchPredictionPDF(customerSource);
    } catch (err) {
      console.error('Failed to download batch prediction PDF:', err);
    } finally {
      setDownloadingBatch(false);
    }
  };

  const handleBatchPdfPreview = async () => {
    setPreviewingBatch(true);
    try {
      await previewBatchPredictionPDF(customerSource);
    } catch (err) {
      console.error('Failed to preview batch prediction PDF:', err);
    } finally {
      setPreviewingBatch(false);
    }
  };

  const handleRunBatchPrediction = async () => {
    setRunningBatch(true);
    try {
      await runBatchPrediction();
      await fetchCustomerData();
    } catch (err) {
      console.error('Failed to run batch prediction:', err);
    } finally {
      setRunningBatch(false);
    }
  };

  const handleCustomerPdfDownload = async () => {
    if (!selectedCustomer?.customer?.id) return;
    setDownloadingCust(true);
    try {
      await downloadCustomerPDF(selectedCustomer.customer.id, selectedCustomer.customer.source_customer_id);
    } catch (err) {
      console.error('Failed to download customer PDF report:', err);
    } finally {
      setDownloadingCust(false);
    }
  };

  const handleCustomerPdfPreview = async () => {
    if (!selectedCustomer?.customer?.id) return;
    setPreviewingCust(true);
    try {
      await previewCustomerPDF(selectedCustomer.customer.id);
    } catch (err) {
      console.error('Failed to preview customer PDF report:', err);
    } finally {
      setPreviewingCust(false);
    }
  };

  const closeModal = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setSelectedCustomer(null);
    setIsDetailsLoading(false);
  };

  const openCustomerModal = async (id, initialCustomer = null) => {
    const t0 = performance.now();
    // 1. Cancel previous pending customer request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    // 2. Locate baseline customer data from row or table state
    const baseCust = initialCustomer || customers.find((c) => c.id === id);

    // 3. Fast Path: Check client-side memory cache
    if (customerCacheRef.current[id]) {
      const cached = customerCacheRef.current[id];
      setSelectedCustomer(cached);
      setIsDetailsLoading(false);
      setLoadingModalId(null);
      if (cached.prediction?.retention_plan && Array.isArray(cached.prediction.retention_plan)) {
        const map = {};
        cached.prediction.retention_plan.forEach((camp) => {
          if (camp.id) map[camp.id] = camp.status || 'Pending Review';
        });
        setActionStatusMap(map);
      }
      console.log(`[Perf UI] Customer ${id} served instantly from Client Cache in ${(performance.now() - t0).toFixed(1)}ms`);
      return;
    }

    // 4. Instant UI Modal Presentation: Show available customer profile immediately (0 ms)
    if (baseCust) {
      setSelectedCustomer({
        customer: baseCust,
        prediction: baseCust.prediction || null,
        orders: [],
        retention_perks: [],
        account_notifications: [],
        isPartial: true
      });
      setIsDetailsLoading(true);
      if (baseCust.prediction?.retention_plan) {
        const map = {};
        baseCust.prediction.retention_plan.forEach((camp) => {
          if (camp.id) map[camp.id] = camp.status || 'Pending Review';
        });
        setActionStatusMap(map);
      }
      console.log(`[Perf UI] Instant modal presented for Customer ${id} in ${(performance.now() - t0).toFixed(1)}ms`);
    } else {
      setLoadingModalId(id);
    }

    // 5. Fetch complete customer profile, live perks, and SHAP diagnostics in background
    try {
      const detail = await getCustomerDetails(id, { signal: abortController.signal });
      if (detail && detail.customer) {
        customerCacheRef.current[id] = detail;
        setSelectedCustomer(detail);
        setIsDetailsLoading(false);

        if (detail.prediction?.retention_plan && Array.isArray(detail.prediction.retention_plan)) {
          const map = {};
          detail.prediction.retention_plan.forEach((camp) => {
            if (camp.id) {
              map[camp.id] = camp.status || 'Pending Review';
            }
          });
          setActionStatusMap(map);
        }
        console.log(`[Perf UI] Customer ${id} full profile loaded in ${(performance.now() - t0).toFixed(1)}ms (Backend: ${detail._perf_ms || 'N/A'}ms)`);
      }
    } catch (err) {
      if (err.name === 'CanceledError' || err.code === 'ERR_CANCELED' || err.message === 'canceled') {
        // Request superseded by another customer selection
        return;
      }
      console.error('Error fetching customer details:', err);
      setIsDetailsLoading(false);
    } finally {
      setLoadingModalId(null);
    }
  };

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap', width: '100%', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <button
            type="button"
            onClick={handleRunBatchPrediction}
            disabled={runningBatch}
            className="btn-amazon-dark"
            style={{
              padding: '0.85rem 1.4rem',
              fontSize: '1.05rem',
              whiteSpace: 'nowrap',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              cursor: runningBatch ? 'wait' : 'pointer'
            }}
          >
            {runningBatch ? '⏳ Scoring...' : '⚡ Re-run Churn Model'}
          </button>

          <button
            type="button"
            onClick={handleBatchPdfPreview}
            disabled={previewingBatch}
            className="btn-amazon-gold"
            style={{
              padding: '0.85rem 1.4rem',
              fontSize: '1.05rem',
              whiteSpace: 'nowrap',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              cursor: previewingBatch ? 'wait' : 'pointer'
            }}
            title={`Preview PDF Report for ${customerSource === 'uploaded' ? 'Uploaded Dataset' : customerSource === 'store' ? 'Live Store' : 'All Customers'}`}
          >
            {previewingBatch
              ? '⏳ Opening PDF...'
              : customerSource === 'uploaded'
              ? '👁️ View PDF (Uploaded Dataset)'
              : customerSource === 'store'
              ? '👁️ View PDF (Live Store)'
              : '👁️ View PDF (All Profiles)'}
          </button>

          <button
            type="button"
            onClick={handleBatchPdfDownload}
            disabled={downloadingBatch}
            className="btn-amazon-dark"
            style={{
              padding: '0.85rem 1.2rem',
              fontSize: '1.05rem',
              whiteSpace: 'nowrap',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              cursor: downloadingBatch ? 'wait' : 'pointer',
              backgroundColor: '#374151',
              color: '#ffffff'
            }}
            title={`Download PDF Report for ${customerSource === 'uploaded' ? 'Uploaded Dataset' : customerSource === 'store' ? 'Live Store' : 'All Customers'}`}
          >
            <Download size={16} />
            <span>{downloadingBatch ? '⏳ Downloading...' : 'Download PDF'}</span>
          </button>
        </div>

        {/* Amazon-style Search Bar */}
          <form onSubmit={handleSearchSubmit} style={{ display: 'flex', border: '1px solid #d5d9d9', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 1px 3px rgba(15,17,17,0.08)' }}>
            <input
              type="text"
              placeholder="Search Account ID, Prime Status, Category..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                padding: '0.85rem 1.2rem',
                border: 'none',
                width: '320px',
                fontSize: '1.1rem',
                outline: 'none',
                fontFamily: 'inherit'
              }}
            />
            <button type="submit" className="btn-amazon-gold" style={{ borderRadius: 0, padding: '0.85rem 1.4rem', fontSize: '1.1rem' }}>
              🔍 Search
            </button>
          </form>
        </div>
      </div>

      {/* Customer Prediction Data Source Selector */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#ffffff',
        border: '1px solid #d5d9d9',
        borderRadius: '10px',
        padding: '12px 18px',
        marginBottom: '1.25rem',
        boxShadow: '0 1px 4px rgba(0,0,0,0.05)',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.78rem', fontWeight: 800, color: '#64748b', letterSpacing: '0.05em' }}>
            PREDICTION DATA SOURCE:
          </span>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button
              type="button"
              onClick={() => { setCustomerSource('store'); setPage(1); }}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 14px',
                borderRadius: '6px',
                border: customerSource === 'store' ? '2px solid #ff9900' : '1px solid #cbd5e1',
                background: customerSource === 'store' ? '#fef8e7' : '#f8fafc',
                color: '#0f1111',
                fontWeight: customerSource === 'store' ? 800 : 600,
                fontSize: '0.88rem',
                cursor: 'pointer'
              }}
            >
              <ShoppingBag size={15} color="#e67e22" />
              <span>🛒 SmartCart Live Store Customers (150 Accounts)</span>
              <span style={{
                background: '#dcfce7',
                color: '#166534',
                fontSize: '10px',
                fontWeight: 800,
                padding: '2px 6px',
                borderRadius: '999px',
                textTransform: 'uppercase'
              }}>Live Store</span>
            </button>

            <button
              type="button"
              onClick={() => { setCustomerSource('uploaded'); setPage(1); }}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 14px',
                borderRadius: '6px',
                border: customerSource === 'uploaded' ? '2px solid #ff9900' : '1px solid #cbd5e1',
                background: customerSource === 'uploaded' ? '#fef8e7' : '#f8fafc',
                color: '#0f1111',
                fontWeight: customerSource === 'uploaded' ? 800 : 600,
                fontSize: '0.88rem',
                cursor: 'pointer'
              }}
            >
              <Upload size={15} color="#007185" />
              <span>📁 Uploaded Dataset Customers</span>
              <span style={{
                background: '#fef3c7',
                color: '#92400e',
                fontSize: '10px',
                fontWeight: 800,
                padding: '2px 6px',
                borderRadius: '999px',
                textTransform: 'uppercase'
              }}>CSV Dataset</span>
            </button>

            <button
              type="button"
              onClick={() => { setCustomerSource('all'); setPage(1); }}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 14px',
                borderRadius: '6px',
                border: customerSource === 'all' ? '2px solid #ff9900' : '1px solid #cbd5e1',
                background: customerSource === 'all' ? '#fef8e7' : '#f8fafc',
                color: '#0f1111',
                fontWeight: customerSource === 'all' ? 800 : 600,
                fontSize: '0.88rem',
                cursor: 'pointer'
              }}
            >
              <span>🌐 All Profiles</span>
            </button>
          </div>
        </div>

        <Link
          to="/upload"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '8px 14px',
            borderRadius: '6px',
            background: '#232f3e',
            color: '#ffffff',
            fontSize: '0.84rem',
            fontWeight: 700,
            textDecoration: 'none'
          }}
        >
          <Upload size={14} />
          <span>Upload Dataset (CSV)</span>
        </Link>
      </div>

      {/* Filter Toolbar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.75rem', backgroundColor: '#ffffff', padding: '1.1rem 1.5rem', borderRadius: '8px', border: '1px solid #d5d9d9' }}>
        <div style={{ display: 'flex', gap: '0.65rem', alignItems: 'center' }}>
          <span style={{ fontSize: '1.05rem', fontWeight: 800, color: '#565959' }}>Model Risk Level:</span>
          {['all', 'High Risk', 'Medium Risk', 'Low Risk'].map((r) => (
            <button
              key={r}
              onClick={() => { setRiskCategory(r); setPage(1); }}
              style={{
                padding: '0.5rem 1.0rem',
                borderRadius: '6px',
                border: '1px solid',
                borderColor: riskCategory === r ? '#ff9900' : '#d5d9d9',
                fontWeight: 800,
                fontSize: '1.05rem',
                cursor: 'pointer',
                backgroundColor: riskCategory === r ? '#ff9900' : '#ffffff',
                color: riskCategory === r ? '#131921' : '#565959',
                transition: 'all 0.15s ease'
              }}
            >
              {r === 'all' ? 'All Risk Levels' : r}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div style={{ padding: '3rem', textAlign: 'center', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #d5d9d9' }}>
          <p style={{ color: '#565959' }}>Loading Amazon Customer Accounts...</p>
        </div>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Account ID</th>
              <th>Membership</th>
              <th>Category</th>
              <th>Total Orders</th>
              <th>Lifetime Spend</th>
              <th>Days Inactive</th>
              <th>Model Churn Prob</th>
              <th>Predicted Risk</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {customers.map((c) => {
              const risk = c.prediction?.risk_category || 'Unanalyzed';
              const badgeClass =
                risk === 'High Risk'
                  ? 'badge-high'
                  : risk === 'Medium Risk'
                  ? 'badge-medium'
                  : 'badge-low';

              const isPrime = c.membership_status?.toLowerCase().includes('prime');

              return (
                <tr key={c.id}>
                  <td>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '3px' }}>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleCopyId(c.source_customer_id);
                        }}
                        className={`btn-copy-mini ${copiedId === c.source_customer_id ? 'copied' : ''}`}
                        title={`Copy Customer ID: ${c.source_customer_id}`}
                      >
                        {copiedId === c.source_customer_id ? <Check size={11} /> : <Copy size={11} />}
                        <span>{copiedId === c.source_customer_id ? 'Copied!' : 'Copy ID'}</span>
                      </button>
                      <strong
                        style={{ color: '#007185', cursor: 'pointer', fontSize: '0.92rem' }}
                        onClick={() => openCustomerModal(c.id, c)}
                        title="Click to view full customer profile"
                      >
                        {c.source_customer_id}
                      </strong>
                    </div>
                  </td>
                  <td>
                    {c.membership_status || 'Standard'}
                  </td>
                  <td>{c.preferred_category || 'General'}</td>
                  <td>{c.total_orders_lifetime || 0}</td>
                  <td><strong style={{ color: '#0f1111' }}>{c.total_spend_inr || '₹0.00'}</strong></td>
                  <td>
                    {c.days_since_last_purchase === 0 ? (
                      <strong style={{ color: '#007600' }}>0 days</strong>
                    ) : (c.total_orders_lifetime === 0 || c.days_since_last_purchase === null) ? (
                      <span style={{ color: '#888', fontStyle: 'italic' }}>Never purchased</span>
                    ) : (
                      `${Math.round(c.days_since_last_purchase)} days`
                    )}
                  </td>
                  <td>
                    <strong style={{ color: c.prediction?.churn_probability > 50 ? '#cc0c39' : '#0f1111' }}>
                      {c.prediction?.churn_probability !== null ? `${c.prediction.churn_probability}%` : 'N/A'}
                    </strong>
                  </td>
                  <td>
                    <span className={badgeClass}>{risk}</span>
                  </td>
                  <td>
                    <button
                      onClick={() => openCustomerModal(c.id, c)}
                      className="btn-amazon-gold"
                      style={{ padding: '0.3rem 0.65rem', fontSize: '0.78rem', minWidth: '105px' }}
                    >
                      Inspect Profile
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}

      {/* Pagination */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.25rem', backgroundColor: '#ffffff', padding: '0.85rem 1.25rem', borderRadius: '8px', border: '1px solid #d5d9d9' }}>
        <span style={{ fontSize: '0.85rem', color: '#565959' }}>
          Showing Page <strong>{page}</strong> of {Math.ceil(total / 15)} (Total <strong>{total?.toLocaleString()}</strong> accounts)
        </span>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button disabled={page <= 1} onClick={() => setPage(page - 1)} className="btn-amazon-dark" style={{ padding: '0.35rem 0.85rem', fontSize: '0.8rem' }}>
            ◀ Previous
          </button>
          <button disabled={page * 15 >= total} onClick={() => setPage(page + 1)} className="btn-amazon-dark" style={{ padding: '0.35rem 0.85rem', fontSize: '0.8rem' }}>
            Next ▶
          </button>
        </div>
      </div>

      {/* Full Screen Customer Detail Executive Popup Window (Rendered at Document Body via React Portal) */}
      {selectedCustomer && createPortal(
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(19, 25, 33, 0.88)',
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'center',
            zIndex: 99999,
            backdropFilter: 'blur(5px)',
            padding: '1.5rem 1rem',
            overflowY: 'auto'
          }}
        >
          <div
            style={{
              backgroundColor: '#ffffff',
              borderRadius: '12px',
              width: '98vw',
              maxWidth: '1600px',
              display: 'flex',
              flexDirection: 'column',
              border: '3px solid #ff9900',
              boxShadow: '0 20px 50px rgba(0,0,0,0.5)',
              margin: '0 auto 3rem auto'
            }}
          >
            {/* Modal Header Bar */}
            <div
              style={{
                backgroundColor: '#131921',
                color: '#ffffff',
                padding: '1.25rem 2rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderBottom: '4px solid #ff9900',
                position: 'sticky',
                top: 0,
                zIndex: 10
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <span className="amazon-logo-dark" style={{ fontSize: '1.8rem' }}>amazon</span>
                  <span className="amazon-smile-dark" style={{ width: '18px', height: '9px' }}></span>
                </div>
                <div style={{ width: '2px', height: '32px', backgroundColor: 'rgba(255,255,255,0.25)' }}></div>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <button
                      type="button"
                      onClick={() => handleCopyId(selectedCustomer.customer.source_customer_id)}
                      className={`btn-copy-mini dark ${copiedId === selectedCustomer.customer.source_customer_id ? 'copied' : ''}`}
                      title="Copy Customer ID"
                    >
                      {copiedId === selectedCustomer.customer.source_customer_id ? <Check size={11} /> : <Copy size={11} />}
                      <span>{copiedId === selectedCustomer.customer.source_customer_id ? 'Copied to Clipboard!' : 'Copy Customer ID'}</span>
                    </button>
                  </div>
                  <h2 style={{ fontSize: '1.55rem', color: '#ffffff', fontWeight: 900 }}>
                    Account Profile: <span style={{ color: '#febd69' }}>{selectedCustomer.customer.source_customer_id}</span>
                  </h2>
                  <p style={{ fontSize: '1.05rem', color: '#d1d5db', marginTop: '0.1rem' }}>
                    Amazon Seller Central Customer Intelligence & Risk Diagnostics
                  </p>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                <button
                  type="button"
                  onClick={handleCustomerPdfPreview}
                  disabled={previewingCust}
                  className="btn-amazon-gold"
                  style={{
                    padding: '0.6rem 1.4rem',
                    fontSize: '1.1rem',
                    fontWeight: 800,
                    borderRadius: '8px',
                    cursor: previewingCust ? 'wait' : 'pointer'
                  }}
                >
                  {previewingCust ? '⏳ Opening PDF...' : '👁️ View PDF (Preview)'}
                </button>
                <button
                  onClick={closeModal}
                  className="btn-amazon-orange"
                  style={{ padding: '0.6rem 1.4rem', fontSize: '1.1rem', fontWeight: 800, borderRadius: '8px' }}
                >
                  ✖ Close Profile Window
                </button>
              </div>
            </div>

            {/* Modal Scrollable Content Grid */}
            <div style={{ padding: '2rem 2rem 4rem 2rem', backgroundColor: '#eaeded' }}>
              {/* Top Summary Banner */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem', marginBottom: '1.75rem' }}>
                <div className="stat-card" style={{ borderTop: '4px solid #ff9900' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                    <h3>Customer Account ID</h3>
                    <button
                      type="button"
                      onClick={() => handleCopyId(selectedCustomer.customer.source_customer_id)}
                      className={`btn-copy-mini ${copiedId === selectedCustomer.customer.source_customer_id ? 'copied' : ''}`}
                      title="Copy Customer ID"
                    >
                      {copiedId === selectedCustomer.customer.source_customer_id ? <Check size={11} /> : <Copy size={11} />}
                      <span>{copiedId === selectedCustomer.customer.source_customer_id ? 'Copied' : 'Copy'}</span>
                    </button>
                  </div>
                  <div className="value" style={{ fontSize: '2.0rem', color: '#007185' }}>
                    {selectedCustomer.customer.source_customer_id}
                  </div>
                  <span style={{ fontSize: '1.05rem', color: '#565959', fontWeight: 600 }}>
                    Signup Date: {selectedCustomer.customer.signup_date || 'N/A'}
                  </span>
                </div>

                <div className="stat-card" style={{ borderTop: '4px solid #131921' }}>
                  <h3>Membership Status</h3>
                  <div className="value" style={{ fontSize: '2.0rem', color: '#0f1111' }}>
                    {selectedCustomer.customer.membership_status || 'Standard'}
                  </div>
                  <span style={{ fontSize: '1.05rem', color: '#565959', fontWeight: 600 }}>
                    City Tier: {selectedCustomer.customer.city_tier || 'Tier 1'}
                  </span>
                </div>

                <div className="stat-card" style={{ borderTop: '4px solid #cc0c39' }}>
                  <h3>Model Churn Probability</h3>
                  <div className="value" style={{ color: selectedCustomer.prediction?.churn_probability >= 50 ? '#cc0c39' : '#007600' }}>
                    {selectedCustomer.prediction?.churn_probability !== null ? `${selectedCustomer.prediction.churn_probability}%` : 'N/A'}
                  </div>
                  <span style={{ fontSize: '1.05rem', color: '#565959', fontWeight: 600 }}>
                    Threshold Applied: {selectedCustomer.prediction?.decision_threshold || 0.5}
                  </span>
                </div>

                <div className="stat-card" style={{ borderTop: '4px solid #007600' }}>
                  <h3>Model Risk Classification</h3>
                  <div style={{ marginTop: '0.4rem' }}>
                    <span className={
                      selectedCustomer.prediction?.risk_category === 'High Risk'
                        ? 'badge-high'
                        : selectedCustomer.prediction?.risk_category === 'Medium Risk'
                        ? 'badge-medium'
                        : 'badge-low'
                    } style={{ fontSize: '1.4rem', padding: '0.6rem 1.2rem' }}>
                      {selectedCustomer.prediction?.risk_category || 'Unanalyzed'}
                    </span>
                  </div>
                  <span style={{ fontSize: '1.05rem', color: '#565959', fontWeight: 600, marginTop: '0.6rem', display: 'inline-block' }}>
                    Model: {selectedCustomer.prediction?.model_version || 'Random Forest v1.0'}
                  </span>
                </div>
              </div>



              {/* Explainable AI: Root Cause Analysis (Customer-Specific SHAP Decision Attribution) */}
              <div
                className="xai-section-card"
                style={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #d5d9d9',
                  borderLeft: '6px solid #0284c7',
                  borderRadius: '8px',
                  padding: '1.5rem 1.75rem',
                  marginBottom: '1.75rem',
                  boxShadow: '0 2px 6px rgba(0,0,0,0.05)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem', flexWrap: 'wrap', gap: '0.75rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                    <span style={{ fontSize: '1.4rem' }}>📊</span>
                    <h3 style={{ fontSize: '1.35rem', fontWeight: 900, color: '#0f1111', margin: 0 }}>
                      Root Cause Analysis
                    </h3>
                  </div>
                  <span style={{ fontSize: '0.85rem', color: '#0369a1', backgroundColor: '#e0f2fe', padding: '0.3rem 0.75rem', borderRadius: '4px', fontWeight: 700 }}>
                    Account Diagnostics for {selectedCustomer.customer.source_customer_id}
                  </span>
                </div>
                <p style={{ fontSize: '1.05rem', color: '#565959', marginBottom: '1.35rem', marginTop: '0.2rem' }}>
                  Attribute weights showing how specific behavioral features mathematically influenced this customer's Random Forest prediction ({selectedCustomer.prediction?.churn_probability}%).
                </p>

                {/* Customer-Specific Model Decision Attribution (SHAP) */}
                {selectedCustomer.prediction?.shap_explanation && selectedCustomer.prediction.shap_explanation.length > 0 ? (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.15rem' }}>
                    {selectedCustomer.prediction.shap_explanation.map((item, idx) => {
                      const isRisk = item.impact?.toLowerCase().includes('increase') || item.direction === 'positive';
                      const isProtect = item.impact?.toLowerCase().includes('protect') || item.direction === 'negative';
                      const pct = item.contribution_val || parseFloat(item.importance_pct) || 10;
                      
                      return (
                        <div
                          key={idx}
                          style={{
                            backgroundColor: '#fafafa',
                            border: '1px solid #e5e7eb',
                            borderRadius: '6px',
                            padding: '0.85rem 1.1rem',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '0.45rem'
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.95rem' }}>
                            <span style={{ fontWeight: 700, color: '#1f2937' }}>{item.label || item.feature}</span>
                            <span
                              style={{
                                fontSize: '0.75rem',
                                fontWeight: 800,
                                padding: '0.15rem 0.55rem',
                                borderRadius: '4px',
                                backgroundColor: isProtect ? '#dcfce7' : isRisk ? '#fee2e2' : '#f3f4f6',
                                color: isProtect ? '#15803d' : isRisk ? '#b91c1c' : '#4b5563'
                              }}
                            >
                              {item.impact}
                            </span>
                          </div>

                          <div style={{ width: '100%', height: '8px', backgroundColor: '#e5e7eb', borderRadius: '999px', overflow: 'hidden' }}>
                            <div
                              style={{
                                width: `${Math.min(100, Math.max(12, pct * 1.5))}%`,
                                height: '100%',
                                borderRadius: '999px',
                                background: isProtect ? 'linear-gradient(90deg, #10b981, #059669)' : 'linear-gradient(90deg, #f59e0b, #ef4444)'
                              }}
                            ></div>
                          </div>

                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', color: '#6b7280', flexWrap: 'wrap', gap: '4px' }}>
                            <span>Feature Impact Weight: <strong style={{ color: '#0f1111' }}>{item.importance_pct || `${pct}%`}</strong></span>
                            <span>Recorded Value: <strong style={{ color: '#0f1111' }}>{item.value}</strong></span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : isDetailsLoading ? (
                  <div className="xai-skeleton-container">
                    <div className="xai-skeleton-header">
                      <span className="spinner-mini"></span>
                      <span>Calculating customer-specific SHAP attribution weights...</span>
                    </div>
                    <div className="xai-skeleton-grid">
                      {[1, 2, 3, 4, 5, 6].map((k) => (
                        <div key={k} className="xai-skeleton-card">
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div className="xai-skeleton-line short"></div>
                            <div className="xai-skeleton-line very-short" style={{ height: '18px', width: '70px', borderRadius: '4px' }}></div>
                          </div>
                          <div className="xai-skeleton-bar"></div>
                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <div className="xai-skeleton-line very-short"></div>
                            <div className="xai-skeleton-line very-short"></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div style={{ padding: '1rem', backgroundColor: '#f8fafc', borderRadius: '6px', border: '1px solid #e2e8f0', color: '#64748b', fontSize: '0.9rem' }}>
                    Feature attribution weights are calculating dynamically for this account...
                  </div>
                )}

                {/* Simple Explanation Section */}
                <div className="simple-explanation-card">
                  <h4 className="simple-explanation-title">
                    Simple Explanation
                  </h4>
                  <p className="simple-explanation-text">
                    {selectedCustomer.prediction?.simple_explanation || generateSimpleExplanation(
                      selectedCustomer.prediction?.churn_probability,
                      selectedCustomer.prediction?.risk_category,
                      selectedCustomer.prediction?.shap_explanation
                    )}
                  </p>
                </div>
              </div>

              {/* Automated Retention Action Plan */}
              {selectedCustomer.prediction && (
                <div className="retention-plan-section">
                  <div className="retention-plan-header">
                    <h3>Automated Retention Action Plan</h3>
                    <p>Review and approve recommended customer retention actions.</p>
                  </div>

                  {/* Feedback Toast */}
                  {retentionToast && (
                    <div className={`retention-feedback-toast ${retentionToast.type}`}>
                      {retentionToast.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
                      <span>{retentionToast.text}</span>
                    </div>
                  )}

                  {/* Campaign Plan Cards List */}
                  {(() => {
                    const rawPlans = (selectedCustomer.prediction?.retention_plan && selectedCustomer.prediction.retention_plan.length > 0)
                      ? selectedCustomer.prediction.retention_plan
                      : (selectedCustomer.prediction?.recommendations || []).map((rec, i) => ({
                          id: `rec_${i}`,
                          title: typeof rec === 'string' && rec.includes(':') ? rec.split(':')[0].trim() : 'Customer Retention Action',
                          action_summary: rec,
                          status: 'Ready for Review'
                        }));

                    if (isDetailsLoading && (!rawPlans || rawPlans.length === 0)) {
                      return (
                        <div className="retention-plan-skeleton">
                          <span className="spinner-mini"></span>
                          <span>Loading recommended retention campaigns and active perks...</span>
                        </div>
                      );
                    }

                    if (!rawPlans || rawPlans.length === 0) {
                      return (
                        <div style={{ fontStyle: 'italic', color: '#64748b', fontSize: '0.9rem', padding: '0.5rem 0' }}>
                          No pending retention actions required for this customer.
                        </div>
                      );
                    }

                    return (
                      <div className="retention-plan-list">
                        {rawPlans.map((camp, idx) => {
                          const campId = camp.id || `camp_${idx}`;
                          const currentStatus = actionStatusMap[campId] || camp.status || 'Ready for Review';
                          const isAccepted = currentStatus === 'Accepted' || currentStatus === 'Approved';
                          const isRejected = currentStatus === 'Rejected';
                          const isProcessing = processingMap[campId];
                          const planText = getConcisePlanText(camp);

                          return (
                            <div key={campId} className="retention-plan-card">
                              <div className="retention-plan-content">
                                <h4 className="retention-plan-title">{cleanPlanString(camp.title)}</h4>
                                <p className="retention-plan-desc">
                                  <span className="retention-plan-label">Plan:</span>
                                  <span>{planText}</span>
                                </p>
                              </div>

                              <div className="retention-plan-actions">
                                {isAccepted ? (
                                  <span className="retention-status-badge accepted">
                                    ✓ Accepted
                                  </span>
                                ) : isRejected ? (
                                  <span className="retention-status-badge rejected">
                                    ✕ Rejected
                                  </span>
                                ) : (
                                  <div className="retention-btn-group">
                                    <button
                                      type="button"
                                      disabled={Boolean(isProcessing)}
                                      onClick={() => handleRetentionDecision(camp, 'Accepted')}
                                      className="btn-retention-accept"
                                      title="Accept and approve this retention plan"
                                    >
                                      {isProcessing === 'Accepted' ? 'Accepting...' : '✓ Accept'}
                                    </button>
                                    <button
                                      type="button"
                                      disabled={Boolean(isProcessing)}
                                      onClick={() => handleRetentionDecision(camp, 'Rejected')}
                                      className="btn-retention-reject"
                                      title="Reject this retention plan"
                                    >
                                      {isProcessing === 'Rejected' ? 'Rejecting...' : '✕ Reject'}
                                    </button>
                                  </div>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    );
                  })()}
                </div>
              )}
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
};

export default CustomerAnalytics;
