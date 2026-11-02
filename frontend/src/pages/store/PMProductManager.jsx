import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Wrench,
  Plus,
  Edit2,
  Trash2,
  AlertTriangle,
  Package,
  DollarSign,
  TrendingUp,
  Search,
  CheckCircle2,
  X,
  Layers,
  Sparkles,
  ShieldCheck,
  ShoppingBag,
  Zap,
  Truck,
  RefreshCw
} from 'lucide-react';
import {
  getStoreProducts,
  createProduct,
  updateProduct,
  deleteProduct,
  getAdminOverview,
  bulkRestockInventory,
  getAdminOrders,
  updateOrderStatus
} from '../../services/storeApi';
import { useStore } from '../../context/StoreContext';
import './PMProductManager.css';

const PMProductManager = () => {
  const { storeUser, loginDirectly } = useStore();
  const isAdmin = storeUser?.role === 'admin';

  // Automatically sync admin session from ML Suite if user is admin
  useEffect(() => {
    try {
      const mlUserStr = localStorage.getItem('user');
      if (mlUserStr) {
        const mlUser = JSON.parse(mlUserStr);
        if (mlUser && mlUser.role === 'admin' && storeUser?.role !== 'admin') {
          const adminUser = {
            id: mlUser.id || 1,
            username: mlUser.email || 'admin',
            role: 'admin',
            full_name: mlUser.name || 'SmartCart Platform Administrator'
          };
          loginDirectly(adminUser);
          localStorage.setItem('smartcart_user', JSON.stringify(adminUser));
        }
      }
    } catch (e) {
      console.error('Error syncing admin session:', e);
    }
  }, [storeUser?.role]);

  // Navigation Tabs: 'products' | 'orders'
  const [activeTab, setActiveTab] = useState('products');

  // Products State
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [editingProduct, setEditingProduct] = useState(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);
  const [restocking, setRestocking] = useState(false);

  // Admin Overview Metrics
  const [overview, setOverview] = useState({
    total_products: 0,
    low_stock_count: 0,
    total_orders: 0,
    total_revenue: 0,
    total_customers: 0,
    total_staff: 0
  });

  // Orders Administration State
  const [ordersList, setOrdersList] = useState([]);
  const [loadingOrders, setLoadingOrders] = useState(false);
  const [orderStatusFilter, setOrderStatusFilter] = useState('all');
  const [orderSearchTerm, setOrderSearchTerm] = useState('');
  const [orderPage, setOrderPage] = useState(1);
  const [orderLimit, setOrderLimit] = useState(25);
  const [orderTotalCount, setOrderTotalCount] = useState(0);
  const [orderTotalPages, setOrderTotalPages] = useState(1);

  // Product Form State
  const [formData, setFormData] = useState({
    title: '',
    category: 'Electronics',
    price: '',
    original_price: '',
    stock_quantity: 100,
    image_url: '',
    description: '',
    is_prime: 1
  });

  useEffect(() => {
    fetchCatalog();
    fetchOverview();
  }, [selectedCategory]);

  useEffect(() => {
    if (activeTab === 'orders') {
      fetchOrders(orderPage, orderLimit, orderSearchTerm, orderStatusFilter);
    }
  }, [activeTab, orderPage, orderLimit, orderStatusFilter]);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const fetchOverview = async () => {
    try {
      const data = await getAdminOverview();
      if (data && data.success) {
        setOverview(data);
      }
    } catch (err) {
      console.warn('Overview fetch error:', err);
    }
  };

  const fetchCatalog = async () => {
    setLoading(true);
    try {
      const params = { limit: 100 };
      if (selectedCategory !== 'All') params.category = selectedCategory;
      const data = await getStoreProducts(params);
      setProducts(data.products || []);
    } catch (err) {
      console.error('Failed to load catalog:', err);
    } finally {
      setLoading(false);
    }
  };


  const fetchOrders = async (
    page = orderPage,
    limit = orderLimit,
    search = orderSearchTerm,
    status = orderStatusFilter
  ) => {
    setLoadingOrders(true);
    try {
      const params = { page, limit };
      if (status !== 'all') params.status_filter = status;
      if (search && search.trim()) params.search = search.trim();
      const data = await getAdminOrders(params);
      if (data && data.success) {
        setOrdersList(data.orders || []);
        setOrderTotalCount(data.total || (data.orders || []).length);
        setOrderTotalPages(data.total_pages || 1);
      }
    } catch (err) {
      console.error('Failed to load admin orders:', err);
    } finally {
      setLoadingOrders(false);
    }
  };


  const handleBulkRestock = async () => {
    setRestocking(true);
    try {
      const res = await bulkRestockInventory();
      showToast(res.message || 'Low stock items replenished to 100 units.');
      fetchCatalog();
      fetchOverview();
    } catch (err) {
      console.error('Bulk restock error:', err);
      alert('Failed to restock inventory.');
    } finally {
      setRestocking(false);
    }
  };


  const handleOrderStatusChange = async (orderId, newStatus) => {
    try {
      const res = await updateOrderStatus(orderId, newStatus);
      showToast(res.message || `Order status updated to ${newStatus}.`);
      fetchOrders();
      fetchOverview();
    } catch (err) {
      console.error(err);
      alert('Failed to update order status.');
    }
  };


  // Product Add / Edit handlers
  const handleOpenAddModal = () => {
    setFormData({
      title: '',
      category: 'Electronics',
      price: '',
      original_price: '',
      stock_quantity: 100,
      image_url: 'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=600&auto=format&fit=crop&q=80',
      description: 'Brand new high quality item on SmartCart.',
      is_prime: 1
    });
    setIsAddModalOpen(true);
  };

  const handleOpenEditModal = (p) => {
    setEditingProduct(p);
    setFormData({
      title: p.title,
      category: p.category,
      price: p.price,
      original_price: p.original_price || p.price,
      stock_quantity: p.stock_quantity,
      image_url: p.image_url,
      description: p.description,
      is_prime: p.is_prime ? 1 : 0
    });
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        title: formData.title,
        category: formData.category,
        price: parseFloat(formData.price),
        original_price: formData.original_price ? parseFloat(formData.original_price) : undefined,
        stock_quantity: parseInt(formData.stock_quantity),
        image_url: formData.image_url,
        description: formData.description,
        is_prime: formData.is_prime
      };

      if (editingProduct) {
        await updateProduct(editingProduct.id, payload);
        showToast(`Product "${formData.title}" updated successfully.`);
        setEditingProduct(null);
      } else {
        await createProduct(payload);
        showToast(`New product "${formData.title}" created successfully.`);
        setIsAddModalOpen(false);
      }
      fetchCatalog();
      fetchOverview();
    } catch (err) {
      console.error('Save error:', err);
      alert('Failed to save product. Check inputs.');
    }
  };

  const handleDelete = async (productId) => {
    if (window.confirm('Are you sure you want to remove this product from the active catalog?')) {
      try {
        await deleteProduct(productId);
        showToast('Product deactivated from catalog.');
        fetchCatalog();
        fetchOverview();
      } catch (err) {
        console.error(err);
      }
    }
  };

  const filteredProducts = products.filter((p) => {
    const matchesSearch =
      p.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (p.sku && p.sku.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesSearch;
  });

  const lowStockCount = overview.low_stock_count || products.filter((p) => p.stock_quantity < 35).length;
  const totalCatalogValue = products.reduce((acc, p) => acc + (p.price * p.stock_quantity), 0);

  return (
    <div className="pm-portal-page">
      {toastMessage && (
        <div className="cart-added-toast">
          <CheckCircle2 size={18} className="text-emerald" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Header Banner */}
      <div className="pm-header-card">
        <div className="pm-header-left">
          <div className="pm-badge">
            <ShieldCheck size={14} /> SmartCart Executive Administrator Console
          </div>
          <h1>Store Catalog & Executive Operations Console</h1>
          <p>
            Welcome, <strong>{storeUser?.full_name || storeUser?.username || 'Administrator'}</strong> ({storeUser?.role === 'admin' ? 'Super Administrator' : 'Product Manager'}).
            Full administrative control over store inventory, staff accounts, and live customer orders.
          </p>
        </div>
        <div className="pm-header-right">
          <button onClick={handleOpenAddModal} className="btn-add-product-action">
            <Plus size={16} />
            <span>Add New Product</span>
          </button>
        </div>
      </div>

      {/* KPI Stats Ribbon */}
      <div className="pm-kpi-ribbon">
        <div className="pm-stat-box">
          <span className="stat-label">TOTAL CATALOG SKUs</span>
          <strong className="stat-value">{products.length || overview.total_products}</strong>
          <span className="stat-desc">Active store items</span>
        </div>
        <div className="pm-stat-box alert">
          <span className="stat-label">LOW STOCK ALERTS</span>
          <strong className="stat-value text-danger">{lowStockCount}</strong>
          <span className="stat-desc">&lt; 35 units remaining</span>
          {lowStockCount > 0 && (
            <button
              type="button"
              onClick={handleBulkRestock}
              disabled={restocking}
              className="btn-bulk-restock"
              title="Instantly restock all low inventory items to 100 units"
            >
              <Zap size={13} />
              <span>{restocking ? 'Restocking...' : '⚡ Bulk Restock (100 Units)'}</span>
            </button>
          )}
        </div>
        <div className="pm-stat-box">
          <span className="stat-label">STORE REVENUE (CONFIRMED)</span>
          <strong className="stat-value">₹{overview.total_revenue?.toLocaleString() || '0'}</strong>
          <span className="stat-desc">{overview.total_orders} total orders recorded</span>
        </div>
        <div className="pm-stat-box">
          <span className="stat-label">UNIFIED ADMINISTRATOR</span>
          <strong className="stat-value" style={{ color: '#007185' }}>admin</strong>
          <span className="stat-desc">Unified login for ML Suite & Store</span>
        </div>
      </div>

      {/* Admin Navigation Tabs */}
      <div className="console-tabs-bar">
        <button
          type="button"
          onClick={() => setActiveTab('products')}
          className={`console-tab-btn ${activeTab === 'products' ? 'active' : ''}`}
        >
          <Package size={17} />
          <span>📦 Catalog & Stock Management</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('orders')}
          className={`console-tab-btn ${activeTab === 'orders' ? 'active' : ''}`}
        >
          <ShoppingBag size={17} />
          <span>📋 Live Store Orders Admin</span>
        </button>
      </div>

      {/* ======================================================== */}
      {/* TAB 1: PRODUCT CATALOG & STOCK                           */}
      {/* ======================================================== */}
      {activeTab === 'products' && (
        <>
          {/* Controls Bar */}
          <div className="pm-controls-bar">
            <div className="search-input-wrap">
              <Search size={16} className="search-icon-pm" />
              <input
                type="text"
                placeholder="Search products by title, SKU, or department..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            <div className="category-filter-wrap">
              <label>Department:</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                <option value="All">All Departments</option>
                <option value="Electronics">Electronics</option>
                <option value="Fashion">Fashion</option>
                <option value="Home & Kitchen">Home & Kitchen</option>
                <option value="Grocery">Grocery</option>
                <option value="Beauty">Beauty</option>
              </select>
            </div>
          </div>

          {/* Products Table Card */}
          <div className="pm-table-card">
            {loading ? (
              <div className="pm-loading-state">
                <p>Loading live store catalog & inventory...</p>
              </div>
            ) : filteredProducts.length === 0 ? (
              <div className="pm-empty-state">
                <p>No products found matching your search.</p>
              </div>
            ) : (
              <table className="pm-catalog-table">
                <thead>
                  <tr>
                    <th>Item Info</th>
                    <th>Category</th>
                    <th>Stock Level</th>
                    <th>Price (INR)</th>
                    <th>Prime</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredProducts.map((p) => {
                    const isLowStock = p.stock_quantity < 35;
                    return (
                      <tr key={p.id}>
                        <td>
                          <div className="item-cell-wrap">
                            <img src={p.image_url} alt={p.title} className="item-thumb-pm" />
                            <div>
                              <strong className="item-title-pm">{p.title}</strong>
                              <span className="item-sku-pm">SKU: {p.sku || `PROD-${p.id}`}</span>
                            </div>
                          </div>
                        </td>
                        <td>
                          <span className="cat-tag-pm">{p.category}</span>
                        </td>
                        <td>
                          <div className="stock-level-cell">
                            <span className={`stock-count ${isLowStock ? 'low-stock' : ''}`}>
                              {p.stock_quantity} in stock
                            </span>
                            {isLowStock && (
                              <span className="low-stock-chip">
                                <AlertTriangle size={11} /> Low Stock
                              </span>
                            )}
                          </div>
                        </td>
                        <td>
                          <div className="price-cell">
                            <strong className="selling-price">₹{p.price.toFixed(2)}</strong>
                            {p.original_price && p.original_price > p.price && (
                              <span className="orig-price">₹{p.original_price.toFixed(2)}</span>
                            )}
                          </div>
                        </td>
                        <td>
                          {p.is_prime ? (
                            <span className="prime-check-pm">✓ Prime</span>
                          ) : (
                            <span className="std-check-pm">Standard</span>
                          )}
                        </td>
                        <td>
                          <div className="action-buttons-cell">
                            <button
                              type="button"
                              onClick={() => handleOpenEditModal(p)}
                              className="btn-action-edit"
                              title="Edit Product"
                            >
                              <Edit2 size={14} />
                            </button>
                            <button
                              type="button"
                              onClick={() => handleDelete(p.id)}
                              className="btn-action-delete"
                              title="Deactivate Product"
                            >
                              <Trash2 size={14} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}

      {/* ======================================================== */}
      {/* TAB 2: LIVE STORE ORDERS ADMIN (ADMIN FUNCTION)          */}
      {/* ======================================================== */}
      {activeTab === 'orders' && (
        <div className="admin-card-section">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '14px' }}>
            <div>
              <div className="admin-card-title" style={{ margin: 0 }}>
                <ShoppingBag size={20} color="#ff9900" />
                <span>Store Orders Fulfillment & Status Management</span>
              </div>
              <p className="admin-card-desc" style={{ margin: '4px 0 0 0' }}>
                Real-time transactions feed. Admins can update fulfillment states (Confirmed → Shipped → Delivered) or cancel orders.
              </p>
            </div>

            <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
              {/* Search Order # or Customer ID */}
              <div style={{ position: 'relative', minWidth: '220px' }}>
                <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
                <input
                  type="text"
                  placeholder="Search Order # or Customer ID..."
                  value={orderSearchTerm}
                  onChange={(e) => {
                    setOrderSearchTerm(e.target.value);
                    setOrderPage(1);
                  }}
                  style={{
                    padding: '6px 10px 6px 30px',
                    borderRadius: '6px',
                    border: '1px solid #cbd5e1',
                    fontSize: '0.84rem',
                    width: '100%'
                  }}
                />
              </div>

              {/* Status Filter */}
              <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                <label style={{ fontSize: '0.82rem', fontWeight: 700, color: '#475569' }}>Status:</label>
                <select
                  value={orderStatusFilter}
                  onChange={(e) => {
                    setOrderStatusFilter(e.target.value);
                    setOrderPage(1);
                  }}
                  style={{ padding: '6px 10px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '0.84rem', fontWeight: 600 }}
                >
                  <option value="all">All Statuses</option>
                  <option value="Confirmed">Confirmed</option>
                  <option value="In Transit">In Transit</option>
                  <option value="Processing">Processing</option>
                  <option value="Shipped">Shipped</option>
                  <option value="Delivered">Delivered</option>
                  <option value="Cancelled">Cancelled</option>
                </select>
              </div>

              {/* Rows Per Page */}
              <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                <label style={{ fontSize: '0.82rem', fontWeight: 700, color: '#475569' }}>Show:</label>
                <select
                  value={orderLimit}
                  onChange={(e) => {
                    setOrderLimit(Number(e.target.value));
                    setOrderPage(1);
                  }}
                  style={{ padding: '6px 8px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '0.84rem', fontWeight: 600 }}
                >
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                  <option value={1000}>All Orders</option>
                </select>
              </div>

              {/* Refresh Button */}
              <button
                type="button"
                onClick={() => fetchOrders(orderPage, orderLimit, orderSearchTerm, orderStatusFilter)}
                title="Refresh orders list"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '6px 10px',
                  borderRadius: '6px',
                  border: '1px solid #cbd5e1',
                  background: '#f8fafc',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                <RefreshCw size={13} />
                <span>Refresh</span>
              </button>
            </div>
          </div>

          {loadingOrders ? (
            <p style={{ color: '#565959', padding: '20px 0' }}>Loading orders feed...</p>
          ) : ordersList.length === 0 ? (
            <p style={{ color: '#565959', padding: '20px 0' }}>No orders found for the selected status filter.</p>
          ) : (
            <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', overflowX: 'auto' }}>
              <table className="admin-data-table">
                <thead>
                  <tr>
                    <th>Order #</th>
                    <th>Customer ID</th>
                    <th>Date</th>
                    <th>Amount</th>
                    <th>Payment</th>
                    <th>Status</th>
                    <th>Admin Status Override</th>
                  </tr>
                </thead>
                <tbody>
                  {ordersList.map((ord) => {
                    const statusLower = (ord.order_status || 'confirmed').toLowerCase();
                    return (
                      <tr key={ord.order_id}>
                        <td>
                          <strong>{ord.order_number}</strong>
                        </td>
                        <td>
                          <span style={{ color: '#007185', fontWeight: 700 }}>
                            {ord.customer?.source_customer_id || `ID: ${ord.customer?.id}`}
                          </span>
                        </td>
                        <td>
                          <span style={{ fontSize: '0.82rem', color: '#565959' }}>
                            {ord.order_date ? ord.order_date.split('T')[0] : 'Today'}
                          </span>
                        </td>
                        <td>
                          <strong>₹{ord.order_amount?.toFixed(2)}</strong>
                        </td>
                        <td>
                          <span style={{ fontSize: '0.82rem' }}>{ord.payment_mode}</span>
                        </td>
                        <td>
                          <span className={`status-badge ${statusLower}`}>
                            {ord.order_status}
                          </span>
                        </td>
                        <td>
                          <select
                            value={ord.order_status}
                            onChange={(e) => handleOrderStatusChange(ord.order_id, e.target.value)}
                            style={{
                              padding: '4px 8px',
                              borderRadius: '4px',
                              border: '1px solid #cbd5e1',
                              fontSize: '0.82rem',
                              fontWeight: 600,
                              background: '#f8fafc'
                            }}
                          >
                            <option value="Confirmed">Confirmed</option>
                            <option value="Processing">Processing</option>
                            <option value="Shipped">Shipped</option>
                            <option value="Delivered">Delivered</option>
                            <option value="Cancelled">Cancelled</option>
                          </select>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>

              {/* Pagination Controls */}
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '12px 16px',
                borderTop: '1px solid #e2e8f0',
                background: '#f8fafc',
                flexWrap: 'wrap',
                gap: '10px'
              }}>
                <span style={{ fontSize: '0.84rem', color: '#475569', fontWeight: 600 }}>
                  Showing {ordersList.length > 0 ? (orderPage - 1) * orderLimit + 1 : 0} to{' '}
                  {Math.min(orderPage * orderLimit, orderTotalCount)} of {orderTotalCount} total orders
                </span>

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <button
                    type="button"
                    disabled={orderPage <= 1 || loadingOrders}
                    onClick={() => setOrderPage((p) => Math.max(1, p - 1))}
                    style={{
                      padding: '5px 12px',
                      borderRadius: '6px',
                      border: '1px solid #cbd5e1',
                      background: orderPage <= 1 ? '#f1f5f9' : '#ffffff',
                      color: orderPage <= 1 ? '#94a3b8' : '#0f172a',
                      cursor: orderPage <= 1 ? 'not-allowed' : 'pointer',
                      fontWeight: 600,
                      fontSize: '0.82rem'
                    }}
                  >
                    ← Previous
                  </button>

                  <span style={{ fontSize: '0.84rem', fontWeight: 700, color: '#334155', padding: '0 6px' }}>
                    Page {orderPage} of {orderTotalPages || 1}
                  </span>

                  <button
                    type="button"
                    disabled={orderPage >= orderTotalPages || loadingOrders}
                    onClick={() => setOrderPage((p) => Math.min(orderTotalPages, p + 1))}
                    style={{
                      padding: '5px 12px',
                      borderRadius: '6px',
                      border: '1px solid #cbd5e1',
                      background: orderPage >= orderTotalPages ? '#f1f5f9' : '#ffffff',
                      color: orderPage >= orderTotalPages ? '#94a3b8' : '#0f172a',
                      cursor: orderPage >= orderTotalPages ? 'not-allowed' : 'pointer',
                      fontWeight: 600,
                      fontSize: '0.82rem'
                    }}
                  >
                    Next →
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Add / Edit Modal */}
      {(isAddModalOpen || editingProduct) && (
        <div className="modal-overlay">
          <div className="modal-dialog">
            <div className="modal-header">
              <h3>{editingProduct ? `Edit Product: ${editingProduct.sku}` : 'Add New Catalog Product'}</h3>
              <button
                type="button"
                className="modal-close-btn"
                onClick={() => { setIsAddModalOpen(false); setEditingProduct(null); }}
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleFormSubmit} className="modal-body-form">
              <div className="form-group">
                <label>Product Title:</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                />
              </div>

              <div className="form-row-2">
                <div className="form-group">
                  <label>Department Category:</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  >
                    <option value="Electronics">Electronics</option>
                    <option value="Fashion">Fashion</option>
                    <option value="Home & Kitchen">Home & Kitchen</option>
                    <option value="Grocery">Grocery</option>
                    <option value="Beauty">Beauty</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Stock Quantity:</label>
                  <input
                    type="number"
                    min="0"
                    value={formData.stock_quantity}
                    onChange={(e) => setFormData({ ...formData, stock_quantity: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="form-row-2">
                <div className="form-group">
                  <label>Selling Price (INR ₹):</label>
                  <input
                    type="number"
                    step="0.01"
                    min="1"
                    value={formData.price}
                    onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Original MRP (INR ₹):</label>
                  <input
                    type="number"
                    step="0.01"
                    min="1"
                    value={formData.original_price}
                    onChange={(e) => setFormData({ ...formData, original_price: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Image URL:</label>
                <input
                  type="url"
                  value={formData.image_url}
                  onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Description:</label>
                <textarea
                  rows={3}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input
                    type="checkbox"
                    checked={formData.is_prime === 1}
                    onChange={(e) => setFormData({ ...formData, is_prime: e.target.checked ? 1 : 0 })}
                  />
                  <span>Amazon Prime Eligible (Free Fast Delivery)</span>
                </label>
              </div>

              <div className="modal-footer-actions">
                <button
                  type="button"
                  onClick={() => { setIsAddModalOpen(false); setEditingProduct(null); }}
                  className="btn-cancel"
                >
                  Cancel
                </button>
                <button type="submit" className="btn-save">
                  {editingProduct ? 'Save Product Changes' : 'Create Product'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PMProductManager;
