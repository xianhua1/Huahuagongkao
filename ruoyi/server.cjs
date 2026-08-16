/* 国考刷题站前端静态服务器：serve dist + 代理 /prod-api 与 /exam-img 到后端 8080 */
const http = require('http')
const fs = require('fs')
const path = require('path')

const DIST = path.join(__dirname, 'dist')
const BACKEND = 'http://127.0.0.1:8080'
const PORT = process.env.PORT || 8090
const REQLOG = path.join(__dirname, 'req.log')

function log(line) {
  try { fs.appendFileSync(REQLOG, new Date().toISOString() + ' ' + line + '\n') } catch (e) { /* ignore */ }
}

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.gz': 'application/gzip'
}

function proxy(req, res, targetPath) {
  // 保留原始查询串（pageNum/paperId/section 等，原样转发避免编码问题）
  const qIdx = req.url.indexOf('?')
  const query = qIdx >= 0 ? req.url.slice(qIdx) : ''
  const options = {
    hostname: '127.0.0.1',
    port: 8080,
    path: targetPath + query,
    method: req.method,
    headers: Object.assign({}, req.headers, { host: '127.0.0.1:8080' })
  }
  const preq = http.request(options, (pres) => {
    log('[PROXY] ' + req.method + ' ' + targetPath + ' -> ' + pres.statusCode)
    res.writeHead(pres.statusCode, pres.headers)
    pres.pipe(res)
  })
  preq.on('error', (err) => {
    log('[PROXY-ERR] ' + req.method + ' ' + targetPath + ' ' + err.message)
    res.writeHead(502, { 'Content-Type': 'text/plain; charset=utf-8' })
    res.end('后端服务不可用（127.0.0.1:8080）')
  })
  req.pipe(preq)
}

const server = http.createServer((req, res) => {
  // 原始路径（保持编码，代理转发时不能再 decode）
  let rawPath = req.url.split('?')[0]
  // 兼容绝对形式请求行（如 “POST http://host/xxx”）
  const abs = rawPath.match(/^https?:\/\/[^/]+(\/.*)?$/)
  if (abs) rawPath = abs[1] || '/'
  const urlPath = decodeURIComponent(rawPath)
  // 访问日志（诊断用，node 直接写文件，绕开 shell 重定向缓冲）
  log('[REQ] ' + req.method + ' ' + rawPath + ' ua=' + String(req.headers['user-agent'] || '').slice(0, 60))
  if (rawPath === '/news/cctv' || rawPath === '/news/xinhua') {
    return serveNews(rawPath === '/news/cctv' ? 'cctv' : 'xinhua', res)
  }
  if (rawPath.startsWith('/prod-api/')) {
    return proxy(req, res, rawPath.replace(/^\/prod-api/, ''))
  }
  if (rawPath.startsWith('/exam-img/')) {
    return proxy(req, res, rawPath)
  }
  if (rawPath.startsWith('/profile/')) {
    return proxy(req, res, rawPath)
  }
  let filePath = path.join(DIST, urlPath === '/' ? 'index.html' : urlPath)
  if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    filePath = path.join(DIST, 'index.html') // SPA 回退
  }
  const ext = path.extname(filePath).toLowerCase()
  res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' })
  fs.createReadStream(filePath).pipe(res)
})

server.listen(PORT, '0.0.0.0', () => {
  console.log('国考刷题站已启动: http://127.0.0.1:' + PORT)
})

/* ---- 时政资讯代理（央视《新闻联播》 + 新华社评论员）---- */
const NEWS_CACHE = new Map()

async function cachedNews(key, ttlMs, loader) {
  const hit = NEWS_CACHE.get(key)
  if (hit && Date.now() - hit.t < ttlMs) return hit.data
  const data = await loader()
  NEWS_CACHE.set(key, { t: Date.now(), data })
  return data
}

