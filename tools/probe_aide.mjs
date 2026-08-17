// 探查 saduck 行测助手页面完整题型结构
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-aide'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9271', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1500,1100', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9271/json')).json()
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
  fs.writeFileSync(`C:\\Users\\admin\\DSH\\tools\\shot-aide-${n}.png`, Buffer.from(r.data, 'base64'))
}

await send('Page.enable')
await send('Runtime.enable')
await send('Network.enable')

// 行测助手页
await send('Page.navigate', { url: 'https://www.saduck.top/my/getAide.html' })
await sleep(6000)
await shot('1-main')
const txt = await ev(`document.body.innerText`)
console.log('=== 页面全文 ===')
console.log(txt.slice(0, 3000))

// 找出 tab 元素并点击 资料专项
const tabs = await ev(`(() => {
  const els = [...document.querySelectorAll('*')].filter(e => e.children.length <= 1 && /资料专项|其他训练|基础练习/.test(e.textContent || '') && (e.textContent || '').trim().length < 20)
  return els.slice(0, 10).map(e => ({ tag: e.tagName, cls: e.className, txt: e.textContent.trim() }))
})()`)
console.log('=== tab 候选元素 ===')
console.log(JSON.stringify(tabs, null, 1))

// 点击资料专项
await ev(`(() => {
  const els = [...document.querySelectorAll('*')].filter(e => e.children.length <= 1 && e.textContent.trim() === '资料专项')
  if (els.length) { els[0].click(); return 'clicked' }
  return 'not found'
})()`)
await sleep(2500)
await shot('2-ziliao')
const t2 = await ev(`document.body.innerText`)
console.log('=== 点击资料专项后 ===')
console.log(t2.slice(0, 2500))

// 点击其他训练
await ev(`(() => {
  const els = [...document.querySelectorAll('*')].filter(e => e.children.length <= 1 && e.textContent.trim() === '其他训练')
  if (els.length) { els[0].click(); return 'clicked' }
  return 'not found'
})()`)
await sleep(2500)
await shot('3-qita')
const t3 = await ev(`document.body.innerText`)
console.log('=== 点击其他训练后 ===')
console.log(t3.slice(0, 2500))

ws.close()
edge.kill()
process.exit(0)
