// 验证错题本所有行展开情况 + 测试点击行本身是否可展开
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-wrong2'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9295', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1600,1000', 'about:blank'
], { stdio: 'ignore' })
let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9295/json')).json()
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
const goto = async url => { await send('Page.navigate', { url }); await sleep(4000) }

await send('Page.enable')
await send('Runtime.enable')
await goto('http://127.0.0.1:8090/login?redirect=/index')
await ev(`(() => {
  const i = document.querySelectorAll('input')
  const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set
  s.call(i[0], 'admin'); i[0].dispatchEvent(new Event('input', { bubbles: true }))
  s.call(i[1], 'admin123'); i[1].dispatchEvent(new Event('input', { bubbles: true }))
})()`)
await sleep(400)
await ev(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.replace(/\\s/g, '').includes('登录')); b && b.click(); return true })()`)
await sleep(6000)
await goto('http://127.0.0.1:8090/practice/wrong')
await sleep(5000)

const rowCount = await ev(`document.querySelectorAll('.el-table__body tr').length`)
console.log('表格行数:', rowCount)

// 1) 逐行点击展开箭头
let okRows = 0
for (let i = 0; i < Math.min(rowCount, 15); i++) {
  await ev(`(() => {
    const rows = document.querySelectorAll('.el-table__body tr')
    const r = rows[${i}]
    const icon = r.querySelector('.el-table__expand-icon')
    if (icon) { icon.click(); return true }
    return false
  })()`)
  await sleep(800)
  const hasDetail = await ev(`!!document.querySelector('.wrong-detail')`)
  if (hasDetail) okRows++
  // 收起
  await ev(`(() => {
    const rows = document.querySelectorAll('.el-table__body tr')
    const r = rows[${i}]
    const icon = r.querySelector('.el-table__expand-icon')
    if (icon) icon.click()
    return true
  })()`)
  await sleep(500)
}
console.log('箭头展开成功行数:', okRows)

// 2) 测试点击行本身（非箭头）能否展开
await ev(`(() => {
  const rows = document.querySelectorAll('.el-table__body tr')
  const r = rows[0]
  // 点击行内容区域（题干单元格）
  const cell = r.querySelectorAll('td')[2]
  cell.click()
  return true
})()`)
await sleep(1000)
const detailAfterRowClick = await ev(`!!document.querySelector('.wrong-detail')`)
console.log('点击行本身后展开:', detailAfterRowClick)

await edge.kill()
process.exit(0)
