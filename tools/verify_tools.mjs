// 验证词库三件套/计时工具/行测助手页面（Edge headless + CDP）
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-tools'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9259', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1600,1000', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9259/json')).json()
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

const pages = [
  ['词语辨析', '/prep/cybx', '词语辨析练习'],
  ['高频词语', '/prep/highword', '高频词语'],
  ['生词锦囊', '/prep/myword', '生词锦囊'],
  ['词语查询', '/prep/getword', '词语查询'],
  ['计时工具', '/prep/timer', '计时工具'],
  ['行测助手', '/prep/aide', '行测助手 · 口算练习']
]
let allOk = true
for (const [name, path, expect] of pages) {
  await goto('http://127.0.0.1:8090' + path)
  const body = await ev(`document.body.innerText`)
  const ok = body && body.includes(expect)
  console.log(`[${ok ? 'OK' : 'FAIL'}] ${name} ${path}`)
  if (!ok) { console.log('   body head: ' + String(body).slice(0, 120).replace(/\n/g, ' ')); allOk = false }
}

// 行测助手交互：开始 → 提交一题
await goto('http://127.0.0.1:8090/prep/aide')
await ev(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.includes('开始练习')); b && b.click(); return !!b })()`)
await sleep(1500)
const q = await ev(`document.querySelector('.p-question') && document.querySelector('.p-question').innerText`)
console.log('题目: ' + q)
if (q) {
  const m = String(q).match(/(-?\d+)\s*([+\\-×÷])\s*(\d+)\s*=\s*？/)
  if (m) {
    const a = parseInt(m[1]), b = parseInt(m[3])
    const ans = m[2] === '+' ? a + b : m[2] === '-' ? a - b : m[2] === '×' ? a * b : Math.round(a / b * 100) / 100
    await ev(`(() => {
      const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set
      const i = document.querySelector('.p-input')
      s.call(i, '${ans}'); i.dispatchEvent(new Event('input', { bubbles: true }))
      i.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }))
      return true
    })()`)
    await sleep(1200)
    const fb = await ev(`document.querySelector('.p-feedback') && document.querySelector('.p-feedback').innerText`)
    console.log('提交反馈: ' + fb)
  }
}

// 计时工具：开始 → 检查倒计时
await goto('http://127.0.0.1:8090/prep/timer')
await ev(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.trim() === '开始'); b && b.click(); return !!b })()`)
await sleep(2500)
const clock = await ev(`document.querySelector('.clock') && document.querySelector('.clock').innerText`)
console.log('计时显示: ' + clock)

// 词语查询：搜索
await goto('http://127.0.0.1:8090/prep/getword')
await ev(`(() => {
  const i = document.querySelector('.search-bar input')
  const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set
  s.call(i, '砥砺'); i.dispatchEvent(new Event('input', { bubbles: true }))
  const b = [...document.querySelectorAll('button')].find(x => x.innerText.includes('查询'))
  b && b.click()
  return true
})()`)
await sleep(1500)
const res = await ev(`document.querySelectorAll('.cy-card').length`)
const descText = await ev(`document.querySelector('.ph-desc') && document.querySelector('.ph-desc').innerText`)
console.log('查询"砥砺"结果数: ' + res + ' | 页头描述: ' + descText)

await edge.kill()
console.log(allOk ? '=== ALL PAGES OK ===' : '=== SOME FAILURES ===')
process.exit(allOk ? 0 : 1)
