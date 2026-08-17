// 验证：材料标注（选中文字 → 下划线/高亮 → 渲染 + 退出不保留）
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-mark'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9239', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1600,1000', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9239/json')).json()
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

// 展开材料1（默认展开），选择前 10 个字模拟标注
const selOk = await ev(`(() => {
  const full = document.querySelector('.sl-material-full')
  if (!full) return 'no-full'
  // 材料1 默认展开（openMat 初始包含全部材料 id）
  const text = full.textContent
  const range = document.createRange()
  range.setStart(full.firstChild || full, 0)
  range.setEnd(full.firstChild || full, Math.min(10, text.length))
  const sel = window.getSelection()
  sel.removeAllRanges()
  sel.addRange(range)
  full.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }))
  return text.slice(0, 10)
})()`)
console.log('选中文本:', selOk)
await sleep(500)
const tbShow = await ev(`!!document.querySelector('.mark-toolbar')`)
console.log('工具条显示:', tbShow)

// 点击下划线按钮
await ev(`(() => { const b = document.querySelector('.mt-btn'); if (b) b.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true })); return !!b })()`)
await sleep(500)
const hasU = await ev(`!!document.querySelector('.sl-material-full span[style*="underline"]')`)
const uText = await ev(`(() => { const s = document.querySelector('.sl-material-full span[style*="underline"]'); return s ? s.textContent.slice(0, 10) : 'none' })()`)
console.log('下划线 span 存在:', hasU, '| 内容:', uText)

// 再选一段加黄色高亮
await ev(`(() => {
  const full = document.querySelector('.sl-material-full')
  const text = full.textContent
  const range = document.createRange()
  range.setStart(full.firstChild || full, 20)
  range.setEnd(full.firstChild || full, 30)
  const sel = window.getSelection()
  sel.removeAllRanges()
  sel.addRange(range)
  full.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }))
  return true
})()`)
await sleep(500)
await ev(`(() => { const bs = [...document.querySelectorAll('.mt-color')]; if (bs.length) bs[0].dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true })); return bs.length })()`)
await sleep(500)
const hasY = await ev(`!!document.querySelector('.sl-material-full span[style*="fff59d"]')`)
console.log('黄色高亮 span 存在:', hasY)

console.log('shot ->', await shot('mark-final'))
ws.close()
edge.kill()
process.exit(0)
