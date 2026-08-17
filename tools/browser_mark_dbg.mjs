// 诊断：标注工具条为何不显示
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-mark2'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9240', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9240/json')).json()
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
const ev = async e => (await send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true })).result.value

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

// 检查材料区状态
console.log('材料数:', await ev(`document.querySelectorAll('.sl-material').length`))
console.log('展开的full数:', await ev(`document.querySelectorAll('.sl-material-full').length`))
// 点击第一个材料展开
await ev(`(() => { const b = document.querySelector('.sl-material-body'); b && b.click(); return true })()`)
await sleep(600)
console.log('点击后full数:', await ev(`document.querySelectorAll('.sl-material-full').length`))

// 选中前 10 字符并派发 mouseup
await ev(`(() => {
  const full = document.querySelector('.sl-material-full')
  if (!full) return 'no-full'
  const nodes = []
  const walker = document.createTreeWalker(full, NodeFilter.SHOW_TEXT)
  let n
  while ((n = walker.nextNode())) nodes.push(n)
  if (!nodes.length) return 'no-text-node'
  const range = document.createRange()
  range.setStart(nodes[0], 0)
  range.setEnd(nodes[0], Math.min(10, nodes[0].textContent.length))
  const sel = window.getSelection()
  sel.removeAllRanges()
  sel.addRange(range)
  full.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true }))
  return 'dispatched'
})()`)
await sleep(800)
console.log('selection 状态:', await ev(`(() => { const s = window.getSelection(); return s ? 'collapsed=' + s.isCollapsed + ' text=' + s.toString().slice(0, 8) : 'none' })()`))
console.log('工具条显示:', await ev(`!!document.querySelector('.mark-toolbar')`))
const exc = events.filter(e => e.method === 'Runtime.exceptionThrown').map(e => {
  const d = e.params.exceptionDetails || {}
  return (d.exception ? d.exception.description : d.text || '')
}).slice(0, 3)
console.log('JS异常:', JSON.stringify(exc))

ws.close()
edge.kill()
process.exit(0)
