// 带 token 探查词库页面数据 API
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ2aXBFbmRUaW1lIjoiMTc4NDg3NDU0MDAwMCIsInNpZ24iOiIwNzMxNjA0NTkxIiwidmlwVHlwZSI6IjAiLCJ2aXBTdGFydFRpbWUiOiIxNzg0NjE1MzQwMDAwIiwiayI6IiIsImtGIjoiIiwiZXhwIjoxNzg4NzA1MzI4LCJlbWFpbCI6IjEzNzc4MTAxNDdAcXEuY29tIn0.UtmrtXi-VNnGAWGqm2JuWOOSbpjjwb3HD5iY4knund8'

const pages = [
  ['词语辨析', '/my/cybx.html', '开始练习'],
  ['高频词语', '/my/highWord.html', ''],
  ['生词锦囊', '/my/myWord.html', ''],
  ['词语查询', '/my/getWord.html', '查成语']
]

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-word'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9263', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9263/json')).json()
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
await send('Page.navigate', { url: 'https://www.saduck.top/' })
await sleep(4000)
await ev(`localStorage.setItem('token', '${TOKEN}'); 'ok'`)

for (const [name, path, btn] of pages) {
  events.length = 0
  await send('Page.navigate', { url: 'https://www.saduck.top' + path })
  await sleep(5000)
  if (btn) {
    await ev(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.includes('${btn}')); b && b.click(); return !!b })()`)
    await sleep(3000)
  }
  const apis = [...new Set(events.filter(e => e.method === 'Network.requestWillBeSent' && e.params.request.url.includes('api/')).map(e => {
    const p = e.params.request
    return p.method + ' ' + p.url.split('saduck.top')[1] + (p.postData ? ' | body:' + p.postData.slice(0, 120) : '')
  }))]
  console.log('【' + name + '】')
  apis.forEach(a => console.log('   ', a))
  if (!apis.length) console.log('    (仍无 API)')
}
ws.close()
edge.kill()
process.exit(0)
