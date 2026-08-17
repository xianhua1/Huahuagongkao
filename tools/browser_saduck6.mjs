// 在 saduck 页面设置 token 并点击试卷，观察真实请求
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ2aXBFbmRUaW1lIjoiMTc4NDg3NDU0MDAwMCIsInNpZ24iOiIwNzMxNjA0NTkxIiwidmlwVHlwZSI6IjAiLCJ2aXBTdGFydFRpbWUiOiIxNzg0NjE1MzQwMDAwIiwiayI6IiIsImtGIjoiIiwiZXhwIjoxNzg4NzA1MzI4LCJlbWFpbCI6IjEzNzc4MTAxNDdAcXEuY29tIn0.UtmrtXi-VNnGAWGqm2JuWOOSbpjjwb3HD5iY4knund8'

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-saduck6'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9253', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9253/json')).json()
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
await sleep(8000)

// 设置 token
await ev(`localStorage.setItem('token', '${TOKEN}'); localStorage.setItem('lx_his', ''); 'ok'`)
await sleep(500)
// 点击 2022 副省试卷
const clicked = await ev(`(() => {
  const els = [...document.querySelectorAll('*')].filter(e => e.children.length === 0 && e.textContent.includes('2022年国家公务员录用考试《行测》（副省级）'))
  const el = els[els.length - 1]
  if (el) { el.click(); return 'clicked:' + el.tagName }
  return 'not-found'
})()`)
console.log('点击:', clicked)
await sleep(6000)

// 抓 sourceInfo 请求与响应
const req = events.filter(e => e.method === 'Network.requestWillBeSent' && e.params.request.url.includes('sourceInfo')).map(e => e.params.request)
req.forEach(r => console.log('sourceInfo 请求:', r.method, r.url, '| postData:', r.postData, '| token头:', r.headers.token))
const responses = events.filter(e => e.method === 'Network.responseReceived' && e.params.response.url.includes('sourceInfo')).map(e => e.params.response.status)
console.log('响应状态:', JSON.stringify(responses))
// 页面提示/内容
const t = await ev(`(() => { const m = document.querySelector('.el-message'); return m ? m.innerText : '' })()`)
console.log('页面提示:', t)
const bodyTxt = await ev(`document.body.innerText.slice(0, 200)`)
console.log('页面:', bodyTxt.replace(/\n+/g, ' | ').slice(0, 150))
ws.close()
edge.kill()
process.exit(0)
