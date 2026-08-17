// 探查 saduck 行测助手每个题型的题目格式
import { spawn } from 'node:child_process'
import fs from 'node:fs'
const sleep = ms => new Promise(r => setTimeout(r, ms))

const dir = 'C:\\Users\\admin\\DSH\\tools\\edge-aide4'
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', [
  '--headless=new', '--remote-debugging-port=9277', `--user-data-dir=${dir}`,
  '--no-first-run', '--disable-gpu', '--no-proxy-server', '--window-size=1500,1100', 'about:blank'
], { stdio: 'ignore' })

let target
for (let i = 0; i < 40; i++) {
  try {
    const l = await (await fetch('http://127.0.0.1:9277/json')).json()
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

const types = [
  '两位数加法', '三位数减法', '两位乘两位', '三位除两位', '多个数相加', '常见平方数',
  '估算基期', '估算增长量', '百化分计算', '分数比较', '基期比较', '年平均量', '年均增长率',
  '舒尔特方格', '数字谜题'
]

for (const t of types) {
  const clicked = await ev(`(() => {
    const items = [...document.querySelectorAll('.el-menu-item')]
    const it = items.find(i => i.textContent.trim() === '${t}')
    if (it) { it.click(); return true }
    return false
  })()`)
  await sleep(2200)
  const body = await ev(`document.body.innerText`)
  // 截取题目区域：从"开始练习"之后到"提交"附近
  const idx = body.indexOf('开始练习')
  let seg = idx >= 0 ? body.slice(idx, idx + 900) : body.slice(0, 900)
  seg = seg.split('提交')[0].slice(0, 500)
  const hasChart = await ev(`!!document.querySelector('canvas, svg, img[src*="data"], .echarts, [class*="chart"], [class*="image"]')`)
  const chartEls = await ev(`(() => {
    const sels = ['canvas', 'svg', '.echarts', '[class*="chart"]', '[class*="image"]', 'table']
    const out = []
    sels.forEach(s => document.querySelectorAll(s).forEach(e => out.push(s + ':' + e.className)))
    return [...new Set(out)].slice(0, 6)
  })()`)
  console.log('【' + t + '】clicked=' + clicked + ' chart=' + hasChart)
  console.log('   ' + seg.replace(/\n+/g, ' | ').slice(0, 350))
  if (chartEls.length) console.log('   chartEls: ' + chartEls.join(', '))
}

ws.close()
edge.kill()
process.exit(0)
