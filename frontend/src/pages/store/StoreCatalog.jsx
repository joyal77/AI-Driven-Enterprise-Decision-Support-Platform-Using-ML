import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Filter,
  Star,
  ShoppingBag,
  SlidersHorizontal,
  CheckCircle,
  X,
  Search
} from 'lucide-react';
import { getStoreProducts, getStoreCategories } from '../../services/storeApi';
import { useStore } from '../../context/StoreContext';
import './StoreCatalog.css';

const StoreCatalog = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [addedPopup, setAddedPopup] = useState(null);

  // Filters
  const categoryFilter = searchParams.get('category') || 'All';
  const searchTerm = searchParams.get('search') || '';
  const primeOnly = searchParams.get('prime') === 'true';
  const sort = searchParams.get('sort') || 'popular';

  const { addToCart } = useStore();
  const navigate = useNavigate();

  useEffect(() => {
    fetchProducts();
    fetchCategories();
  }, [searchParams]);

  const fetchCategories = async () => {
    try {
      const data = await getStoreCategories();
      setCategories(data || []);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const params = {
        limit: 48,
        sort
      };
      if (categoryFilter !== 'All') params.category = categoryFilter;
      if (searchTerm) params.search = searchTerm;
      if (primeOnly) params.prime_only = true;

      const data = await getStoreProducts(params);
      setProducts(data.products || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error('Failed to load catalog products:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateFilter = (key, value) => {
    const nextParams = new URLSearchParams(searchParams);
    if (value === null || value === '' || value === 'All' || value === false) {
      nextParams.delete(key);
    } else {
      nextParams.set(key, value);
    }
    setSearchParams(nextParams);
  };

  const handleAddToCart = (product, e) => {
    e.preventDefault();
    e.stopPropagation();
    addToCart(product, 1);
    setAddedPopup(product.title);
    setTimeout(() => setAddedPopup(null), 2500);
  };

  return (
    <div className="catalog-page-container">
      {addedPopup && (
        <div className="cart-added-toast">
          <CheckCircle size={18} className="text-emerald" />
          <span>Added to Cart: <strong>{addedPopup.slice(0, 32)}...</strong></span>
        </div>
      )}

      {/* Catalog Top Sub-Header */}
      <div className="catalog-top-bar">
        <div className="catalog-breadcrumb">
          <span>SmartCart Store</span> / <strong>{categoryFilter}</strong> {searchTerm && `for "${searchTerm}"`}
        </div>
        <div className="catalog-results-count">
          Showing <strong>{products.length}</strong> of <strong>{total}</strong> products
        </div>
      </div>

      <div className="catalog-layout">
        {/* Left Filter Sidebar */}
        <aside className="catalog-sidebar">
          <div className="sidebar-filter-section">
            <h4>Department</h4>
            <ul className="filter-list">
              <li
                className={categoryFilter === 'All' ? 'active' : ''}
                onClick={() => updateFilter('category', 'All')}
              >
                All Departments
              </li>
              {categories.map((c) => (
                <li
                  key={c.category}
                  className={categoryFilter === c.category ? 'active' : ''}
                  onClick={() => updateFilter('category', c.category)}
                >
                  <span>{c.category}</span>
                  <span className="filter-count">({c.count})</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="sidebar-filter-section">
            <h4>Amazon Prime</h4>
            <label className="filter-checkbox-label">
              <input
                type="checkbox"
                checked={primeOnly}
                onChange={(e) => updateFilter('prime', e.target.checked ? 'true' : null)}
              />
              <span className="prime-chip-sidebar">prime</span>
              <span>Eligible for Free Delivery</span>
            </label>
          </div>

          <div className="sidebar-filter-section">
            <h4>Customer Review</h4>
            <div className="rating-filter-options">
              {[4, 3].map((r) => (
                <div key={r} className="rating-filter-row">
                  <div className="stars-row">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} size={14} className={i < r ? 'star-filled' : 'star-empty'} />
                    ))}
                  </div>
                  <span>& Up</span>
                </div>
              ))}
            </div>
          </div>

          <div className="sidebar-filter-section">
            <button
              onClick={() => setSearchParams(new URLSearchParams())}
              className="btn-clear-filters"
            >
              Clear All Filters
            </button>
          </div>
        </aside>

        {/* Product Grid Area */}
        <main className="catalog-main-content">
          {/* Active Filter Chips & Sort Controls */}
          <div className="catalog-controls-ribbon">
            <div className="active-chips-row">
              {categoryFilter !== 'All' && (
                <span className="filter-active-chip">
                  Category: {categoryFilter}
                  <X size={12} onClick={() => updateFilter('category', 'All')} />
                </span>
              )}
              {searchTerm && (
                <span className="filter-active-chip">
                  Search: {searchTerm}
                  <X size={12} onClick={() => updateFilter('search', '')} />
                </span>
              )}
              {primeOnly && (
                <span className="filter-active-chip">
                  Prime Only
                  <X size={12} onClick={() => updateFilter('prime', null)} />
                </span>
              )}
            </div>

            <div className="sort-box">
              <label>Sort by:</label>
              <select value={sort} onChange={(e) => updateFilter('sort', e.target.value)}>
                <option value="popular">Featured / Most Popular</option>
                <option value="price_asc">Price: Low to High</option>
                <option value="price_desc">Price: High to Low</option>
                <option value="rating">Avg. Customer Review</option>
              </select>
            </div>
          </div>

          {loading ? (
            <div className="store-loading">Fetching products from inventory...</div>
          ) : products.length === 0 ? (
            <div className="empty-catalog-box">
              <h3>No products found matching your filter criteria.</h3>
              <p>Try clearing filters or search for another department.</p>
              <button onClick={() => setSearchParams(new URLSearchParams())} className="btn-hero-primary" style={{ marginTop: '12px' }}>
                Reset Filters
              </button>
            </div>
          ) : (
            <div className="catalog-grid">
              {products.map((p) => (
                <div key={p.id} className="catalog-card" onClick={() => navigate(`/store/product/${p.id}`)}>
                  {p.is_prime && (
                    <div className="prime-badge-tag">
                      <span>prime</span>
                    </div>
                  )}

                  <div className="catalog-img-wrapper">
                    <img src={p.image_url} alt={p.title} loading="lazy" />
                  </div>

                  <div className="catalog-card-info">
                    <span className="product-category-chip">{p.category}</span>
                    <h3 className="catalog-card-title" title={p.title}>{p.title}</h3>

                    <div className="product-rating">
                      <div className="stars-row">
                        {[...Array(5)].map((_, i) => (
                          <Star key={i} size={13} className={i < Math.floor(p.rating) ? 'star-filled' : 'star-empty'} />
                        ))}
                      </div>
                      <span className="rating-val">{p.rating}</span>
                      <span className="rating-count">({p.rating_count.toLocaleString()})</span>
                    </div>

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

                    <div className="delivery-note">
                      Get it by <strong>Tomorrow, 11 AM</strong> with FREE Prime Delivery
                    </div>

                    <button
                      type="button"
                      className="btn-add-to-cart"
                      onClick={(e) => handleAddToCart(p, e)}
                      disabled={!p.in_stock}
                    >
                      <ShoppingBag size={14} />
                      <span>{p.in_stock ? 'Add to Cart' : 'Out of Stock'}</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default StoreCatalog;
