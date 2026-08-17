// 带 token 打开申论详情页，抓题目接口
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ2aXBFbmRUaW1lIjoiMTc4NDg3NDU0MDAwMCIsInNpZ24iOiIwNzMxNjA0NTkxIiwidmlwVHlwZSI6IjAiLCJ2aXBTdGFydFRpbWUiOiIxNzg0NjE1MzQwMDAwIiwiayI6IiIsImtGIjoiIiwiZXhwIjoxNzg4NzA1MzI4LCJlbWFpbCI6IjEzNzc4MTAxNDdAcXEuY29tIn0.UtmrtXi-VNnGAWGqm2JuWOOSbpjjwb3HD5iY4knund8'

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-slitem'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9260', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9260/json')).json()
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
// 先到 saduck 设置 token
await send('Page.navigate', { url: 'https://www.saduck.top/' })
await sleep(5000)
await ev(`localStorage.setItem('token', '${TOKEN}'); 'ok'`)
// 打开申论详情页
await send('Page.navigate', { url: 'https://www.saduck.top/questionBank/slItem.html?id=64065900594218033266&name=2026年国家公考《申论》题（副省级）' })
await sleep(10000)
const apis = events.filter(e => e.method === 'Network.requestWillBeSent' && e.params.request.url.includes('api')).map(e => {
  const p = e.params.request
  return p.method + ' ' + p.url + (p.postData ? ' | body:' + p.postData.slice(0, 200) : '')
})
console.log('=== 详情页 API ===')
apis.forEach(u => console.log(' ', u))
const t = await ev(`document.body.innerText.slice(0, 500)`)
console.log('页面:', t.replace(/\n+/g, ' | ').slice(0, 350))
ws.close()
edge.kill()
process.exit(0)
