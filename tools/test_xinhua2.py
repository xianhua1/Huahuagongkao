# -*- coding: utf-8 -*-
"""测试新华社评论员列表页解析。"""
import urllib.request, ssl, re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
HDRS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0'}

def get(url, timeout=15):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HDRS), timeout=timeout, context=ctx).read()

# 找页面里的数据接口
html = get('https://www.news.cn/depthobserve/xhsply.html').decode('utf-8', 'ignore')
pats = [r'https?://[^"\'\s]*api[^"\'\s]*', r'url\s*:\s*["\']([^"\']+)', r'getList[^"\']{0,60}', r'columnId[^"\']{0,60}', r'nodeId[^"\']{0,60}']
for p in pats:
    m = re.findall(p, html)
    if m:
        print(p, '->', m[:6])
print('---page tail---')
print(html[-1500:])

