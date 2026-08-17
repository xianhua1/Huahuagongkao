# -*- coding: utf-8 -*-
"""验证修复：把 &amp; 解码为 & 后公式图能否下载"""
import os, re, sys, json, time, urllib.request, urllib.error, html as htmllib
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

print('原始 URL 含 &amp; 的数量:', sum(1 for u in urls if '&amp;' in u))

# 测试前 5 个公式图：原始 vs 解码后
formula_urls = [u for u in urls if 'formulas' in u]
print('公式图总数:', len(formula_urls))

for u in formula_urls[:5]:
    print()
    print('原始:', u[:120])
    fixed = u.replace('&amp;', '&')
    print('修复:', fixed[:120])
    for label, url in [('原始', u), ('解码后', fixed)]:
        try:
            req = urllib.request.Request(url, headers=HDRS)
            data = urllib.request.urlopen(req, timeout=20).read()
            print('  %s: OK len=%d type=%s' % (label, len(data), 'PNG' if data[:4] == b'\x89PNG' else 'other'))
        except urllib.error.HTTPError as e:
            print('  %s: HTTP %d' % (label, e.code))
        except Exception as e:
            print('  %s: %s' % (label, repr(e)[:80]))