async function fetchCctvNews() {
  // ① 新闻联播视频条目
  const lianbo = []
  try {
    const url = 'https://api.cntv.cn/NewVideo/getVideoListByColumn?serviceId=tvcctv&id=TOPC1451528971114112&p=1&n=12&sort=desc&mode=0'
    const res = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0', Referer: 'https://tv.cctv.com/' }
    })
    if (res.ok) {
      const body = await res.json()
      ;((body.data || {}).list || []).forEach(it => {
        if (!it.title || !it.url) return
        lianbo.push({
          title: String(it.title || ''),
          date: String(it.date || '').replace(/^(\d{4})(\d{2})(\d{2})$/, '$1-$2-$3'),
          time: it.time || '',
          url: it.url || ''
        })
      })
    }
  } catch (e) { /* 联播失败不影响快讯 */ }

  // ② 央视图文快讯（带文字简讯）
  const kuaixun = []
  try {
    const res = await fetch('https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/news_1.jsonp?cb=t', {
      headers: { 'User-Agent': 'Mozilla/5.0' }
    })
    if (res.ok) {
      let text = await res.text()
      const m = text.match(/\((\{.*\})\)\s*$/)
      const body = JSON.parse(m ? m[1] : text)
      const list = ((body.data || {}).list) || []
      list.forEach(it => {
        if (!it.title) return
        kuaixun.push({
          title: String(it.title || ''),
          brief: String(it.brief || '').slice(0, 160),
          date: String(it.focus_date || '').slice(5, 16),
          url: it.url || ''
        })
      })
    }
  } catch (e) { /* ignore */ }

  return { lianbo: lianbo.slice(0, 12), kuaixun: kuaixun.slice(0, 30) }
}

async function fetchXinhuaNews() {
  const res = await fetch('https://www.news.cn/depthobserve/xhsply.html', {
    headers: { 'User-Agent': 'Mozilla/5.0' }
  })
  if (!res.ok) throw new Error('新华社接口返回 ' + res.status)
  const html = await res.text()
  const items = []
  const re = /<a href='([^']+)'[^>]*>([^<]{8,90})<\/a>/g
  let m
  while ((m = re.exec(html)) !== null) {
    const url = m[1].trim()
    const title = m[2].replace(/<[^>]+>/g, '').trim()
    if (url.indexOf('news.cn') >= 0 && /\.html?$/.test(url) && title) {
      items.push({ title, url })
    }
  }
  // 去重
  const seen = new Set()
  const unique = items.filter(it => {
    if (seen.has(it.title)) return false
    seen.add(it.title)
    return true
  }).slice(0, 12)

  // 并发抓取正文首段作为文字简讯
  const withBrief = await Promise.all(unique.map(async it => {
    try {
      const r = await fetch(it.url, { headers: { 'User-Agent': 'Mozilla/5.0' }, signal: AbortSignal.timeout(8000) })
      if (!r.ok) return { ...it, brief: '' }
      const html2 = await r.text()
      const ps = html2.match(/<p[^>]*>([\s\S]*?)<\/p>/g) || []
      let txt = ''
      for (const p of ps) {
        const clean = p.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim()
        if (clean.length > 12) {
          txt = clean
          break
        }
      }
      // 去掉电头（新华社北京8月14日电 题：…）
      const ti = txt.indexOf('题：')
      if (ti >= 0 && ti < 30) txt = txt.slice(ti + 2)
      const ti2 = txt.indexOf('题:')
      if (ti2 >= 0 && ti2 < 30) txt = txt.slice(ti2 + 2)
      txt = txt.trim()
      return { ...it, brief: txt.slice(0, 150) }
    } catch (e) {
      return { ...it, brief: '' }
    }
  }))
  return withBrief
}

function serveNews(which, res) {
  cachedNews(which, 30 * 60 * 1000, which === 'cctv' ? fetchCctvNews : fetchXinhuaNews)
    .then(items => {
      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-cache' })
      res.end(JSON.stringify({ ok: true, source: which, updatedAt: new Date().toISOString(), items }))
    })
    .catch(err => {
      res.writeHead(502, { 'Content-Type': 'application/json; charset=utf-8' })
      res.end(JSON.stringify({ ok: false, msg: '资讯获取失败：' + String((err && err.message) || err) }))
    })
}
