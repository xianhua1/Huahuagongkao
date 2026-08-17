import { spawn } from "node:child_process"
import fs from "node:fs"
const sleep = ms => new Promise(r => setTimeout(r, ms))
const dir = "C:\\Users\\admin\\DSH\\tools\\edge-mark3"
fs.rmSync(dir, { recursive: true, force: true })
const edge = spawn("C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe", ["--headless=new", "--remote-debugging-port=9241", `--user-data-dir=${dir}`, "--no-first-run", "--disable-gpu", "--no-proxy-server", "about:blank"], { stdio: "ignore" })
let target
for (let i = 0; i < 40; i++) { try { const l = await (await fetch("http://127.0.0.1:9241/json")).json(); target = l.find(t => t.type === "page"); if (target) break } catch {} await sleep(500) }
const ws = new WebSocket(target.webSocketDebuggerUrl)
let id = 0
const pend = new Map()
const send = (m, p = {}) => new Promise((res, rej) => { const i = ++id; pend.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method: m, params: p })) })
ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && pend.has(m.id)) { pend.get(m.id).res(m.result); pend.delete(m.id) } }
await new Promise(r => ws.onopen = r)
const ev = async e => (await send("Runtime.evaluate", { expression: e, returnByValue: true, awaitPromise: true })).result.value
await send("Page.enable")
await send("Runtime.enable")
await send("Page.navigate", { url: "http://127.0.0.1:8090/login?redirect=/index" })
await sleep(5000)
await ev(`(() => { const i = document.querySelectorAll("input"); const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set; s.call(i[0], "admin"); i[0].dispatchEvent(new Event("input", { bubbles: true })); s.call(i[1], "admin123"); i[1].dispatchEvent(new Event("input", { bubbles: true })) })()`)
await sleep(400)
await ev(`(() => { const b = [...document.querySelectorAll("button")].find(x => x.innerText.replace(/\\s/g, "").includes("登录")); b && b.click(); return true })()`)
await sleep(7000)
await send("Page.navigate", { url: "http://127.0.0.1:8090/practice/shenlun" })
await sleep(4000)
await ev(`(() => { const c = document.querySelector(".sl-card"); c && c.click(); return true })()`)
await sleep(4000)
await ev(`(() => { const b = document.querySelector(".sl-material-body"); b && b.click(); return true })()`)
await sleep(600)
await ev(`(() => {
  const full = document.querySelector(".sl-material-full")
  const nodes = []
  const walker = document.createTreeWalker(full, NodeFilter.SHOW_TEXT)
  let n
  while ((n = walker.nextNode())) nodes.push(n)
  const range = document.createRange()
  range.setStart(nodes[0], 0)
  range.setEnd(nodes[0], Math.min(10, nodes[0].textContent.length))
  const sel = window.getSelection()
  sel.removeAllRanges()
  sel.addRange(range)
  full.dispatchEvent(new MouseEvent("mouseup", { bubbles: true, cancelable: true }))
})()`)
await sleep(800)
const diag = await ev(`(() => {
  const full = document.querySelector(".sl-material-full")
  const sel = window.getSelection()
  const range = sel.getRangeAt(0)
  function offsetIn(root, node, off) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT)
    let total = 0, br = 0, n
    while ((n = walker.nextNode())) {
      if (n.nodeType === Node.TEXT_NODE) { if (n === node) return total + off + br; total += n.textContent.length }
      else if (n.nodeName === "BR") { if (n === node) return total + br + 1; br++ }
      else if (n === node) {
        let sub = 0
        for (let i = 0; i < off && i < n.childNodes.length; i++) { const k = n.childNodes[i]; if (k.nodeType === 3) sub += k.textContent.length; else if (k.nodeName === "BR") sub += 1; else sub += k.textContent.length }
        return total + br + sub
      }
    }
    return 0
  }
  return JSON.stringify({
    contains: full.contains(range.commonAncestorContainer),
    s: offsetIn(full, range.startContainer, range.startOffset),
    e: offsetIn(full, range.endContainer, range.endOffset),
    startNode: range.startContainer.nodeName,
    endNode: range.endContainer.nodeName,
    selText: sel.toString().slice(0, 8)
  })
})()`)
console.log("诊断:", diag)
console.log("工具条:", await ev(`!!document.querySelector(".mark-toolbar")`))
ws.close()
edge.kill()
process.exit(0)