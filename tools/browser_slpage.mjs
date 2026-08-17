// 抓申论题库页 JS 与 API
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-slpage'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9258', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9258/json')).json()
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
await send('Page.navigate', { url: 'https://www.saduck.top/questionBank/sl.html' })
await sleep(9000)

const apis = [...new Set(events.filter(e => e.method === 'Network.requestWillBeSent' && /api\//.test(e.params.request.url)).map(e => e.params.request.url))]
console.log('=== 申论页 API ===')
apis.forEach(u => console.log(' ', u))
const reqs = events.filter(e => e.method === 'Network.requestWillBeSent' && e.params.request.url.includes('api')).map(e => {
  const p = e.params.request
  return p.method + ' ' + p.url + (p.postData ? ' | body:' + p.postData.slice(0, 120) : '')
})
reqs.forEach(u => console.log('  REQ:', u))
const t = await ev(`document.body.innerText.slice(0, 300)`)
console.log('页面:', t.replace(/\n+/g, ' | ').slice(0, 220))
ws.close()
edge.kill()
process.exit(0)
