// 抓高频词语数据 + 词语辨析题目 + 成语查询接口
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ2aXBFbmRUaW1lIjoiMTc4NDg3NDU0MDAwMCIsInNpZ24iOiIwNzMxNjA0NTkxIiwidmlwVHlwZSI6IjAiLCJ2aXBTdGFydFRpbWUiOiIxNzg0NjE1MzQwMDAwIiwiayI6IiIsImtGIjoiIiwiZXhwIjoxNzg4NzA1MzI4LCJlbWFpbCI6IjEzNzc4MTAxNDdAcXEuY29tIn0.UtmrtXi-VNnGAWGqm2JuWOOSbpjjwb3HD5iY4knund8'

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-word2'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9264', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9264/json')).json()
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

// 高频词语
await send('Page.navigate', { url: 'https://www.saduck.top/my/highWord.html' })
await sleep(5000)
const hw = await ev(`fetch('https://saduck.top/api/word/getHWordEncryption', { method: 'POST', headers: { 'Content-Type': 'application/json', 'token': localStorage.getItem('token') }, body: '{}' }).then(r => r.text()).catch(e => 'ERR ' + e)`)
console.log('高频词语响应长度:', hw.length)
console.log('响应:', String(hw).slice(0, 400))
fs.writeFileSync('C:\\Users\\admin\\DSH\\data\\saduck_hword_raw.txt', String(hw))

// 词语辨析：点击"看词语选意思"模式
await send('Page.navigate', { url: 'https://www.saduck.top/my/cybx.html' })
await sleep(4000)
events.length = 0
await ev(`(() => { const b = [...document.querySelectorAll('*')].find(x => x.children.length === 0 && x.textContent.includes('看词语选意思')); b && b.click(); return !!b })()`)
await sleep(3500)
const cybxApis = [...new Set(events.filter(e => e.method === 'Network.requestWillBeSent' && e.params.request.url.includes('api/')).map(e => {
  const p = e.params.request
  return p.method + ' ' + p.url.split('saduck.top')[1] + (p.postData ? ' | body:' + p.postData.slice(0, 150) : '')
}))]
console.log('词语辨析练习 API:', JSON.stringify(cybxApis))

// 成语查询：输入"奋发"查询
await send('Page.navigate', { url: 'https://www.saduck.top/my/getWord.html' })
await sleep(4000)
events.length = 0
await ev(`(() => {
  const inputs = [...document.querySelectorAll('input')]
  const inp = inputs[0]
  if (!inp) return false
  const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set
  s.call(inp, '奋发')
  inp.dispatchEvent(new Event('input', { bubbles: true }))
  inp.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }))
  return true
})()`)
await sleep(3500)
const wordApis = [...new Set(events.filter(e => e.method === 'Network.requestWillBeSent' && e.params.request.url.includes('api/')).map(e => {
  const p = e.params.request
  return p.method + ' ' + p.url.split('saduck.top')[1] + (p.postData ? ' | body:' + p.postData.slice(0, 150) : '')
}))]
console.log('词语查询 API:', JSON.stringify(wordApis))
const wres = await ev(`(() => { const m = document.querySelector('.el-message'); return m ? m.innerText : '' })()`)
console.log('提示:', wres)
const bodyTxt = await ev(`document.body.innerText.slice(400, 700)`)
console.log('查询结果区域:', bodyTxt.replace(/\n+/g, ' | ').slice(0, 200))
ws.close()
edge.kill()
process.exit(0)
