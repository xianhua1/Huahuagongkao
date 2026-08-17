// 深度探查：行测助手 + 词库页面（JS 中 API 与交互）
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const pages = [
  ['行测助手', '/my/getAide.html'],
  ['词语辨析', '/my/cybx.html'],
  ['高频词语', '/my/highWord.html'],
  ['词语查询', '/my/getWord.html']
]

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-deep'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9262', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9262/json')).json()
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

fs.mkdirSync('C:\\Users\\admin\\DSH\\data\\saduck_js3', { recursive: true })
for (const [name, path] of pages) {
  events.length = 0
  await send('Page.navigate', { url: 'https://www.saduck.top' + path })
  await sleep(5000)
  // 页面主体内容（排除导航）
  const main = await ev(`(() => { const m = document.querySelector('.VPNavBar') ? document.body.innerText : document.body.innerText; return m.slice(0, 700) })()`)
  console.log('=====【' + name + '】=====')
  console.log('页面内容:', main.replace(/\n+/g, ' | ').slice(0, 450))
  // 抓页面专属 JS（页面模块 chunk）
  const jsUrls = [...new Set(events.filter(e => e.method === 'Network.requestWillBeSent' && e.params.request.url.includes('.js')).map(e => e.params.request.url))]
  for (const u of jsUrls) {
    const fname = u.split('/').pop().split('?')[0]
    if (!fs.existsSync('C:\\Users\\admin\\DSH\\data\\saduck_js3\\' + fname)) {
      try {
        const r = await fetch(u)
        fs.writeFileSync('C:\\Users\\admin\\DSH\\data\\saduck_js3\\' + fname, await r.text())
      } catch { }
    }
  }
  // 页面交互：点击页面上第一个按钮/输入
  const interact = await ev(`(() => {
    const btns = [...document.querySelectorAll('button')].filter(b => b.innerText.length < 12 && b.innerText.length > 0)
    const btn = btns[0]
    if (btn) { btn.click(); return 'clicked:' + btn.innerText }
    return 'no-btn'
  })()`)
  console.log('交互:', interact)
  await sleep(2500)
  const apis = [...new Set(events.filter(e => e.method === 'Network.requestWillBeSent' && e.params.request.url.includes('api/')).map(e => {
    const p = e.params.request
    return p.method + ' ' + p.url.split('saduck.top')[1] + (p.postData ? ' | body:' + p.postData.slice(0, 100) : '')
  }))]
  apis.forEach(a => console.log('   API:', a))
}
ws.close()
edge.kill()
process.exit(0)
