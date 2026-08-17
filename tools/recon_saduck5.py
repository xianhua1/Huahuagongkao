# -*- coding: utf-8 -*-
"""在 JS 中找解密调用点与密钥"""
import re, os

jsdir = r'C:\Users\admin\DSH\data\saduck_js'
for fn in os.listdir(jsdir):
    code = open(os.path.join(jsdir, fn), encoding='utf-8', errors='ignore').read()
    # 找 16 字节字符串常量（可能为密钥）
    keys16 = re.findall(r'["\']([A-Za-z0-9]{16})["\']', code)
    if keys16:
        print(fn, '16字节常量:', list(dict.fromkeys(keys16)))
    # 找解密调用 d(x, 'key') 模式
    calls = re.findall(r'\.d\(([^,]{1,60}),\s*["\']([^"\']{1,40})["\']\)', code)
    if calls:
        print(fn, 'd() 调用:', calls[:6])
    # 找 itemizes 相关代码
    if 'itemizes' in code:
        idx = code.find('itemizes')
        print(fn, 'itemizes 上下文:')
        print(code[max(0, idx - 500):idx + 300].replace('\n', ' ')[:700])
        print('---')
