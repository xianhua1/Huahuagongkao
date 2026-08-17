// 点击申论试卷抓详情 API
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-sld'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9259', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9259/json')).json()
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
await sleep(8000)
// 点击 2026 副省申论
const clicked = await ev(`(() => {
  const els = [...document.querySelectorAll('*')].filter(e => e.children.length === 0 && e.textContent.includes('2026年国家公考《申论》题（副省级）'))
  const el = els[els.length - 1]
  if (el) { el.click(); return true }
  return false
})()`)
console.log('点击:', clicked)
await sleep(6000)
const apis = events.filter(e => e.method === 'Network.requestWillBeSent' && e.params.request.url.includes('api')).map(e => {
  const p = e.params.request
  return p.method + ' ' + p.url + (p.postData ? ' | body:' + p.postData.slice(0, 200) : '')
})
console.log('=== 详情请求 ===')
apis.forEach(u => console.log(' ', u))
const t = await ev(`document.body.innerText.slice(0, 400)`)
console.log('页面:', t.replace(/\n+/g, ' | ').slice(0, 300))
ws.close()
edge.kill()
process.exit(0)
