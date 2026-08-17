// 无头浏览器模拟：打开登录页 → 填表 → 点登录 → 截图 + 收集网络失败
import { spawn } from 'node:child_process'
import fs from 'node:fs'

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
const PORT = 9222
const OUT = 'C:\\Users\\admin\\DSH\\tools\\'
const sleep = ms => new Promise(r => setTimeout(r, ms))

// 清理上次的用户数据目录
fs.rmSync(OUT + 'edge-check', { recursive: true, force: true })

const edge = spawn(EDGE, [
  '--headless=new',
  `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${OUT}edge-check`,
  '--no-first-run',
  '--disable-gpu',
  '--no-proxy-server',
  '--window-size=1400,900',
  'about:blank'
], { stdio: 'ignore' })

async function getTarget() {
  for (let i = 0; i < 40; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${PORT}/json`)
      const list = await res.json()
      const page = list.find(t => t.type === 'page')
      if (page) return page
    } catch { /* retry */ }
    await sleep(500)
  }
  throw new Error('CDP target timeout')
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
    if (m.error) p.reject(new Error(m.error.message))
    else p.resolve(m.result)
    pending.delete(m.id)
  } else if (m.method) {
    events.push(m)
  }
}

await new Promise((resolve, reject) => {
  ws.onopen = resolve
  ws.onerror = reject
})

const evalJs = async expr => {
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true })
  return r && r.result ? r.result.value : undefined
}

const shot = async name => {
  const r = await send('Page.captureScreenshot', { format: 'png' })
  fs.writeFileSync(OUT + 'shot-' + name + '.png', Buffer.from(r.data, 'base64'))
  return OUT + 'shot-' + name + '.png'
}

await send('Page.enable')
await send('Network.enable')
await send('Runtime.enable')

// 1) 打开站点
console.log('navigating...')
await send('Page.navigate', { url: 'http://127.0.0.1:8090/' })
let ready = false
for (let i = 0; i < 40; i++) {
  await sleep(500)
  const s = await evalJs('document.readyState')
  const hasLogin = await evalJs(`document.body && document.body.innerText.includes('登录')`)
  if (s === 'complete' && hasLogin) { ready = true; break }
}
console.log('login page ready:', ready)
if (!ready) {
  const t = await evalJs('document.body ? document.body.innerText.slice(0, 300) : "NO BODY"')
  console.log('page text:', t)
}
await sleep(1200)
console.log('screenshot login page ->', await shot('1-login'))

// 2) 填写账号密码
const inputCount = await evalJs(`
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
console.log('filled inputs:', inputCount)
await sleep(600)

// 3) 点击登录（按钮文字可能是"登 录"带空格）
const clicked = await evalJs(`
  (() => {
    const btn = [...document.querySelectorAll('button')].find(x => x.innerText.replace(/\\s/g, '').includes('登录'));
    if (btn) { btn.click(); return true; }
    const b2 = document.querySelector('.login-btn');
    if (b2) { b2.click(); return 'fallback'; }
    return false;
  })()
`)
console.log('login clicked:', clicked)

// 4) 等待跳转/结果（最多 30 秒）
let finalUrl = ''
let loginSpinning = false
for (let i = 0; i < 30; i++) {
  await sleep(1000)
  finalUrl = await evalJs('location.href')
  const btnText = await evalJs(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.includes('登录')); return b ? b.innerText : '' })()`)
  if (btnText.includes('登录中') || btnText.includes('加载中')) loginSpinning = true
  if (!finalUrl.includes('/login')) break
}
await sleep(3000)
console.log('final url:', finalUrl)
const bodyText = await evalJs('document.body ? document.body.innerText.slice(0, 500) : ""')
console.log('body:', bodyText.replace(/\n+/g, ' | '))
console.log('screenshot after login ->', await shot('2-after-login'))

// 6) 登录成功后访问「备考中心」页面
await send('Page.navigate', { url: 'http://127.0.0.1:8090/prep' })
await sleep(6000)
const prepUrl = await evalJs('location.href')
const prepText = await evalJs('document.body ? document.body.innerText.slice(0, 600) : ""')
console.log('prep url:', prepUrl)
console.log('prep body:', prepText.replace(/\n+/g, ' | '))
console.log('screenshot prep ->', await shot('3-prep'))
// 每日一练随机题是否加载
const dailyText = await evalJs('document.body ? document.body.innerText.slice(0, 900) : ""')
console.log('daily check:', dailyText.includes('正在为你挑选') ? 'loading' : (dailyText.includes('材料') || dailyText.includes('常识判断') || dailyText.includes('下一题') ? 'loaded' : 'unknown'))
const bad2 = events.filter(e => e.method === 'Network.responseReceived' && (e.params.response || {}).status >= 400).map(e => e.params.response.status + ' ' + e.params.response.url)
console.log('prep bad status:', JSON.stringify(bad2.slice(0, 10)))
console.log('screenshot prep2 ->', await shot('4-prep-loaded'))

// 5) 网络诊断
const failures = events.filter(e => e.method === 'Network.loadingFailed').map(e => {
  const p = e.params || {}
  return p.errorText + ' ' + (p.requestId || '')
})
const badStatus = events
  .filter(e => e.method === 'Network.responseReceived' && (e.params.response || {}).status >= 400)
  .map(e => e.params.response.status + ' ' + e.params.response.url)
console.log('network failures:', JSON.stringify(failures.slice(0, 10)))
console.log('bad status:', JSON.stringify(badStatus.slice(0, 10)))
console.log('pending requests:', events.filter(e => e.method === 'Network.requestWillBeSent').length - events.filter(e => e.method === 'Network.responseReceived' || e.method === 'Network.loadingFailed').length)

ws.close()
edge.kill()
process.exit(0)
