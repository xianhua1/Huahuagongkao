# -*- coding: utf-8 -*-
"""找 sourceInfo 的密钥、token 来源"""
import re, os

jsdir = r'C:\Users\admin\DSH\data\saduck_js'
for fn in os.listdir(jsdir):
    code = open(os.path.join(jsdir, fn), encoding='utf-8', errors='ignore').read()
    if 'sourceInfo' in code:
        idx = code.find('sourceInfo')
        print('====', fn)
        # 往前找解密调用和 token
        seg = code[max(0, idx - 1500):idx + 400]
        print(seg.replace('\n', ' ')[-1600:])
        print('---')
