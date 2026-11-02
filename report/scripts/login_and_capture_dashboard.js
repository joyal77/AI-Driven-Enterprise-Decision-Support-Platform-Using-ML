const fs = require('fs');
const http = require('http');

async function getJson(url) {
  return new Promise((res, rej) => {
    http.get(url, r => {
      let d = '';
      r.on('data', c => d += c);
      r.on('end', () => res(JSON.parse(d)));
    }).on('error', rej);
  });
}

(async () => {
  const pages = await getJson('http://127.0.0.1:9222/json/list');
  const target = pages.find(p => p.type === 'page') || pages[0];
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise(r => ws.onopen = r);

  let id = 1;
  const send = (method, params = {}) => new Promise((res, rej) => {
    const curId = id++;
    const handler = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.id === curId) {
        ws.removeEventListener('message', handler);
        if (msg.error) rej(msg.error);
        else res(msg.result);
      }
    };
    ws.addEventListener('message', handler);
    ws.send(JSON.stringify({ id: curId, method, params }));
  });

  await send('Emulation.setDeviceMetricsOverride', {
    width: 1440,
    height: 960,
    deviceScaleFactor: 1,
    mobile: false
  });

  console.log('Navigating to login?tab=admin...');
  await send('Page.navigate', { url: 'http://127.0.0.1:5173/login?tab=admin' });
  await new Promise(r => setTimeout(r, 1500));

  console.log('Clicking Use Demo Account and Sign In...');
  await send('Runtime.evaluate', {
    expression: `(() => {
      const demoBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Use Demo Account'));
      if (demoBtn) demoBtn.click();
    })()`
  });

  await new Promise(r => setTimeout(r, 500));

  await send('Runtime.evaluate', {
    expression: `(() => {
      const signInBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Sign In');
      if (signInBtn) signInBtn.click();
    })()`
  });

  await new Promise(r => setTimeout(r, 3500));

  console.log('Capturing executive dashboard...');
  const { data } = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('report/assets/screenshots/executive_dashboard.png', Buffer.from(data, 'base64'));
  console.log('Saved executive_dashboard.png (' + fs.statSync('report/assets/screenshots/executive_dashboard.png').size + ' bytes)');
  ws.close();
})().catch(console.error);
