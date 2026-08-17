// 实测个人中心头像上传，抓请求头与响应
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

// 生成测试头像图
const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==', 'base64')
fs.writeFileSync('C:\\Users\\admin\\DSH\\data\\avatar-test.png', png)

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-avatar'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9245', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9245/json')).json()
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
await send('DOM.enable')
await send('Page.navigate', { url: 'http://127.0.0.1:8090/login?redirect=/index' })
await sleep(5000)
await ev(`(() => {
  const i = document.querySelectorAll('input')
  const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set
  s.call(i[0], 'admin'); i[0].dispatchEvent(new Event('input', { bubbles: true }))
  s.call(i[1], 'admin123'); i[1].dispatchEvent(new Event('input', { bubbles: true }))
})()`)
await sleep(400)
await ev(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.replace(/\\s/g, '').includes('登录')); b && b.click(); return true })()`)
await sleep(7000)

// 进入个人中心
await send('Page.navigate', { url: 'http://127.0.0.1:8090/user/profile' })
await sleep(5000)
// 点击头像打开裁剪框
await ev(`(() => { const h = document.querySelector('.user-info-head'); h && h.click(); return true })()`)
await sleep(2000)
console.log('裁剪框打开:', await ev(`!!document.querySelector('.el-dialog')`))

// 用 CDP 设置文件到 el-upload 的 input（弹窗 append-to-body）
const doc = await send('DOM.getDocument')
const qr = await send('DOM.querySelector', { nodeId: doc.root.nodeId, selector: '.el-dialog input[type=file]' })
if (qr.nodeId) {
  await send('DOM.setFileInputFiles', { nodeId: qr.nodeId, files: ['C:\\Users\\admin\\DSH\\data\\avatar-test.png'] })
  console.log('文件已设置')
} else {
  console.log('未找到文件 input')
}
await sleep(3000)

// 抓取上传请求（提交）
await ev(`(() => { const bs = [...document.querySelectorAll('button')]; const b = bs.find(x => x.innerText.includes('提 交') || x.innerText.includes('提交')); b && b.click(); return !!b })()`)
await sleep(4000)

// 分析 avatar 请求
const reqs = events.filter(e => e.method === 'Network.requestWillBeSent' && e.params.request.url.includes('avatar'))
reqs.forEach(r => {
  const req = r.params.request
  console.log('请求:', req.method, req.url)
  console.log('  Content-Type:', req.headers['Content-Type'] || req.headers['content-type'])
  console.log('  有 body:', !!req.postData)
})
const resp = events.filter(e => e.method === 'Network.responseReceived' && e.params.response.url.includes('avatar')).map(r => r.params.response.status + ' ' + r.params.response.url)
console.log('响应:', JSON.stringify(resp))
const toast = await ev(`(() => { const m = document.querySelector('.el-message'); return m ? m.innerText : '' })()`)
console.log('提示:', toast)
console.log('弹窗还开着:', await ev(`!!document.querySelector('.el-dialog')`))

fs.rmSync('C:\\Users\\admin\\DSH\\data\\avatar-test.png', { force: true })
ws.close()
edge.kill()
process.exit(0)
