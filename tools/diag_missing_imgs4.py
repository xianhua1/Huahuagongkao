# -*- coding: utf-8 -*-
"""诊断 v4：测试全部 63 张（含全部公式图），看哪些失败、失败模式是什么"""
import os, re, sys, json, time, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crawl_all import TOKEN, KEY_ENC, aes_encrypt, post, HDRS

enc_id = aes_encrypt('19517', KEY_ENC)
r = post('https://saduck.top/api/tk/sourceInfo', {'id': enc_id}, {'token': TOKEN})
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

ok = 0
fail = []
for i, u in enumerate(urls):
    ok_flag = False
    last_err = ''
    for attempt in range(3):
        try:
            req = urllib.request.Request(u, headers=HDRS)
            data = urllib.request.urlopen(req, timeout=25).read()
            if len(data) >= 100:
                ok_flag = True
                break
            last_err = 'len=%d' % len(data)
        except urllib.error.HTTPError as e:
            last_err = 'HTTP %d %s' % (e.code, e.reason)
        except Exception as e:
            last_err = repr(e)[:100]
        time.sleep(1.5)
    if ok_flag:
        ok += 1
    else:
        fail.append((u, last_err))
    if (i + 1) % 10 == 0:
        print('进度 %d/%d 成功 %d' % (i + 1, len(urls), ok))

print()
print('全部测试: 成功', ok, '/', len(urls), '失败', len(fail))
print('=== 失败详情 ===')
for u, e in fail:
    print(' ', e, '|', u[:130])
