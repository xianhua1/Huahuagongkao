// 验证行测助手新题型：基础练习/资料专项/舒尔特方格/数字谜题
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-aide-v'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9281', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1600,1000', 'about:blank'
], { stdio: 'ignore' })
let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9281/json')).json()
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
const shot = async n => {
  const r = await send('Page.captureScreenshot', { format: 'png' })
  fs.writeFileSync(`C:\\Users\\admin\\DSH\\tools\\shot-aide-v-${n}.png`, Buffer.from(r.data, 'base64'))
}

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

// 1) 基础练习默认
await goto('http://127.0.0.1:8090/prep/aide')
await sleep(1500)
const catTabs = await ev(`[...document.querySelectorAll('.cat-tab')].map(e => e.textContent.trim())`)
const typeItems = await ev(`[...document.querySelectorAll('.type-item')].map(e => e.textContent.trim())`)
console.log('分类:', catTabs.join('/'))
console.log('基础题型数:', typeItems.length, '=>', typeItems.join('/'))

// 点开始练习
await ev(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.includes('开始练习')); b && b.click(); return true })()`)
await sleep(1200)
const q1 = await ev(`document.querySelector('.p-question') && document.querySelector('.p-question').innerText`)
console.log('题1:', q1)

// 答对第一题（解析算式）
function solveExpr(expr) {
  // 处理 ＋ × ÷ - 及多位数
  const m = expr.match(/(-?\d+(?:\.\d+)?)\s*([＋+×÷\-])\s*(\d+(?:\.\d+)?)/)
  if (!m) return null
  const a = parseFloat(m[1]), b = parseFloat(m[3])
  switch (m[2]) {
    case '＋': case '+': return a + b
    case '×': return a * b
    case '÷': return a / b
    case '-': return a - b
  }
}
const expr = String(q1).replace(/ =$/, '')
const ans1 = solveExpr(expr)
console.log('计算答案:', ans1)
if (ans1 !== null) {
  await ev(`(() => {
    const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set
    const i = document.querySelector('.p-input')
    s.call(i, '${ans1}')
    i.dispatchEvent(new Event('input', { bubbles: true }))
    i.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }))
    return true
  })()`)
  await sleep(300)
  const fb = await ev(`document.querySelector('.p-feedback') && document.querySelector('.p-feedback').innerText`)
  console.log('反馈:', fb)
}

// 2) 资料专项 - 年平均量（图表）
await goto('http://127.0.0.1:8090/prep/aide')
await sleep(1500)
await ev(`(() => { const t = [...document.querySelectorAll('.cat-tab')].find(e => e.textContent.includes('资料专项')); t && t.click(); return true })()`)
await sleep(600)
await ev(`(() => { const t = [...document.querySelectorAll('.type-item')].find(e => e.textContent.includes('年平均量')); t && t.click(); return true })()`)
await sleep(400)
await ev(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.includes('开始练习')); b && b.click(); return true })()`)
await sleep(1500)
const hasChart = await ev(`!!document.querySelector('.chart-svg')`)
const chartQ = await ev(`document.querySelector('.chart-question') && document.querySelector('.chart-question').innerText`)
console.log('图表存在:', hasChart, '| 问题:', chartQ)

// 3) 舒尔特方格
await goto('http://127.0.0.1:8090/prep/aide')
await sleep(1500)
await ev(`(() => { const t = [...document.querySelectorAll('.cat-tab')].find(e => e.textContent.includes('其他训练')); t && t.click(); return true })()`)
await sleep(600)
const otherTypes = await ev(`[...document.querySelectorAll('.type-item')].map(e => e.textContent.trim())`)
console.log('其他训练题型:', otherTypes.join('/'))
await ev(`(() => { const t = [...document.querySelectorAll('.type-item')].find(e => e.textContent.includes('舒尔特方格')); t && t.click(); return true })()`)
await sleep(400)
await ev(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.includes('开始练习')); b && b.click(); return true })()`)
await sleep(1200)
const gridCells = await ev(`document.querySelectorAll('.s-cell').length`)
console.log('舒尔特方格格子数:', gridCells)
// 点击 1
await ev(`(() => { const c = [...document.querySelectorAll('.s-cell')].find(x => x.textContent.trim() === '1'); c && c.click(); return true })()`)
await sleep(300)
const nextNum = await ev(`document.querySelector('.s-tip') && document.querySelector('.s-tip').innerText`)
console.log('点击1后提示:', nextNum)

// 4) 数字谜题
await goto('http://127.0.0.1:8090/prep/aide')
await sleep(1500)
await ev(`(() => { const t = [...document.querySelectorAll('.cat-tab')].find(e => e.textContent.includes('其他训练')); t && t.click(); return true })()`)
await sleep(600)
await ev(`(() => { const t = [...document.querySelectorAll('.type-item')].find(e => e.textContent.includes('数字谜题')); t && t.click(); return true })()`)
await sleep(400)
await ev(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.includes('开始练习')); b && b.click(); return true })()`)
await sleep(1200)
const rule = await ev(`document.querySelector('.m-rule') && document.querySelector('.m-rule').innerText.slice(0, 60)`)
console.log('谜题规则:', rule)
await ev(`(() => {
  const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set
  const i = document.querySelector('.m-input')
  s.call(i, '1234')
  i.dispatchEvent(new Event('input', { bubbles: true }))
  const b = [...document.querySelectorAll('button')].find(x => x.innerText.trim() === '猜')
  b && b.click()
  return true
})()`)
await sleep(800)
const hist = await ev(`document.querySelector('.m-row') && document.querySelector('.m-row').innerText`)
console.log('第一次猜测反馈:', hist)

await shot('final')
await edge.kill()
process.exit(0)
