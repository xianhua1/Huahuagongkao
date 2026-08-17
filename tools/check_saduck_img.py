# -*- coding: utf-8 -*-
"""检查 saduck 图片 URL 格式"""
import json, re

data = json.load(open(r'C:\Users\admin\DSH\data\saduck_sample_raw.json', encoding='utf-8'))
for q in data:
    t = (q.get('title') or '') + (q.get('material') or '') + (q.get('analysis') or '')
    imgs = re.findall(r'<img[^>]*>', t)
    if imgs:
        print('img 标签样例:', imgs[0][:220])
        srcs = re.findall(r'src="([^"]+)"', t)
        print('src:', srcs[:3])
        # 测试第一个图片是否可访问
        if srcs:
            u = srcs[0]
            if u.startswith('/'):
                u = 'https://saduck.top' + u
            try:
                import urllib.request
                r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=15)
                print('图片可访问:', r.status, r.headers.get('Content-Type'), '长度:', r.headers.get('Content-Length'))
            except Exception as e:
                print('图片访问失败:', e)
        break
