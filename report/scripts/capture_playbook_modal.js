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

  console.log('Scrolling down in modal...');
  await send('Runtime.evaluate', {
    expression: `(() => {
      const modal = document.querySelector('[style*="overflow-y"], .modal-content, [style*="position: fixed"] > div');
      if (modal) {
        modal.scrollTop = 450;
      } else {
        window.scrollBy(0, 450);
      }
    })()`
  });

  await new Promise(r => setTimeout(r, 2000));

  console.log('Capturing retention playbook screenshot...');
  const { data } = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('report/assets/screenshots/retention_playbook_modal.png', Buffer.from(data, 'base64'));
  console.log('Saved retention_playbook_modal.png');
  ws.close();
})().catch(console.error);

