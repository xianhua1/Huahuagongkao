// 验证申论刷题页：菜单 → 列表 → 作答页 → 答题卡
import { spawn } from 'node:child_process'
import fs from 'node:fs'

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
const PORT = 9228
const OUT = 'C:\\Users\\admin\\DSH\\tools\\'
const sleep = ms => new Promise(r => setTimeout(r, ms))

fs.rmSync(OUT + 'edge-sl', { recursive: true, force: true })
const edge = spawn(EDGE, [
  '--headless=new', `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${OUT}edge-sl`, '--no-first-run', '--disable-gpu', '--no-proxy-server',
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
const shot = async name => {
  const r = await send('Page.captureScreenshot', { format: 'png' })
  fs.writeFileSync(OUT + 'shot-' + name + '.png', Buffer.from(r.data, 'base64'))
}

await send('Page.enable')
await send('Runtime.enable')

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

// 点击「申论刷题」菜单
const clicked = await evalJs(`(() => { const el = [...document.querySelectorAll('.el-menu-item')].find(x => x.innerText.replace(/\\s/g, '').includes('申论刷题')); if (el) { el.click(); return true } return false })()`)
console.log('clicked 申论刷题:', clicked)
await sleep(4500)
console.log('URL:', await evalJs('location.href'))
const listText = await evalJs(`document.body.innerText.slice(0, 400)`)
console.log('列表页:', listText.replace(/\n+/g, ' | ').slice(0, 250))
console.log('shot ->', await shot('sl1-list'))

// 进入第一套试卷
await evalJs(`(() => { const card = document.querySelector('.sl-card'); if (card) { card.click(); return true } return false })()`)
await sleep(4000)
const workText = await evalJs(`document.body.innerText.slice(0, 700)`)
console.log('作答页:', workText.replace(/\n+/g, ' | ').slice(0, 450))
const cellCount = await evalJs(`document.querySelectorAll('.sl-cells').length`)
const matCount = await evalJs(`document.querySelectorAll('.sl-material').length`)
console.log('答题卡数:', cellCount, '| 材料数:', matCount)
console.log('shot ->', await shot('sl2-work'))

// 模拟输入第一题作答
await evalJs(`
  (() => {
    const ta = document.querySelector('.sl-cells');
    if (ta) {
      const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
      setter.call(ta, 'N市通过绿色通道快速兑现补贴，推出免申即享服务，实现政策找人，搭建亲清家园平台，实现跨省通办。');
      ta.dispatchEvent(new Event('input', { bubbles: true }));
      return ta.value.length;
    }
    return -1;
  })()
`)
await sleep(800)
const charCount = await evalJs(`(() => { const bar = document.querySelector('.sl-cellbar span'); return bar ? bar.innerText : '' })()`)
console.log('字数统计:', charCount)
console.log('shot ->', await shot('sl3-typed'))

// 交卷保存按钮
await evalJs(`(() => { const btns = [...document.querySelectorAll('button')]; const b = btns.find(x => x.innerText.includes('交卷保存')); if (b) { b.click(); return true } return false })()`)
await sleep(2500)
const toast = await evalJs(`(() => { const m = document.querySelector('.el-message'); return m ? m.innerText : '' })()`)
console.log('交卷提示:', toast)

// 检查菜单「申论管理」存在（管理员）
const adminMenu = await evalJs(`[...document.querySelectorAll('.el-menu-item')].some(x => x.innerText.includes('申论管理'))`)
console.log('申论管理菜单:', adminMenu)

const bad = events.filter(e => e.method === 'Network.responseReceived' && (e.params.response || {}).status >= 400).map(e => e.params.response.status + ' ' + e.params.response.url)
console.log('bad status:', JSON.stringify(bad.slice(0, 6)))

ws.close()
edge.kill()
process.exit(0)
