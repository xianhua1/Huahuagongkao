// 验证资料页悬浮返回顶部按钮
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-backtop'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9247', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1600,1000', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9247/json')).json()
    target = l.find(t => t.type === 'page')
    if (target) break
  } catch { }
  await sleep(500)
}
const ws = new WebSocket(target.webSocketDebuggerUrl)
let id = 0
const pend = new Map()
const send = (m, p = {}) => new Promise((res, rej) => {
  const i = ++id
  pend.set(i, { res, rej })
  ws.send(JSON.stringify({ id: i, method: m, params: p }))
})
ws.onmessage = ev => {
  const m = JSON.parse(ev.data)
  if (m.id && pend.has(m.id)) { pend.get(m.id).res(m.result); pend.delete(m.id) }
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
await send('Page.navigate', { url: 'http://127.0.0.1:8090/docs' })
await sleep(4000)
// 选择一篇长文档
await ev(`(() => { const it = [...document.querySelectorAll('.toc-item')].find(x => x.innerText.includes('数量关系')); it && it.click(); return true })()`)
await sleep(2000)
// 滚动 docs-main 到底部
await ev(`(() => { const m = document.querySelector('.docs-main'); m && (m.scrollTop = m.scrollHeight); return true })()`)
await sleep(1500)
const btnVisible = await ev(`(() => { const b = document.querySelector('.el-backtop'); return b ? { display: getComputedStyle(b).display, pos: getComputedStyle(b).position } : 'none' })()`)
console.log('返回顶部按钮:', JSON.stringify(btnVisible))
// 点击返回顶部
await ev(`(() => { const b = document.querySelector('.el-backtop'); b && b.click(); return true })()`)
await sleep(1500)
const scrollTop = await ev(`document.querySelector('.docs-main').scrollTop`)
console.log('点击后 scrollTop:', scrollTop, '(应为 0)')
ws.close()
edge.kill()
process.exit(0)
