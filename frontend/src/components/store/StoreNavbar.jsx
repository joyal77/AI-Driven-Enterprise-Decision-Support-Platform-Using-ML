import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import {
  Search,
  ShoppingCart,
  MapPin,
  User,
  ChevronDown,
  Package,
  Bell,
  Tag,
  Zap,
  LogOut,
  Menu,
  X
} from 'lucide-react';
import { useStore } from '../../context/StoreContext';
import './StoreNavbar.css';

const StoreNavbar = () => {
  const {
    storeUser,
    cartCount = 0,
    logoutStore,
    activeVouchers = [],
    hasExpressShipping = false,
    unreadNotificationsCount = 0
  } = useStore();

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [showAccountDropdown, setShowAccountDropdown] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();
  const accountDropdownRef = useRef(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (accountDropdownRef.current && !accountDropdownRef.current.contains(e.target)) {
        setShowAccountDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close menus on route change
  useEffect(() => {
    setShowAccountDropdown(false);
    setMobileMenuOpen(false);
  }, [location.pathname, location.search]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchTerm.trim() || selectedCategory !== 'All') {
      const params = new URLSearchParams();
      if (searchTerm.trim()) params.set('search', searchTerm.trim());
      if (selectedCategory !== 'All') params.set('category', selectedCategory);
      navigate(`/store/catalog?${params.toString()}`);
    } else {
      navigate('/store/catalog');
    }
  };

  const handleStoreLogout = () => {
    logoutStore();
    setShowAccountDropdown(false);
    navigate('/store/login');
  };

  const customerName = storeUser?.full_name
    ? storeUser.full_name.replace(/^Customer\s+/i, '').split(' ')[0]
    : storeUser?.username || 'Customer';

  const customerLocation = storeUser?.city
    ? `${storeUser.city}${storeUser.postal_code ? ` ${storeUser.postal_code}` : ''}`
    : 'Bengaluru 560001';

  const hasDiscountCoupon = Boolean(storeUser && activeVouchers && activeVouchers.length > 0);
  const isEligibleFreeDelivery = Boolean(storeUser && hasExpressShipping);

  return (
    <header className="smartcart-header-wrapper">
      {/* Top Navigation Bar:
          SmartCart | Search Products... | Deliver to... | Account ▼ | Cart (count) | Sign Out */}
      <div className="smartcart-top-bar">
        {/* Brand Logo */}
        <Link to="/store" className="smartcart-brand" title="SmartCart E-Commerce Home">
          <div className="brand-logo-group">
            <span className="brand-smart">smart</span>
            <span className="brand-cart">cart</span>
            <span className="brand-smile"></span>
          </div>
          <span className="brand-domain">.in</span>
        </Link>

        {/* Product Search Bar */}
        <form onSubmit={handleSearchSubmit} className="smartcart-search-bar">
          <select
            className="search-category-select"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            aria-label="Filter search by department"
          >
            <option value="All">All Departments</option>
            <option value="Electronics">Electronics</option>
            <option value="Fashion">Fashion</option>
            <option value="Home & Kitchen">Home & Kitchen</option>
            <option value="Grocery">Grocery</option>
            <option value="Beauty">Beauty</option>
          </select>

          <input
            type="text"
            className="search-input"
            placeholder="Search Products..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            aria-label="Search products"
          />

          <button type="submit" className="search-submit-btn" title="Search SmartCart">
            <Search size={18} />
          </button>
        </form>

        {/* Deliver to Location (Displayed once in header) */}
        <div
          className="nav-delivery-location"
          title={`Deliver to ${customerName}, ${customerLocation}`}
        >
          <MapPin size={18} className="loc-pin-icon" />
          <div className="loc-text-col">
            <span className="loc-label-line">
              Deliver to {storeUser ? customerName : 'Bengaluru'}
            </span>
            <span className="loc-city-line">{customerLocation}</span>
          </div>
        </div>

        {/* Customer Account Dropdown */}
        <div className="nav-account-wrapper" ref={accountDropdownRef}>
          <button
            type="button"
            className={`nav-account-btn ${showAccountDropdown ? 'active' : ''}`}
            onClick={() => setShowAccountDropdown((prev) => !prev)}
            aria-expanded={showAccountDropdown}
            aria-label="Customer Account Dropdown"
          >
            <User size={18} className="account-user-icon" />
            <div className="account-btn-text">
              <span className="account-greeting">
                Hello, {storeUser ? customerName : 'Sign in'}
              </span>
              <span className="account-label">
                <span>Account</span>
                <ChevronDown
                  size={13}
                  className={`account-chevron ${showAccountDropdown ? 'rotated' : ''}`}
                />
              </span>
            </div>
          </button>

          {showAccountDropdown && (
            <div className="account-dropdown-card">
              {/* Account summary header */}
              <div className="account-card-header">
                <div className="account-user-info">
                  <div className="account-name">
                    {storeUser?.full_name || storeUser?.username || 'Guest Shopper'}
                  </div>
                  {storeUser?.username && (
                    <div className="account-id">
                      Customer ID: <strong>{storeUser.username}</strong>
                    </div>
                  )}
                </div>
              </div>

              <div className="account-dropdown-divider" />

              {/* Required Menu Items:
                  - My Account
                  - My Orders
                  - Messages / Notifications
                  - Available Offers
                  - Sign Out */}
              <div className="account-menu-list">
                <Link
                  to="/store"
                  className="account-menu-item"
                  onClick={() => setShowAccountDropdown(false)}
                >
                  <User size={15} />
                  <span>My Account</span>
                </Link>

                <Link
                  to="/store/my-orders"
                  className="account-menu-item"
                  onClick={() => setShowAccountDropdown(false)}
                >
                  <Package size={15} />
                  <span>My Orders</span>
                </Link>

                <Link
                  to="/store/notifications"
                  className="account-menu-item"
                  onClick={() => setShowAccountDropdown(false)}
                >
                  <Bell size={15} />
                  <span>Messages / Notifications</span>
                  {unreadNotificationsCount > 0 && (
                    <span className="menu-unread-badge">{unreadNotificationsCount}</span>
                  )}
                </Link>

                <Link
                  to="/store/cart"
                  className="account-menu-item"
                  onClick={() => setShowAccountDropdown(false)}
                >
                  <Tag size={15} />
                  <span>Available Offers</span>
                  {activeVouchers && activeVouchers.length > 0 && (
                    <span className="menu-offers-badge">{activeVouchers.length}</span>
                  )}
                </Link>
              </div>

              <div className="account-dropdown-divider" />

              {/* Sign Out Option */}
              {storeUser ? (
                <button
                  type="button"
                  className="account-logout-btn"
                  onClick={handleStoreLogout}
                >
                  <LogOut size={15} />
                  <span>Sign Out</span>
                </button>
              ) : (
                <Link
                  to="/store/login"
                  className="account-signin-btn"
                  onClick={() => setShowAccountDropdown(false)}
                >
                  <LogOut size={15} />
                  <span>Sign In</span>
                </Link>
              )}
            </div>
          )}
        </div>

        {/* Shopping Cart Button with Current Item Count */}
        <Link to="/store/cart" className="nav-cart-btn" title="Shopping Cart">
          <div className="cart-icon-wrapper">
            <ShoppingCart size={22} />
            <span className="cart-item-count">{cartCount || 0}</span>
          </div>
          <span className="cart-btn-label">Cart</span>
        </Link>

        {/* Single Sign Out Option in Top Bar */}
        {storeUser ? (
          <button
            type="button"
            onClick={handleStoreLogout}
            className="nav-top-signout-btn"
            title="Sign Out of SmartCart"
          >
            <LogOut size={15} />
            <span>Sign Out</span>
          </button>
        ) : (
          <Link to="/store/login" className="nav-top-signin-btn">
            Sign In
          </Link>
        )}
      </div>

      {/* Second Navigation Bar:
          All Departments | Electronics | Fashion | Home & Kitchen | Grocery | Beauty
          Optional right-side badges: 10% OFF | Free Delivery */}
      <nav className="smartcart-second-nav">
        {/* Mobile Hamburger toggle */}
        <button
          type="button"
          className="mobile-departments-toggle"
          onClick={() => setMobileMenuOpen((prev) => !prev)}
          aria-expanded={mobileMenuOpen}
          aria-label="Toggle Departments Menu"
        >
          {mobileMenuOpen ? <X size={17} /> : <Menu size={17} />}
          <span>Departments</span>
          <ChevronDown size={13} className={`toggle-chevron ${mobileMenuOpen ? 'rotated' : ''}`} />
        </button>

        {/* Department Links (Desktop row & Mobile expandable) */}
        <div className={`second-nav-departments ${mobileMenuOpen ? 'mobile-open' : ''}`}>
          <Link
            to="/store/catalog"
            className="department-link"
            onClick={() => setMobileMenuOpen(false)}
          >
            <span className="dept-all-icon">☰</span>
            <span>All Departments</span>
          </Link>
          <Link
            to="/store/catalog?category=Electronics"
            className="department-link"
            onClick={() => setMobileMenuOpen(false)}
          >
            Electronics
          </Link>
          <Link
            to="/store/catalog?category=Fashion"
            className="department-link"
            onClick={() => setMobileMenuOpen(false)}
          >
            Fashion
          </Link>
          <Link
            to="/store/catalog?category=Home+%26+Kitchen"
            className="department-link"
            onClick={() => setMobileMenuOpen(false)}
          >
            Home & Kitchen
          </Link>
          <Link
            to="/store/catalog?category=Grocery"
            className="department-link"
            onClick={() => setMobileMenuOpen(false)}
          >
            Grocery
          </Link>
          <Link
            to="/store/catalog?category=Beauty"
            className="department-link"
            onClick={() => setMobileMenuOpen(false)}
          >
            Beauty
          </Link>
        </div>

        {/* Optional Right-Side Badges (Shown ONLY if customer is authenticated & eligible) */}
        {storeUser && (hasDiscountCoupon || isEligibleFreeDelivery) && (
          <div className="second-nav-perks">
            {hasDiscountCoupon && (
              <Link
                to="/store/cart"
                className="perk-badge perk-coupon"
                title={`Active Voucher: ${activeVouchers[0].code}`}
              >
                <Tag size={12} />
                <span>
                  {activeVouchers[0].discount_pct
                    ? `${activeVouchers[0].discount_pct}% OFF`
                    : activeVouchers[0].discount_amount
                    ? `₹${activeVouchers[0].discount_amount} OFF`
                    : '10% OFF'}
                </span>
              </Link>
            )}

            {isEligibleFreeDelivery && (
              <span
                className="perk-badge perk-delivery"
                title="Free Express Priority Shipping active on your account"
              >
                <Zap size={12} />
                <span>Free Delivery</span>
              </span>
            )}
          </div>
        )}
      </nav>
    </header>
  );
};

export default StoreNavbar;
