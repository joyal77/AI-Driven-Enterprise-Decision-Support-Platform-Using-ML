import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ShieldAlert,
  ShoppingBag,
  ExternalLink,
  Sparkles,
  TrendingUp,
  CreditCard,
  UserCheck,
  Search,
  Filter,
  CheckCircle,
  Clock,
  ArrowRight,
  RefreshCw,
  Copy,
  Check
} from 'lucide-react';
import { getAllStoreOrders } from '../../services/storeApi';
import { useStore } from '../../context/StoreContext';
import './AdminOrdersFeed.css';

const AdminOrdersFeed = () => {
  const navigate = useNavigate();
  const { storeUser } = useStore();
  const [orders, setOrders] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPayment, setFilterPayment] = useState('All');
  const [copiedId, setCopiedId] = useState(null);

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
  }, []);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const data = await getAllStoreOrders({ limit: 100 });
      setOrders(data.orders || []);
      setTotalCount(data.total || (data.orders ? data.orders.length : 0));
    } catch (err) {
      console.error('Failed to load store orders for Admin:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredOrders = orders.filter((o) => {
    const custId = o.customer?.source_customer_id || '';
    const ordNum = o.order_number || '';
    const matchesSearch =
      custId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ordNum.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPayment =
      filterPayment === 'All' || o.payment_mode === filterPayment;
    return matchesSearch && matchesPayment;
  });

  const totalRevenue = orders.reduce((sum, o) => sum + (o.order_amount || 0), 0);
  const avgOrderValue = orders.length > 0 ? totalRevenue / orders.length : 0;

  return (
    <div className="admin-feed-container">
      {/* Top Banner */}
      <div className="admin-header-card">
        <div className="admin-header-left">
          <div className="admin-role-badge">
            <ShieldAlert size={14} /> Store Administration & ML Pipeline Monitor
          </div>
          <h1>Live Store Transactions & Order Feed</h1>
          <p>
            Real-time shopping transactions placed by all 150 customer accounts on the SmartCart storefront. Every checkout instantly updates customer lifetime value and re-computes churn probability in our Random Forest model.
          </p>
        </div>
        <div className="admin-header-right">
          <button onClick={fetchOrders} className="btn-refresh-feed" title="Refresh Live Transactions">
            <RefreshCw size={15} className={loading ? 'animate-spin' : ''} />
            <span>Refresh Feed</span>
          </button>
        </div>
      </div>

      {/* KPI Stats Ribbon */}
      <div className="admin-kpi-ribbon">
        <div className="admin-stat-box">
          <span className="stat-label">TOTAL STORE ORDERS</span>
          <strong className="stat-value">{totalCount}</strong>
          <span className="stat-desc">Live checkouts in database</span>
        </div>
        <div className="admin-stat-box highlight">
          <span className="stat-label">TOTAL GROSS REVENUE</span>
          <strong className="stat-value">₹{totalRevenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong>
          <span className="stat-desc">Captured store sales</span>
        </div>
        <div className="admin-stat-box">
          <span className="stat-label">AVERAGE ORDER VALUE (AOV)</span>
          <strong className="stat-value">₹{avgOrderValue.toFixed(2)}</strong>
          <span className="stat-desc">Synced into customer profile</span>
        </div>
        <div className="admin-stat-box success">
          <span className="stat-label">ML REAL-TIME SYNC</span>
          <strong className="stat-value text-emerald">Active</strong>
          <span className="stat-desc">Zero-delay feature pipeline</span>
        </div>
      </div>

      {/* Controls & Search */}
      <div className="admin-controls-card">
        <div className="admin-search-wrapper">
          <Search size={16} />
          <input
            type="text"
            placeholder="Filter by Order Number or Customer ID (e.g. AMZ_PRED1_1001)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="admin-payment-filter">
          <Filter size={15} />
          <span>Payment:</span>
          {['All', 'UPI', 'Credit/Debit Card', 'Net Banking', 'Cash on Delivery'].map((mode) => (
            <button
              key={mode}
              className={`filter-chip ${filterPayment === mode ? 'active' : ''}`}
              onClick={() => setFilterPayment(mode)}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>

      {/* Orders Table */}
      <div className="admin-table-card">
        {loading ? (
          <div className="admin-loading-state">
            <RefreshCw size={24} className="animate-spin text-amber" />
            <p>Loading real-time transactions from MySQL...</p>
          </div>
        ) : filteredOrders.length === 0 ? (
          <div className="admin-empty-state">
            <ShoppingBag size={48} />
            <h3>No orders found</h3>
            <p>No store transactions match the current filters.</p>
          </div>
        ) : (
          <table className="admin-orders-table">
            <thead>
              <tr>
                <th>Order Number</th>
                <th>Order Date</th>
                <th>Customer ID</th>
                <th>Membership</th>
                <th>Items</th>
                <th>Payment Mode</th>
                <th>Order Total</th>
                <th>Status</th>
                <th>ML Decision Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredOrders.map((o) => {
                const custId = o.customer?.source_customer_id || 'N/A';
                const isPrime = o.customer?.membership_status?.toLowerCase().includes('prime');
                const formattedDate = new Date(o.order_date).toLocaleString('en-IN', {
                  day: 'numeric',
                  month: 'short',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                });

                return (
                  <tr key={o.order_id}>
                    <td>
                      <code className="order-num-code">{o.order_number}</code>
                    </td>
                    <td>
                      <span className="order-date-text">{formattedDate}</span>
                    </td>
                    <td>
                      <div className="cust-cell" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '3px' }}>
                        {custId && custId !== 'N/A' && (
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleCopyId(custId);
                            }}
                            className={`btn-copy-mini ${copiedId === custId ? 'copied' : ''}`}
                            title={`Copy Customer ID: ${custId}`}
                          >
                            {copiedId === custId ? <Check size={10} /> : <Copy size={10} />}
                            <span>{copiedId === custId ? 'Copied' : 'Copy ID'}</span>
                          </button>
                        )}
                        <strong>{custId}</strong>
                        <span className="cust-sub">{o.customer?.preferred_category || 'Store Shopper'}</span>
                      </div>
                    </td>
                    <td>
                      {isPrime ? (
                        <span className="membership-pill prime">Prime</span>
                      ) : (
                        <span className="membership-pill standard">Standard</span>
                      )}
                    </td>
                    <td>
                      <span className="items-chip">{o.items_count} item{o.items_count !== 1 ? 's' : ''}</span>
                    </td>
                    <td>
                      <span className="payment-mode-text">{o.payment_mode}</span>
                    </td>
                    <td>
                      <strong className="order-total-text">₹{o.order_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}</strong>
                    </td>
                    <td>
                      <span className="status-badge-confirmed">
                        <CheckCircle size={12} /> {o.order_status}
                      </span>
                    </td>
                    <td>
                      <div className="ml-action-group">
                        <Link
                          to={`/churn-prediction?search=${custId}`}
                          className="btn-inspect-churn"
                          title={`Inspect ${custId} in Churn Prediction Engine`}
                        >
                          <Sparkles size={13} />
                          <span>Inspect Churn Risk</span>
                        </Link>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

    </div>
  );
};

export default AdminOrdersFeed;
