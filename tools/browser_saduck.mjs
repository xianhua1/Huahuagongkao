// 打开 saduck 页面，监听所有网络请求找数据源
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-saduck'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9248', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9248/json')).json()
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

await send('Page.enable')
await send('Runtime.enable')
await send('Network.enable')
await send('Page.navigate', { url: 'https://www.saduck.top/questionBank/overTheYears.html' })
await sleep(9000)

// 非静态资源请求
const reqs = events.filter(e => e.method === 'Network.requestWillBeSent').map(e => e.params.request.url)
const interesting = [...new Set(reqs)].filter(u => !/\.(js|css|png|jpg|svg|woff2?|ico|gif|webp)(\?|$)/.test(u))
console.log('数据请求:')
interesting.forEach(u => console.log(' ', u))

// 页面渲染的列表内容
const text = await ev(`document.body.innerText.slice(0, 800)`)
console.log('页面文本:', text.replace(/\n+/g, ' | ').slice(0, 500))

ws.close()
edge.kill()
process.exit(0)
