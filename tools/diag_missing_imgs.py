# -*- coding: utf-8 -*-
"""诊断：重新拉取 2022-gk-xzf 卷数据，提取图片 URL 并逐个测试下载，打印错误详情"""
import os, re, sys, json, time, base64, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crawl_all import TOKEN, KEY_LIST, KEY_ENC, aes_encrypt, aes_decrypt, post, HDRS

# 1) 从清单找 2022 国考行政执法卷的 sid
r = post('https://saduck.top/api/tk/itemizes?type=1', {})
data = json.loads(aes_decrypt(r['result'], KEY_LIST))
target = None
for g in data:
    for s in g.get('tkSources', []):
        src = s.get('source', '')
        if '2022' in src and '国考' in src and '行政执法' in src:
            target = s
            break
    if target:
        break
if not target:
    print('未找到目标卷')
    sys.exit(1)
print('卷:', target['source'], '| sid:', target['sid'])

# 2) 拉取题目
enc_id = aes_encrypt(str(target['sid']), KEY_ENC)
r2 = post('https://saduck.top/api/tk/sourceInfo', {'id': enc_id}, {'token': TOKEN})
print('API code:', r2.get('code'), '| 题目数:', len(r2.get('result') or []))

# 3) 提取所有图片 URL
urls = []
for q in r2.get('result') or []:
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

# 4) 逐个测试（每个最多 2 次尝试）
ok = 0
fail = []
for i, u in enumerate(urls[:40]):
    ok_flag = False
    last_err = ''
    for attempt in range(2):
        try:
            req = urllib.request.Request(u, headers=HDRS)
            data = urllib.request.urlopen(req, timeout=20).read()
            if len(data) >= 100:
                ok_flag = True
                break
            else:
                last_err = 'len=%d <100' % len(data)
        except urllib.error.HTTPError as e:
            last_err = 'HTTP %d' % e.code
        except Exception as e:
            last_err = repr(e)[:80]
        time.sleep(1)
    if ok_flag:
        ok += 1
    else:
        fail.append((u, last_err))
    if (i + 1) % 10 == 0:
        print('进度 %d/%d, 成功 %d' % (i + 1, len(urls[:40]), ok))

print()
print('成功:', ok, '失败:', len(fail))
print('=== 失败详情（前 10）===')
for u, e in fail[:10]:
    print(' ', e, '|', u[:120])
