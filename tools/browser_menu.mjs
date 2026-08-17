// 验证：登录 → 侧边栏展开备考中心 → 点击子菜单 → 检查页面
import { spawn } from 'node:child_process'
import fs from 'node:fs'

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
const PORT = 9224
const OUT = 'C:\\Users\\admin\\DSH\\tools\\'
const sleep = ms => new Promise(r => setTimeout(r, ms))

fs.rmSync(OUT + 'edge-check3', { recursive: true, force: true })
const edge = spawn(EDGE, [
  '--headless=new', `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${OUT}edge-check3`, '--no-first-run', '--disable-gpu', '--no-proxy-server',
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
console.log('after login url:', await evalJs('location.href'))

// 侧边栏菜单结构
const sidebarMenus = await evalJs(`
  [...document.querySelectorAll('.el-sub-menu__title, .el-menu-item')].map(el => el.innerText.trim().replace(/\\n/g, ' ')).filter(Boolean).slice(0, 40)
`)
console.log('sidebar:', JSON.stringify(sidebarMenus))

// 点击「备考中心」目录展开
await evalJs(`(() => { const el = [...document.querySelectorAll('.el-sub-menu__title')].find(x => x.innerText.replace(/\\s/g, '').includes('备考中心')); if (el) { el.click(); return true } return false })()`)
await sleep(1000)
const expanded = await evalJs(`
  [...document.querySelectorAll('.el-menu-item')].map(el => el.innerText.trim()).filter(Boolean)
`)
console.log('expanded children:', JSON.stringify(expanded))

// 点击「每日一练」
await evalJs(`(() => { const el = [...document.querySelectorAll('.el-menu-item')].find(x => x.innerText.replace(/\\s/g, '').includes('每日一练')); if (el) { el.click(); return true } return false })()`)
await sleep(6000)
console.log('daily url:', await evalJs('location.href'))
const dailyText = await evalJs('document.body.innerText.slice(0, 400)')
console.log('daily body:', dailyText.replace(/\n+/g, ' | ').slice(0, 300))
console.log('shot ->', await shot('m1-daily'))

// 点击「时政速递」（含实时资讯）
await evalJs(`(() => { const el = [...document.querySelectorAll('.el-menu-item')].find(x => x.innerText.replace(/\\s/g, '').includes('时政速递')); if (el) { el.click(); return true } return false })()`)
await sleep(8000)
console.log('shizheng url:', await evalJs('location.href'))
const szText = await evalJs('document.body.innerText.slice(0, 700)')
console.log('shizheng body:', szText.replace(/\n+/g, ' | ').slice(0, 500))
console.log('shot ->', await shot('m2-shizheng'))

// 点击「学习报告」
await evalJs(`(() => { const el = [...document.querySelectorAll('.el-menu-item')].find(x => x.innerText.replace(/\\s/g, '').includes('学习报告')); if (el) { el.click(); return true } return false })()`)
await sleep(5000)
console.log('report url:', await evalJs('location.href'))
const rpText = await evalJs('document.body.innerText.slice(0, 300)')
console.log('report body:', rpText.replace(/\n+/g, ' | ').slice(0, 250))
console.log('shot ->', await shot('m3-report'))

// 网络错误统计
const bad = events.filter(e => e.method === 'Network.responseReceived' && (e.params.response || {}).status >= 400).map(e => e.params.response.status + ' ' + e.params.response.url)
const fails = events.filter(e => e.method === 'Network.loadingFailed').map(e => (e.params || {}).errorText)
console.log('bad status:', JSON.stringify(bad.slice(0, 8)))
console.log('failures:', JSON.stringify(fails.slice(0, 8)))

ws.close()
edge.kill()
process.exit(0)
