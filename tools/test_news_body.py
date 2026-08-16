# -*- coding: utf-8 -*-
"""测试：1) 央视网图文快讯接口 2) 新华社评论员文章正文抓取"""
import urllib.request, ssl, re, json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
HDRS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0'}

def get(url, timeout=15):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HDRS), timeout=timeout, context=ctx).read()

# 1) 央视网新闻列表 jsonp 接口
for u in [
    'https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/news_1.jsonp?cb=t',
    'https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/news_1.jsonp',
]:
    try:
        raw = get(u).decode('utf-8', 'ignore')
        m = re.search(r'\((\{.*\})\)\s*$', raw.strip())
        d = json.loads(m.group(1)) if m else json.loads(raw)
        items = d.get('data') or d.get('list') or []
        print('CCTV news api OK items:', len(items))
        for it in items[:3]:
            print('  -', (it.get('title') or '')[:40], '|', (it.get('brief') or '')[:50], '|', (it.get('url') or '')[:60])
        break
    except Exception as e:
        print('CCTV news api ERR', type(e).__name__, str(e)[:70])

# 2) 新华社评论员文章正文
try:
    html = get('https://www.news.cn/depthobserve/xhsply.html').decode('utf-8', 'ignore')
    links = re.findall(r"<a href='([^']+)'[^>]*>([^<]{8,90})</a>", html)
    arts = [(u2, t.strip()) for u2, t in links if 'news.cn' in u2 and u2.endswith(('.html', '.htm'))]
    print('xinhua articles:', len(arts))
    if arts:
        u2, t = arts[0]
        body = get(u2).decode('utf-8', 'ignore')
        # 提取正文（<p> 标签内容）
        ps = re.findall(r'<p[^>]*>(.*?)</p>', body, re.S)
        txt = ' '.join(re.sub(r'<[^>]+>', '', p).strip() for p in ps if len(re.sub(r'<[^>]+>', '', p).strip()) > 10)
        print('  first article:', t[:40])
        print('  body len:', len(txt))
        print('  head:', txt[:200])
except Exception as e:
    print('xinhua ERR', type(e).__name__, str(e)[:70])
