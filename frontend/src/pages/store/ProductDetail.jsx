import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Star,
  ShieldCheck,
  Truck,
  RotateCcw,
  ShoppingBag,
  Zap,
  CheckCircle,
  ChevronRight,
  Sparkles,
  Lock,
  MapPin,
  RefreshCw,
  Clock,
  ArrowRight,
  PackageCheck,
  Award
} from 'lucide-react';
import { getProductDetail } from '../../services/storeApi';
import { useStore } from '../../context/StoreContext';
import './ProductDetail.css';

const ProductDetail = () => {
  const { id, productId } = useParams();
  const currentProductId = id || productId;
  const navigate = useNavigate();
  const { addToCart, storeUser } = useStore();

  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [addedPopup, setAddedPopup] = useState(false);
  const [addedItemTitle, setAddedItemTitle] = useState('');
  const [directBuying, setDirectBuying] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    fetchDetail();
  }, [currentProductId]);

  const fetchDetail = async (retryCount = 0) => {
    setLoading(true);
    setError(null);
    try {
      const cleanId = String(currentProductId || '').trim();
      const data = await getProductDetail(cleanId);
      if (data && (data.id || data.title)) {
        setProduct(data);
      } else {
        throw new Error("Invalid product response received from server.");
      }
    } catch (err) {
      console.error('Failed to load product details:', err);
      if (retryCount < 1) {
        setTimeout(() => fetchDetail(retryCount + 1), 600);
        return;
      }
      setError(err?.response?.data?.detail || "Product not found or currently unavailable.");
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = (itemToAdd = product, qty = quantity) => {
    if (!itemToAdd) return;
    addToCart(itemToAdd, qty);
    setAddedItemTitle(itemToAdd.title);
    setAddedPopup(true);
    setTimeout(() => setAddedPopup(false), 3000);
  };

  const handleBuyNow = () => {
    if (!product) return;
    setDirectBuying(true);
    // 1. Add current item to isolated cart with selected quantity
    addToCart(product, quantity);
    // 2. Direct Buy navigation to checkout
    navigate('/store/checkout');
  };

  if (loading) {
    return (
      <div className="product-detail-page">
        <div className="detail-loading-box">
          <div className="loading-spinner"></div>
          <h2>Loading product specifications and reviews...</h2>
          <p>Connecting to SmartCart Storefront & ML Product Catalog...</p>
        </div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="product-detail-page">
        <div className="detail-not-found-card">
          <div className="not-found-icon">
            <ShoppingBag size={52} />
          </div>
          <h2>{error || "Product not found"}</h2>
          <p>
            The requested product (ID: <code>{id}</code>) could not be retrieved from the active catalog.
          </p>
          <div className="not-found-actions">
            <button type="button" onClick={() => fetchDetail(0)} className="btn-retry-product">
              <RefreshCw size={15} />
              <span>Retry Loading</span>
            </button>
            <Link to="/store/catalog" className="btn-hero-primary">
              Browse All Store Products
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const discountAmount = product.original_price && product.original_price > product.price
    ? Math.round(product.original_price - product.price)
    : 0;

  return (
    <div className="product-detail-page">
      {/* Toast Notification */}
      {addedPopup && (
        <div className="cart-added-toast">
          <CheckCircle size={20} className="text-emerald" />
          <div className="toast-text-box">
            <strong>Added to Cart!</strong>
            <span>{addedItemTitle.slice(0, 50)}... (Qty: {quantity})</span>
          </div>
          <Link to="/store/cart" className="btn-toast-view-cart">
            View Cart
          </Link>
        </div>
      )}

      {/* Breadcrumb Navigation */}
      <div className="detail-breadcrumb-bar">
        <div className="detail-breadcrumb-inner">
          <Link to="/store">SmartCart</Link>
          <ChevronRight size={14} />
          <Link to={`/store/catalog?category=${encodeURIComponent(product.category || 'All')}`}>
            {product.category || 'Catalog'}
          </Link>
          <ChevronRight size={14} />
          <span className="current-title">{product.title.slice(0, 50)}...</span>
        </div>
      </div>

      {/* Main 3-Column Layout: Image | Specs & Description | Buy Box */}
      <div className="detail-main-layout">
        {/* Left Column: Product Visuals & Trust Badges */}
        <div className="detail-img-column">
          <div className="detail-main-img-box">
            <img src={product.image_url} alt={product.title} />
            <div className="img-corner-badge">
              <Award size={15} />
              <span>Amazon Verified</span>
            </div>
          </div>

          <div className="guarantee-ribbon">
            <div className="guarantee-item">
              <Truck size={20} />
              <span>Fast 24-hr Delivery</span>
            </div>
            <div className="guarantee-item">
              <RotateCcw size={20} />
              <span>7 Days Returnable</span>
            </div>
            <div className="guarantee-item">
              <ShieldCheck size={20} />
              <span>1 Year Warranty</span>
            </div>
            <div className="guarantee-item">
              <Lock size={20} />
              <span>Secure Payment</span>
            </div>
          </div>
        </div>

        {/* Center Column: Title, Ratings, Pricing, Features, Specs */}
        <div className="detail-info-column">
          <div className="category-sku-row">
            <span className="category-tag">{product.category}</span>
            <span className="sku-label">SKU: {product.sku}</span>
          </div>

          <h1 className="detail-product-title">{product.title}</h1>

          {/* Star Ratings Row */}
          <div className="product-rating-row">
            <div className="stars-row">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  size={17}
                  className={i < Math.floor(product.rating || 4.5) ? 'star-filled' : 'star-empty'}
                />
              ))}
            </div>
            <span className="rating-val">{product.rating || 4.5}</span>
            <span className="rating-count">
              ({(product.rating_count || 120).toLocaleString()} customer reviews)
            </span>
            <span className="rating-divider">|</span>
            <span className="badge-choice">SmartCart's Choice</span>
          </div>

          <div className="detail-divider"></div>

          {/* Deal & Price Section */}
          <div className="detail-price-section">
            <div className="deal-pill">Limited time deal</div>
            <div className="price-tag-row">
              <span className="discount-pct-badge">-{product.discount_pct || 20}%</span>
              <div className="price-main">
                <span className="currency-symbol">₹</span>
                <span className="price-num">{product.price.toLocaleString()}</span>
              </div>
            </div>
            {product.original_price && (
              <div className="mrp-row">
                <span>M.R.P.: </span>
                <span className="mrp-strikethrough">₹{product.original_price.toLocaleString()}</span>
                {discountAmount > 0 && (
                  <span className="savings-highlight">
                    You Save: ₹{discountAmount.toLocaleString()} ({product.discount_pct}%)
                  </span>
                )}
              </div>
            )}
            <div className="inclusive-taxes-note">Inclusive of all taxes. EMI starts at ₹115/month.</div>
          </div>

          {/* Prime Advantage */}
          {product.is_prime && (
            <div className="prime-detail-banner">
              <span className="prime-chip">prime</span>
              <span>Enjoy <strong>FREE One-Day Delivery</strong> and exclusive deals as a Prime member.</span>
            </div>
          )}

          <div className="detail-divider"></div>

          {/* Bullet Points: About This Item */}
          <div className="about-item-section">
            <h3>About this item</h3>
            <ul className="specs-list">
              {product.features && product.features.length > 0 ? (
                product.features.map((feat, idx) => (
                  <li key={idx}>{feat}</li>
                ))
              ) : (
                <>
                  <li>{product.description}</li>
                  <li>Engineered with durable high-grade components for long-lasting daily use.</li>
                  <li>100% Genuine, brand-authorized authentic merchandise with certified warranty.</li>
                  <li>Seamless multi-device compatibility and easy setup out of the box.</li>
                </>
              )}
            </ul>
          </div>

          {/* Technical Specifications Table */}
          {product.specifications && (
            <div className="specs-table-wrapper">
              <h3>Technical Specifications</h3>
              <table className="specs-table">
                <tbody>
                  {Object.entries(product.specifications).map(([key, val]) => (
                    <tr key={key}>
                      <td className="spec-label">{key}</td>
                      <td className="spec-value">{val}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* ML Sync Bridge Callout */}
          <div className="ml-bridge-box">
            <div className="ml-box-header">
              <Sparkles size={17} className="text-amazon-gold" />
              <strong>Real-Time Enterprise Machine Learning Integration</strong>
            </div>
            <p>
              Shopping on SmartCart as <strong>{storeUser?.username || 'Customer'}</strong> connects directly to our Random Forest Churn Predictor. Every checkout immediately updates lifetime metrics and refreshes the Multi-Horizon Sales Forecast.
            </p>
          </div>
        </div>

        {/* Right Column: Amazon-Style Sticky Buy Box */}
        <div className="detail-buybox-column">
          <div className="buybox-card">
            <div className="buybox-price">
              <span className="currency-symbol">₹</span>
              <span className="price-num">{product.price.toLocaleString()}</span>
            </div>

            <div className="delivery-highlight">
              <div className="delivery-row">
                <Truck size={16} className="text-emerald" />
                <span><strong>FREE Delivery</strong> Tomorrow, 11 AM</span>
              </div>
              <div className="delivery-sub">Order within <strong>3 hrs 24 mins</strong></div>
            </div>

            <div className="deliver-to-box">
              <MapPin size={14} />
              <span>Deliver to {storeUser?.full_name || storeUser?.username || 'Bengaluru 560001'}</span>
            </div>

            <div className="buybox-stock">
              {product.stock_quantity > 0 ? (
                <span className="stock-green">
                  <CheckCircle size={15} /> In Stock ({product.stock_quantity} available)
                </span>
              ) : (
                <span className="stock-red">Currently Unavailable</span>
              )}
            </div>

            {product.stock_quantity > 0 && (
              <div className="buybox-actions-group">
                <div className="quantity-select-row">
                  <label htmlFor="qty-select">Quantity:</label>
                  <select
                    id="qty-select"
                    value={quantity}
                    onChange={(e) => setQuantity(Number(e.target.value))}
                  >
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
                      <option key={num} value={num}>
                        {num}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Add to Cart Button */}
                <button
                  type="button"
                  className="btn-add-cart-large"
                  onClick={() => handleAddToCart(product, quantity)}
                >
                  <ShoppingBag size={17} />
                  <span>Add to Cart</span>
                </button>

                {/* Direct Buy (Buy Now) Button */}
                <button
                  type="button"
                  className="btn-buy-now-large"
                  onClick={handleBuyNow}
                  disabled={directBuying}
                >
                  <Zap size={17} />
                  <span>{directBuying ? 'Preparing Checkout...' : 'Buy Now'}</span>
                </button>
              </div>
            )}

            <div className="buybox-secure">
              <Lock size={14} />
              <span>SmartCart 100% Purchase Protection Guarantee</span>
            </div>

            <div className="buyer-note">
              <div>Ships from: <strong>SmartCart Logistics</strong></div>
              <div>Sold by: <strong>Authorized Brand Partner</strong></div>
              <div>Return policy: <strong>7 Days Replacement</strong></div>
            </div>
          </div>
        </div>
      </div>

      {/* Customer Reviews Section */}
      {product.reviews && product.reviews.length > 0 && (
        <div className="detail-bottom-section">
          <div className="section-header-row">
            <h2>Customer Reviews & Verified Feedback</h2>
            <div className="rating-pill">
              <Star size={15} className="star-filled" />
              <strong>{product.rating} out of 5</strong>
              <span>({product.rating_count?.toLocaleString()} ratings)</span>
            </div>
          </div>

          <div className="reviews-grid">
            {product.reviews.map((rev) => (
              <div key={rev.id} className="review-card">
                <div className="reviewer-top">
                  <div className="reviewer-avatar">{rev.author[0]}</div>
                  <div>
                    <strong>{rev.author}</strong>
                    {rev.verified && (
                      <div className="verified-badge">
                        <PackageCheck size={12} />
                        <span>Verified Purchase</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="review-rating-row">
                  <div className="stars-row">
                    {[...Array(rev.rating)].map((_, i) => (
                      <Star key={i} size={14} className="star-filled" />
                    ))}
                  </div>
                  <span className="review-date">{rev.date}</span>
                </div>

                <strong className="review-title">{rev.title}</strong>
                <p className="review-comment">{rev.comment}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Related Products Carousel / Grid */}
      {product.related_products && product.related_products.length > 0 && (
        <div className="detail-bottom-section related-section">
          <div className="section-header-row">
            <div>
              <h2>Related Products & Customers Also Viewed</h2>
              <p className="section-subtext">Discover popular items frequently shopped together in {product.category}</p>
            </div>
            <Link to={`/store/catalog?category=${encodeURIComponent(product.category || 'All')}`} className="see-more-link">
              <span>See more in {product.category}</span>
              <ArrowRight size={14} />
            </Link>
          </div>

          <div className="related-products-grid">
            {product.related_products.map((rel) => (
              <div key={rel.id} className="related-card">
                <div
                  className="related-img-box"
                  onClick={() => navigate(`/store/product/${rel.id}`)}
                >
                  <img src={rel.image_url} alt={rel.title} />
                  {rel.discount_pct > 0 && (
                    <span className="discount-tag">-{rel.discount_pct}%</span>
                  )}
                </div>

                <div className="related-info-box">
                  <h4
                    className="related-title"
                    onClick={() => navigate(`/store/product/${rel.id}`)}
                    title={rel.title}
                  >
                    {rel.title}
                  </h4>

                  <div className="related-rating-row">
                    <div className="stars-row">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          size={13}
                          className={i < Math.floor(rel.rating || 4.5) ? 'star-filled' : 'star-empty'}
                        />
                      ))}
                    </div>
                    <span className="rel-rating-count">({rel.rating_count})</span>
                  </div>

                  <div className="related-price-row">
                    <span className="rel-currency">₹</span>
                    <strong className="rel-price">{rel.price.toLocaleString()}</strong>
                    {rel.original_price && rel.original_price > rel.price && (
                      <span className="rel-mrp">₹{rel.original_price.toLocaleString()}</span>
                    )}
                  </div>

                  {rel.is_prime && (
                    <div className="rel-prime-row">
                      <span className="prime-chip-sm">prime</span>
                      <span>Tomorrow</span>
                    </div>
                  )}

                  <div className="related-btn-group">
                    <button
                      type="button"
                      className="btn-quick-add-cart"
                      onClick={() => handleAddToCart(rel, 1)}
                    >
                      <ShoppingBag size={14} />
                      <span>Add to Cart</span>
                    </button>
                    <button
                      type="button"
                      className="btn-quick-buy"
                      onClick={() => {
                        addToCart(rel, 1);
                        navigate('/store/checkout');
                      }}
                    >
                      <Zap size={14} />
                      <span>Buy Now</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductDetail;
