# -*- coding: utf-8 -*-
"""测试央视/新华社数据源可用性。"""
import urllib.request, json, ssl, re, sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
HDRS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0', 'Referer': 'https://tv.cctv.com/'}

def get(url, hdrs=None, timeout=15):
    return urllib.request.urlopen(urllib.request.Request(url, headers=hdrs or HDRS), timeout=timeout, context=ctx).read()

# 1) CCTV API 变体
for u in ['https://api.cntv.cn/NewVideo/getVideoListByColumn?serviceId=tvcctv&id=TOPC1451528971114112&p=1&n=10&sort=desc&mode=0',
          'https://api.cntv.cn/NewVideo/getVideoListByColumn?id=TOPC1451528971114112&serviceId=tvcctv&n=10&sort=desc&p=1&mode=0&cb=jsonp1']:
    try:
        raw = get(u).decode('utf-8', 'ignore')
        raw2 = re.sub(r'^[^(]*\(|\)\s*;?\s*$', '', raw).strip()
        d = json.loads(raw2)
        v = (d.get('data') or {}).get('list') or []
        print('CCTV var OK items:', len(v))
        for it in v[:3]:
            print('  -', it.get('title'), '|', it.get('url'))
        break
    except Exception as e:
        print('CCTV var ERR', type(e).__name__, str(e)[:80])

# 2) CCTV 网页（tv.cctv.com/lm/xwlb）
try:
    html = get('https://tv.cctv.com/lm/xwlb/').decode('utf-8', 'ignore')
    m = re.findall(r'"title":"([^"]{4,60})"', html)
    print('CCTV page titles:', len(m), m[:3])
    urls = re.findall(r'"url":"([^"]+)"', html)
    print('CCTV page urls:', len(urls), urls[:2])
except Exception as e:
    print('CCTV page ERR', type(e).__name__, str(e)[:80])

# 3) 新华社 新华网评 网页
try:
    html = get('http://www.news.cn/comment/').decode('utf-8', 'ignore')
    links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>([^<]{8,60})</a>', html)
    seen = []
    for u2, t in links:
        if 'news.cn' in u2 and u2.endswith(('.html', '.htm')):
            seen.append((u2.strip(), t.strip()))
    print('XINHUA page links:', len(seen))
    for u2, t in seen[:6]:
        print('  -', t, '|', u2[:90])
except Exception as e:
    print('XINHUA page ERR', type(e).__name__, str(e)[:80])

# 4) 新华社客户端 API 候选
for u in ['http://qc.wa.news.cn/nodeart/list?nid=11147664&pgnum=1&cnt=8&tp=1&page=0',
          'http://qc.wa.news.cn/nodeart/list?nid=11147664&pgnum=1&cnt=8&tp=1']:
    try:
        raw = get(u, {'User-Agent': 'Mozilla/5.0'}).decode('utf-8', 'ignore')
        d = json.loads(raw)
        items = ((d.get('data') or {}).get('list') or [])
        print('XINHUA api OK items:', len(items))
        for it in items[:3]:
            print('  -', it.get('Title') or it.get('title'))
        break
    except Exception as e:
        print('XINHUA api ERR', type(e).__name__, str(e)[:80])
