import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './pages/Dashboard';
import DatasetUpload from './pages/DatasetUpload';
import CustomerAnalytics from './pages/CustomerAnalytics';
import SalesForecast from './pages/SalesForecast';
import Login from './pages/Login';

// SmartCart Storefront & Multi-Role Commerce
import { StoreProvider } from './context/StoreContext';
import StoreLayout from './components/store/StoreLayout';
import StoreHome from './pages/store/StoreHome';
import StoreCatalog from './pages/store/StoreCatalog';
import ProductDetail from './pages/store/ProductDetail';
import CartPage from './pages/store/CartPage';
import CheckoutPage from './pages/store/CheckoutPage';
import CustomerOrders from './pages/store/CustomerOrders';
import CustomerNotifications from './pages/store/CustomerNotifications';
import PMProductManager from './pages/store/PMProductManager';
import AdminOrdersFeed from './pages/store/AdminOrdersFeed';
import StoreLogin from './pages/store/StoreLogin';

function App() {
  return (
    <Router>
      <StoreProvider>
        <Routes>
          {/* Default entry point: Unified Login Page */}
          <Route path="/" element={<Navigate to="/login" replace />} />

          {/* ======================================================== */}
          {/* SITE 1: SMARTCART E-COMMERCE STOREFRONT (AMAZON-STYLE)   */}
          {/* ======================================================== */}
          <Route path="/store/login" element={<StoreLogin />} />

          <Route
            path="/store"
            element={
              <StoreLayout>
                <StoreHome />
              </StoreLayout>
            }
          />

          <Route
            path="/store/catalog"
            element={
              <StoreLayout>
                <StoreCatalog />
              </StoreLayout>
            }
          />

          <Route
            path="/store/product/:productId"
            element={
              <StoreLayout>
                <ProductDetail />
              </StoreLayout>
            }
          />

          <Route
            path="/store/cart"
            element={
              <StoreLayout>
                <CartPage />
              </StoreLayout>
            }
          />

          <Route
            path="/store/checkout"
            element={
              <StoreLayout>
                <CheckoutPage />
              </StoreLayout>
            }
          />

          <Route
            path="/store/my-orders"
            element={
              <StoreLayout>
                <CustomerOrders />
              </StoreLayout>
            }
          />

          <Route
            path="/store/notifications"
            element={
              <StoreLayout>
                <CustomerNotifications />
              </StoreLayout>
            }
          />

          <Route
            path="/store/manage-products"
            element={
              <StoreLayout>
                <PMProductManager />
              </StoreLayout>
            }
          />

          <Route
            path="/store/admin-orders"
            element={<Navigate to="/store/manage-products" replace />}
          />

          {/* ======================================================== */}
          {/* SITE 2: ML PREDICTION & DECISION PLATFORM                */}
          {/* ======================================================== */}
          <Route path="/login" element={<StoreLogin />} />

          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/upload"
            element={
              <ProtectedRoute>
                <Layout>
                  <DatasetUpload />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/churn-prediction"
            element={
              <ProtectedRoute>
                <Layout>
                  <CustomerAnalytics />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route path="/customers" element={<Navigate to="/churn-prediction" replace />} />
          <Route path="/analytics" element={<Navigate to="/churn-prediction" replace />} />

          <Route
            path="/sales-forecast"
            element={
              <ProtectedRoute>
                <Layout>
                  <SalesForecast />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route path="/model-info" element={<Navigate to="/dashboard" replace />} />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/store" replace />} />
        </Routes>
      </StoreProvider>
    </Router>
  );
}

export default App;