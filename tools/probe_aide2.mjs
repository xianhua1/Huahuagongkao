// 探查 saduck 行测助手：展开子菜单，收集三大类下的全部题型
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-aide2'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9273', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1500,1100', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9273/json')).json()
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

// 展开三个大类的子菜单
for (const name of ['基础练习', '资料专项', '其他训练']) {
  await ev(`(() => {
    const els = [...document.querySelectorAll('.el-sub-menu__title')].filter(e => e.textContent.trim() === '${name}')
    if (els.length) { els[0].click(); return 'ok' }
    return 'not found'
  })()`)
  await sleep(1200)
}

// 收集所有可见子菜单项
const items = await ev(`(() => {
  const out = []
  document.querySelectorAll('.el-menu--inline .el-menu-item, .el-sub-menu .el-sub-menu .el-menu-item').forEach(e => {
    const t = e.textContent.trim()
    if (t) out.push(t)
  })
  return [...new Set(out)]
})()`)
console.log('=== 子菜单项 ===')
console.log(JSON.stringify(items, null, 1))

// 点击"资料专项"分类下第一个子项
await ev(`(() => {
  const items = [...document.querySelectorAll('.el-menu--inline .el-menu-item')]
  const labels = items.map(e => e.textContent.trim())
  return JSON.stringify(labels)
})()`).then(async labels => {
  console.log('=== inline items ===')
  console.log(labels)
  // 尝试点击资料专项下的第一项
  await ev(`(() => {
    const subs = [...document.querySelectorAll('.el-sub-menu')]
    const zl = subs.find(s => s.querySelector('.el-sub-menu__title') && s.querySelector('.el-sub-menu__title').textContent.trim() === '资料专项')
    if (zl) {
      const it = zl.querySelector('.el-menu-item')
      if (it) { it.click(); return it.textContent.trim() }
    }
    return 'none'
  })()`).then(async clicked => {
    console.log('=== 点击资料专项子项:', clicked, '===')
    await sleep(2500)
    const t = await ev(`document.body.innerText`)
    console.log(t.slice(500, 3000))
  })
})

// 点击"其他训练"分类下第一个子项
await ev(`(() => {
  const subs = [...document.querySelectorAll('.el-sub-menu')]
  const qt = subs.find(s => s.querySelector('.el-sub-menu__title') && s.querySelector('.el-sub-menu__title').textContent.trim() === '其他训练')
  if (qt) {
    const it = qt.querySelector('.el-menu-item')
    if (it) { it.click(); return it.textContent.trim() }
  }
  return 'none'
})()`).then(async clicked => {
  console.log('=== 点击其他训练子项:', clicked, '===')
  await sleep(2500)
  const t = await ev(`document.body.innerText`)
  console.log(t.slice(500, 3000))
})

ws.close()
edge.kill()
process.exit(0)
