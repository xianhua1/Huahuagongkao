// 综合验证：登录 → 时政速递(新闻简讯) → 申论素材(范文) → 截图
import { spawn } from 'node:child_process'
import fs from 'node:fs'

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
const PORT = 9225
const OUT = 'C:\\Users\\admin\\DSH\\tools\\'
const sleep = ms => new Promise(r => setTimeout(r, ms))

fs.rmSync(OUT + 'edge-check4', { recursive: true, force: true })
const edge = spawn(EDGE, [
  '--headless=new', `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${OUT}edge-check4`, '--no-first-run', '--disable-gpu', '--no-proxy-server',
  '--window-size=1500,950', 'about:blank'
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
const shot = async name => {
  const r = await send('Page.captureScreenshot', { format: 'png' })
  fs.writeFileSync(OUT + 'shot-' + name + '.png', Buffer.from(r.data, 'base64'))
  return OUT + 'shot-' + name + '.png'
}

await send('Page.enable')
await send('Runtime.enable')
await send('Network.enable')

// 登录
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
    return inputs.length;
  })()
`)
await sleep(500)
await evalJs(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.replace(/\\s/g, '').includes('登录')); if (b) b.click(); return true })()`)
await sleep(6000)
console.log('logged in:', await evalJs('location.href'))

// 1) 时政速递：新闻简讯
await send('Page.navigate', { url: 'http://127.0.0.1:8090/prep/shizheng' })
await sleep(9000)
const sz = await evalJs('document.body.innerText.slice(0, 900)')
console.log('--- shizheng ---')
console.log(sz.replace(/\n+/g, ' | ').slice(0, 600))
console.log('shot ->', await shot('u1-shizheng'))
const newsCardCount = await evalJs(`document.querySelectorAll('.news-card').length`)
const briefSample = await evalJs(`(() => { const el = document.querySelector('.news-card .nc-brief'); return el ? el.innerText.slice(0, 80) : '' })()`)
console.log('news cards:', newsCardCount, '| brief sample:', briefSample)

// 2) 申论素材：范文
await send('Page.navigate', { url: 'http://127.0.0.1:8090/prep/sucai' })
await sleep(6000)
const sc = await evalJs('document.body.innerText.slice(0, 800)')
console.log('--- sucai ---')
console.log(sc.replace(/\n+/g, ' | ').slice(0, 500))
console.log('shot ->', await shot('u2-sucai'))
const fwCount = await evalJs(`document.querySelectorAll('.fw-card').length`)
const fwOpen = await evalJs(`(() => { const el = document.querySelector('.fw-text'); return el ? el.innerText.slice(0, 60) : '' })()`)
console.log('fanwen cards:', fwCount, '| first text:', fwOpen)

// 3) 每日一练（渐变头部）
await send('Page.navigate', { url: 'http://127.0.0.1:8090/prep/daily' })
await sleep(5000)
console.log('shot ->', await shot('u3-daily'))

// 4) 速记卡片
await send('Page.navigate', { url: 'http://127.0.0.1:8090/prep/cards' })
await sleep(5000)
console.log('shot ->', await shot('u4-cards'))

// 网络错误
const bad = events.filter(e => e.method === 'Network.responseReceived' && (e.params.response || {}).status >= 400).map(e => e.params.response.status + ' ' + e.params.response.url)
const fails = events.filter(e => e.method === 'Network.loadingFailed').map(e => (e.params || {}).errorText)
console.log('bad status:', JSON.stringify(bad.slice(0, 8)))
console.log('failures:', JSON.stringify(fails.slice(0, 8)))

ws.close()
edge.kill()
process.exit(0)
