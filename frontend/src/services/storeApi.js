import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

const storeApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Authentication
export const storeLogin = async (username, password) => {
  const response = await storeApi.post('/store/auth/login', { username, password });
  return response.data;
};

export const recordCustomerLogin = async (customerId) => {
  const response = await storeApi.post(`/store/auth/record-login/${customerId}`);
  return response.data;
};

export const getDemoCustomers = async () => {
  const response = await storeApi.get('/store/auth/demo-customers');
  return response.data;
};

// Products & Catalog
export const getStoreProducts = async (params = {}) => {
  const response = await storeApi.get('/store/products', { params });
  return response.data;
};

export const getStoreCategories = async () => {
  const response = await storeApi.get('/store/products/categories');
  return response.data;
};

export const getProductDetail = async (productId) => {
  const response = await storeApi.get(`/store/products/${productId}`);
  return response.data;
};

export const getRelatedProducts = async (productId) => {
  const response = await storeApi.get(`/store/products/${productId}/related`);
  return response.data;
};

export const createProduct = async (productData) => {
  const response = await storeApi.post('/store/products', productData);
  return response.data;
};

export const updateProduct = async (productId, productData) => {
  const response = await storeApi.put(`/store/products/${productId}`, productData);
  return response.data;
};

export const deleteProduct = async (productId) => {
  const response = await storeApi.delete(`/store/products/${productId}`);
  return response.data;
};

// Orders & Checkout
export const placeStoreOrder = async (orderPayload) => {
  const response = await storeApi.post('/store/orders', orderPayload);
  return response.data;
};

export const validateStoreVoucher = async (customerId, voucherCode, cartSubtotal = 0) => {
  const response = await storeApi.post('/store/orders/validate-voucher', {
    customer_id: customerId,
    voucher_code: voucherCode,
    cart_subtotal: cartSubtotal,
  });
  return response.data;
};

export const getCustomerOrders = async (customerId) => {
  const response = await storeApi.get('/store/orders/my-orders', {
    params: { customer_id: customerId },
  });
  return response.data;
};

export const getAllStoreOrders = async (params = {}) => {
  const response = await storeApi.get('/store/orders/all', { params });
  return response.data;
};

// User-Isolated Shopping Cart API
export const getStoreCart = async (customerId) => {
  const response = await storeApi.get('/store/cart', {
    params: { customer_id: customerId },
  });
  return response.data;
};

export const addStoreCartItem = async (customerId, productId, quantity = 1) => {
  const response = await storeApi.post('/store/cart', {
    customer_id: customerId,
    product_id: productId,
    quantity,
  });
  return response.data;
};

export const updateStoreCartQuantity = async (customerId, productId, quantity) => {
  const response = await storeApi.put('/store/cart/item', {
    customer_id: customerId,
    product_id: productId,
    quantity,
  });
  return response.data;
};

export const removeStoreCartItem = async (customerId, productId) => {
  const response = await storeApi.delete('/store/cart/item', {
    params: { customer_id: customerId, product_id: productId },
  });
  return response.data;
};

export const clearStoreCart = async (customerId) => {
  const response = await storeApi.delete('/store/cart', {
    params: { customer_id: customerId },
  });
  return response.data;
};

export const getCustomerPerks = async (customerId) => {
  const response = await storeApi.get(`/customers/${customerId}/retention-perks`);
  return response.data;
};

// Store Notification Endpoints (/store/notifications)
export const getStoreNotifications = async (customerId, params = {}) => {
  const response = await storeApi.get('/store/notifications', {
    params: { customer_id: customerId, ...params }
  });
  return response.data;
};

export const getStoreUnreadNotificationsCount = async (customerId, params = {}) => {
  const response = await storeApi.get('/store/notifications/unread-count', {
    params: { customer_id: customerId, ...params }
  });
  return response.data;
};

export const markStoreNotificationAsRead = async (customerId, notificationId) => {
  const response = await storeApi.post(`/store/notifications/${notificationId}/read`, {}, {
    params: { customer_id: customerId }
  });
  return response.data;
};

export const markStoreAllNotificationsAsRead = async (customerId) => {
  const response = await storeApi.post('/store/notifications/read-all', {}, {
    params: { customer_id: customerId }
  });
  return response.data;
};

export const getCustomerNotifications = async (customerId) => {
  try {
    const response = await storeApi.get('/store/notifications', {
      params: { customer_id: customerId }
    });
    return response.data;
  } catch {
    const response = await storeApi.get(`/customers/${customerId}/notifications`);
    return response.data;
  }
};

export const markNotificationAsRead = async (customerId, notificationId) => {
  try {
    const response = await storeApi.post(`/store/notifications/${notificationId}/read`, {}, {
      params: { customer_id: customerId }
    });
    return response.data;
  } catch {
    const response = await storeApi.post(`/customers/${customerId}/notifications/${notificationId}/read`);
    return response.data;
  }
};

export const markAllNotificationsAsRead = async (customerId) => {
  try {
    const response = await storeApi.post('/store/notifications/read-all', {}, {
      params: { customer_id: customerId }
    });
    return response.data;
  } catch {
    const response = await storeApi.post(`/customers/${customerId}/notifications/read-all`);
    return response.data;
  }
};

// Store Administrator Console API
export const getAdminOverview = async () => {
  const response = await storeApi.get('/store/admin/overview');
  return response.data;
};

export const createAdminAccount = async (payload) => {
  const response = await storeApi.post('/store/admin/create-admin', payload);
  return response.data;
};

export const getStaffUsers = async () => {
  const response = await storeApi.get('/store/admin/staff-users');
  return response.data;
};

export const deleteStaffUser = async (userId) => {
  const response = await storeApi.delete(`/store/admin/staff-users/${userId}`);
  return response.data;
};

export const bulkRestockInventory = async () => {
  const response = await storeApi.post('/store/admin/bulk-restock');
  return response.data;
};

export const getAdminOrders = async (params = {}) => {
  const response = await storeApi.get('/store/admin/orders', { params });
  return response.data;
};

export const updateOrderStatus = async (orderId, status) => {
  const response = await storeApi.put(`/store/admin/orders/${orderId}/status`, { status });
  return response.data;
};

export const grantCustomerPerk = async (payload) => {
  const response = await storeApi.post('/store/admin/grant-perk', payload);
  return response.data;
};

export default storeApi;
