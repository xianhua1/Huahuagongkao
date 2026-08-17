// 深度诊断：监控 JS 异常 + XHR/fetch 调用 + 按钮状态
import { spawn } from 'node:child_process'
import fs from 'node:fs'

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
const PORT = 9223
const OUT = 'C:\\Users\\admin\\DSH\\tools\\'
const sleep = ms => new Promise(r => setTimeout(r, ms))

fs.rmSync(OUT + 'edge-check2', { recursive: true, force: true })
const edge = spawn(EDGE, [
  '--headless=new', `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${OUT}edge-check2`, '--no-first-run', '--disable-gpu', '--no-proxy-server',
  '--window-size=1400,900', 'about:blank'
], { stdio: 'ignore' })

async function getTarget() {
  for (let i = 0; i < 40; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${PORT}/json`)
      const list = await res.json()
      const page = list.find(t => t.type === 'page')
      if (page) return page
    } catch { }
    await sleep(500)
  }
  throw new Error('timeout')
}

const target = await getTarget()
const ws = new WebSocket(target.webSocketDebuggerUrl)
let msgId = 0
const pending = new Map()
const events = []

function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++msgId
    pending.set(id, { resolve, reject })
    ws.send(JSON.stringify({ id, method, params }))
  })
}
ws.onmessage = ev => {
  const m = JSON.parse(ev.data)
  if (m.id && pending.has(m.id)) {
    const p = pending.get(m.id)
    if (m.error) p.reject(new Error(m.error.message)); else p.resolve(m.result)
    pending.delete(m.id)
  } else if (m.method) events.push(m)
}
await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject })

const evalJs = async expr => {
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true })
  return r && r.result ? r.result.value : undefined
}

await send('Page.enable')
await send('Runtime.enable')
await send('Network.enable')

// 预注入：监控 XHR/fetch/console/异常
await evalJs(`
  window.__xhr = [];
  const oOpen = XMLHttpRequest.prototype.open, oSend = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function(m, u) { this.__u = u; return oOpen.apply(this, arguments); };
  XMLHttpRequest.prototype.send = function() {
    window.__xhr.push({ url: this.__u, t: Date.now() });
    return oSend.apply(this, arguments);
  };
  window.__fetch = [];
  const oFetch = window.fetch;
  window.fetch = function(u, o) { window.__fetch.push({ url: String(u), t: Date.now() }); return oFetch.apply(this, arguments); };
  window.__errors = [];
  window.addEventListener('error', e => window.__errors.push('error: ' + e.message));
  window.addEventListener('unhandledrejection', e => window.__errors.push('unhandledrejection: ' + String(e.reason && e.reason.message || e.reason)));
  true;
`)

await send('Page.navigate', { url: 'http://127.0.0.1:8090/login?redirect=/index' })
await sleep(6000)

// 填表
await evalJs(`
  (() => {
    const inputs = document.querySelectorAll('input');
    const setVal = (el, v) => {
      const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
      setter.call(el, v);
      el.dispatchEvent(new Event('input', { bubbles: true }));
    };
    if (inputs.length >= 2) { setVal(inputs[0], 'admin'); setVal(inputs[1], 'admin123'); }
    return inputs.length;
  })()
`)
await sleep(800)

// 点击前状态
console.log('before click: xhr calls =', await evalJs('window.__xhr.length'))
console.log('before click: fetch calls =', await evalJs('window.__fetch.length'))

// 点击登录
const clicked = await evalJs(`
  (() => {
    const btn = [...document.querySelectorAll('button')].find(x => x.innerText.replace(/\\s/g, '').includes('登录'));
    if (btn) { btn.click(); return true; }
    return false;
  })()
`)
console.log('clicked:', clicked)

// 5 秒后查看
await sleep(5000)
console.log('--- 5s after click ---')
console.log('url:', await evalJs('location.href'))
console.log('xhr calls:', JSON.stringify(await evalJs('window.__xhr')))
console.log('fetch calls:', JSON.stringify(await evalJs('window.__fetch')))
console.log('js errors:', JSON.stringify(await evalJs('window.__errors')))
console.log('button text:', await evalJs(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.replace(/\\s/g, '').includes('登录')); return b ? b.innerText : 'none' })()`))
console.log('page err text:', await evalJs(`(() => { const els = [...document.querySelectorAll('.el-message, .el-message__content')]; return els.map(e => e.innerText).join('; ') })()`))

// 15 秒后再次查看
await sleep(10000)
console.log('--- 15s after click ---')
console.log('url:', await evalJs('location.href'))
console.log('xhr calls:', JSON.stringify(await evalJs('window.__xhr')))
console.log('js errors:', JSON.stringify(await evalJs('window.__errors')))
console.log('button text:', await evalJs(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.replace(/\\s/g, '').includes('登录')); return b ? b.innerText : 'none' })()`))

// CDP 侧异常事件
const exceptions = events.filter(e => e.method === 'Runtime.exceptionThrown').map(e => {
  const d = e.params.exceptionDetails || {}
  return (d.exception ? d.exception.description || d.exception.value : d.text || '') + ' @' + (d.url || '') + ':' + d.lineNumber
})
console.log('CDP exceptions:', JSON.stringify(exceptions.slice(0, 5)))
const consoles = events.filter(e => e.method === 'Runtime.consoleAPICalled').map(e => (e.params.type || '') + ': ' + (e.params.args || []).map(a => a.value || a.description || '').join(' '))
console.log('console:', JSON.stringify(consoles.slice(-15)))

ws.close()
edge.kill()
process.exit(0)
