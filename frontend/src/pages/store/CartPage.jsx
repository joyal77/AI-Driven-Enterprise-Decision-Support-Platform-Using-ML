import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Trash2,
  Plus,
  Minus,
  ShoppingBag,
  ArrowRight,
  ShieldCheck,
  CheckCircle,
  Truck
} from 'lucide-react';
import { useStore } from '../../context/StoreContext';
import './CartPage.css';

const CartPage = () => {
  const {
    cartItems,
    updateCartQuantity,
    removeFromCart,
    clearCart,
    cartCount,
    cartSubtotal,
    storeUser,
    walletBalance = 0,
    activeVouchers = [],
    hasExpressShipping = false,
    appliedVoucher
  } = useStore();

  const navigate = useNavigate();

  const voucherGrantsFreeShipping = Boolean(
    appliedVoucher?.free_shipping ||
    (appliedVoucher?.code && ['RECOVER', 'SPEED', 'FLEX'].some((pfx) => appliedVoucher.code.toUpperCase().startsWith(pfx)))
  );
  const isPrime = (storeUser?.membership_status && storeUser.membership_status.toLowerCase().includes('prime')) || hasExpressShipping || voucherGrantsFreeShipping;
  const isFreeDelivery = isPrime || cartSubtotal >= 500;
  const shippingFee = isFreeDelivery ? 0 : 40;

  let voucherDiscount = 0;
  if (appliedVoucher) {
    if (appliedVoucher.discount_pct && appliedVoucher.discount_pct > 0) {
      voucherDiscount = roundVal(cartSubtotal * (appliedVoucher.discount_pct / 100));
    } else if (appliedVoucher.discount_amount && appliedVoucher.discount_amount > 0) {
      voucherDiscount = Math.min(cartSubtotal, appliedVoucher.discount_amount);
    }
  }

  const subtotalAfterVoucher = Math.max(0, cartSubtotal - voucherDiscount);
  const estimatedTax = roundVal(subtotalAfterVoucher * 0.05);
  const totalAmount = roundVal(subtotalAfterVoucher + shippingFee + estimatedTax);

  function roundVal(num) {
    return Math.round((num + Number.EPSILON) * 100) / 100;
  }

  if (cartItems.length === 0) {
    return (
      <div className="cart-page-wrapper">
        <div className="cart-empty-card">
          <div className="cart-empty-icon">
            <ShoppingBag size={48} />
          </div>
          <h2>Your SmartCart is empty</h2>
          <p>You have no items in your shopping basket. Check out today's best deals and add products!</p>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginTop: '18px' }}>
            <Link to="/store/catalog" className="btn-hero-primary">
              Continue Shopping
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="cart-page-wrapper">
      <div className="cart-main-grid">
        {/* Left Column: Cart Items List */}
        <div className="cart-items-column">
          <div className="cart-items-header">
            <div>
              <h1 className="cart-heading">Shopping Cart</h1>
              <span className="deselect-link" onClick={clearCart}>Deselect all items</span>
            </div>
            <span className="price-column-label">Price</span>
          </div>

          {/* Free Shipping Alert */}
          {isFreeDelivery ? (
            <div className="free-shipping-bar success">
              <CheckCircle size={18} />
              <span>
                Your order qualifies for <strong>FREE Delivery</strong> {hasExpressShipping && 'via SmartCart Express Air Priority Logistics'}
              </span>
            </div>
          ) : (
            <div className="free-shipping-bar info">
              <Truck size={18} />
              <span>Add <strong>₹{(500 - cartSubtotal).toFixed(2)}</strong> of eligible items to get FREE Delivery</span>
            </div>
          )}

          {/* Retention Rewards Active Banner */}
          {((activeVouchers && activeVouchers.length > 0) || hasExpressShipping || walletBalance > 0) && (
            <div style={{
              margin: '12px 0 16px 0',
              padding: '12px 16px',
              backgroundColor: '#ecfdf5',
              border: '1px solid #6ee7b7',
              borderRadius: '8px',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 800, color: '#065f46', fontSize: '14px' }}>
                <span>🎁 Active Retention Perks on Your Account:</span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', fontSize: '13px', color: '#047857' }}>
                {activeVouchers && activeVouchers.map((v, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '6px', backgroundColor: '#ffffff', padding: '4px 10px', borderRadius: '6px', border: '1px solid #a7f3d0' }}>
                    <span>🎟️</span>
                    <span>Coupon <strong>{v.code}</strong> ({v.discount_pct ? `${v.discount_pct}% OFF` : `₹${v.discount_amount} OFF`} applied at checkout)</span>
                  </div>
                ))}
                {hasExpressShipping && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', backgroundColor: '#ffffff', padding: '4px 10px', borderRadius: '6px', border: '1px solid #a7f3d0' }}>
                    <span>⚡</span>
                    <span><strong>Free Express Air Priority Delivery (₹0 Shipping)</strong> unlocked on all orders</span>
                  </div>
                )}
                {walletBalance > 0 && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', backgroundColor: '#ffffff', padding: '4px 10px', borderRadius: '6px', border: '1px solid #a7f3d0' }}>
                    <span>👛</span>
                    <span><strong>₹{walletBalance.toFixed(2)}</strong> SmartCart Wallet Balance</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Line Items */}
          <div className="cart-line-items-list">
            {cartItems.map((item) => (
              <div key={item.id} className="cart-item-row">
                <div className="item-img-box" onClick={() => navigate(`/store/product/${item.id}`)}>
                  <img src={item.image_url} alt={item.title} />
                </div>

                <div className="item-info-box">
                  <h3 className="item-title" onClick={() => navigate(`/store/product/${item.id}`)}>
                    {item.title}
                  </h3>
                  <div className="item-stock-status">In Stock</div>
                  {item.is_prime && (
                    <div className="prime-chip-cart">prime</div>
                  )}

                  <div className="item-actions-row">
                    {/* Quantity modifier */}
                    <div className="qty-counter-box">
                      <button
                        type="button"
                        onClick={() => updateCartQuantity(item.id, item.quantity - 1)}
                        title="Decrease"
                      >
                        <Minus size={13} />
                      </button>
                      <span className="qty-number">{item.quantity}</span>
                      <button
                        type="button"
                        onClick={() => updateCartQuantity(item.id, item.quantity + 1)}
                        title="Increase"
                      >
                        <Plus size={13} />
                      </button>
                    </div>

                    <span className="action-divider">|</span>

                    <button
                      type="button"
                      className="btn-item-delete"
                      onClick={() => removeFromCart(item.id)}
                    >
                      <Trash2 size={13} />
                      <span>Delete</span>
                    </button>
                  </div>
                </div>

                <div className="item-price-box">
                  <span className="item-price-val">₹{(item.price * item.quantity).toLocaleString()}</span>
                  {item.quantity > 1 && (
                    <span className="unit-price-sub">₹{item.price.toLocaleString()} each</span>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="cart-subtotal-footer">
            Subtotal ({cartCount} {cartCount === 1 ? 'item' : 'items'}): <strong>₹{cartSubtotal.toLocaleString()}</strong>
          </div>
        </div>

        {/* Right Column: Checkout Summary Box */}
        <div className="cart-summary-column">
          <div className="summary-card">
            {isFreeDelivery && (
              <div className="delivery-perk-badge">
                <CheckCircle size={15} />
                <span>Your order is eligible for FREE Delivery</span>
              </div>
            )}

            <div className="summary-subtotal-row">
              <span>Subtotal ({cartCount} items):</span>
              <span className="summary-price-bold">₹{cartSubtotal.toLocaleString()}</span>
            </div>

            {appliedVoucher && voucherDiscount > 0 && (
              <div className="summary-line-item" style={{ color: '#059669', fontWeight: 600 }}>
                <span>Coupon ({appliedVoucher.code}):</span>
                <span>-₹{voucherDiscount.toLocaleString()}</span>
              </div>
            )}

            <div className="summary-line-item">
              <span>Estimated 5% GST:</span>
              <span>₹{estimatedTax.toLocaleString()}</span>
            </div>

            <div className="summary-line-item">
              <span>Shipping Fee:</span>
              <span>{shippingFee === 0 ? <strong style={{ color: '#007600' }}>FREE</strong> : `₹${shippingFee}`}</span>
            </div>

            <div className="summary-divider"></div>

            <div className="summary-total-row">
              <span>Order Total:</span>
              <span className="total-highlight">₹{totalAmount.toLocaleString()}</span>
            </div>

            <button
              type="button"
              className="btn-proceed-checkout"
              onClick={() => navigate('/store/checkout')}
            >
              <span>Proceed to Buy ({cartCount} items)</span>
              <ArrowRight size={16} />
            </button>

            <div className="shopping-as-note">
              Shopping as: <strong>{storeUser?.username || 'Guest'}</strong>
              <br />
              <span style={{ fontSize: '11px', color: '#565959' }}>
                Completing this order directly updates this account's churn probability in the decision platform.
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartPage;
