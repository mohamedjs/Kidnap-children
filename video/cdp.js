// Tiny Chrome DevTools Protocol client (Node 22+, no dependencies).
// Drives the Mic Clean window for screenshots and screen recordings.
'use strict';

async function connect(port, match = () => true) {
  let pages = [];
  for (let i = 0; i < 60 && !pages.length; i++) {
    try { pages = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).filter((p) => p.type === 'page' && match(p)); } catch {}
    if (!pages.length) await new Promise((r) => setTimeout(r, 500));
  }
  if (!pages.length) throw new Error('no page on the DevTools port');
  const ws = new WebSocket(pages[0].webSocketDebuggerUrl);
  await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
  let id = 0; const waiting = new Map(); const listeners = [];
  ws.onmessage = (m) => {
    const d = JSON.parse(m.data);
    if (d.id && waiting.has(d.id)) { const { res, rej } = waiting.get(d.id); waiting.delete(d.id); d.error ? rej(new Error(d.error.message)) : res(d.result); }
    else if (d.method) listeners.forEach((f) => f(d));
  };
  const send = (method, params = {}) => new Promise((res, rej) => { const n = ++id; waiting.set(n, { res, rej }); ws.send(JSON.stringify({ id: n, method, params })); });
  const evaluate = async (expr) => {
    const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true, userGesture: true });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text);
    return r.result.value;
  };
  const shot = async (file, opts = {}) => {
    const r = await send('Page.captureScreenshot', { format: 'png', ...opts });
    require('fs').writeFileSync(file, Buffer.from(r.data, 'base64'));
  };
  return { send, evaluate, shot, on: (f) => listeners.push(f), close: () => ws.close() };
}

module.exports = { connect };
