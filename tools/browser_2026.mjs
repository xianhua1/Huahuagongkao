// 验证 2026 卷在项目中可用（列表/做题/图片/材料/判分）
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-2026'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9254', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1600,1000', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9254/json')).json()
    target = l.find(t => t.type === 'page')
    if (target) break
  } catch { }
  await sleep(500)
}
const ws = new WebSocket(target.webSocketDebuggerUrl)
let id = 0
const pend = new Map()
const events = []
const send = (m, p = {}) => new Promise((res, rej) => {
  const i = ++id
  pend.set(i, { res, rej })
  ws.send(JSON.stringify({ id: i, method: m, params: p }))
})
ws.onmessage = ev => {
  const m = JSON.parse(ev.data)
  if (m.id && pend.has(m.id)) { pend.get(m.id).res(m.result); pend.delete(m.id) }
  else if (m.method) events.push(m)
}
await new Promise(r => ws.onopen = r)
const ev = async e => {
  try {
    const r = await send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true })
    return r && r.result ? r.result.value : undefined
  } catch { return undefined }
}
const shot = async n => {
  const r = await send('Page.captureScreenshot', { format: 'png' })
  fs.writeFileSync(`C:\\Users\\admin\\DSH\\tools\\shot-${n}.png`, Buffer.from(r.data, 'base64'))
}

await send('Page.enable')
await send('Runtime.enable')
await send('Network.enable')
await send('Page.navigate', { url: 'http://127.0.0.1:8090/login?redirect=/index' })
await sleep(5000)
await ev(`(() => {
  const i = document.querySelectorAll('input')
  const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set
  s.call(i[0], 'admin'); i[0].dispatchEvent(new Event('input', { bubbles: true }))
  s.call(i[1], 'admin123'); i[1].dispatchEvent(new Event('input', { bubbles: true }))
})()`)
await sleep(400)
await ev(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.replace(/\\s/g, '').includes('登录')); b && b.click(); return true })()`)
await sleep(7000)

// 试卷练习页
await send('Page.navigate', { url: 'http://127.0.0.1:8090/practice/papers' })
await sleep(5000)
const has2026 = await ev(`document.body.innerText.includes('2026年国家公务员录用考试')`)
console.log('列表含2026卷:', has2026)

// 打开 2026 卷（找包含2026的试卷卡点击）
await ev(`(() => {
  const cards = [...document.querySelectorAll('*')].filter(e => e.children.length === 0 && e.textContent.includes('2026年国家公务员录用考试'))
  const el = cards[cards.length - 1]
  if (el) {
    // 找到卡片容器点击
    let p = el
    for (let i = 0; i < 5 && p; i++) { p = p.parentElement; if (p && p.onclick === null && p.className && String(p.className).includes('paper')) { p.click(); break } }
    el.click()
    return true
  }
  return false
})()`)
await sleep(5000)
const url = await ev('location.href')
console.log('打开后 URL:', url)

// 题目渲染检查
const qText = await ev(`document.body.innerText.slice(0, 300)`)
console.log('页面:', qText.replace(/\n+/g, ' | ').slice(0, 220))
const imgCount = await ev(`document.querySelectorAll('img[src*="exam-img"]').length`)
console.log('题目图片数:', imgCount)
const imgOk = await ev(`(() => { const imgs = [...document.querySelectorAll('img[src*="exam-img"]')]; return imgs.length ? imgs[0].naturalWidth : -1 })()`)
console.log('首图加载宽度:', imgOk)

// 材料面板
const matPanel = await ev(`document.querySelectorAll('.material-box, .mat-panel, [class*="material"]').length`)
console.log('材料元素数:', matPanel)

console.log('shot ->', await shot('2026-work'))

// 图片 HTTP 验证
const bad = events.filter(e => e.method === 'Network.responseReceived' && (e.params.response || {}).status >= 400).map(e => e.params.response.status + ' ' + e.params.response.url)
console.log('4xx/5xx:', JSON.stringify(bad.slice(0, 6)))
ws.close()
edge.kill()
process.exit(0)
