// 重截申论刷题 + 申论管理 + 错题本展开
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const SHOT_DIR = 'C:\\Users\\admin\\DSH\\repo_shots'
const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-shots2'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9301', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1600,1000', 'about:blank'
], { stdio: 'ignore' })
let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9301/json')).json()
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
const goto = async url => { await send('Page.navigate', { url }); await sleep(5000) }
const shot = async (name, wait) => {
  await sleep(wait || 3000)
  const r = await send('Page.captureScreenshot', { format: 'png' })
  fs.writeFileSync(`${SHOT_DIR}\\${name}.png`, Buffer.from(r.data, 'base64'))
  console.log('shot:', name)
}

await send('Page.enable')
await send('Runtime.enable')
await goto('http://127.0.0.1:8090/login?redirect=/index')
await ev(`(() => {
  const i = document.querySelectorAll('input')
  const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set
  s.call(i[0], 'admin'); i[0].dispatchEvent(new Event('input', { bubbles: true }))
  s.call(i[1], 'admin123'); i[1].dispatchEvent(new Event('input', { bubbles: true }))
})()`)
await sleep(400)
await ev(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.replace(/\\s/g, '').includes('登录')); b && b.click(); return true })()`)
await sleep(7000)

// 申论刷题列表（正确路由 /practice/shenlun）
await goto('http://127.0.0.1:8090/practice/shenlun')
const slBody = await ev(`document.body.innerText.slice(0, 120)`)
console.log('申论页内容:', slBody.replace(/\n/g, ' '))
await shot('18-申论刷题', 3500)

await edge.kill()
console.log('DONE')
process.exit(0)
