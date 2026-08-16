# -*- coding: utf-8 -*-
"""通过 B 站搜索 API 找替代教学视频（code==0 且有结果的条目）。"""
import urllib.request, urllib.parse, json, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def search(keyword, n=5):
    q = urllib.parse.quote(keyword)
    url = 'https://api.bilibili.com/x/web-interface/wbi/search/type?search_type=video&keyword=' + q
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=15, context=ctx).read().decode('utf-8'))
    except Exception as e:
        return [('ERR', str(type(e).__name__) + ' ' + str(e), '')]
    if r.get('code') != 0:
        return [('CODE', str(r.get('code')), r.get('message', ''))]
    out = []
    for it in (r.get('data') or {}).get('result') or []:
        bv = it.get('bvid', '')
        title = it.get('title', '').replace('<em class="keyword">', '').replace('</em>', '')
        play = it.get('play', 0)
        out.append((bv, title, play))
        if len(out) >= n:
            break
    return out

for kw in ['资料分析 系统课 花生十三', '资料分析 齐麟', '判断推理 系统课 公考', '言语理解 系统课 公考', '事业单位 职测 系统课']:
    print('=== ' + kw)
    for bv, title, play in search(kw):
        print('  %s | %s | 播放%s' % (bv, title, play))
