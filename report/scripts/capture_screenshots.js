const fs = require('fs');
const path = require('path');
const http = require('http');

async function getJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(JSON.parse(data)));
    }).on('error', reject);
  });
}

function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

class CDPClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.ws = null;
    this.id = 1;
    this.callbacks = new Map();
  }

  async connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.wsUrl);
      this.ws.onopen = () => resolve();
      this.ws.onerror = reject;
      this.ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.id && this.callbacks.has(msg.id)) {
          const { resolve, reject } = this.callbacks.get(msg.id);
          this.callbacks.delete(msg.id);
          if (msg.error) reject(msg.error);
          else resolve(msg.result);
        }
      };
    });
  }

  async send(method, params = {}) {
    const id = this.id++;
    return new Promise((resolve, reject) => {
      this.callbacks.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  close() {
    if (this.ws) this.ws.close();
  }
}

async function run() {
  const screenshotsDir = path.resolve(__dirname, '../assets/screenshots');
  if (!fs.existsSync(screenshotsDir)) {
    fs.mkdirSync(screenshotsDir, { recursive: true });
  }

  console.log('Querying Chrome pages...');
  const pages = await getJson('http://127.0.0.1:9222/json/list');
  const targetPage = pages.find(p => p.type === 'page') || pages[0];
  if (!targetPage) {
    throw new Error('No page target found');
  }

  console.log('Connecting to page:', targetPage.webSocketDebuggerUrl);
  const client = new CDPClient(targetPage.webSocketDebuggerUrl);
  await client.connect();

  await client.send('Page.enable');
  await client.send('DOM.enable');
  await client.send('Emulation.setDeviceMetricsOverride', {
    width: 1366,
    height: 768,
    deviceScaleFactor: 1,
    mobile: false
  });

  // Helper to capture a page
  async function capture(url, outFilename, setupFn, delayMs = 2500) {
    console.log(`Navigating to ${url}...`);
    await client.send('Page.navigate', { url });
    await wait(1500);

    if (setupFn) {
      await client.send('Runtime.evaluate', { expression: `(${setupFn.toString()})()` });
      await wait(1000);
    }

    await wait(delayMs);
    console.log(`Capturing screenshot -> ${outFilename}`);
    const { data } = await client.send('Page.captureScreenshot', { format: 'png' });
    const filePath = path.join(screenshotsDir, outFilename);
    fs.writeFileSync(filePath, Buffer.from(data, 'base64'));
    console.log(`Saved ${outFilename} (${Math.round(fs.statSync(filePath).size / 1024)} KB)`);
  }

  // 1. Login Page
  await capture('http://127.0.0.1:5173/login', 'login_screen.png');

  // 2. SmartCart Home
  await capture('http://127.0.0.1:5173/store', 'smartcart_home.png', () => {
    localStorage.setItem('store_user', JSON.stringify({
      id: 5,
      username: 'AMZ_PRED1_1001',
      role: 'customer',
      customer_id: 1,
      full_name: 'Customer AMZ_PRED1_1001'
    }));
  });

  // 3. Product Catalog
  await capture('http://127.0.0.1:5173/store/catalog', 'product_catalog.png');

  // 4. Product Detail (first product)
  await capture('http://127.0.0.1:5173/store/product/1', 'product_detail.png');

  // 5. Shopping Cart
  await capture('http://127.0.0.1:5173/store/cart', 'shopping_cart.png');

  // 6. Checkout Page
  await capture('http://127.0.0.1:5173/store/checkout', 'checkout_confirmation.png');

  // 7. Customer Orders
  await capture('http://127.0.0.1:5173/store/my-orders', 'customer_orders.png');

  // 8. Customer Notifications & Perks
  await capture('http://127.0.0.1:5173/store/notifications', 'customer_notifications.png');

  // 9. Admin Product Management
  await capture('http://127.0.0.1:5173/store/manage-products', 'admin_product_manager.png', () => {
    localStorage.setItem('store_user', JSON.stringify({
      id: 2,
      username: 'admin',
      role: 'admin',
      full_name: 'Platform Administrator'
    }));
  });

  // Set Admin session for Executive Platform
  const setAdminSession = () => {
    localStorage.setItem('user', JSON.stringify({
      id: 1,
      name: 'Platform Administrator',
      email: 'admin@ecommerce.com',
      role: 'admin'
    }));
    localStorage.setItem('token', 'mock_or_valid_admin_token');
  };

  // 10. Executive Dashboard
  await capture('http://127.0.0.1:5173/dashboard', 'executive_dashboard.png', setAdminSession, 3000);

  // 11. Customer Churn Analytics & Risk Table
  await capture('http://127.0.0.1:5173/churn-prediction', 'customer_churn_analytics.png', setAdminSession, 3000);

  // 12. SHAP Waterfall Explanation & Modal (simulate click or open customer 1 modal)
  await capture('http://127.0.0.1:5173/churn-prediction', 'shap_explanation.png', () => {
    // Attempt to click first customer row or open modal if available
    const rows = document.querySelectorAll('tr.cursor-pointer, tbody tr, .customer-row');
    if (rows && rows.length > 0) {
      rows[0].click();
    }
  }, 2500);

  // 13. Sales Forecasting Charts
  await capture('http://127.0.0.1:5173/sales-forecast', 'sales_forecast.png', setAdminSession, 3500);

  // 14. Dataset Upload & Model Evaluation
  await capture('http://127.0.0.1:5173/upload', 'dataset_upload.png', setAdminSession, 2500);

  console.log('All screenshots captured successfully!');
  client.close();
}

run().catch(err => {
  console.error('Error during screenshot capture:', err);
  process.exit(1);
});

