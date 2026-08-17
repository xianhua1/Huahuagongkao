// 探查 saduck 行测助手 DOM：找到题型列表容器
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-aide3'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9275', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1500,1100', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9275/json')).json()
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
await send('Page.navigate', { url: 'https://www.saduck.top/my/getAide.html' })
await sleep(6000)

// 检查 el-sub-menu 结构
const dom = await ev(`(() => {
  const subs = [...document.querySelectorAll('.el-sub-menu')]
  return subs.map(s => {
    const title = s.querySelector('.el-sub-menu__title')
    const items = [...s.querySelectorAll('.el-menu-item, .el-menu--inline li')].map(i => i.textContent.trim())
    return { title: title ? title.textContent.trim() : '', cls: s.className, items }
  })
})()`)
console.log('=== sub-menus ===')
console.log(JSON.stringify(dom, null, 1))

// 检查 el-menu 外部的题型按钮（可能在主区域）
const btns = await ev(`(() => {
  const out = []
  document.querySelectorAll('button, .el-button, [class*="type"], [class*="item"]').forEach(e => {
    const t = (e.textContent || '').trim()
    if (t && t.length < 15) out.push({ t, cls: String(e.className).slice(0, 60) })
  })
  return out.slice(0, 60)
})()`)
console.log('=== buttons ===')
console.log(JSON.stringify(btns, null, 1))

// 页面上所有文字块（非导航）
const words = await ev(`(() => {
  const nav = document.querySelector('nav, .navbar, header, aside, .sidebar')
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT)
  const out = []
  let n
  while (n = walker.nextNode()) {
    const t = n.textContent.trim()
    if (t && t.length < 12) out.push(t)
  }
  return [...new Set(out)]
})()`)
console.log('=== 短文本 ===')
console.log(JSON.stringify(words, null, 1))

ws.close()
edge.kill()
process.exit(0)
