import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, NavLink } from 'react-router-dom';
import {
  ShoppingBag,
  ArrowRight,
  LogOut,
  Menu,
  X,
  BarChart3,
  UploadCloud,
  Users,
  TrendingUp
} from 'lucide-react';
import Sidebar from './Sidebar';
import { useStore } from '../context/StoreContext';
import './Layout.css';

const Layout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { loginDirectly } = useStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Close mobile drawer on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  // Close drawer on Escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && mobileMenuOpen) {
        setMobileMenuOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [mobileMenuOpen]);

  const handleSwitchToStoreAdmin = (e) => {
    e.preventDefault();
    setMobileMenuOpen(false);
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

  const handleLogout = () => {
    setMobileMenuOpen(false);
    localStorage.removeItem('user');
    localStorage.removeItem('smartcart_user');
    navigate('/login');
  };

  return (
    <div className="app-container">
      {/* Mobile Drawer Backdrop */}
      {mobileMenuOpen && (
        <div
          className="sidebar-backdrop"
          onClick={() => setMobileMenuOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Responsive Sidebar (Drawer on mobile, fixed on desktop) */}
      <Sidebar
        isOpen={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
      />

      <div className="main-wrapper">
        <header className="topbar">
          <div className="topbar-left">
            {/* Mobile Hamburger Toggle Button */}
            <button
              type="button"
              className="mobile-hamburger-btn"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label={mobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
              aria-expanded={mobileMenuOpen}
            >
              {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
            </button>

            <div className="amazon-header-brand">
              <span className="amazon-logo-dark">amazon</span>
              <span className="amazon-smile-dark"></span>
              <span className="platform-tag">Analytics</span>
            </div>

            <div className="topbar-divider"></div>

            <div className="topbar-title">
              <h1>Customer Churn & Retention Analytics Platform</h1>
              <p>Amazon Seller Decision Support & Predictive Machine Learning</p>
            </div>
          </div>

          <div className="topbar-right">
            <button
              type="button"
              onClick={handleSwitchToStoreAdmin}
              className="topbar-store-btn"
              title="Directly login to SmartCart E-Commerce with Admin Functions"
            >
              <ShoppingBag size={15} />
              <span className="topbar-btn-text">SmartCart Store (Admin)</span>
              <ArrowRight size={14} className="hide-on-mobile-sm" />
            </button>

            <button
              type="button"
              onClick={handleLogout}
              className="topbar-logout-btn"
              title="Sign out of ML Platform"
            >
              <LogOut size={15} />
              <span className="topbar-btn-text">Sign Out</span>
            </button>
          </div>
        </header>

        <main className="content-area">{children}</main>

        {/* Mobile Bottom Navigation Bar (< 768px) */}
        <nav className="mobile-bottom-nav" aria-label="Quick Navigation">
          <NavLink
            to="/dashboard"
            className={({ isActive }) => (isActive ? 'bottom-nav-item active' : 'bottom-nav-item')}
          >
            <BarChart3 size={19} />
            <span>Dashboard</span>
          </NavLink>

          <NavLink
            to="/upload"
            className={({ isActive }) => (isActive ? 'bottom-nav-item active' : 'bottom-nav-item')}
          >
            <UploadCloud size={19} />
            <span>Upload</span>
          </NavLink>

          <NavLink
            to="/churn-prediction"
            className={({ isActive }) => (isActive ? 'bottom-nav-item active' : 'bottom-nav-item')}
          >
            <Users size={19} />
            <span>Churn</span>
          </NavLink>

          <NavLink
            to="/sales-forecast"
            className={({ isActive }) => (isActive ? 'bottom-nav-item active' : 'bottom-nav-item')}
          >
            <TrendingUp size={19} />
            <span>Forecast</span>
          </NavLink>
        </nav>
      </div>
    </div>
  );
};

export default Layout;
