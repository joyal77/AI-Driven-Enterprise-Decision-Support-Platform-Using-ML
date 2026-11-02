import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShoppingBag, ArrowRight, LogOut } from 'lucide-react';
import Sidebar from './Sidebar';
import { useStore } from '../context/StoreContext';
import './Layout.css';

const Layout = ({ children }) => {
  const navigate = useNavigate();
  const { loginDirectly } = useStore();

  const handleSwitchToStoreAdmin = (e) => {
    e.preventDefault();
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
    localStorage.removeItem('user');
    localStorage.removeItem('smartcart_user');
    navigate('/login');
  };

  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-wrapper">
        <header className="topbar">
          <div className="topbar-left">
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
              <span>Switch to SmartCart Store (Admin)</span>
              <ArrowRight size={14} />
            </button>

            <button
              type="button"
              onClick={handleLogout}
              className="topbar-logout-btn"
              title="Sign out of ML Platform"
            >
              <LogOut size={15} />
              <span>Sign Out</span>
            </button>
          </div>
        </header>

        <main className="content-area">{children}</main>
      </div>
    </div>
  );
};

export default Layout;
