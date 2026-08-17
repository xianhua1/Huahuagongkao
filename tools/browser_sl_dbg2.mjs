// 抓 console 警告：点击申论刷题后看 vue-router 匹配日志
import { spawn } from 'node:child_process'
import fs from 'node:fs'

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
const PORT = 9230
const OUT = 'C:\\Users\\admin\\DSH\\tools\\'
const sleep = ms => new Promise(r => setTimeout(r, ms))

fs.rmSync(OUT + 'edge-dbg2', { recursive: true, force: true })
const edge = spawn(EDGE, [
  '--headless=new', `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${OUT}edge-dbg2`, '--no-first-run', '--disable-gpu', '--no-proxy-server',
  '--window-size=1600,1000', 'about:blank'
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
await send('Log.enable')

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
await sleep(7000)
console.log('登录后:', await evalJs('location.href'))

// 展开刷题中心，点击申论刷题
await evalJs(`(() => { const el = [...document.querySelectorAll('.el-sub-menu__title')].find(x => x.innerText.replace(/\\s/g, '').includes('刷题中心')); if (el) { el.click(); return true } return false })()`)
await sleep(800)
const items = await evalJs(`[...document.querySelectorAll('.el-menu-item')].map(x => x.innerText.trim())`)
console.log('可见菜单项:', JSON.stringify(items))
const clicked = await evalJs(`(() => { const el = [...document.querySelectorAll('.el-menu-item')].find(x => x.innerText.replace(/\\s/g, '').includes('申论刷题')); if (el) { el.click(); return true } return false })()`)
console.log('点击:', clicked)
await sleep(4000)
console.log('URL:', await evalJs('location.href'))
console.log('页面文本:', (await evalJs('document.body.innerText.slice(0, 150)')).replace(/\n+/g, ' | '))

// 收集 console 消息（warning/error）
const consoles = events.filter(e => e.method === 'Runtime.consoleAPICalled').map(e => {
  const t = e.params.type
  const args = (e.params.args || []).map(a => a.value || a.description || '').join(' ')
  return t + ': ' + args.slice(0, 300)
}).filter(x => /warn|error|No match/i.test(x))
console.log('相关console:', JSON.stringify(consoles.slice(0, 8)))
const logEntries = events.filter(e => e.method === 'Log.entryAdded').map(e => (e.params.entry || {}).text || '').filter(t => /match|warn|error/i.test(t))
console.log('Log条目:', JSON.stringify(logEntries.slice(0, 8)))

// 手动 import chunk 测试
const chunkOk = await evalJs(`fetch('/assets/shenlun-ldVEYHiI.js').then(r => r.status + ' ' + r.headers.get('content-type')).catch(e => 'ERR ' + e)`)
console.log('chunk fetch:', chunkOk)

ws.close()
edge.kill()
process.exit(0)
