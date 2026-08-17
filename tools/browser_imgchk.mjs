// 打开含图试卷，统计 /exam-img/ 请求的成功/失败
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-imgchk'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9291', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1600,1000', 'about:blank'
], { stdio: 'ignore' })
let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9291/json')).json()
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
const goto = async url => { await send('Page.navigate', { url }); await sleep(4000) }

await send('Page.enable')
await send('Runtime.enable')
await send('Network.enable')

// 登录
await goto('http://127.0.0.1:8090/login?redirect=/index')
await ev(`(() => {
  const i = document.querySelectorAll('input')
  const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set
  s.call(i[0], 'admin'); i[0].dispatchEvent(new Event('input', { bubbles: true }))
  s.call(i[1], 'admin123'); i[1].dispatchEvent(new Event('input', { bubbles: true }))
})()`)
await sleep(400)
await ev(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.replace(/\\s/g, '').includes('登录')); b && b.click(); return true })()`)
await sleep(6000)

// 直接打开试卷页（试卷练习列表）
await goto('http://127.0.0.1:8090/practice/papers')
await sleep(4000)
const has2022 = await ev(`document.body.innerText.includes('2022年国家公务员')`)
console.log('列表含2022国考:', has2022)

// 打开 2022 国考行政执法卷（点击含该标题的元素）
await ev(`(() => {
  const els = [...document.querySelectorAll('*')].filter(e => e.children.length === 0 && e.textContent.includes('2022年国家公务员录用考试《行测》（行政执法卷）'))
  const el = els[els.length - 1]
  if (el) {
    let p = el
    for (let i = 0; i < 6 && p; i++) { p = p.parentElement; if (p && String(p.className).includes('paper')) { p.click(); break } }
    el.click()
    return true
  }
  return false
})()`)
await sleep(6000)

// 统计 exam-img 请求
const imgStats = events.filter(e => e.method === 'Network.responseReceived' && e.params.response.url.includes('/exam-img/'))
  .map(e => ({ url: e.params.response.url.split('/exam-img/')[1], status: e.params.response.status }))
const fails = imgStats.filter(x => x.status >= 400)
const oks = imgStats.filter(x => x.status < 400)
console.log('exam-img 请求总数:', imgStats.length, '| 成功:', oks.length, '| 失败:', fails.length)
if (fails.length) {
  const byCode = {}
  fails.forEach(f => { byCode[f.status] = (byCode[f.status] || 0) + 1 })
  console.log('失败状态码分布:', JSON.stringify(byCode))
  console.log('失败示例:', fails.slice(0, 8).map(f => f.url))
}

// 页面 DOM 中 img 是否显示
const brokenImgs = await ev(`(() => {
  const imgs = [...document.querySelectorAll('img')]
  const broken = imgs.filter(i => !i.complete || i.naturalWidth === 0)
  return JSON.stringify({ total: imgs.length, broken: broken.length, brokenSrc: broken.slice(0, 8).map(i => i.src) })
})()`)
console.log('DOM img 状态:', brokenImgs)

await edge.kill()
process.exit(0)
