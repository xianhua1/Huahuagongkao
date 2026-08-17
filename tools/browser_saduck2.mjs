// 抓 itemizes API 的完整请求（method/参数/响应）
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-saduck2'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9249', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9249/json')).json()
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

// 抓 itemizes 请求详情 + 响应
const itemReq = events.find(e => e.method === 'Network.requestWillBeSent' && e.params.request.url.includes('api/tk'))
if (itemReq) {
  const p = itemReq.params
  console.log('method:', p.request.method)
  console.log('url:', p.request.url)
  console.log('postData:', p.request.postData ? p.request.postData.slice(0, 500) : '(无)')
  console.log('headers:', JSON.stringify(p.request.headers).slice(0, 400))
}
// 响应内容
const respEv = events.find(e => e.method === 'Network.responseReceived' && e.params.response.url.includes('api/tk'))
if (respEv) {
  console.log('响应状态:', respEv.params.response.status)
}
// 从页面内 fetch 响应
const resp = await ev(`fetch('https://saduck.top/api/tk/itemizes?type=1', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' }).then(r => r.text()).catch(e => 'ERR ' + e)`)
console.log('POST {} 响应:', resp.slice(0, 400))
ws.close()
edge.kill()
process.exit(0)
