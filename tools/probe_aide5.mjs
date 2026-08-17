// 探查 saduck 数字谜题交互
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-aide5'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9279', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1500,1100', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9279/json')).json()
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
const ev = async e => {
  try {
    const r = await send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true })
    return r && r.result ? r.result.value : undefined
  } catch { return undefined }
}

await send('Page.enable')
await send('Runtime.enable')
await send('Page.navigate', { url: 'https://www.saduck.top/my/getAide.html' })
await sleep(6000)

// 点击数字谜题
await ev(`(() => {
  const items = [...document.querySelectorAll('.el-menu-item')]
  const it = items.find(i => i.textContent.trim() === '数字谜题')
  if (it) { it.click(); return true }
  return false
})()`)
await sleep(2500)

// 点击开始练习
await ev(`(() => {
  const b = [...document.querySelectorAll('button')].find(x => x.textContent.trim() === '开始练习')
  if (b) { b.click(); return true }
  return false
})()`)
await sleep(2500)

const t = await ev(`document.body.innerText`)
console.log('=== 数字谜题 开始后 ===')
console.log(t.slice(400, 2800))

// 找输入框/按钮
const inputs = await ev(`(() => {
  const out = []
  document.querySelectorAll('input, [class*="cell"], [class*="grid"], [class*="num"], [class*="box"]').forEach(e => {
    const cls = String(e.className).slice(0, 50)
    if (cls) out.push({ tag: e.tagName, cls, val: e.value !== undefined ? e.value : '', txt: (e.textContent || '').trim().slice(0, 20) })
  })
  return out.slice(0, 30)
})()`)
console.log('=== 元素 ===')
console.log(JSON.stringify(inputs, null, 1))

ws.close()
edge.kill()
process.exit(0)
