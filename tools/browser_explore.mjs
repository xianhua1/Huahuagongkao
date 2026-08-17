// 探查 saduck 全部功能页面与申论题库入口
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-explore'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9257', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9257/json')).json()
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
await sleep(8000)

// 1) 首页可见功能菜单
const nav = await ev(`[...document.querySelectorAll('a')].map(a => a.textContent.trim() + ' => ' + a.getAttribute('href')).filter(x => x.includes('=>') && !x.includes('=> #')).slice(0, 80)`)
console.log('=== 全站链接 ===')
nav.forEach(l => console.log(' ', l))

// 2) 申论题库相关链接
const sl = await ev(`[...document.querySelectorAll('a')].map(a => ({ t: a.textContent.trim(), h: a.getAttribute('href') })).filter(x => x.t.includes('申论'))`)
console.log('=== 申论入口 ===', JSON.stringify(sl))

// 3) 网络请求（API 端点）
const apis = [...new Set(events.filter(e => e.method === 'Network.requestWillBeSent' && /api\//.test(e.params.request.url)).map(e => e.params.request.url))]
console.log('=== API 端点 ===')
apis.forEach(u => console.log(' ', u))

ws.close()
edge.kill()
process.exit(0)
