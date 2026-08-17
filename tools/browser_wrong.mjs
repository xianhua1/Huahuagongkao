// 测试错题本页面：展开详情行，检查内容与报错
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-wrong'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9293', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1600,1000', 'about:blank'
], { stdio: 'ignore' })
let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9293/json')).json()
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
const goto = async url => { await send('Page.navigate', { url }); await sleep(4000) }

await send('Page.enable')
await send('Runtime.enable')
await send('Log.enable')

// 捕获控制台错误
const consoleErrors = []
const orig = console.log

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

// 打开错题本
await goto('http://127.0.0.1:8090/practice/wrong')
await sleep(5000)
const body = await ev(`document.body.innerText`)
console.log('页面内容:', body.slice(0, 300).replace(/\n/g, ' '))

// 点击第一行的展开箭头
await ev(`(() => {
  const btn = document.querySelector('.el-table__expand-icon')
  if (btn) { btn.click(); return 'clicked' }
  return 'no expand icon'
})()`)
await sleep(1500)

const detail = await ev(`(() => {
  const d = document.querySelector('.wrong-detail')
  return d ? d.innerText.slice(0, 500) : 'NO DETAIL'
})()`)
console.log('展开详情:', detail ? String(detail).replace(/\n/g, ' | ').slice(0, 400) : 'null')

// 检查是否有图片加载失败
const imgs = await ev(`(() => {
  const list = [...document.querySelectorAll('.wrong-detail img')]
  return JSON.stringify(list.map(i => ({ src: i.src.slice(0, 60), broken: !i.complete || i.naturalWidth === 0 })))
})()`)
console.log('详情图片:', imgs)

// 读取 console 错误
const logs = events.filter(e => e.method === 'Runtime.consoleAPICalled' && e.params.type === 'error')
console.log('console errors:', logs.length)
logs.slice(0, 3).forEach(l => console.log('  ', JSON.stringify(l.params.args).slice(0, 200)))

await edge.kill()
process.exit(0)
