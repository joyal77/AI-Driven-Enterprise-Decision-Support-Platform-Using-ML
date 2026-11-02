import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../../context/StoreContext';
import './CustomerNotifications.css';

const CustomerNotifications = () => {
  const {
    notifications = [],
    unreadNotificationsCount = 0,
    markNotificationRead,
    markAllNotificationsRead,
    activeVouchers = [],
    setAppliedVoucher
  } = useStore();

  const [filter, setFilter] = useState('all'); // 'all' | 'unread'
  const navigate = useNavigate();

  const unreadList = notifications.filter((n) => !n.is_read);
  const displayedNotifications = filter === 'unread' ? unreadList : notifications;

  const isCouponUsed = (n) => {
    if (!n.coupon_code) return false;
    if (n.is_coupon_used) return true;
    const code = n.coupon_code.trim().toUpperCase();
    const isActive = (activeVouchers || []).some(
      (v) => (v.code || '').toUpperCase() === code
    );
    return !isActive;
  };

  const handleApplyOffer = (n, e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }

    if (isCouponUsed(n)) return;

    if (!n.is_read) {
      markNotificationRead(n.id);
    }

    const code = (n.coupon_code || '').trim().toUpperCase();
    const matchedVoucher = (activeVouchers || []).find(
      (v) => v.code && v.code.toUpperCase() === code
    );

    const voucherToApply = matchedVoucher || {
      code: code,
      title: n.title || 'Promotional Offer',
      perk_type: n.perk_type || 'discount_voucher',
      discount_pct: n.perk_value && n.perk_value <= 50 ? n.perk_value : (code.includes('15') ? 15 : (code.includes('5') ? 5 : 10)),
      free_shipping: Boolean(
        n.perk_type === 'express_shipping' ||
        ['RECOVER', 'SPEED', 'FLEX'].some((pfx) => code.startsWith(pfx))
      ),
      discount_amount: n.perk_value && n.perk_value > 50 ? n.perk_value : 0
    };

    setAppliedVoucher(voucherToApply);
    navigate('/store/cart');
  };

  const handleExploreAction = (n, e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    if (!n.is_read) {
      markNotificationRead(n.id);
    }
    navigate(n.navigation_target || '/store/catalog');
  };

  // Determine the clean customer-facing message
  const getDisplayMessage = (n) => {
    if (!n || !n.message) return '';
    let msg = n.message.trim();
    if (msg.includes('Body:')) {
      msg = msg.split('Body:').pop().trim();
    }
    return msg
      .replace(/WhatsApp \/ SMS/gi, 'Customer Account')
      .replace(/via WhatsApp/gi, 'in your messages')
      .replace(/WhatsApp nudge/gi, 'message')
      .replace(/WhatsApp/gi, 'SmartCart');
  };

  // Render exactly one action button when needed, or null when not needed
  const renderActionButton = (n) => {
    // 1. Coupon-backed offer
    if (n.coupon_code) {
      if (isCouponUsed(n)) {
        return (
          <span className="msg-coupon-redeemed-tag">
            ✓ Offer Redeemed
          </span>
        );
      }
      return (
        <button
          type="button"
          className="msg-btn-action"
          onClick={(e) => handleApplyOffer(n, e)}
        >
          Apply Offer
        </button>
      );
    }

    // 2. Sponsored product announcement or catalog promotion -> Explore Products
    const typeLower = (n.notification_type || '').toLowerCase();
    const titleLower = (n.title || '').toLowerCase();
    const msgLower = (n.message || '').toLowerCase();
    const isSponsoredOrShowcase =
      typeLower.includes('ads') ||
      typeLower.includes('sponsored') ||
      msgLower.includes('trending') ||
      msgLower.includes('arrivals') ||
      titleLower.includes('ads') ||
      titleLower.includes('sponsored');

    if (isSponsoredOrShowcase) {
      return (
        <button
          type="button"
          className="msg-btn-action"
          onClick={(e) => handleExploreAction(n, e)}
        >
          Explore Products
        </button>
      );
    }

    // 3. Customer service message or announcement without action -> no button
    return null;
  };

  return (
    <div className="msg-inbox-page">
      <div className="msg-inbox-container">
        {/* Inbox Header */}
        <div className="msg-inbox-header">
          <div className="msg-header-title-row">
            <h1 className="msg-inbox-title">Messages</h1>
            {unreadNotificationsCount > 0 && (
              <span className="msg-unread-pill">
                {unreadNotificationsCount} unread
              </span>
            )}
          </div>

          <div className="msg-header-actions">
            {unreadNotificationsCount > 0 && (
              <button
                type="button"
                className="msg-btn-mark-all"
                onClick={markAllNotificationsRead}
              >
                Mark all as read
              </button>
            )}
          </div>
        </div>

        {/* Minimal Filter Tabs */}
        {notifications.length > 0 && (
          <div className="msg-filter-tabs">
            <button
              type="button"
              className={`msg-tab-btn ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
            >
              All ({notifications.length})
            </button>
            <button
              type="button"
              className={`msg-tab-btn ${filter === 'unread' ? 'active' : ''}`}
              onClick={() => setFilter('unread')}
            >
              Unread ({unreadList.length})
            </button>
          </div>
        )}

        {/* Messages Feed */}
        <div className="msg-list-wrapper">
          {displayedNotifications.length === 0 ? (
            <div className="msg-empty-box">
              <p className="msg-empty-title">
                {filter === 'unread' ? 'No unread messages' : 'Your inbox is empty'}
              </p>
              <p className="msg-empty-desc">
                {filter === 'unread'
                  ? "You're all caught up with your notifications."
                  : 'Special offers and updates will appear here.'}
              </p>
            </div>
          ) : (
            <div className="msg-cards-stack">
              {displayedNotifications.map((n) => {
                const isUnread = !n.is_read;
                const messageText = getDisplayMessage(n);
                const actionButton = renderActionButton(n);
                const hasImage = Boolean(n.image_url && n.image_url.trim().length > 0);

                return (
                  <div
                    key={n.id}
                    className={`msg-card ${isUnread ? 'is-unread' : ''}`}
                    onClick={() => {
                      if (isUnread) markNotificationRead(n.id);
                    }}
                  >
                    {hasImage && (
                      <div className="msg-image-col">
                        <img
                          src={n.image_url}
                          alt=""
                          className="msg-card-image"
                          loading="lazy"
                          onError={(e) => {
                            e.currentTarget.style.display = 'none';
                          }}
                        />
                      </div>
                    )}

                    <div className="msg-content-col">
                      <p className="msg-text">{messageText}</p>

                      {n.coupon_code && (
                        <div className="msg-coupon-line">
                          Coupon: <strong className={`msg-coupon-code ${isCouponUsed(n) ? 'used' : ''}`}>{n.coupon_code}</strong>
                          {isCouponUsed(n) && (
                            <span className="msg-coupon-status-pill">Used</span>
                          )}
                        </div>
                      )}

                      {actionButton && (
                        <div className="msg-action-container">
                          {actionButton}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CustomerNotifications;
