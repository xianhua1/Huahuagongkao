// 验证学习计划/学习报告菜单点击后的 URL
import { spawn } from 'node:child_process'
import fs from 'node:fs'

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
const PORT = 9227
const OUT = 'C:\\Users\\admin\\DSH\\tools\\'
const sleep = ms => new Promise(r => setTimeout(r, ms))

fs.rmSync(OUT + 'edge-check6', { recursive: true, force: true })
const edge = spawn(EDGE, [
  '--headless=new', `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${OUT}edge-check6`, '--no-first-run', '--disable-gpu', '--no-proxy-server',
  '--window-size=1500,950', 'about:blank'
], { stdio: 'ignore' })

async function getTarget() {
  for (let i = 0; i < 40; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${PORT}/json`)
      const list = await res.json()
      const page = list.find(t => t.type === 'page')
      if (page) return page
    } catch { }
    await sleep(500)
  }
  throw new Error('timeout')
}

const target = await getTarget()
const ws = new WebSocket(target.webSocketDebuggerUrl)
let msgId = 0
const pending = new Map()
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++msgId
    pending.set(id, { resolve, reject })
    ws.send(JSON.stringify({ id, method, params }))
  })
}
ws.onmessage = ev => {
  const m = JSON.parse(ev.data)
  if (m.id && pending.has(m.id)) {
    const p = pending.get(m.id)
    if (m.error) p.reject(new Error(m.error.message)); else p.resolve(m.result)
    pending.delete(m.id)
  }
}
await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject })

const evalJs = async expr => {
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true })
  return r && r.result ? r.result.value : undefined
}

await send('Page.enable')
await send('Runtime.enable')

await send('Page.navigate', { url: 'http://127.0.0.1:8090/login?redirect=/index' })
await sleep(5000)
await evalJs(`
  (() => {
    const inputs = document.querySelectorAll('input');
    const setVal = (el, v) => {
      const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
      setter.call(el, v);
      el.dispatchEvent(new Event('input', { bubbles: true }));
    };
    if (inputs.length >= 2) { setVal(inputs[0], 'admin'); setVal(inputs[1], 'admin123'); }
  })()
`)
await sleep(500)
await evalJs(`(() => { const b = [...document.querySelectorAll('button')].find(x => x.innerText.replace(/\\s/g, '').includes('登录')); if (b) b.click(); return true })()`)
await sleep(6000)

// 点击学习计划
await evalJs(`(() => { const el = [...document.querySelectorAll('.el-menu-item')].find(x => x.innerText.replace(/\\s/g, '').includes('学习计划')); if (el) { el.click(); return true } return false })()`)
await sleep(4500)
console.log('学习计划 URL:', await evalJs('location.href'))
console.log('学习计划 内容:', await evalJs(`document.body.innerText.includes('90 天学习计划')`))

// 点击学习报告
await evalJs(`(() => { const el = [...document.querySelectorAll('.el-menu-item')].find(x => x.innerText.replace(/\\s/g, '').includes('学习报告')); if (el) { el.click(); return true } return false })()`)
await sleep(4500)
console.log('学习报告 URL:', await evalJs('location.href'))
console.log('学习报告 内容:', await evalJs(`document.body.innerText.includes('学习报告')`))

ws.close()
edge.kill()
process.exit(0)
