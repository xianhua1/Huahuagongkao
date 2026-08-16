# -*- coding: utf-8 -*-
"""再次全量复查文档内所有 BV 链接：view + playurl 双重验证。"""
import urllib.request, json, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
HDRS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'}

LINKS = [
    ('BV1fM4m1z7zb', '2025粉笔980(言语/资料)'),
    ('BV1R5g56xEFW', '2027聂佳判断推理全集'),
    ('BV1gv4y127gu', '聂佳老师直播课'),
    ('BV1Rtn1zHE7T', '田鹏秒题必杀技'),
    ('BV1dssTeKERe', '粉笔5000题方程法'),
    ('BV1QD4LzmEE8', '数量四大必拿分题型'),
    ('BV1a7411d71V', '齐麟2018国考资料分析'),
]

def get(url):
    req = urllib.request.Request(url, headers=HDRS)
    return json.loads(urllib.request.urlopen(req, timeout=15, context=ctx).read().decode('utf-8'))

for bv, name in LINKS:
    try:
        r = get('https://api.bilibili.com/x/web-interface/view?bvid=' + bv)
        if r.get('code') != 0:
            print('%s | %s | DEAD(view=%s %s)' % (bv, name, r.get('code'), r.get('message')))
            continue
        d = r['data']
        p = get('https://api.bilibili.com/x/player/playurl?bvid=%s&cid=%s&qn=64' % (bv, d['cid']))
        durls = (p.get('data') or {}).get('durl') or []
        ok = p.get('code') == 0 and len(durls) > 0
        print('%s | %s | %s | 标题:%s | 播放:%s' % (bv, name, 'OK' if ok else 'DEAD(playurl=%s)' % p.get('code'), d.get('title', '')[:38], d.get('stat', {}).get('view', 0)))
    except Exception as e:
        print('%s | %s | ERROR %s' % (bv, name, e))
