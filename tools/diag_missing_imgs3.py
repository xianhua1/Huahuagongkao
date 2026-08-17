# -*- coding: utf-8 -*-
"""诊断 v3：拉取 2022 国考行政执法卷（sid 19517）图片 URL 并逐个测试"""
import os, re, sys, json, time, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crawl_all import TOKEN, KEY_ENC, aes_encrypt, post, HDRS

enc_id = aes_encrypt('19517', KEY_ENC)
r = post('https://saduck.top/api/tk/sourceInfo', {'id': enc_id}, {'token': TOKEN})
print('API code:', r.get('code'), '| 题目数:', len(r.get('result') or []))
if r.get('code') != 0:
    print('message:', r.get('message'))
    sys.exit(1)

urls = []
for q in r.get('result') or []:
    for field in ('title', 'analysis', 'material'):
        html = q.get(field) or ''
        for m in re.finditer(r'src=["\']([^"\']+)["\']', html):
            u = m.group(1)
            if u.startswith('//'):
                u = 'https:' + u
            elif u.startswith('/'):
                u = 'https://saduck.top' + u
            if u not in urls:
                urls.append(u)
print('图片 URL 总数:', len(urls))
print('=== URL 示例 ===')
for u in urls[:8]:
    print(' ', u[:140])

ok = 0
fail = []
for i, u in enumerate(urls[:30]):
    ok_flag = False
    last_err = ''
    for attempt in range(2):
        try:
            req = urllib.request.Request(u, headers=HDRS)
            data = urllib.request.urlopen(req, timeout=20).read()
            if len(data) >= 100:
                ok_flag = True
                break
            last_err = 'len=%d' % len(data)
        except urllib.error.HTTPError as e:
            last_err = 'HTTP %d %s' % (e.code, e.reason)
        except Exception as e:
            last_err = repr(e)[:100]
        time.sleep(1)
    if ok_flag:
        ok += 1
    else:
        fail.append((u, last_err))

print()
print('测试前30张: 成功', ok, '失败', len(fail))
print('=== 失败详情 ===')
for u, e in fail[:12]:
    print(' ', e, '|', u[:130])
