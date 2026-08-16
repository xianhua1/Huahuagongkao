# -*- coding: utf-8 -*-
"""批量检测 B 站视频链接有效性（API code==0 表示可看）。"""
import urllib.request, json, ssl, sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BVS = [
    ('BV1fM4m1z7zb', '2025粉笔980系统班(言语等)'),
    ('BV1R5g56xEFW', '2027聂佳判断推理全集'),
    ('BV1eWgr6PEmc', '2027聂佳判断推理备用'),
    ('BV1Rtn1zHE7T', '田鹏秒题必杀技-比例关系'),
    ('BV1dssTeKERe', '粉笔5000题-方程法进阶'),
    ('BV1QD4LzmEE8', '数量关系四大必拿分题型'),
    ('BV1HxuF6ZEbM', '2027粉笔980系统班(资料分析)'),
    ('BV16RMJ61Efv', '2027聂佳判断推理含云盘讲义'),
    ('BV18F411Z7m5', '类比推理(搜索推荐)'),
    ('BV1gv4y127gu', '聂佳老师直播课'),
]

def check(bv):
    url = 'https://api.bilibili.com/x/web-interface/view?bvid=' + bv
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    r = json.loads(urllib.request.urlopen(req, timeout=15, context=ctx).read().decode('utf-8'))
    if r.get('code') == 0:
        d = r['data']
        return 'OK', d.get('title', '')[:45], d.get('stat', {}).get('view', 0)
    return 'DEAD', r.get('message', ''), 0

for bv, name in BVS:
    try:
        st, title, views = check(bv)
        print('%s | %s | %s | %s | 播放%s' % (bv, name, st, title, views))
    except Exception as e:
        print('%s | %s | ERROR %s: %s' % (bv, name, type(e).__name__, e))
