import React from 'react';
import { NavLink, useNavigate, Link } from 'react-router-dom';
import {
  BarChart3,
  UploadCloud,
  Users,
  TrendingUp,
  ShoppingBag,
  Package,
  Layers,
  ArrowRight,
  LogOut,
  Sparkles,
  X
} from 'lucide-react';
import { useStore } from '../context/StoreContext';

const Sidebar = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const { loginDirectly } = useStore();

  const handleLogout = () => {
    onClose?.();
    localStorage.removeItem('user');
    localStorage.removeItem('smartcart_user');
    navigate('/login');
  };

  const handleSwitchToStoreAdmin = (e) => {
    e.preventDefault();
    onClose?.();
    // Directly log into the admin account of the e-commerce website with admin functions
    const adminUser = {
      id: 1,
      username: 'admin',
      role: 'admin',
      full_name: 'SmartCart Platform Administrator'
    };
    loginDirectly(adminUser);
    localStorage.setItem('smartcart_user', JSON.stringify(adminUser));
    navigate('/store/manage-products');
  };

  const handleNavClick = () => {
    onClose?.();
  };

  return (
    <aside className={`sidebar ${isOpen ? 'mobile-open' : ''}`} aria-label="Sidebar Navigation">
      <div>
        {/* Brand Header */}
        <div className="sidebar-brand">
          <div className="brand-header-row">
            <div className="brand-logo-container">
              <span className="amazon-logo-text">amazon</span>
              <span className="amazon-smile-curve"></span>
              <span className="brand-badge">seller central</span>
            </div>
            <button
              type="button"
              className="sidebar-close-btn"
              onClick={onClose}
              aria-label="Close navigation menu"
            >
              <X size={20} />
            </button>
          </div>
          <div className="brand-subtext">
            Sales Forecast & Churn Intelligence
          </div>
        </div>

        {/* Live Storefront Quick-Jump Banner */}
        <div style={{ marginTop: '14px', marginBottom: '8px' }}>
          <button
            type="button"
            onClick={handleSwitchToStoreAdmin}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              background: 'linear-gradient(135deg, #ff9900 0%, #ffad33 100%)',
              color: '#0f1111',
              padding: '9px 12px',
              borderRadius: '7px',
              border: 'none',
              cursor: 'pointer',
              fontWeight: '700',
              fontSize: '0.82rem',
              boxShadow: '0 2px 8px rgba(255, 153, 0, 0.35)',
              transition: 'transform 0.15s ease',
              fontFamily: 'inherit'
            }}
            title="Directly login to SmartCart E-Commerce with Admin Functions"
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <ShoppingBag size={15} /> SmartCart Store (Admin)
            </span>
            <ArrowRight size={14} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav">
          <div className="nav-group-label">DECISION PLATFORM (ML)</div>
          <NavLink
            to="/dashboard"
            onClick={handleNavClick}
            className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
          >
            <span className="nav-icon">📊</span>
            <span className="nav-label">Executive Dashboard</span>
          </NavLink>

          <NavLink
            to="/upload"
            onClick={handleNavClick}
            className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
          >
            <span className="nav-icon">📦</span>
            <span className="nav-label">Upload Dataset</span>
          </NavLink>

          <NavLink
            to="/churn-prediction"
            onClick={handleNavClick}
            className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
          >
            <span className="nav-icon">👥</span>
            <span className="nav-label">Customer Churn Prediction</span>
          </NavLink>

          <NavLink
            to="/sales-forecast"
            onClick={handleNavClick}
            className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
          >
            <span className="nav-icon">📈</span>
            <span className="nav-label">Sales Forecast</span>
          </NavLink>
        </nav>
      </div>

      <div className="sidebar-footer">
        <div className="user-info">
          <div className="avatar">A</div>
          <div className="user-details">
            <span className="user-name">Amazon Seller Admin</span>
            <span className="user-role">SmartCart Unified Platform</span>
          </div>
        </div>
        <button onClick={handleLogout} className="sidebar-signout-btn" title="Sign out of ML Platform">
          <LogOut size={14} />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
