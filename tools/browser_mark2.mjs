// 完整验证：下划线 + 黄色高亮 + 叠加 + 清除
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-mark4'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9242', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9242/json')).json()
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

// 辅助：选中 full 内第 from..to 字符（跨文本节点）
const selRange = async (from, to) => ev(`(() => {
  try {
    const full = document.querySelector('.sl-material-full')
    if (!full) return 'no-full'
    const nodes = []
    const walker = document.createTreeWalker(full, NodeFilter.SHOW_TEXT)
    let n
    while ((n = walker.nextNode())) nodes.push(n)
    if (!nodes.length) return 'no-text'
    let acc = 0, startNode = null, startOff = 0, endNode = null, endOff = 0
    for (const node of nodes) {
      const len = node.textContent.length
      if (!startNode && ${from} >= acc && ${from} <= acc + len) { startNode = node; startOff = ${from} - acc }
      if (!endNode && ${to} >= acc && ${to} <= acc + len) { endNode = node; endOff = ${to} - acc }
      acc += len
      if (startNode && endNode) break
    }
    if (!startNode || !endNode) return 'range-fail'
    const range = document.createRange()
    range.setStart(startNode, startOff)
    range.setEnd(endNode, endOff)
    const sel = window.getSelection()
    sel.removeAllRanges()
    sel.addRange(range)
    full.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true }))
    return 'ok'
  } catch (err) { return 'ERR:' + err.message }
})()`)

// 1) 下划线 0-10
console.log('sel1:', await selRange(0, 10))
await sleep(500)
console.log('工具条:', await ev(`!!document.querySelector('.mark-toolbar')`))
await ev(`(() => { const b = document.querySelector('.mt-btn'); b && b.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true })); return !!b })()`)
await sleep(400)
// 2) 黄色高亮 15-25
await selRange(15, 25)
await sleep(500)
await ev(`(() => { const bs = [...document.querySelectorAll('.mt-color')]; bs[0] && bs[0].dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true })); return bs.length })()`)
await sleep(400)
// 3) 红色高亮 20-30（与黄色叠加部分区间）
await selRange(20, 30)
await sleep(500)
await ev(`(() => { const bs = [...document.querySelectorAll('.mt-color')]; bs[2] && bs[2].dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true })); return bs.length })()`)
await sleep(400)

const result = await ev(`(() => {
  const full = document.querySelector('.sl-material-full')
  return JSON.stringify({
    underline: !!full.querySelector('span[style*="underline"]'),
    yellow: !!full.querySelector('span[style*="fff59d"]'),
    red: !!full.querySelector('span[style*="ffcdd2"]'),
    nested: full.querySelectorAll('span span').length > 0
  })
})()`)
console.log('标注结果:', result)
console.log('shot ->', await shot('mark-all'))

// 4) 清除标注按钮
await ev(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.includes('清除标注')); b && b.click(); return true })()`)
await sleep(400)
const cleared = await ev(`(() => {
  const full = document.querySelector('.sl-material-full')
  return JSON.stringify({ underline: !!full.querySelector('span'), yellow: !!full.querySelector('span[style*="fff59d"]') })
})()`)
console.log('清除后:', cleared)

ws.close()
edge.kill()
process.exit(0)
