// 批量探查 saduck 各功能页面的 API
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const pages = [
  ['词语辨析', '/my/cybx.html'],
  ['高频词语', '/my/highWord.html'],
  ['生词锦囊', '/my/myWord.html'],
  ['每日打卡', '/my/plan.html'],
  ['计时工具', '/my/timer.html'],
  ['行测助手', '/my/getAide.html'],
  ['每日晨读', '/my/dailyRead.html'],
  ['每日日报', '/my/sixtyWorld.html'],
  ['今日热榜', '/my/hotSearch.html'],
  ['新闻联播', '/my/getNews.html'],
  ['词语查询', '/my/getWord.html']
]

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-tools'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9261', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9261/json')).json()
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

for (const [name, path] of pages) {
  events.length = 0
  await send('Page.navigate', { url: 'https://www.saduck.top' + path })
  await sleep(4500)
  const apis = [...new Set(events.filter(e => e.method === 'Network.requestWillBeSent' && e.params.request.url.includes('api/')).map(e => {
    const p = e.params.request
    return p.method + ' ' + p.url.split('saduck.top')[1] + (p.postData ? ' | body:' + p.postData.slice(0, 80) : '')
  }))]
  const t = (await ev(`document.body.innerText.slice(0, 150)`)) || ''
  console.log('【' + name + '】' + path)
  apis.forEach(a => console.log('   ', a))
  if (!apis.length) console.log('    (无 API 请求)')
  console.log('    页面:', t.replace(/\n+/g, ' ').slice(0, 100))
}
ws.close()
edge.kill()
process.exit(0)
