# -*- coding: utf-8 -*-
"""搜索登录/注册 API 路径与 token 生成"""
import re, os

jsdir = r'C:\Users\admin\DSH\data\saduck_js'
pats = [r'["\'](/[a-zA-Z0-9_\-/]*(?:login|register|auth|token|sign)[a-zA-Z0-9_\-/]*)["\']',
        r'post\(h\+"([^"]{2,60})"']
seen = set()
for fn in os.listdir(jsdir):
    code = open(os.path.join(jsdir, fn), encoding='utf-8', errors='ignore').read()
    for p in pats:
        for m in re.findall(p, code):
            if m not in seen:
                seen.add(m)
                print(fn, '->', m)
