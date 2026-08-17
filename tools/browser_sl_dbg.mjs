// 诊断：直接访问 /practice/shenlun，抓 console 错误与网络请求
import { spawn } from 'node:child_process'
import fs from 'node:fs'

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
const PORT = 9229
const OUT = 'C:\\Users\\admin\\DSH\\tools\\'
const sleep = ms => new Promise(r => setTimeout(r, ms))

fs.rmSync(OUT + 'edge-dbg', { recursive: true, force: true })
const edge = spawn(EDGE, [
  '--headless=new', `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${OUT}edge-dbg`, '--no-first-run', '--disable-gpu', '--no-proxy-server', 'about:blank'
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

await send('Page.navigate', { url: 'http://127.0.0.1:8090/login?redirect=/index' })
await sleep(5000)
await evalJs(`
  (() => {
    const inputs = document.querySelectorAll('input');
    const setVal = (el, v) => {
      const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
      setter.call(el, v);
      el.dispatchEvent(new Event('input', { bubbles: true }));
    };
    if (inputs.length >= 2) { setVal(inputs[0], 'admin'); setVal(inputs[1], 'admin123'); }
  })()
`)
await sleep(400)
await evalJs(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.replace(/\\s/g, '').includes('登录')); if (b) b.click(); return true })()`)
await sleep(6000)
console.log('已登录:', await evalJs('location.href'))

// 直接导航到申论页
await send('Page.navigate', { url: 'http://127.0.0.1:8090/practice/shenlun' })
await sleep(5000)
console.log('URL:', await evalJs('location.href'))
console.log('页面文本:', (await evalJs('document.body.innerText.slice(0, 200)')).replace(/\n+/g, ' | '))

// 抓取 shenlun chunk 请求与失败
const chunkReqs = events.filter(e => e.method === 'Network.requestWillBeSent' && e.params.request.url.includes('shenlun')).map(e => e.params.request.url)
console.log('shenlun 请求:', JSON.stringify(chunkReqs))
const fails = events.filter(e => e.method === 'Network.loadingFailed').map(e => (e.params.errorText || '') + ' ' + (e.params.requestId || ''))
console.log('加载失败:', JSON.stringify(fails.slice(0, 8)))
const exceptions = events.filter(e => e.method === 'Runtime.exceptionThrown').map(e => {
  const d = e.params.exceptionDetails || {}
  return (d.exception ? d.exception.description || d.exception.value : d.text || '') + ' @' + (d.url || '') + ':' + d.lineNumber
})
console.log('JS异常:', JSON.stringify(exceptions.slice(0, 6)))

ws.close()
edge.kill()
process.exit(0)
