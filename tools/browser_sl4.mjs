// 验证：隐藏textarea方案答题卡（中文输入法兼容 + 光标 + 退格删除 + 点击定位）
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-sl4'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9237', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1600,1000', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9237/json')).json()
    target = l.find(t => t.type === 'page')
    if (target) break
  } catch { }
  await sleep(500)
}
const ws = new WebSocket(target.webSocketDebuggerUrl)
let id = 0
const pend = new Map()
const send = (m, p = {}) => new Promise((res, rej) => {
  const i = ++id
  pend.set(i, { res, rej })
  ws.send(JSON.stringify({ id: i, method: m, params: p }))
})
ws.onmessage = ev => {
  const m = JSON.parse(ev.data)
  if (m.id && pend.has(m.id)) { pend.get(m.id).res(m.result); pend.delete(m.id) }
}
await new Promise(r => ws.onopen = r)
const ev = async e => (await send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true })).result.value
const shot = async n => {
  const r = await send('Page.captureScreenshot', { format: 'png' })
  fs.writeFileSync(`C:\\Users\\admin\\DSH\\tools\\shot-${n}.png`, Buffer.from(r.data, 'base64'))
}

await send('Page.enable')
await send('Runtime.enable')
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

await send('Page.navigate', { url: 'http://127.0.0.1:8090/practice/shenlun' })
await sleep(4000)
await ev(`(() => { const c = document.querySelector('.sl-card'); c && c.click(); return true })()`)
await sleep(4000)

// 结构检查
const cellCount = await ev(`document.querySelectorAll('.answer-card .cell').length`)
const hiddenTa = await ev(`!!document.querySelector('.hidden-input')`)
const cursorExists = await ev(`!!document.querySelector('.cursor')`)
console.log('格子数:', cellCount, '| 隐藏textarea:', hiddenTa, '| 光标存在:', cursorExists)

// 通过隐藏 textarea 模拟输入（模拟中文输入法 composition 事件）
await ev(`(() => {
  const ta = document.querySelector('.hidden-input')
  ta.focus()
  // 模拟 composition 输入"政府"
  ta.dispatchEvent(new CompositionEvent('compositionstart', { bubbles: true }))
  const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set
  setter.call(ta, '政府')
  ta.dispatchEvent(new Event('input', { bubbles: true }))
  ta.dispatchEvent(new CompositionEvent('compositionend', { data: '政府', bubbles: true }))
  setter.call(ta, '')
  return true
})()`)
await sleep(500)
const afterInput = await ev(`[...document.querySelectorAll('.answer-card .cell')].slice(0, 2).map(c => c.innerText.trim())`)
const countTxt = await ev(`(() => { const b = document.querySelector('.count-info b'); return b ? b.innerText : '' })()`)
console.log('前两格内容:', JSON.stringify(afterInput), '| 字数:', countTxt)

// 模拟退格
await ev(`(() => {
  const ta = document.querySelector('.hidden-input')
  ta.dispatchEvent(new KeyboardEvent('keydown', { key: 'Backspace', bubbles: true }))
  return true
})()`)
await sleep(400)
const afterBack = await ev(`[...document.querySelectorAll('.answer-card .cell')].slice(0, 2).map(c => c.innerText.trim())`)
console.log('退格后前两格:', JSON.stringify(afterBack))

// 点击第 3 格定位光标
await ev(`(() => {
  const cells = document.querySelectorAll('.answer-card .cell')
  cells[2].click()
  return true
})()`)
await sleep(300)
const cursorAt = await ev(`(() => {
  const cells = document.querySelectorAll('.answer-card .cell')
  let idx = -1
  cells.forEach((c, i) => { if (c.querySelector('.cursor')) idx = i })
  return idx
})()`)
console.log('点击后光标在第', cursorAt, '格')

console.log('shot ->', await shot('sl-card-final'))
ws.close()
edge.kill()
process.exit(0)
