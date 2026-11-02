import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Package,
  CheckCircle,
  Truck,
  ArrowRight,
  Clock,
  ExternalLink,
  Sparkles,
  Copy,
  Check,
  RotateCcw,
  ShoppingBag,
  MessageSquare,
  AlertCircle,
  Calendar,
  Layers,
  ChevronRight,
  Bell,
  Tag,
  Gift,
  Mail,
  ShieldCheck
} from 'lucide-react';
import { getCustomerOrders } from '../../services/storeApi';
import { useStore } from '../../context/StoreContext';
import './CustomerOrders.css';

const CustomerOrders = () => {
  const navigate = useNavigate();
  const { storeUser, addToCart, notifications = [], unreadNotificationsCount = 0, markNotificationRead } = useStore();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [copiedId, setCopiedId] = useState(null);
  const [copiedCoupon, setCopiedCoupon] = useState(null);
  const [activeTab, setActiveTab] = useState('all'); // 'all' | 'placed' | 'delivered' | 'notifications'
  const [buyAgainToast, setBuyAgainToast] = useState(null);

  const handleCopyCoupon = (code) => {
    if (!code) return;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(code).catch(() => fallbackCopy(code));
    } else {
      fallbackCopy(code);
    }
    setCopiedCoupon(code);
    setTimeout(() => {
      setCopiedCoupon(null);
    }, 2000);
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
    fetchOrders();
  }, [storeUser]);

  const fetchOrders = async () => {
    if (!storeUser?.customer_id && !storeUser?.id) return;
    setLoading(true);
    try {
      const data = await getCustomerOrders(storeUser.customer_id || storeUser.id);
      setOrders(data.orders || []);
    } catch (err) {
      console.error('Failed to load customer orders:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBuyAgain = (item) => {
    if (!item) return;
    const cartProduct = {
      id: item.product_id,
      title: item.title,
      price: item.unit_price || item.total_price / (item.quantity || 1),
      image_url: item.image_url,
      sku: `PROD-${item.product_id}`
    };
    addToCart(cartProduct, 1);
    setBuyAgainToast(item.title);
    setTimeout(() => setBuyAgainToast(null), 3000);
  };

  // Status Categorization
  const isDelivered = (status) => {
    if (!status) return false;
    const s = status.toLowerCase();
    return s === 'delivered' || s === 'completed';
  };

  const isOrderPlacedOrInProgress = (status) => {
    if (!status) return true;
    const s = status.toLowerCase();
    return s !== 'delivered' && s !== 'completed' && s !== 'cancelled' && s !== 'returned';
  };

  const deliveredOrders = orders.filter((o) => isDelivered(o.order_status));
  const placedOrders = orders.filter((o) => isOrderPlacedOrInProgress(o.order_status));

  // Filter based on active tab
  const displayedOrders = activeTab === 'delivered'
    ? deliveredOrders
    : activeTab === 'placed'
    ? placedOrders
    : orders;

  return (
    <div className="orders-page-wrapper">
      {/* Toast alert on Quick Buy Again */}
      {buyAgainToast && (
        <div className="orders-toast">
          <CheckCircle size={18} className="text-emerald" />
          <span>Added <strong>{buyAgainToast.slice(0, 35)}...</strong> to your cart!</span>
          <Link to="/store/cart" className="toast-cart-link">View Cart</Link>
        </div>
      )}

      <div className="orders-container">
        {/* Header Card */}
        <div className="orders-header-card">
          <div className="header-left">
            <div className="header-title-row">
              <Package className="text-amazon-orange" size={28} />
              <h1>Your Orders & Purchases</h1>
            </div>
            <div className="orders-subtext">
              <span>Account: <strong>{storeUser?.full_name || storeUser?.username}</strong></span>
              {storeUser?.username && (
                <div className="cust-id-copy-wrapper">
                  <span className="cust-id-tag">ID: {storeUser.username}</span>
                  <button
                    type="button"
                    onClick={() => handleCopyId(storeUser.username)}
                    className={`btn-copy-mini ${copiedId === storeUser.username ? 'copied' : ''}`}
                    title="Copy Customer ID"
                  >
                    {copiedId === storeUser.username ? <Check size={11} /> : <Copy size={11} />}
                    <span>{copiedId === storeUser.username ? 'Copied' : 'Copy ID'}</span>
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="header-right">
            <Link to="/store/catalog" className="btn-view-ml-impact">
              <span>Continue Shopping →</span>
            </Link>
          </div>
        </div>

        {/* Quick Order Stats / Summary Cards */}
        <div className="orders-summary-metrics">
          <div
            className={`metric-stat-card ${activeTab === 'all' ? 'active-metric' : ''}`}
            onClick={() => setActiveTab('all')}
            role="button"
            tabIndex={0}
          >
            <div className="metric-icon-box bg-slate">
              <Layers size={20} />
            </div>
            <div className="metric-info">
              <span className="metric-label">All Orders</span>
              <strong className="metric-value">{orders.length}</strong>
            </div>
          </div>

          <div
            className={`metric-stat-card ${activeTab === 'placed' ? 'active-metric' : ''}`}
            onClick={() => setActiveTab('placed')}
            role="button"
            tabIndex={0}
          >
            <div className="metric-icon-box bg-blue">
              <Clock size={20} />
            </div>
            <div className="metric-info">
              <span className="metric-label">Order Placed / In Progress</span>
              <strong className="metric-value text-blue">{placedOrders.length}</strong>
            </div>
          </div>

          <div
            className={`metric-stat-card ${activeTab === 'delivered' ? 'active-metric' : ''}`}
            onClick={() => setActiveTab('delivered')}
            role="button"
            tabIndex={0}
          >
            <div className="metric-icon-box bg-emerald">
              <CheckCircle size={20} />
            </div>
            <div className="metric-info">
              <span className="metric-label">Delivered Orders</span>
              <strong className="metric-value text-emerald">{deliveredOrders.length}</strong>
            </div>
          </div>

          <div
            className={`metric-stat-card ${activeTab === 'notifications' ? 'active-metric' : ''}`}
            onClick={() => setActiveTab('notifications')}
            role="button"
            tabIndex={0}
          >
            <div className="metric-icon-box bg-purple">
              <Bell size={20} />
            </div>
            <div className="metric-info">
              <span className="metric-label">Account Alerts & Perks</span>
              <strong className="metric-value text-purple">
                {notifications.length}
                {unreadNotificationsCount > 0 && (
                  <span className="unread-dot-badge"> ({unreadNotificationsCount} new)</span>
                )}
              </strong>
            </div>
          </div>
        </div>

        {/* Amazon-Style Tab Bar */}
        <div className="orders-tabs-nav">
          <button
            type="button"
            className={`orders-tab-btn ${activeTab === 'all' ? 'active' : ''}`}
            onClick={() => setActiveTab('all')}
          >
            <span>All Orders</span>
            <span className="tab-count-badge">{orders.length}</span>
          </button>

          <button
            type="button"
            className={`orders-tab-btn ${activeTab === 'placed' ? 'active' : ''}`}
            onClick={() => setActiveTab('placed')}
          >
            <Clock size={15} />
            <span>Order Placed & In Progress</span>
            <span className="tab-count-badge badge-blue">{placedOrders.length}</span>
          </button>

          <button
            type="button"
            className={`orders-tab-btn ${activeTab === 'delivered' ? 'active' : ''}`}
            onClick={() => setActiveTab('delivered')}
          >
            <CheckCircle size={15} />
            <span>Delivered Orders</span>
            <span className="tab-count-badge badge-emerald">{deliveredOrders.length}</span>
          </button>

          <button
            type="button"
            className={`orders-tab-btn ${activeTab === 'notifications' ? 'active' : ''}`}
            onClick={() => setActiveTab('notifications')}
          >
            <Bell size={15} />
            <span>Account Notifications & Offers</span>
            {unreadNotificationsCount > 0 ? (
              <span className="tab-count-badge badge-orange">{unreadNotificationsCount} new</span>
            ) : (
              <span className="tab-count-badge">{notifications.length}</span>
            )}
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'notifications' ? (
          <div className="orders-notifications-section">
            <div className="notifications-tab-header">
              <div className="notif-header-left">
                <h2>Customer Account Inbox & Alerts</h2>
                <p>Personalized campaign incentives, coupons, and outreach notifications dispatched directly to your account.</p>
              </div>
              <Link to="/store/notifications" className="btn-open-full-notifs">
                <span>Open Dedicated Notification Center</span>
                <ArrowRight size={15} />
              </Link>
            </div>

            {notifications.length === 0 ? (
              <div className="empty-orders-box">
                <Bell size={52} className="empty-pkg-icon" />
                <h2>No Notifications Yet</h2>
                <p>When retention campaigns are accepted in the Decision Platform, personalized messages and promotional perks appear here immediately!</p>
              </div>
            ) : (
              <div className="orders-notif-cards-list">
                {notifications.map((n) => (
                  <div key={n.id} className={`orders-notif-card ${!n.is_read ? 'unread-card' : ''}`}>
                    <div className="orders-notif-card-header">
                      <div className="orders-notif-title-row">
                        <span className="notif-channel-tag">
                          <Mail size={12} />
                          <span>{n.channel || 'Direct In-App Alert'}</span>
                        </span>
                        <span className="dispatch-badge">✓ {n.dispatch_status || 'Delivered to Account'}</span>
                        {!n.is_read && <span className="new-badge">NEW</span>}
                      </div>
                      <span className="orders-notif-time">
                        {n.created_at ? new Date(n.created_at).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' }) : 'Recently'}
                      </span>
                    </div>

                    <h3 className="orders-notif-title">{n.title}</h3>
                    <p className="orders-notif-body">{n.message}</p>

                    <div className="orders-notif-footer">
                      {n.coupon_code && (
                        <div className="orders-notif-coupon-box">
                          <span className="coupon-label">Coupon Code:</span>
                          <code className="coupon-code-value">{n.coupon_code}</code>
                          <button
                            type="button"
                            onClick={() => handleCopyCoupon(n.coupon_code)}
                            className="btn-copy-code"
                          >
                            {copiedCoupon === n.coupon_code ? <Check size={12} /> : <Copy size={12} />}
                            <span>{copiedCoupon === n.coupon_code ? 'Copied' : 'Copy'}</span>
                          </button>
                          <Link to="/store/catalog" className="btn-shop-coupon">
                            Shop Catalog →
                          </Link>
                        </div>
                      )}

                      {!n.is_read && (
                        <button
                          type="button"
                          onClick={() => markNotificationRead(n.id)}
                          className="btn-mark-order-notif-read"
                        >
                          <CheckCircle size={14} />
                          <span>Mark as Read</span>
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : loading ? (
          <div className="orders-loading-box">
            <div className="loading-spinner"></div>
            <p>Loading your order history from SmartCart storefront database...</p>
          </div>
        ) : displayedOrders.length === 0 ? (
          <div className="empty-orders-box">
            <Package size={52} className="empty-pkg-icon" />
            {activeTab === 'placed' ? (
              <>
                <h2>No Active Orders In Progress</h2>
                <p>You have zero orders currently awaiting dispatch or out for delivery.</p>
                <Link to="/store/catalog" className="btn-hero-primary" style={{ marginTop: '16px', display: 'inline-block' }}>
                  Explore Products & Place an Order
                </Link>
              </>
            ) : activeTab === 'delivered' ? (
              <>
                <h2>No Delivered Orders Yet</h2>
                <p>Orders that have reached final fulfillment and delivery will appear here.</p>
                <button
                  type="button"
                  onClick={() => setActiveTab('placed')}
                  className="btn-retry-product"
                  style={{ marginTop: '16px' }}
                >
                  View Pending / Placed Orders ({placedOrders.length})
                </button>
              </>
            ) : (
              <>
                <h2>No Orders Placed Yet for this Account</h2>
                <p>Explore the store catalog and place an order to see actual sales data flow into the database!</p>
                <Link to="/store/catalog" className="btn-hero-primary" style={{ marginTop: '16px', display: 'inline-block' }}>
                  Start Shopping Now
                </Link>
              </>
            )}
          </div>
        ) : (
          <div className="orders-cards-list">
            {displayedOrders.map((o) => {
              const delivered = isDelivered(o.order_status);

              return (
                <div
                  key={o.order_id}
                  className={`order-history-card ${delivered ? 'card-delivered' : 'card-in-progress'}`}
                >
                  {/* Order Top Ribbon */}
                  <div className="order-top-ribbon">
                    <div className="ribbon-col">
                      <span className="ribbon-lbl">ORDER PLACED</span>
                      <span className="ribbon-val">
                        {o.order_date
                          ? new Date(o.order_date).toLocaleDateString('en-IN', {
                              day: 'numeric',
                              month: 'short',
                              year: 'numeric'
                            })
                          : 'Today'}
                      </span>
                    </div>

                    <div className="ribbon-col">
                      <span className="ribbon-lbl">TOTAL AMOUNT</span>
                      <span className="ribbon-val price-highlight">₹{o.order_amount?.toLocaleString()}</span>
                    </div>

                    {(o.discount > 0 || o.voucher_code || o.free_shipping_applied) && (
                      <div className="ribbon-col">
                        <span className="ribbon-lbl">OFFERS & SAVINGS</span>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', alignItems: 'center' }}>
                          {o.voucher_code && (
                            <span style={{ fontSize: '11px', fontWeight: 800, color: '#15803d', backgroundColor: '#dcfce7', padding: '1px 6px', borderRadius: '4px' }}>
                              🎟️ {o.voucher_code}
                            </span>
                          )}
                          {o.discount > 0 && (
                            <span style={{ fontSize: '12px', fontWeight: 700, color: '#15803d' }}>
                              -₹{o.discount?.toLocaleString()}
                            </span>
                          )}
                          {o.free_shipping_applied && (
                            <span style={{ fontSize: '11px', fontWeight: 800, color: '#0369a1', backgroundColor: '#e0f2fe', padding: '1px 6px', borderRadius: '4px' }}>
                              ⚡ Free Delivery
                            </span>
                          )}
                        </div>
                      </div>
                    )}

                    <div className="ribbon-col">
                      <span className="ribbon-lbl">SHIP TO</span>
                      <span className="ribbon-val">{storeUser?.full_name || storeUser?.username}</span>
                    </div>

                    <div className="ribbon-col right">
                      <div className="order-number-row">
                        <span className="ribbon-lbl">ORDER #</span>
                        <span className="order-num-text">{o.order_number}</span>
                      </div>
                      <span className="payment-badge">{o.payment_mode || 'UPI'}</span>
                    </div>
                  </div>

                  {/* Status Banner */}
                  {delivered ? (
                    <div className="order-status-banner banner-delivered">
                      <div className="banner-status-left">
                        <CheckCircle size={20} className="text-emerald" />
                        <div>
                          <strong>Delivered {o.order_date ? new Date(o.order_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : 'Recently'}</strong>
                          <span className="banner-subtext">Package was handed directly to resident or placed at doorstep.</span>
                        </div>
                      </div>
                      <span className="status-pill pill-delivered">Delivered</span>
                    </div>
                  ) : (
                    <div className="order-status-banner banner-in-progress">
                      <div className="banner-status-left">
                        <Clock size={20} className="text-blue" />
                        <div>
                          <strong>Order Placed & Confirmed — {o.order_status}</strong>
                          <span className="banner-subtext">Estimated Delivery: Arriving in 1-2 business days with SmartCart Prime Express</span>
                        </div>
                      </div>
                      <span className="status-pill pill-in-progress">{o.order_status}</span>
                    </div>
                  )}

                  {/* Visual Stepper for In-Progress Orders */}
                  {!delivered && (
                    <div className="order-tracking-stepper">
                      <div className="step-item step-completed">
                        <div className="step-dot"><Check size={12} /></div>
                        <span className="step-label">Order Placed</span>
                      </div>
                      <div className="step-line active"></div>
                      <div className={`step-item ${o.order_status?.toLowerCase().includes('transit') || o.order_status?.toLowerCase().includes('shipped') ? 'step-completed' : 'step-current'}`}>
                        <div className="step-dot"><Clock size={12} /></div>
                        <span className="step-label">{o.order_status?.toLowerCase().includes('transit') ? 'In Transit' : 'Confirmed'}</span>
                      </div>
                      <div className="step-line"></div>
                      <div className="step-item step-pending">
                        <div className="step-dot"><Truck size={12} /></div>
                        <span className="step-label">Out for Delivery</span>
                      </div>
                      <div className="step-line"></div>
                      <div className="step-item step-pending">
                        <div className="step-dot"><CheckCircle size={12} /></div>
                        <span className="step-label">Delivered</span>
                      </div>
                    </div>
                  )}

                  {/* Order Body Items */}
                  <div className="order-card-body">
                    <div className="order-items-sublist">
                      {o.items?.map((it, idx) => (
                        <div key={idx} className="order-sub-item">
                          <Link to={`/store/product/${it.product_id}`} className="sub-item-img-link">
                            <img
                              src={it.image_url || 'https://images.unsplash.com/photo-1543512214-318c7553f230?w=200'}
                              alt={it.title}
                            />
                          </Link>

                          <div className="sub-item-text">
                            <Link to={`/store/product/${it.product_id}`} className="sub-item-title">
                              {it.title}
                            </Link>

                            <div className="sub-item-meta-row">
                              <span className="sub-item-meta">Quantity: <strong>{it.quantity}</strong></span>
                              <span className="meta-separator">•</span>
                              <span className="sub-item-meta">Item Total: <strong>₹{it.total_price?.toLocaleString()}</strong></span>
                            </div>

                            <div className="sub-item-actions-row">
                              <button
                                type="button"
                                className="btn-buy-again"
                                onClick={() => handleBuyAgain(it)}
                              >
                                <ShoppingBag size={13} />
                                <span>Buy it again</span>
                              </button>

                              <Link to={`/store/product/${it.product_id}`} className="btn-view-item">
                                <span>View item</span>
                                <ChevronRight size={13} />
                              </Link>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default CustomerOrders;
