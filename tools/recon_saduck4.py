# -*- coding: utf-8 -*-
"""分析 app.js 找解密函数"""
import urllib.request, ssl, re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
HDRS = {'User-Agent': 'Mozilla/5.0'}

code = urllib.request.urlopen(urllib.request.Request('https://www.saduck.top/assets/app.CRzsxcgK.js', headers=HDRS), timeout=30, context=ctx).read().decode('utf-8', 'ignore')
print('app.js 大小:', len(code))
open(r'C:\Users\admin\DSH\data\saduck_app.js', 'w', encoding='utf-8').write(code)

# 找加密/解密关键词
for kw in ['decrypt', 'encrypt', 'AES', 'CryptoJS', 'atob', 'base64', 'secretKey', 'key:', 'iv:', 'DES', 'RSA']:
    idxs = [m.start() for m in re.finditer(re.escape(kw), code)]
    print(kw, '出现次数:', len(idxs))
    if idxs and kw in ('decrypt', 'atob', 'secretKey'):
        i = idxs[0]
        print('  上下文:', code[max(0, i - 120):i + 200].replace('\n', ' ')[:320])
