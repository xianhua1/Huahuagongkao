// 验证：新菜单结构 + 翻译练习/测验模式修复 + 万能模板
import { spawn } from 'node:child_process'
import fs from 'node:fs'

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
const PORT = 9226
const OUT = 'C:\\Users\\admin\\DSH\\tools\\'
const sleep = ms => new Promise(r => setTimeout(r, ms))

fs.rmSync(OUT + 'edge-check5', { recursive: true, force: true })
const edge = spawn(EDGE, [
  '--headless=new', `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${OUT}edge-check5`, '--no-first-run', '--disable-gpu', '--no-proxy-server',
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
  })()
`)
await sleep(500)
await evalJs(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.replace(/\\s/g, '').includes('登录')); if (b) b.click(); return true })()`)
await sleep(6000)

// 1) 侧边栏菜单结构
const menu = await evalJs(`
  [...document.querySelectorAll('.el-sub-menu__title, .el-menu-item')].map(el => el.innerText.trim().replace(/\\n/g, '')).filter(Boolean).slice(0, 45)
`)
console.log('SIDEBAR:', JSON.stringify(menu))

// 2) 规范词：切到翻译练习（应自动出题）
await send('Page.navigate', { url: 'http://127.0.0.1:8090/prep/guifan' })
await sleep(5000)
await evalJs(`(() => { const r = [...document.querySelectorAll('.el-radio-button')].find(x => x.innerText.includes('翻译练习')); if (r) r.click(); return !!r })()`)
await sleep(1500)
const gfQuiz = await evalJs(`(() => { const el = document.querySelector('.quiz-question'); return el ? el.innerText.slice(0, 60) : 'NO QUIZ' })()`)
const gfOpts = await evalJs(`document.querySelectorAll('.quiz-opt').length`)
console.log('GUIFAN quiz question:', gfQuiz, '| options:', gfOpts)
console.log('shot ->', await shot('v1-guifan-quiz'))

// 3) 成语：切到测验模式（应自动出题）
await send('Page.navigate', { url: 'http://127.0.0.1:8090/prep/chengyu' })
await sleep(5000)
await evalJs(`(() => { const r = [...document.querySelectorAll('.el-radio-button')].find(x => x.innerText.includes('测验')); if (r) r.click(); return !!r })()`)
await sleep(1500)
const cyQuiz = await evalJs(`(() => { const el = document.querySelector('.quiz-question'); return el ? el.innerText.slice(0, 60) : 'NO QUIZ' })()`)
const cyOpts = await evalJs(`document.querySelectorAll('.quiz-opt').length`)
console.log('CHENGYU quiz question:', cyQuiz, '| options:', cyOpts)
console.log('shot ->', await shot('v2-chengyu-quiz'))

// 4) 申论素材：万能模板板块
await send('Page.navigate', { url: 'http://127.0.0.1:8090/prep/sucai' })
await sleep(5000)
await evalJs(`(() => { const el = [...document.querySelectorAll('.theme-tab')].find(x => x.innerText.includes('万能模板')); if (el) { el.click(); return true } return false })()`)
await sleep(1500)
const mbCount = await evalJs(`document.querySelectorAll('.fw-card').length`)
const mbFirst = await evalJs(`(() => { const el = document.querySelector('.fw-title'); return el ? el.innerText : '' })()`)
const mbOpen = await evalJs(`(() => { const el = document.querySelector('.mb-text'); return el ? el.innerText.slice(0, 60) : '' })()`)
console.log('MOBAN cards:', mbCount, '| first:', mbFirst, '| open text:', mbOpen)
console.log('shot ->', await shot('v3-moban'))

// 5) 每日一练新路径 /practice/daily
await send('Page.navigate', { url: 'http://127.0.0.1:8090/practice/daily' })
await sleep(5000)
const dailyUrl = await evalJs('location.href')
const dailyOk = await evalJs(`document.body.innerText.includes('每日一练') && document.body.innerText.includes('常识判断')`)
console.log('DAILY at /practice/daily:', dailyUrl, '| renders:', dailyOk)
console.log('shot ->', await shot('v4-daily'))

// 6) 学习计划 /plan、学习报告 /report 独立页面
await send('Page.navigate', { url: 'http://127.0.0.1:8090/plan' })
await sleep(4500)
console.log('PLAN page:', await evalJs('document.body.innerText.includes("90 天学习计划")'))
await send('Page.navigate', { url: 'http://127.0.0.1:8090/report' })
await sleep(4500)
console.log('REPORT page:', await evalJs('document.body.innerText.includes("学习报告")'))
console.log('shot ->', await shot('v5-report'))

// 网络错误
const bad = events.filter(e => e.method === 'Network.responseReceived' && (e.params.response || {}).status >= 400).map(e => e.params.response.status + ' ' + e.params.response.url)
const fails = events.filter(e => e.method === 'Network.loadingFailed').map(e => (e.params || {}).errorText)
console.log('bad status:', JSON.stringify(bad.slice(0, 8)))
console.log('failures:', JSON.stringify(fails.slice(0, 8)))

ws.close()
edge.kill()
process.exit(0)
