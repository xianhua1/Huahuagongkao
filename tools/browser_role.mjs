// 用普通用户 ry 登录，检查 5 个新菜单是否可见
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-role'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9297', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1600,1000', 'about:blank'
], { stdio: 'ignore' })
let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9297/json')).json()
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
const goto = async url => { await send('Page.navigate', { url }); await sleep(4000) }

await send('Page.enable')
await send('Runtime.enable')
await goto('http://127.0.0.1:8090/login?redirect=/index')
// ry 密码与 admin 相同（admin123）
await ev(`(() => {
  const i = document.querySelectorAll('input')
  const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set
  s.call(i[0], 'ry'); i[0].dispatchEvent(new Event('input', { bubbles: true }))
  s.call(i[1], 'admin123'); i[1].dispatchEvent(new Event('input', { bubbles: true }))
})()`)
await sleep(400)
await ev(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.replace(/\\s/g, '').includes('登录')); b && b.click(); return true })()`)
await sleep(6000)

const url = await ev(`location.href`)
console.log('登录后 URL:', url)
const body = await ev(`document.body.innerText.slice(0, 600)`)
console.log('页面:', body.replace(/\n/g, ' | ').slice(0, 400))

// 检查侧边栏是否包含 5 个新菜单
await ev(`(() => {
  // 展开 备考中心 子菜单
  const els = [...document.querySelectorAll('*')].filter(e => e.children.length <= 1 && e.textContent.trim() === '备考中心')
  const el = els[els.length - 1]
  if (el) el.click()
  return true
})()`)
await sleep(1500)
const menuText = await ev(`document.body.innerText`)
for (const name of ['词语辨析', '高频词语', '生词锦囊', '计时工具', '行测助手', '词语查询']) {
  console.log(name, '可见:', menuText.includes(name))
}

await edge.kill()
process.exit(0)
