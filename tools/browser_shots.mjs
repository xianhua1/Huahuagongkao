// 全站功能截图：登录后依次访问各页面截图
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const SHOT_DIR = 'C:\\Users\\admin\\DSH\\repo_shots'
fs.rmSync(SHOT_DIR, { recursive: true, force: true })
fs.mkdirSync(SHOT_DIR, { recursive: true })

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-shots'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9299', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1600,1000', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9299/json')).json()
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
const goto = async url => { await send('Page.navigate', { url }); await sleep(4500) }
const shot = async (name, wait) => {
  await sleep(wait || 2500)
  const r = await send('Page.captureScreenshot', { format: 'png' })
  fs.writeFileSync(`${SHOT_DIR}\\${name}.png`, Buffer.from(r.data, 'base64'))
  console.log('shot:', name)
}

await send('Page.enable')
await send('Runtime.enable')

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

// 首页门户
await goto('http://127.0.0.1:8090/index')
await shot('01-首页', 3000)

// 试卷练习（题库列表）
await goto('http://127.0.0.1:8090/practice/papers')
await shot('02-试卷练习', 3000)

// 刷题页面（打开一套卷）
await goto('http://127.0.0.1:8090/practice/papers')
await sleep(2500)
await ev(`(() => {
  const els = [...document.querySelectorAll('*')].filter(e => e.children.length === 0 && e.textContent.includes('2024年国家公务员录用考试《行测》（地市级）'))
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
await shot('03-刷题页面', 3000)

// 错题本
await goto('http://127.0.0.1:8090/practice/wrong')
await shot('04-错题本', 3000)

// 学习计划（含打卡日历）
await goto('http://127.0.0.1:8090/plan')
await shot('05-学习计划', 3000)

// 学习报告
await goto('http://127.0.0.1:8090/report')
await shot('06-学习报告', 3000)

// 备考中心首页（每日一练）
await goto('http://127.0.0.1:8090/prep/daily')
await shot('07-每日一练', 3000)

// 成语积累
await goto('http://127.0.0.1:8090/prep/chengyu')
await shot('08-成语积累', 3000)

// 申论规范词
await goto('http://127.0.0.1:8090/prep/guifan')
await shot('09-申论规范词', 3000)

// 时政速递
await goto('http://127.0.0.1:8090/prep/shizheng')
await shot('10-时政速递', 3000)

// 速记卡片
await goto('http://127.0.0.1:8090/prep/cards')
await shot('11-速记卡片', 3000)

// 申论素材
await goto('http://127.0.0.1:8090/prep/sucai')
await shot('12-申论素材', 3000)

// 词语辨析
await goto('http://127.0.0.1:8090/prep/cybx')
await shot('13-词语辨析', 3000)

// 高频词语
await goto('http://127.0.0.1:8090/prep/highword')
await shot('14-高频词语', 3000)

// 生词锦囊
await goto('http://127.0.0.1:8090/prep/myword')
await shot('15-生词锦囊', 3000)

// 计时工具
await goto('http://127.0.0.1:8090/prep/timer')
await shot('16-计时工具', 3000)

// 行测助手
await goto('http://127.0.0.1:8090/prep/aide')
await shot('17-行测助手', 3000)

// 申论刷题
await goto('http://127.0.0.1:8090/shenlun')
await shot('18-申论刷题', 3000)

// 资料教程
await goto('http://127.0.0.1:8090/docs')
await shot('19-资料教程', 3000)

await edge.kill()
console.log('ALL DONE, shots in', SHOT_DIR)
process.exit(0)
