// 验证新首页 + 透明 logo
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-home'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9233', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1600,1000', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9233/json')).json()
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
const ev = async e => (await send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true })).result.value
const shot = async n => {
  const r = await send('Page.captureScreenshot', { format: 'png' })
  fs.writeFileSync(`C:\\Users\\admin\\DSH\\tools\\shot-${n}.png`, Buffer.from(r.data, 'base64'))
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
console.log('URL:', await ev('location.href'))

// 登录页 logo 检查
const loginLogoOk = await ev(`(() => { const imgs = [...document.querySelectorAll('img')]; return imgs.filter(i => i.src.includes('logo')).length })()`)
console.log('登录页 logo img:', loginLogoOk)

// 首页内容
const t = await ev('document.body.innerText.slice(0, 500)')
console.log('首页:', t.replace(/\n+/g, ' | ').slice(0, 400))
const hasTopbar = await ev(`!!document.querySelector('.topbar')`)
const hasBanner = await ev(`!!document.querySelector('.banner')`)
const modCount = await ev(`document.querySelectorAll('.mod-card').length`)
const statCount = await ev(`document.querySelectorAll('.stat-card').length`)
console.log('topbar:', hasTopbar, '| banner:', hasBanner, '| 模块卡:', modCount, '| 统计卡:', statCount)
console.log('shot ->', await shot('home-new'))

// 侧边栏 logo
const sideLogo = await ev(`(() => { const el = document.querySelector('.sidebar-logo img, .sidebar-container img'); return el ? el.src.split('/').pop() : 'none' })()`)
console.log('侧边栏 logo:', sideLogo)

ws.close()
edge.kill()
process.exit(0)
