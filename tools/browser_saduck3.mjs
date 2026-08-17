// 抓取 saduck 页面加载的所有 JS 并逐个分析解密关键词
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-saduck3'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9250', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9250/json')).json()
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
await sleep(10000)

const jsUrls = [...new Set(events.filter(e => e.method === 'Network.requestWillBeSent' && e.params.request.url.includes('.js')).map(e => e.params.request.url))]
console.log('JS 总数:', jsUrls.length)

// 在页面内直接搜索解密逻辑（全局 window 上的函数/变量）
const keys = await ev(`Object.keys(window).filter(k => /decrypt|encrypt|crypt/i.test(k))`)
console.log('window 解密相关:', JSON.stringify(keys))

// 尝试在页面里直接调用常见解密（也许挂在全局）
const probe = await ev(`(() => {
  const out = {}
  // 抓取 itemizes 响应再尝试
  return fetch('https://saduck.top/api/tk/itemizes?type=1', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' }).then(r => r.text())
})()`)
console.log('原始响应前 200:', String(probe).slice(0, 200))

ws.close()
edge.kill()
process.exit(0)
