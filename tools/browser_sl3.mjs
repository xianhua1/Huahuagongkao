// 验证：真表格答题卡（一字一格）+ 管理页题目可编辑
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-sl3'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9236', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1600,1000', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9236/json')).json()
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

// 进入申论刷题 → 第一套
await send('Page.navigate', { url: 'http://127.0.0.1:8090/practice/shenlun' })
await sleep(4000)
await ev(`(() => { const c = document.querySelector('.sl-card'); c && c.click(); return true })()`)
await sleep(4000)

// 答题卡结构检查
const cells = await ev(`document.querySelectorAll('.answer-card .cell').length`)
const firstCell = await ev(`(() => { const c = document.querySelector('.cell input'); return c ? { w: c.style.width, max: c.maxLength, type: c.type } : 'none' })()`)
const marks = await ev(`[...document.querySelectorAll('.mark')].map(m => m.innerText)`)
const rows = await ev(`(() => { const g = document.querySelector('.grid-container'); return g ? getComputedStyle(g).gridTemplateColumns : '' })()`)
console.log('格子总数:', cells, '| 每行格数列:', rows, '| 首格属性:', JSON.stringify(firstCell), '| 字数标记:', JSON.stringify(marks.slice(0, 4)))

// 模拟逐格输入（第一格输入"政"，验证自动跳格）
await ev(`(() => {
  const inp = document.querySelector('.cell input')
  const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set
  setter.call(inp, '政')
  inp.dispatchEvent(new Event('input', { bubbles: true }))
  return document.activeElement === document.querySelectorAll('.cell input')[1]
})()`)
await sleep(400)
const focusJump = await ev(`document.activeElement === document.querySelectorAll('.cell input')[1]`)
console.log('输入后自动跳到下一格:', focusJump)

// 退格回跳测试
await ev(`(() => {
  const inp = document.querySelectorAll('.cell input')[1]
  const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set
  setter.call(inp, '')
  inp.dispatchEvent(new Event('input', { bubbles: true }))
  inp.dispatchEvent(new KeyboardEvent('keydown', { key: 'Backspace', bubbles: true }))
  return true
})()`)
await sleep(400)
const backJump = await ev(`document.activeElement === document.querySelectorAll('.cell input')[0]`)
console.log('退格回到上一格:', backJump)
console.log('shot ->', await shot('sl-table'))

// 管理页题目可编辑
await send('Page.navigate', { url: 'http://127.0.0.1:8090/exam/shenlun-manage' })
await sleep(4000)
await ev(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.includes('材料与题目')); b && b.click(); return true })()`)
await sleep(3000)
await ev(`(() => { const t = [...document.querySelectorAll('.el-tabs__item')].find(x => x.innerText.includes('题目')); t && t.click(); return true })()`)
await sleep(1500)
const hasAddQ = await ev(`[...document.querySelectorAll('button')].some(x => x.innerText.includes('新增题目'))`)
const hasEditQ = await ev(`[...document.querySelectorAll('button')].some(x => x.innerText.includes('编辑'))`)
console.log('管理页: 新增题目按钮:', hasAddQ, '| 题目编辑按钮:', hasEditQ)

ws.close()
edge.kill()
process.exit(0)
