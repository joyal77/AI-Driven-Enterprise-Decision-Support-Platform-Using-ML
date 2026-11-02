import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Eye, EyeOff, AlertCircle, Info } from 'lucide-react';
import { useStore } from '../../context/StoreContext';
import { loginUser } from '../../services/api';
import { storeLogin } from '../../services/storeApi';
import './StoreLogin.css';

const StoreLogin = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { loginAsRole, loginDirectly } = useStore();

  // Selected tab: 'customer' | 'admin'
  const [activeTab, setActiveTab] = useState(() => {
    return searchParams.get('tab') === 'admin' ? 'admin' : 'customer';
  });

  // Customer credentials
  const [custUsername, setCustUsername] = useState('AMZ_PRED1_1001');
  const [custPassword, setCustPassword] = useState('customer123');
  const [showCustPassword, setShowCustPassword] = useState(false);

  // Admin credentials
  const [adminUsername, setAdminUsername] = useState('');
  const [adminPassword, setAdminPassword] = useState('');
  const [showAdminPassword, setShowAdminPassword] = useState(false);

  // States
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [infoMsg, setInfoMsg] = useState('');

  // Handle URL query parameters (e.g. ?tab=admin or ?error=admin_required)
  useEffect(() => {
    const tabParam = searchParams.get('tab');
    if (tabParam === 'admin') {
      setActiveTab('admin');
    } else if (tabParam === 'customer') {
      setActiveTab('customer');
    }

    if (searchParams.get('error') === 'admin_required') {
      setActiveTab('admin');
      setErrorMsg('Administrator privileges required to access the ML platform.');
    }
  }, [searchParams]);

  // Customer Form Submit -> Redirects to /store
  const handleCustomerSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;
    setErrorMsg('');
    setInfoMsg('');
    setLoading(true);

    try {
      const user = await loginAsRole(custUsername.trim(), custPassword.trim());

      // If user provided admin credentials, route to dashboard
      if (user.role === 'admin') {
        localStorage.setItem(
          'user',
          JSON.stringify({
            id: user.id || 1,
            email: user.username,
            name: user.full_name || 'Store Administrator',
            role: 'admin'
          })
        );
        navigate('/dashboard');
      } else {
        // Standard customer: directly to storefront
        navigate('/store');
      }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Invalid Customer ID or password.';
      setErrorMsg(msg);
    } finally {
      setLoading(false);
    }
  };

  // Admin Form Submit -> Redirects to /dashboard
  const handleAdminSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;
    setErrorMsg('');
    setInfoMsg('');
    setLoading(true);

    try {
      const mlData = await loginUser(adminUsername.trim(), adminPassword.trim());

      if (!mlData.success || !mlData.user || mlData.user.role !== 'admin') {
        throw new Error(mlData.message || 'Access Denied: Administrator account required.');
      }

      // Synchronize session across store context
      try {
        const storeData = await storeLogin(adminUsername.trim(), adminPassword.trim());
        if (storeData.success && storeData.user) {
          loginDirectly(storeData.user);
        }
      } catch {
        loginDirectly({
          id: mlData.user.id || 1,
          username: adminUsername.trim(),
          role: 'admin',
          full_name: mlData.user.name || 'Store Administrator'
        });
      }

      // Store unified admin credentials for ProtectedRoute
      localStorage.setItem('user', JSON.stringify(mlData.user));
      navigate('/dashboard');
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        err.message ||
        'Invalid administrator username or password.';
      setErrorMsg(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = (role) => {
    if (role === 'customer') {
      setInfoMsg('For demo access, customer accounts use default password: customer123');
    } else {
      setInfoMsg('For demo access, administrator account uses default password: admin123');
    }
  };

  const handleFillDemoAdmin = (e) => {
    e.preventDefault();
    setAdminUsername('admin');
    setAdminPassword('admin123');
    setErrorMsg('');
    setInfoMsg('');
  };

  return (
    <div className="minimal-login-wrapper">
      <div className="minimal-login-card">
        {/* Brand Header */}
        <div className="login-brand-header">
          <h1 className="login-brand-title">SmartCart</h1>
          <p className="login-brand-subtitle">Sign in to continue</p>
        </div>

        {/* Tab Switcher */}
        <div className="login-tab-switcher">
          <button
            type="button"
            className={`login-tab-btn ${activeTab === 'customer' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('customer');
              setErrorMsg('');
              setInfoMsg('');
            }}
          >
            Customer Login
          </button>
          <button
            type="button"
            className={`login-tab-btn ${activeTab === 'admin' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('admin');
              setErrorMsg('');
              setInfoMsg('');
            }}
          >
            Admin Login
          </button>
        </div>

        {/* Validation / Alert Messages */}
        {errorMsg && (
          <div className="login-alert-box error" role="alert">
            <AlertCircle size={15} className="alert-icon" />
            <span>{errorMsg}</span>
          </div>
        )}

        {infoMsg && (
          <div className="login-alert-box info" role="status">
            <Info size={15} className="alert-icon" />
            <span>{infoMsg}</span>
          </div>
        )}

        {/* Customer Login Form */}
        {activeTab === 'customer' && (
          <form onSubmit={handleCustomerSubmit} className="login-form">
            <div className="login-form-group">
              <label htmlFor="cust-id" className="login-label">
                Customer ID, email, or username
              </label>
              <input
                id="cust-id"
                type="text"
                className="login-input"
                value={custUsername}
                onChange={(e) => setCustUsername(e.target.value)}
                placeholder="AMZ_PRED1_1001"
                required
                autoComplete="username"
                autoFocus
              />
              <span className="login-helper-text">
                Demo customer: <code>AMZ_PRED1_1001</code>
              </span>
            </div>

            <div className="login-form-group">
              <label htmlFor="cust-password" className="login-label">
                Password
              </label>
              <div className="password-input-wrapper">
                <input
                  id="cust-password"
                  type={showCustPassword ? 'text' : 'password'}
                  className="login-input password-input"
                  value={custPassword}
                  onChange={(e) => setCustPassword(e.target.value)}
                  placeholder="Enter password"
                  required
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  className="password-toggle-btn"
                  onClick={() => setShowCustPassword(!showCustPassword)}
                  aria-label={showCustPassword ? 'Hide password' : 'Show password'}
                >
                  {showCustPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <div className="login-options-row">
              <button
                type="button"
                className="btn-forgot-password"
                onClick={() => handleForgotPassword('customer')}
              >
                Forgot Password?
              </button>
            </div>

            <button
              type="submit"
              className="btn-signin-primary"
              disabled={loading}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        )}

        {/* Admin Login Form */}
        {activeTab === 'admin' && (
          <form onSubmit={handleAdminSubmit} className="login-form">
            <div className="login-form-group">
              <label htmlFor="admin-id" className="login-label">
                Username or email
              </label>
              <input
                id="admin-id"
                type="text"
                className="login-input"
                value={adminUsername}
                onChange={(e) => setAdminUsername(e.target.value)}
                placeholder="admin"
                required
                autoComplete="username"
                autoFocus
              />
            </div>

            <div className="login-form-group">
              <label htmlFor="admin-password" className="login-label">
                Password
              </label>
              <div className="password-input-wrapper">
                <input
                  id="admin-password"
                  type={showAdminPassword ? 'text' : 'password'}
                  className="login-input password-input"
                  value={adminPassword}
                  onChange={(e) => setAdminPassword(e.target.value)}
                  placeholder="Enter password"
                  required
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  className="password-toggle-btn"
                  onClick={() => setShowAdminPassword(!showAdminPassword)}
                  aria-label={showAdminPassword ? 'Hide password' : 'Show password'}
                >
                  {showAdminPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <div className="login-options-row">
              <button
                type="button"
                className="btn-forgot-password"
                onClick={() => handleForgotPassword('admin')}
              >
                Forgot Password?
              </button>

              <button
                type="button"
                className="btn-demo-account-link"
                onClick={handleFillDemoAdmin}
              >
                Use Demo Account
              </button>
            </div>

            <button
              type="submit"
              className="btn-signin-primary"
              disabled={loading}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        )}
      </div>

      {/* Minimal Footer */}
      <footer className="minimal-login-footer">
        <p>© 2026 SmartCart</p>
      </footer>
    </div>
  );
};

export default StoreLogin;
