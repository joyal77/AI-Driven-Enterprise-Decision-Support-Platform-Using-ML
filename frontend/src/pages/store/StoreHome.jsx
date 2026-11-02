import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Sparkles,
  ShoppingBag,
  Star,
  CheckCircle,
  TrendingUp,
  ShieldCheck,
  ChevronRight,
  Zap,
  ArrowRight
} from 'lucide-react';
import { getStoreProducts, getStoreCategories } from '../../services/storeApi';
import { useStore } from '../../context/StoreContext';
import './StoreHome.css';

const StoreHome = () => {
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addedPopup, setAddedPopup] = useState(null);

  const { addToCart, storeUser } = useStore();
  const navigate = useNavigate();

  useEffect(() => {
    fetchHomeData();
  }, []);

  const fetchHomeData = async () => {
    setLoading(true);
    try {
      const [prodsData, catsData] = await Promise.all([
        getStoreProducts({ limit: 12 }),
        getStoreCategories()
      ]);
      setFeaturedProducts(prodsData.products || []);
      setCategories(catsData || []);
    } catch (err) {
      console.error('Failed to load store home data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = (product, e) => {
    e.preventDefault();
    e.stopPropagation();
    addToCart(product, 1);
    setAddedPopup(product.title);
    setTimeout(() => setAddedPopup(null), 2500);
  };

  return (
    <div className="store-home-page">
      {/* Toast Notification when adding item to cart */}
      {addedPopup && (
        <div className="cart-added-toast">
          <CheckCircle size={18} className="text-emerald" />
          <span>Added to Cart: <strong>{addedPopup.slice(0, 32)}...</strong></span>
        </div>
      )}

      {/* Hero Banner Section (Amazon Prime Big Deals Style) */}
      <div className="store-hero-banner">
        <div className="hero-content">
          <div className="hero-badge">
            <Zap size={14} /> SmartCart Prime Super Sale
          </div>
          <h1 className="hero-title">
            Up to 70% Off Electronics, Fashion, Home & Daily Essentials
          </h1>
          <p className="hero-subtitle">
            Shop 40+ authentic products with instant delivery across electronics, fashion, groceries, and home essentials.
          </p>
          <div className="hero-actions">
            <Link to="/store/catalog" className="btn-hero-primary">
              <span>Shop All Deals Now</span>
              <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </div>

      {/* Category Showcase Cards */}
      <div className="store-container">
        <div className="category-card-grid">
          <div className="cat-card">
            <h3>📱 Top Deals in Electronics</h3>
            <p className="cat-desc">Audio, smart devices, tablets & accessories</p>
            <div className="cat-img-box">
              <img src="https://images.unsplash.com/photo-1543512214-318c7553f230?w=400&auto=format&fit=crop&q=80" alt="Electronics" />
            </div>
            <Link to="/store/catalog?category=Electronics" className="cat-link">
              Explore Electronics →
            </Link>
          </div>

          <div className="cat-card">
            <h3>👗 Latest Trends in Fashion</h3>
            <p className="cat-desc">Polo shirts, slim jeans, luxury watches & shoes</p>
            <div className="cat-img-box">
              <img src="https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=400&auto=format&fit=crop&q=80" alt="Fashion" />
            </div>
            <Link to="/store/catalog?category=Fashion" className="cat-link">
              Explore Fashion →
            </Link>
          </div>

          <div className="cat-card">
            <h3>🍳 Modern Home & Kitchen</h3>
            <p className="cat-desc">750W mixers, instant pots, vacuums & flasks</p>
            <div className="cat-img-box">
              <img src="https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=400&auto=format&fit=crop&q=80" alt="Home & Kitchen" />
            </div>
            <Link to="/store/catalog?category=Home+%26+Kitchen" className="cat-link">
              Explore Kitchen →
            </Link>
          </div>

          <div className="cat-card">
            <h3>🛒 Fresh Groceries & Pantry</h3>
            <p className="cat-desc">Tea, premium basmati, almonds & hazelnut spreads</p>
            <div className="cat-img-box">
              <img src="https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400&auto=format&fit=crop&q=80" alt="Grocery" />
            </div>
            <Link to="/store/catalog?category=Grocery" className="cat-link">
              Explore Groceries →
            </Link>
          </div>
        </div>

        {/* Featured Products Section */}
        <div className="featured-section">
          <div className="section-header">
            <div>
              <h2 className="section-title">Today's Trending & Best Sellers</h2>
              <p className="section-subtitle">Real-time inventory connected to automated restock demand forecasting</p>
            </div>
            <Link to="/store/catalog" className="see-more-link">
              <span>See all 40 products</span>
              <ChevronRight size={16} />
            </Link>
          </div>

          {loading ? (
            <div className="store-loading">Loading catalog products...</div>
          ) : (
            <div className="products-grid">
              {featuredProducts.map((p) => (
                <div key={p.id} className="product-card" onClick={() => navigate(`/store/product/${p.id}`)}>
                  {/* Prime Badge */}
                  {p.is_prime && (
                    <div className="prime-badge-tag">
                      <span>prime</span>
                    </div>
                  )}

                  {/* Product Image */}
                  <div className="product-img-wrapper">
                    <img src={p.image_url} alt={p.title} loading="lazy" />
                  </div>

                  {/* Product Info */}
                  <div className="product-details">
                    <span className="product-category-chip">{p.category}</span>
                    <h3 className="product-title" title={p.title}>{p.title}</h3>

                    {/* Star Rating */}
                    <div className="product-rating">
                      <div className="stars-row">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            size={14}
                            className={i < Math.floor(p.rating) ? 'star-filled' : 'star-empty'}
                          />
                        ))}
                      </div>
                      <span className="rating-val">{p.rating}</span>
                      <span className="rating-count">({p.rating_count.toLocaleString()})</span>
                    </div>

                    {/* Pricing */}
                    <div className="product-price-block">
                      <div className="price-main">
                        <span className="currency-symbol">₹</span>
                        <span className="price-num">{p.price.toLocaleString()}</span>
                      </div>
                      {p.original_price && p.original_price > p.price && (
                        <div className="price-strike">
                          <span>M.R.P: ₹{p.original_price.toLocaleString()}</span>
                          <span className="discount-tag">({p.discount_pct}% off)</span>
                        </div>
                      )}
                    </div>

                    {/* Stock status */}
                    <div className="product-stock-tag">
                      {p.stock_quantity > 0 ? (
                        <span className="in-stock-label">In Stock ({p.stock_quantity} units)</span>
                      ) : (
                        <span className="out-stock-label">Out of Stock</span>
                      )}
                    </div>

                    {/* Add to Cart Button */}
                    <button
                      type="button"
                      className="btn-add-to-cart"
                      onClick={(e) => handleAddToCart(p, e)}
                      disabled={p.stock_quantity <= 0}
                    >
                      <ShoppingBag size={15} />
                      <span>{p.stock_quantity > 0 ? 'Add to Cart' : 'Unavailable'}</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StoreHome;
