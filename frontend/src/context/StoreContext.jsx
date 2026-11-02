import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import {
  getDemoCustomers,
  storeLogin,
  recordCustomerLogin,
  getStoreCart,
  addStoreCartItem,
  updateStoreCartQuantity,
  removeStoreCartItem,
  clearStoreCart,
  getCustomerPerks,
  getCustomerNotifications,
  markNotificationAsRead,
  markAllNotificationsAsRead
} from '../services/storeApi';

const StoreContext = createContext();

export const getCartStorageKey = (user) => {
  if (!user) return 'smartcart_cart_guest';
  const idStr = user.username || user.customer_id || user.id;
  return `smartcart_cart_${idStr}`;
};

export const StoreProvider = ({ children }) => {
  // Store user: { id, username, role: 'customer' | 'product_manager' | 'admin', full_name, customer_id, membership_status }
  const [storeUser, setStoreUser] = useState(() => {
    try {
      const saved = localStorage.getItem('smartcart_user');
      if (saved) return JSON.parse(saved);
    } catch (e) {
      console.error(e);
    }
    // Default demo customer login
    return {
      id: 5,
      username: 'AMZ_PRED1_1001',
      role: 'customer',
      full_name: 'Customer AMZ_PRED1_1001',
      customer_id: 1,
      membership_status: 'none',
      preferred_category: 'Electronics'
    };
  });

  // User-isolated cart state initialized strictly from current user's isolated storage
  const [cartItems, setCartItems] = useState(() => {
    try {
      const savedUserStr = localStorage.getItem('smartcart_user');
      const savedUser = savedUserStr ? JSON.parse(savedUserStr) : null;
      const key = getCartStorageKey(savedUser || { username: 'AMZ_PRED1_1001', customer_id: 1 });
      const savedCart = localStorage.getItem(key);
      if (savedCart) return JSON.parse(savedCart);
    } catch (e) {
      console.error(e);
    }
    return [];
  });

  const [demoCustomers, setDemoCustomers] = useState([]);
  const [loadingDemoCustomers, setLoadingDemoCustomers] = useState(false);
  const isInitialMount = useRef(true);

  // Retention Perks & Customer Account Features
  const [customerPerks, setCustomerPerks] = useState({
    walletBalance: 0,
    activeVouchers: [],
    hasExpressShipping: false,
    hasPrimeTrial: false,
    hasVipSupport: false,
    approvedActions: []
  });
  const [notifications, setNotifications] = useState([]);
  const [unreadNotificationsCount, setUnreadNotificationsCount] = useState(0);
  const [useWalletCredit, setUseWalletCredit] = useState(true);
  const [appliedVoucher, setAppliedVoucher] = useState(null);

  const refreshCustomerPerks = async (cid) => {
    const targetId = cid || storeUser?.customer_id || storeUser?.id || storeUser?.username;
    if (!targetId) {
      setCustomerPerks({
        walletBalance: 0,
        activeVouchers: [],
        hasExpressShipping: false,
        hasPrimeTrial: false,
        hasVipSupport: false,
        approvedActions: []
      });
      setNotifications([]);
      setUnreadNotificationsCount(0);
      return;
    }
    try {
      const data = await getCustomerPerks(targetId);
      if (data && data.success) {
        const freshVouchers = Array.isArray(data.active_vouchers) ? data.active_vouchers : [];
        setCustomerPerks({
          walletBalance: Number(data.wallet_balance || 0),
          activeVouchers: freshVouchers,
          hasExpressShipping: Boolean(data.has_express_shipping),
          hasPrimeTrial: Boolean(data.has_prime_trial),
          hasVipSupport: Boolean(data.has_vip_support),
          approvedActions: Array.isArray(data.approved_actions) ? data.approved_actions : []
        });

        // Auto-clear applied voucher if no longer present in fresh active vouchers
        setAppliedVoucher((curr) => {
          if (!curr) return null;
          const currCode = (curr.code || curr.voucher_code || '').toUpperCase();
          const isStillActive = freshVouchers.some(
            (v) => (v.code || v.voucher_code || '').toUpperCase() === currCode
          );
          return isStillActive ? curr : null;
        });

        const notifsList = Array.isArray(data.notifications) ? data.notifications : [];
        setNotifications(notifsList);
        const unread = typeof data.unread_count === 'number'
          ? data.unread_count
          : notifsList.filter((n) => !n.is_read).length;
        setUnreadNotificationsCount(unread);

        // If Prime trial was granted, update user membership status
        if (data.has_prime_trial && storeUser && storeUser.membership_status !== 'Prime') {
          setStoreUser((prev) => (prev ? { ...prev, membership_status: 'Prime' } : prev));
        }
      }
    } catch (err) {
      console.warn('[Perks Sync] Could not fetch customer retention perks:', err?.message);
    }
  };

  const markNotificationRead = async (notifId) => {
    const targetId = storeUser?.customer_id || storeUser?.id || storeUser?.username;
    if (!targetId || !notifId) return;
    try {
      await markNotificationAsRead(targetId, notifId);
      setNotifications((prev) =>
        prev.map((n) => (n.id === notifId ? { ...n, is_read: true } : n))
      );
      setUnreadNotificationsCount((prev) => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Failed to mark notification as read:', err);
    }
  };

  const markAllNotificationsRead = async () => {
    const targetId = storeUser?.customer_id || storeUser?.id || storeUser?.username;
    if (!targetId) return;
    try {
      await markAllNotificationsAsRead(targetId);
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadNotificationsCount(0);
    } catch (err) {
      console.error('Failed to mark all notifications as read:', err);
    }
  };

  const refreshNotifications = async () => {
    const targetId = storeUser?.customer_id || storeUser?.id || storeUser?.username;
    if (!targetId) return;
    try {
      const res = await getCustomerNotifications(targetId);
      if (res && res.success) {
        setNotifications(res.notifications || []);
        setUnreadNotificationsCount(res.unread_count || 0);
      }
    } catch (err) {
      console.error('Failed to load notifications:', err);
    }
  };

  // Sync active user to localStorage
  useEffect(() => {
    if (storeUser) {
      localStorage.setItem('smartcart_user', JSON.stringify(storeUser));
    } else {
      localStorage.removeItem('smartcart_user');
    }
  }, [storeUser]);

  // When storeUser changes, switch cart strictly to THAT specific account's cart and refresh perks
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      // On first load, sync from backend if customer
      if (storeUser?.customer_id) {
        syncCartFromBackend(storeUser.customer_id, getCartStorageKey(storeUser));
        refreshCustomerPerks(storeUser.customer_id);
      }
      return;
    }

    if (!storeUser) {
      setCartItems([]);
      setCustomerPerks({
        walletBalance: 0,
        activeVouchers: [],
        hasExpressShipping: false,
        hasPrimeTrial: false,
        hasVipSupport: false,
        approvedActions: []
      });
      setAppliedVoucher(null);
      return;
    }

    const userKey = getCartStorageKey(storeUser);
    let cachedCart = [];
    try {
      const saved = localStorage.getItem(userKey);
      if (saved) cachedCart = JSON.parse(saved);
    } catch (e) {
      console.error(e);
    }
    setCartItems(cachedCart);

    if (storeUser.customer_id) {
      syncCartFromBackend(storeUser.customer_id, userKey);
      refreshCustomerPerks(storeUser.customer_id);
    }
  }, [storeUser?.username, storeUser?.customer_id]);

  // Sync cart items to user-specific storage key whenever cart changes
  useEffect(() => {
    if (storeUser) {
      const userKey = getCartStorageKey(storeUser);
      localStorage.setItem(userKey, JSON.stringify(cartItems));
    }
  }, [cartItems, storeUser?.username, storeUser?.customer_id]);

  useEffect(() => {
    fetchDemoCustomers();
  }, []);

  const syncCartFromBackend = async (customerId, storageKey) => {
    try {
      const res = await getStoreCart(customerId);
      if (res && res.success && Array.isArray(res.items)) {
        setCartItems(res.items);
        localStorage.setItem(storageKey, JSON.stringify(res.items));
      }
    } catch (err) {
      // Backend cart sync optional fallback if network error
      console.warn('[Cart Sync] Could not fetch backend cart for customer:', customerId, err?.message);
    }
  };

  const fetchDemoCustomers = async () => {
    setLoadingDemoCustomers(true);
    try {
      const data = await getDemoCustomers();
      setDemoCustomers(data.customers || []);
    } catch (err) {
      console.error('Failed to load demo customers:', err);
    } finally {
      setLoadingDemoCustomers(false);
    }
  };

  // Switch customer account directly (e.g. from the top bar dropdown or account switcher)
  const switchCustomerAccount = (customerObj) => {
    const newUser = {
      id: customerObj.id,
      username: customerObj.source_customer_id,
      role: 'customer',
      full_name: `Customer ${customerObj.source_customer_id}`,
      customer_id: customerObj.id,
      membership_status: customerObj.membership_status || 'Standard',
      preferred_category: customerObj.preferred_category,
      risk_category: customerObj.risk_category,
      churn_probability: customerObj.churn_probability
    };

    // 1. Immediately switch to the new user's isolated local cart
    const newKey = getCartStorageKey(newUser);
    let newCachedCart = [];
    try {
      const saved = localStorage.getItem(newKey);
      if (saved) newCachedCart = JSON.parse(saved);
    } catch (e) {
      console.error(e);
    }

    setCartItems(newCachedCart);
    setAppliedVoucher(null);
    setStoreUser(newUser);

    // 2. Refresh from backend database for that specific customer & record active login
    if (newUser.customer_id) {
      recordCustomerLogin(newUser.customer_id).catch((err) =>
        console.warn('[Switch Account Record Login Warning]', err?.message)
      );
      syncCartFromBackend(newUser.customer_id, newKey);
      refreshCustomerPerks(newUser.customer_id);
    }
  };

  const loginAsRole = async (username, password) => {
    const data = await storeLogin(username, password);
    if (data.success && data.user) {
      const newUser = data.user;
      const newKey = getCartStorageKey(newUser);
      let userCart = [];
      try {
        const saved = localStorage.getItem(newKey);
        if (saved) userCart = JSON.parse(saved);
      } catch (e) {
        console.error(e);
      }
      setCartItems(userCart);
      setStoreUser(newUser);

      if (newUser.customer_id) {
        syncCartFromBackend(newUser.customer_id, newKey);
      }
      return newUser;
    }
    throw new Error(data.message || 'Login failed');
  };

  const loginDirectly = (newUser) => {
    const newKey = getCartStorageKey(newUser);
    localStorage.setItem('smartcart_user', JSON.stringify(newUser));
    setCartItems([]);
    setStoreUser(newUser);
    return newUser;
  };

  const logoutStore = () => {
    localStorage.removeItem('smartcart_user');
    setStoreUser(null);
    setCartItems([]);
  };

  // User-Isolated Cart Operations: strictly acts on active storeUser only
  const addToCart = async (product, quantity = 1) => {
    let updatedCart = [];
    setCartItems((prev) => {
      const existingIdx = prev.findIndex((item) => item.id === product.id);
      if (existingIdx > -1) {
        updatedCart = [...prev];
        updatedCart[existingIdx] = {
          ...updatedCart[existingIdx],
          quantity: (updatedCart[existingIdx].quantity || 1) + quantity
        };
      } else {
        updatedCart = [...prev, { ...product, quantity }];
      }
      if (storeUser) {
        localStorage.setItem(getCartStorageKey(storeUser), JSON.stringify(updatedCart));
      }
      return updatedCart;
    });

    if (storeUser?.customer_id) {
      try {
        await addStoreCartItem(storeUser.customer_id, product.id, quantity);
      } catch (err) {
        console.warn('[Cart] Failed to sync item addition to backend:', err?.message);
      }
    }
  };

  const updateCartQuantity = async (productId, newQty) => {
    if (newQty <= 0) {
      removeFromCart(productId);
      return;
    }

    let updatedCart = [];
    setCartItems((prev) => {
      updatedCart = prev.map((item) =>
        item.id === productId ? { ...item, quantity: newQty } : item
      );
      if (storeUser) {
        localStorage.setItem(getCartStorageKey(storeUser), JSON.stringify(updatedCart));
      }
      return updatedCart;
    });

    if (storeUser?.customer_id) {
      try {
        await updateStoreCartQuantity(storeUser.customer_id, productId, newQty);
      } catch (err) {
        console.warn('[Cart] Failed to sync quantity update to backend:', err?.message);
      }
    }
  };

  const removeFromCart = async (productId) => {
    let updatedCart = [];
    setCartItems((prev) => {
      updatedCart = prev.filter((item) => item.id !== productId);
      if (storeUser) {
        localStorage.setItem(getCartStorageKey(storeUser), JSON.stringify(updatedCart));
      }
      return updatedCart;
    });

    if (storeUser?.customer_id) {
      try {
        await removeStoreCartItem(storeUser.customer_id, productId);
      } catch (err) {
        console.warn('[Cart] Failed to sync item removal to backend:', err?.message);
      }
    }
  };

  const clearCart = async () => {
    setCartItems([]);
    if (storeUser) {
      localStorage.setItem(getCartStorageKey(storeUser), JSON.stringify([]));
    }

    if (storeUser?.customer_id) {
      try {
        await clearStoreCart(storeUser.customer_id);
      } catch (err) {
        console.warn('[Cart] Failed to sync cart clear to backend:', err?.message);
      }
    }
  };

  const cartCount = cartItems.reduce((acc, item) => acc + (item.quantity || 1), 0);
  const cartSubtotal = cartItems.reduce(
    (acc, item) => acc + (item.price || 0) * (item.quantity || 1),
    0
  );

  return (
    <StoreContext.Provider
      value={{
        storeUser,
        setStoreUser,
        loginAsRole,
        loginDirectly,
        logoutStore,
        switchCustomerAccount,
        demoCustomers,
        loadingDemoCustomers,
        cartItems,
        addToCart,
        updateCartQuantity,
        removeFromCart,
        clearCart,
        cartCount,
        cartSubtotal,
        customerPerks,
        walletBalance: customerPerks.walletBalance,
        activeVouchers: customerPerks.activeVouchers,
        hasExpressShipping: customerPerks.hasExpressShipping,
        hasPrimeTrial: customerPerks.hasPrimeTrial,
        hasVipSupport: customerPerks.hasVipSupport,
        useWalletCredit,
        setUseWalletCredit,
        appliedVoucher,
        setAppliedVoucher,
        refreshCustomerPerks,
        notifications,
        unreadNotificationsCount,
        markNotificationRead,
        markAllNotificationsRead,
        refreshNotifications
      }}
    >
      {children}
    </StoreContext.Provider>
  );
};

export const useStore = () => {
  const context = useContext(StoreContext);
  if (!context) {
    throw new Error('useStore must be used within a StoreProvider');
  }
  return context;
};
