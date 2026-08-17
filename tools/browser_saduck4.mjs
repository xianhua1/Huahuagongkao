// 下载全部 JS chunk 并搜索解密关键词
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-saduck4'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9251', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9251/json')).json()
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

await send('Page.enable')
await send('Network.enable')
await send('Page.navigate', { url: 'https://www.saduck.top/questionBank/overTheYears.html' })
await sleep(10000)

const jsUrls = [...new Set(events.filter(e => e.method === 'Network.requestWillBeSent' && e.params.request.url.includes('.js')).map(e => e.params.request.url))]
console.log('JS:', jsUrls.length)
fs.mkdirSync('C:\\Users\\admin\\DSH\\data\\saduck_js', { recursive: true })
for (const u of jsUrls) {
  try {
    const r = await fetch(u)
    const code = await r.text()
    const name = u.split('/').pop()
    fs.writeFileSync('C:\\Users\\admin\\DSH\\data\\saduck_js\\' + name, code)
    const hits = []
    for (const kw of ['decrypt', 'encrypt', 'AES', 'CryptoJS', 'atob', 'fromCharCode', 'charCodeAt', 'secret']) {
      if (code.includes(kw)) hits.push(kw)
    }
    console.log(name, code.length, '关键词:', hits.join(','))
  } catch (e) {
    console.log(u, '下载失败', e.message)
  }
}
ws.close()
edge.kill()
process.exit(0)
