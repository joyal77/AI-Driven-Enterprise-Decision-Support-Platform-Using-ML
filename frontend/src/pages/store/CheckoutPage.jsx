import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  CheckCircle,
  Truck,
  CreditCard,
  Smartphone,
  Banknote,
  Building,
  Sparkles,
  ArrowRight,
  AlertCircle
} from 'lucide-react';
import { placeStoreOrder, validateStoreVoucher } from '../../services/storeApi';
import { useStore } from '../../context/StoreContext';
import './CheckoutPage.css';

const CheckoutPage = () => {
  const {
    cartItems,
    cartSubtotal,
    cartCount,
    clearCart,
    storeUser,
    walletBalance = 0,
    activeVouchers = [],
    hasExpressShipping = false,
    appliedVoucher: contextAppliedVoucher,
    setAppliedVoucher: setContextAppliedVoucher,
    refreshCustomerPerks
  } = useStore();
  const navigate = useNavigate();

  const [address, setAddress] = useState('Flat 402, Green Valley Apartments, Outer Ring Road, Bellandur, Bengaluru 560103');
  const [paymentMode, setPaymentMode] = useState('UPI');
  const [placingOrder, setPlacingOrder] = useState(false);
  const [orderSuccess, setOrderSuccess] = useState(null);
  const [error, setError] = useState(null);

  // Retention perks discount controls
  const [useWallet, setUseWallet] = useState(true);
  const [voucherCodeInput, setVoucherCodeInput] = useState('');
  const [appliedVoucher, setAppliedVoucher] = useState(contextAppliedVoucher || null);
  const [voucherMsg, setVoucherMsg] = useState(null);

  // Sync with context applied voucher or auto-apply highest/first active voucher if available
  React.useEffect(() => {
    if (contextAppliedVoucher) {
      const stillActive = (activeVouchers || []).some(
        (v) => (v.code || '').toUpperCase() === (contextAppliedVoucher.code || '').toUpperCase()
      );
      if (stillActive) {
        setAppliedVoucher(contextAppliedVoucher);
      } else {
        setAppliedVoucher(null);
        if (setContextAppliedVoucher) setContextAppliedVoucher(null);
      }
    } else if (appliedVoucher) {
      const stillActive = (activeVouchers || []).some(
        (v) => (v.code || '').toUpperCase() === (appliedVoucher.code || '').toUpperCase()
      );
      if (!stillActive) {
        setAppliedVoucher(null);
        setVoucherMsg(null);
      }
    } else if (activeVouchers && activeVouchers.length > 0 && !appliedVoucher) {
      setAppliedVoucher(activeVouchers[0]);
    }
  }, [contextAppliedVoucher, activeVouchers]);

  const isPrime = (storeUser?.membership_status && storeUser.membership_status.toLowerCase().includes('prime')) || hasExpressShipping;
  const voucherGrantsFreeShipping = Boolean(
    appliedVoucher?.free_shipping ||
    (appliedVoucher?.code && ['RECOVER', 'SPEED', 'FLEX'].some((prefix) => appliedVoucher.code.toUpperCase().startsWith(prefix)))
  );
  const isFreeDelivery = isPrime || cartSubtotal >= 500 || hasExpressShipping || voucherGrantsFreeShipping;
  const shippingFee = isFreeDelivery ? 0 : 40;

  // 1. Calculate Voucher Discount
  let voucherDiscount = 0.0;
  if (appliedVoucher) {
    if (appliedVoucher.discount_pct && appliedVoucher.discount_pct > 0) {
      voucherDiscount = Math.round(cartSubtotal * (appliedVoucher.discount_pct / 100.0) * 100) / 100;
    } else if (appliedVoucher.discount_amount && appliedVoucher.discount_amount > 0) {
      voucherDiscount = Math.min(cartSubtotal, appliedVoucher.discount_amount);
    }
  }

  // 2. Calculate Wallet Discount
  const subtotalAfterVoucher = Math.max(0, cartSubtotal - voucherDiscount);
  const walletDiscount = useWallet && walletBalance > 0
    ? Math.min(walletBalance, subtotalAfterVoucher)
    : 0.0;

  const totalDiscount = Math.round((voucherDiscount + walletDiscount) * 100) / 100;
  const netSubtotal = Math.max(0, Math.round((cartSubtotal - totalDiscount) * 100) / 100);
  const estimatedTax = Math.round((netSubtotal * 0.05 + Number.EPSILON) * 100) / 100;
  const totalAmount = Math.round((netSubtotal + shippingFee + estimatedTax + Number.EPSILON) * 100) / 100;

  const handleApplyVoucher = async (codeParam) => {
    const code = (codeParam || voucherCodeInput || '').trim().toUpperCase();
    if (!code) return;

    try {
      const custId = storeUser?.customer_id || storeUser?.id || 1;
      const res = await validateStoreVoucher(custId, code, cartSubtotal);
      if (res && res.valid) {
        const found = (activeVouchers || []).find((v) => (v.code || '').toUpperCase() === code);
        const newV = {
          code: res.code,
          discount_pct: res.discount_pct || 0,
          discount_amount: res.discount_amount || 0,
          free_shipping: Boolean(res.free_shipping),
          title: found?.title || `Retention Coupon ${res.code}`
        };
        setAppliedVoucher(newV);
        if (setContextAppliedVoucher) setContextAppliedVoucher(newV);
        const freeShipText = newV.free_shipping ? ' + Free Delivery' : '';
        const discText = newV.discount_pct ? `${newV.discount_pct}% OFF` : `₹${newV.discount_amount} OFF`;
        setVoucherMsg({ type: 'success', text: `Coupon '${res.code}' (${discText}${freeShipText}) applied successfully!` });
      } else {
        setAppliedVoucher(null);
        if (setContextAppliedVoucher) setContextAppliedVoucher(null);
        setVoucherMsg({ type: 'error', text: res?.message || `Coupon '${code}' is invalid or has already been used.` });
      }
    } catch (err) {
      setAppliedVoucher(null);
      if (setContextAppliedVoucher) setContextAppliedVoucher(null);
      const errMsg = err.response?.data?.detail || err.message || `Coupon '${code}' is invalid or expired.`;
      setVoucherMsg({ type: 'error', text: errMsg });
    }
  };

  const handleRemoveVoucher = () => {
    setAppliedVoucher(null);
    if (setContextAppliedVoucher) setContextAppliedVoucher(null);
    setVoucherCodeInput('');
    setVoucherMsg(null);
  };

  const handlePlaceOrder = async (e) => {
    e.preventDefault();
    if (placingOrder) return;
    if (cartItems.length === 0) {
      setError('Your shopping cart is empty.');
      return;
    }

    setPlacingOrder(true);
    setError(null);

    try {
      const payload = {
        customer_id: storeUser?.customer_id || storeUser?.id || 1,
        items: cartItems.map((item) => ({
          product_id: item.id,
          quantity: item.quantity || 1
        })),
        shipping_address: address,
        payment_mode: paymentMode,
        wallet_credit_applied: walletDiscount,
        voucher_code: appliedVoucher ? appliedVoucher.code : null
      };

      const result = await placeStoreOrder(payload);
      if (result.success) {
        setOrderSuccess(result);
        clearCart();
        setAppliedVoucher(null);
        if (setContextAppliedVoucher) setContextAppliedVoucher(null);
        setVoucherCodeInput('');
        setVoucherMsg(null);
        if (refreshCustomerPerks) {
          await refreshCustomerPerks(storeUser?.customer_id || storeUser?.id);
        }
      } else {
        setError(result.message || 'Failed to complete order.');
      }
    } catch (err) {
      console.error('Checkout error:', err);
      setError(err.response?.data?.detail || 'An error occurred while placing your order. Please try again.');
    } finally {
      setPlacingOrder(false);
    }
  };

  // SUCCESS SCREEN
  if (orderSuccess) {
    const { order, realtime_ml_sync } = orderSuccess;
    return (
      <div className="checkout-page-wrapper">
        <div className="order-confirmed-card">
          <div className="confirmed-icon-box">
            <CheckCircle size={44} className="text-emerald" />
          </div>
          <h1>Order Placed Successfully!</h1>
          <p className="confirmed-subtext">
            Thank you for shopping on SmartCart. A confirmation receipt has been generated.
          </p>

          <div className="order-meta-grid">
            <div className="meta-cell">
              <span className="meta-label">Order Number</span>
              <strong className="meta-value">{order.order_number}</strong>
            </div>
            <div className="meta-cell">
              <span className="meta-label">Payment Mode</span>
              <strong className="meta-value">{order.payment_mode}</strong>
            </div>
            <div className="meta-cell">
              <span className="meta-label">Total Amount Paid</span>
              <strong className="meta-value" style={{ color: '#007185' }}>₹{order.total_amount?.toLocaleString()}</strong>
            </div>
            {order.discount > 0 && (
              <div className="meta-cell">
                <span className="meta-label">Discounts & Credits Applied</span>
                <strong className="meta-value" style={{ color: '#007600' }}>-₹{order.discount?.toLocaleString()}</strong>
              </div>
            )}
            <div className="meta-cell">
              <span className="meta-label">Estimated Delivery</span>
              <strong className="meta-value" style={{ color: '#007600' }}>Tomorrow, 11 AM</strong>
            </div>
          </div>

          {/* Real-Time ML Synchronization Callout Card */}
          {realtime_ml_sync && (
            <div className="realtime-ml-success-card">
              <div className="ml-card-badge">
                <Sparkles size={16} />
                <span>Real-Time Enterprise ML Model Re-scored</span>
              </div>
              <h3>Customer Churn Risk & Sales Forecast Synchronized Live!</h3>
              <p>
                The purchase was automatically logged in the MySQL/SQLite database. The Random Forest Churn Model immediately re-scored account <strong>{realtime_ml_sync.source_customer_id}</strong>:
              </p>

              <div className="ml-metrics-pill-row">
                <div className="metric-pill">
                  <span>Inactivity Reset</span>
                  <strong>{realtime_ml_sync.days_since_last_purchase} Days</strong>
                </div>
                <div className="metric-pill">
                  <span>New Lifetime Orders</span>
                  <strong>{realtime_ml_sync.total_orders_lifetime} Orders</strong>
                </div>
                <div className="metric-pill">
                  <span>New Lifetime Spend</span>
                  <strong>{realtime_ml_sync.total_spend_inr}</strong>
                </div>
                <div className="metric-pill highlight">
                  <span>Updated Churn Probability</span>
                  <strong>{realtime_ml_sync.new_churn_probability}%</strong>
                </div>
                <div className="metric-pill highlight-risk">
                  <span>Predicted Risk Tier</span>
                  <strong>{realtime_ml_sync.new_risk_category || 'Low Risk'}</strong>
                </div>
              </div>
            </div>
          )}

          <div className="order-next-actions">
            <Link to="/store/my-orders" className="btn-amazon-gold">
              <span>📦 View My Orders & Tracking</span>
              <ArrowRight size={15} />
            </Link>
            <Link to="/store" className="btn-outline-store">
              <span>🛍️ Continue Shopping</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="checkout-page-wrapper">
      <div className="checkout-main-grid">
        {/* Left Column: Checkout Steps */}
        <div className="checkout-form-column">
          <h1 className="checkout-main-title">SmartCart Secure Checkout</h1>

          {error && (
            <div className="checkout-error-box">
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          )}

          {/* Step 1: Customer Account & Address */}
          <div className="checkout-section-card">
            <div className="section-step-header">
              <span className="step-num">1</span>
              <div>
                <h2>Shipping Address & Account Details</h2>
                <span className="step-subtitle">Logged in as: <strong>{storeUser?.username}</strong> ({storeUser?.full_name})</span>
              </div>
            </div>

            <div className="address-input-group">
              <label>Delivery Address:</label>
              <textarea
                rows={3}
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                required
              />
            </div>
          </div>

          {/* Step 2: Payment Mode */}
          <div className="checkout-section-card">
            <div className="section-step-header">
              <span className="step-num">2</span>
              <div>
                <h2>Select a Payment Method</h2>
                <span className="step-subtitle">All transactions are encrypted and secured</span>
              </div>
            </div>

            <div className="payment-options-grid">
              <label className={`payment-option-card ${paymentMode === 'UPI' ? 'selected' : ''}`}>
                <input
                  type="radio"
                  name="payment"
                  value="UPI"
                  checked={paymentMode === 'UPI'}
                  onChange={(e) => setPaymentMode(e.target.value)}
                />
                <Smartphone size={20} className="pay-icon" />
                <div>
                  <strong>UPI (Instant PhonePe, Google Pay, Paytm)</strong>
                  <span className="pay-desc">Pay directly from your bank with zero transaction fees</span>
                </div>
              </label>

              <label className={`payment-option-card ${paymentMode === 'Credit/Debit Card' ? 'selected' : ''}`}>
                <input
                  type="radio"
                  name="payment"
                  value="Credit/Debit Card"
                  checked={paymentMode === 'Credit/Debit Card'}
                  onChange={(e) => setPaymentMode(e.target.value)}
                />
                <CreditCard size={20} className="pay-icon" />
                <div>
                  <strong>Credit / Debit Card (Visa, MasterCard, RuPay)</strong>
                  <span className="pay-desc">Safe 256-bit encryption</span>
                </div>
              </label>

              <label className={`payment-option-card ${paymentMode === 'Net Banking' ? 'selected' : ''}`}>
                <input
                  type="radio"
                  name="payment"
                  value="Net Banking"
                  checked={paymentMode === 'Net Banking'}
                  onChange={(e) => setPaymentMode(e.target.value)}
                />
                <Building size={20} className="pay-icon" />
                <div>
                  <strong>Net Banking (All Major Indian Banks)</strong>
                  <span className="pay-desc">HDFC, SBI, ICICI, Axis, Kotak</span>
                </div>
              </label>

              <label className={`payment-option-card ${paymentMode === 'Cash on Delivery' ? 'selected' : ''}`}>
                <input
                  type="radio"
                  name="payment"
                  value="Cash on Delivery"
                  checked={paymentMode === 'Cash on Delivery'}
                  onChange={(e) => setPaymentMode(e.target.value)}
                />
                <Banknote size={20} className="pay-icon" />
                <div>
                  <strong>Cash on Delivery / Pay on Delivery</strong>
                  <span className="pay-desc">Cash, UPI, or Cards accepted at your doorstep</span>
                </div>
              </label>
            </div>
          </div>

          {/* Step 3: Apply Account Retention Perks, Coupons & Delivery Benefits */}
          <div className="checkout-section-card">
            <div className="section-step-header">
              <span className="step-num">3</span>
              <div>
                <h2>Apply Retention Coupons & Delivery Perks</h2>
                <span className="step-subtitle">Perks authorized by Seller Retention Intelligence</span>
              </div>
            </div>

            {/* Express Air Priority Delivery Perk Banner */}
            {hasExpressShipping && (
              <div style={{
                padding: '12px 16px',
                backgroundColor: '#eff6ff',
                border: '1px solid #bfdbfe',
                borderRadius: '8px',
                marginBottom: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '10px'
              }}>
                <span style={{ fontSize: '22px' }}>⚡</span>
                <div>
                  <div style={{ fontWeight: 800, color: '#1e40af', fontSize: '14px' }}>
                    Free Express Air Priority Delivery Active (₹0 Shipping Fee)
                  </div>
                  <div style={{ fontSize: '12px', color: '#2563eb' }}>
                    Standard shipping fee is completely waived via SmartCart Express Air Logistics.
                  </div>
                </div>
              </div>
            )}

            {/* Active Retention Coupons & Promo Code Input */}
            <div style={{ marginBottom: walletBalance > 0 ? '16px' : '0' }}>
              <label style={{ display: 'block', fontWeight: 700, fontSize: '14px', color: '#1e293b', marginBottom: '8px' }}>
                Retention Coupons & Discount Vouchers:
              </label>

              {/* Clickable Active Vouchers Chips */}
              {activeVouchers && activeVouchers.length > 0 && (
                <div style={{ marginBottom: '12px' }}>
                  <span style={{ fontSize: '12px', color: '#475569', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                    Available Account Coupons (Click to apply):
                  </span>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {activeVouchers.map((v, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => handleApplyVoucher(v.code)}
                        style={{
                          padding: '8px 14px',
                          borderRadius: '6px',
                          border: appliedVoucher?.code === v.code ? '2px solid #16a34a' : '1px solid #cbd5e1',
                          backgroundColor: appliedVoucher?.code === v.code ? '#dcfce7' : '#ffffff',
                          color: appliedVoucher?.code === v.code ? '#15803d' : '#0f172a',
                          fontWeight: 800,
                          fontSize: '13px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                          boxShadow: appliedVoucher?.code === v.code ? '0 1px 3px rgba(22,163,74,0.2)' : 'none'
                        }}
                      >
                        <span>🎟️ {v.code}</span>
                        <span>({v.discount_pct ? `${v.discount_pct}% OFF` : `₹${v.discount_amount} OFF`})</span>
                        {appliedVoucher?.code === v.code && <span style={{ color: '#15803d' }}>✓ Applied</span>}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Manual Voucher Input */}
              <div style={{ display: 'flex', gap: '8px', maxWidth: '420px' }}>
                <input
                  type="text"
                  placeholder="Enter promo or voucher code..."
                  value={voucherCodeInput}
                  onChange={(e) => setVoucherCodeInput(e.target.value)}
                  style={{
                    flex: 1,
                    padding: '8px 12px',
                    borderRadius: '6px',
                    border: '1px solid #cbd5e1',
                    fontSize: '13px',
                    textTransform: 'uppercase'
                  }}
                />
                <button
                  type="button"
                  onClick={() => handleApplyVoucher()}
                  className="btn-amazon-gold"
                  style={{ padding: '8px 16px', fontSize: '13px', borderRadius: '6px' }}
                >
                  Apply
                </button>
                {appliedVoucher && (
                  <button
                    type="button"
                    onClick={handleRemoveVoucher}
                    style={{
                      padding: '8px 12px',
                      fontSize: '12px',
                      borderRadius: '6px',
                      border: '1px solid #ef4444',
                      background: '#fee2e2',
                      color: '#b91c1c',
                      cursor: 'pointer',
                      fontWeight: 700
                    }}
                  >
                    Remove
                  </button>
                )}
              </div>

              {voucherMsg && (
                <div style={{
                  marginTop: '8px',
                  fontSize: '12px',
                  fontWeight: 700,
                  color: voucherMsg.type === 'success' ? '#15803d' : '#b91c1c'
                }}>
                  {voucherMsg.text}
                </div>
              )}

              {/* Optional Wallet Balance if positive */}
              {walletBalance > 0 && (
                <div style={{
                  marginTop: '16px',
                  padding: '10px 14px',
                  backgroundColor: '#fffbeb',
                  border: '1px solid #fef3c7',
                  borderRadius: '6px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '10px'
                }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', margin: 0 }}>
                    <input
                      type="checkbox"
                      checked={useWallet}
                      onChange={(e) => setUseWallet(e.target.checked)}
                      style={{ width: '16px', height: '16px', accentColor: '#ff9900' }}
                    />
                    <span style={{ fontSize: '13px', fontWeight: 700, color: '#92400e' }}>
                      👛 Use Wallet Balance (₹{walletBalance.toFixed(2)} Available)
                    </span>
                  </label>
                  {useWallet && (
                    <span style={{ fontWeight: 800, color: '#15803d', fontSize: '13px', backgroundColor: '#dcfce7', padding: '2px 8px', borderRadius: '4px' }}>
                      -₹{walletDiscount.toFixed(2)} Applied
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Step 4: Review Items */}
          <div className="checkout-section-card">
            <div className="section-step-header">
              <span className="step-num">4</span>
              <div>
                <h2>Review Items in Your Order</h2>
                <span className="step-subtitle">{cartCount} items scheduled for delivery</span>
              </div>
            </div>

            <div className="checkout-items-preview">
              {cartItems.map((item) => (
                <div key={item.id} className="preview-item-row">
                  <img src={item.image_url} alt={item.title} />
                  <div className="preview-item-info">
                    <strong>{item.title}</strong>
                    <span>Qty: {item.quantity} | Unit Price: ₹{item.price.toLocaleString()}</span>
                  </div>
                  <strong className="preview-item-total">₹{(item.price * item.quantity).toLocaleString()}</strong>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Order Summary & Place Button */}
        <div className="checkout-summary-column">
          <div className="order-place-card">
            <button
              type="button"
              className="btn-place-order-big"
              onClick={handlePlaceOrder}
              disabled={placingOrder || cartItems.length === 0}
            >
              {placingOrder ? '⏳ Processing Order & Syncing ML...' : 'Place Your Order and Pay'}
            </button>

            <div className="order-calc-breakdown">
              <h3>Order Summary</h3>
              <div className="calc-row">
                <span>Items Subtotal:</span>
                <span>₹{cartSubtotal.toLocaleString()}</span>
              </div>

              {voucherDiscount > 0 && (
                <div className="calc-row" style={{ color: '#15803d', fontWeight: 700 }}>
                  <span>Voucher Discount ({appliedVoucher?.code}):</span>
                  <span>-₹{voucherDiscount.toFixed(2)}</span>
                </div>
              )}

              {walletDiscount > 0 && (
                <div className="calc-row" style={{ color: '#15803d', fontWeight: 700 }}>
                  <span>Wallet Credit Applied:</span>
                  <span>-₹{walletDiscount.toFixed(2)}</span>
                </div>
              )}

              <div className="calc-row">
                <span>Delivery:</span>
                <span>{shippingFee === 0 ? <strong style={{ color: '#007600' }}>FREE</strong> : `₹${shippingFee}`}</span>
              </div>
              <div className="calc-row">
                <span>Estimated 5% GST:</span>
                <span>₹{estimatedTax.toLocaleString()}</span>
              </div>
              <div className="calc-divider"></div>
              <div className="calc-total-row">
                <span>Order Total:</span>
                <span className="calc-grand-total">₹{totalAmount.toLocaleString()}</span>
              </div>
            </div>

            <div className="enterprise-sync-notice">
              <Sparkles size={16} className="text-amazon-gold" />
              <div>
                <strong>Live ML Pipeline Connected:</strong>
                <p>
                  Placing this order writes the transaction to the database, resets customer inactivity to 0, and updates the Multi-Horizon Sales Forecast immediately.
                </p>
              </div>
            </div>

            <div className="secure-badge-box">
              <ShieldCheck size={16} />
              <span>SmartCart 100% Purchase Protection Guarantee</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CheckoutPage;
