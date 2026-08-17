// 打开 2026 卷并验证做题全流程
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-2026c'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9256', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1600,1000', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9256/json')).json()
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
await send('Page.navigate', { url: 'http://127.0.0.1:8090/practice/papers' })
await sleep(5000)

// 点击 2026 卡片里的"开始"按钮
const clicked = await ev(`(() => {
  const cards = [...document.querySelectorAll('.paper-card')]
  const card = cards.find(c => c.textContent.includes('2026'))
  if (!card) return false
  const btn = card.querySelector('button')
  if (btn) { btn.click(); return 'btn' }
  card.click()
  return 'card'
})()`)
console.log('点击:', clicked)
await sleep(6000)
console.log('URL:', await ev('location.href'))

const bodyText = await ev(`document.body.innerText.slice(0, 500)`)
console.log('页面:', bodyText.replace(/\n+/g, ' | ').slice(0, 300))

// 图片
const imgInfo = await ev(`(() => {
  const imgs = [...document.querySelectorAll('img[src*="exam-img"]')]
  return JSON.stringify({ count: imgs.length, loaded: imgs.filter(i => i.complete && i.naturalWidth > 0).length })
})()`)
console.log('题目图片:', imgInfo)

// 材料（资料分析题会显示材料面板）
const matInfo = await ev(`(() => {
  const mats = [...document.querySelectorAll('[class*="material"]')]
  return mats.length
})()`)
console.log('材料元素:', matInfo)

// 答一题（第一个选项）
await ev(`(() => { const opt = document.querySelector('.q-opt, .option-item, [class*="opt"]'); opt && opt.click(); return !!opt })()`)
await sleep(1500)
const judged = await ev(`document.body.innerText.includes('解析') || document.body.innerText.includes('正确') || document.body.innerText.includes('错误')`)
console.log('判分结果展示:', judged)

console.log('shot ->', await shot('2026-final'))
const bad = events.filter(e => e.method === 'Network.responseReceived' && (e.params.response || {}).status >= 400).map(e => e.params.response.status + ' ' + e.params.response.url)
console.log('4xx/5xx:', JSON.stringify(bad.slice(0, 8)))
ws.close()
edge.kill()
process.exit(0)
