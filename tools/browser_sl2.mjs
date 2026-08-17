// 验证：申论页无AI设置入口、真表格答题卡、管理页题目只读
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-sl2'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9235', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1600,1000', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9235/json')).json()
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

// 申论刷题页
await send('Page.navigate', { url: 'http://127.0.0.1:8090/practice/shenlun' })
await sleep(4000)
const hasAiBtn = await ev(`[...document.querySelectorAll('button')].some(x => x.innerText.includes('AI 评分设置'))`)
console.log('AI设置按钮已移除:', !hasAiBtn)
// 进入试卷
await ev(`(() => { const c = document.querySelector('.sl-card'); c && c.click(); return true })()`)
await sleep(4000)
const cellStyle = await ev(`(() => { const t = document.querySelector('.sl-cells'); if (!t) return 'none'; const cs = getComputedStyle(t); return 'fontSize=' + cs.fontSize + ' lineHeight=' + cs.lineHeight + ' letterSpacing=' + cs.letterSpacing + ' color=' + cs.color })()`)
console.log('答题卡样式:', cellStyle)
await ev(`(() => {
  const ta = document.querySelector('.sl-cells')
  const s = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set
  s.call(ta, '政府服务要撤掉眼中的柜台，更要撤掉心中的柜台，转变观念服务群众。')
  ta.dispatchEvent(new Event('input', { bubbles: true }))
})()`)
await sleep(600)
const count = await ev(`(() => { const bar = document.querySelector('.sl-cellbar'); return bar ? bar.innerText : '' })()`)
console.log('字数统计:', count)
console.log('shot ->', await shot('sl-final'))

// 管理页题目只读
await send('Page.navigate', { url: 'http://127.0.0.1:8090/exam/shenlun-manage' })
await sleep(4000)
await ev(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.includes('材料与题目')); b && b.click(); return true })()`)
await sleep(3000)
await ev(`(() => { const t = [...document.querySelectorAll('.el-tabs__item')].find(x => x.innerText.includes('题目')); t && t.click(); return true })()`)
await sleep(1500)
const hasAddQ = await ev(`[...document.querySelectorAll('button')].some(x => x.innerText.includes('新增题目'))`)
const qRows = await ev(`document.querySelectorAll('.el-table__row').length`)
console.log('管理页: 新增题目按钮存在:', hasAddQ, '| 题目行数:', qRows)
console.log('shot ->', await shot('sl-mg-final'))

ws.close()
edge.kill()
process.exit(0)
